// Edge AI / on-device fatigue engine.
//
// This module makes the paper's central privacy claim literally true: ALL fatigue
// inference (the Ego-Depletion EDO and the Hawkes dual-kernel) runs IN THE BROWSER.
// Raw behavioral telemetry (v_scroll, v_alt) is NEVER sent to any server — it lives
// and dies inside this class. There are intentionally ZERO network calls here.
//
// The math mirrors the Python recommender domain (recommender/src/domain/math_models.py
// and inference/hawkes_classifier.py) so on-device and (former) server results agree:
//
//   Ego depletion (Eq. 4):
//     new_R = clamp(0, R + (mu_rest*(R_max - R) - (k1*v_scroll + k2*v_alt)) * dt, R_max)
//
//   Hawkes intensity (Eq. 2):
//     lambda_s1 = Σ_{tk∈S1, tk<t} alpha1*exp(-beta1*(t-tk))
//     lambda_s2 = Σ_{tm∈S2, tm<t} alpha2*exp(-beta2*(t-tm))
//     ratio = lambda_s1 / lambda_s2   (System 1 dominant when ratio >= 1)
//   An interaction is labeled S1 when the interval preceding it is < ~3s, else S2.
//
//   Friction from reserve ratio R/R_max:
//     < 0.20 -> "block", < 0.35 -> "high", < 0.60 -> "mild", else "none".

export type FrictionLevel = 'none' | 'mild' | 'high' | 'block';

/** Ego-Depletion EDO parameters (Eq. 4). Defaults mirror the paper's suggested values. */
export interface FatigueParams {
    /** Passive recovery rate toward R_max (per second). */
    muRest: number;
    /** Scroll-velocity depletion coefficient (kappa_1). */
    k1: number;
    /** Context-switch depletion coefficient (kappa_2). */
    k2: number;
    /** Maximum cognitive reserve (R_max). */
    rMax: number;
}

/** Hawkes dual-kernel parameters (Eq. 2). Defaults mirror HawkesClassifier. */
export interface HawkesParams {
    /** System 1 (impulsive) jump size — strong. */
    alpha1: number;
    /** System 1 decay rate — fast. */
    beta1: number;
    /** System 2 (deliberate) jump size — moderate. */
    alpha2: number;
    /** System 2 decay rate — slow (long trace). */
    beta2: number;
    /** Interval (seconds) below which an interaction is impulsive (System 1). */
    s1IntervalThreshold: number;
}

export interface EdgeFatigueOptions {
    /** Starting reserve. Defaults to fatigue.rMax (full). */
    initialReserve?: number;
    fatigue?: Partial<FatigueParams>;
    hawkes?: Partial<HawkesParams>;
    /**
     * Injectable clock returning the current time in SECONDS. Defaults to a wall
     * clock. Exposed purely to make the engine deterministically testable.
     */
    now?: () => number;
}

// --- Sensible defaults ---------------------------------------------------------

const DEFAULT_FATIGUE: FatigueParams = {
    muRest: 0.1,
    k1: 0.1,
    k2: 0.5,
    rMax: 100,
};

const DEFAULT_HAWKES: HawkesParams = {
    alpha1: 1.0,
    beta1: 0.5,
    alpha2: 0.5,
    beta2: 0.01,
    s1IntervalThreshold: 3.0,
};

// Scroll pixels/second is normalized by this factor into the dimensionless v_scroll
// the EDO expects. Tuned against muRest=0.1 so that (roughly) sustained scrolling at
// ~800 px/s settles reserve near the "mild" band and ~1600 px/s drives it to "block".
const SCROLL_PX_PER_UNIT = 20;
// Cap on normalized v_scroll so a single violent flick cannot instantly nuke reserve.
const MAX_V_SCROLL = 150;
// Ignore sub-pixel jitter when recording Hawkes interaction events.
const SCROLL_EVENT_MIN_PX = 4;
// Hawkes rolling window (seconds). Old events (esp. fast-decaying S1) are pruned.
const HAWKES_WINDOW_SECONDS = 180;
// Hard cap on buffered interaction timestamps (memory bound).
const HAWKES_MAX_EVENTS = 256;
// Minimum interactions before the Hawkes ratio is trusted for escalation.
const HAWKES_MIN_EVENTS = 4;
// ratio >= this => System 1 (impulsive) dominant.
const HAWKES_DOMINANCE_THRESHOLD = 1.0;

const LEVEL_ORDER: FrictionLevel[] = ['none', 'mild', 'high', 'block'];

function clamp(value: number, lo: number, hi: number): number {
    if (!Number.isFinite(value)) return lo;
    return Math.max(lo, Math.min(hi, value));
}

/**
 * On-device fatigue engine. Holds the user's current cognitive reserve, integrates the
 * Ego-Depletion EDO from locally-measured signals, and classifies interaction rhythm via
 * a Hawkes dual-kernel. Everything stays in memory in the browser.
 */
export class EdgeFatigueEngine {
    private readonly fatigue: FatigueParams;
    private readonly hawkes: HawkesParams;
    private readonly now: () => number;

    /** Current cognitive reserve R(t). */
    private reserve: number;

    // Per-tick accumulators (reset on every tick()).
    private scrollDistanceAccum = 0; // total |px| scrolled since last tick
    private contextSwitchAccum = 0; // context switches since last tick

    // Absolute interaction timestamps (seconds) for the Hawkes process.
    private eventTimes: number[] = [];

    // Cached outputs.
    private lastHawkesRatio = 0;
    private lastFriction: FrictionLevel = 'none';

    constructor(options: EdgeFatigueOptions = {}) {
        this.fatigue = { ...DEFAULT_FATIGUE, ...(options.fatigue ?? {}) };
        this.hawkes = { ...DEFAULT_HAWKES, ...(options.hawkes ?? {}) };
        this.now = options.now ?? (() => Date.now() / 1000);

        const start = options.initialReserve ?? this.fatigue.rMax;
        this.reserve = clamp(start, 0, this.fatigue.rMax);
    }

    /**
     * Record a scroll measurement. `scrollDeltaPixels` is the (signed or unsigned) change
     * in scroll position; `dtSeconds` is the elapsed time since the previous measurement.
     * Accumulates distance for the EDO and records a Hawkes interaction event when the
     * movement is non-trivial. No network I/O.
     */
    recordScroll(scrollDeltaPixels: number, dtSeconds: number): void {
        const distance = Math.abs(scrollDeltaPixels);
        if (!Number.isFinite(distance) || distance <= 0) return;

        this.scrollDistanceAccum += distance;

        // A real scroll gesture is an interaction on the Hawkes timeline. `dtSeconds` is
        // accepted for API symmetry / future velocity weighting; the timeline itself is
        // driven by the wall clock so inter-event intervals stay physically meaningful.
        void dtSeconds;
        if (distance >= SCROLL_EVENT_MIN_PX) {
            this.pushEvent();
        }
    }

    /**
     * Record a context switch (tab/window blur, visibility change away). Feeds v_alt in
     * the EDO and counts as a Hawkes interaction.
     */
    recordContextSwitch(): void {
        this.contextSwitchAccum += 1;
        this.pushEvent();
    }

    /**
     * Integrate the Ego-Depletion EDO one step over `dtSeconds` from the locally-estimated
     * v_scroll / v_alt, update the reserve R, refresh the Hawkes ratio, and recompute the
     * friction level. Returns the new friction level.
     */
    tick(dtSeconds: number): FrictionLevel {
        const dt = Number.isFinite(dtSeconds) && dtSeconds > 0 ? dtSeconds : 0;

        // Local behavioral signal estimates (never leave this object).
        const vScroll = clamp(this.scrollDistanceAccum / dt / SCROLL_PX_PER_UNIT, 0, MAX_V_SCROLL);
        const vAlt = dt > 0 ? this.contextSwitchAccum / dt : 0;

        // Eq. 4 — Ego depletion kinetics.
        const load = this.fatigue.k1 * vScroll + this.fatigue.k2 * vAlt;
        const recovery = this.fatigue.muRest * (this.fatigue.rMax - this.reserve);
        const delta = (recovery - load) * dt;
        this.reserve = clamp(this.reserve + delta, 0, this.fatigue.rMax);

        // Consume this tick's accumulators.
        this.scrollDistanceAccum = 0;
        this.contextSwitchAccum = 0;

        // Eq. 2 — Hawkes intensity ratio from the local interaction buffer.
        this.lastHawkesRatio = this.computeHawkesRatio();

        this.lastFriction = this.deriveFriction();
        return this.lastFriction;
    }

    /** Current friction level, escalated by Hawkes System-1 dominance where warranted. */
    frictionLevel(): FrictionLevel {
        return this.lastFriction;
    }

    // --- Read-only accessors (debug / tests) ----------------------------------

    getReserve(): number {
        return this.reserve;
    }

    getReserveRatio(): number {
        return this.fatigue.rMax > 0 ? this.reserve / this.fatigue.rMax : 0;
    }

    getHawkesRatio(): number {
        return this.lastHawkesRatio;
    }

    /** Reset all in-memory state to a fresh, full-reserve engine. */
    reset(): void {
        this.reserve = this.fatigue.rMax;
        this.scrollDistanceAccum = 0;
        this.contextSwitchAccum = 0;
        this.eventTimes = [];
        this.lastHawkesRatio = 0;
        this.lastFriction = 'none';
    }

    // --- Internals ------------------------------------------------------------

    private pushEvent(): void {
        const t = this.now();
        if (!Number.isFinite(t)) return;
        this.eventTimes.push(t);
        this.pruneEvents(t);
    }

    private pruneEvents(nowSec: number): void {
        const cutoff = nowSec - HAWKES_WINDOW_SECONDS;
        // Drop events older than the rolling window.
        let start = 0;
        while (start < this.eventTimes.length && this.eventTimes[start] < cutoff) {
            start++;
        }
        if (start > 0) this.eventTimes = this.eventTimes.slice(start);
        // Hard memory cap: keep the most recent events.
        if (this.eventTimes.length > HAWKES_MAX_EVENTS) {
            this.eventTimes = this.eventTimes.slice(this.eventTimes.length - HAWKES_MAX_EVENTS);
        }
    }

    /**
     * Hawkes dual-kernel ratio lambda_s1 / lambda_s2 evaluated just after the latest event.
     * Mirrors HawkesClassifier: label each interaction S1/S2 by the interval preceding it,
     * then sum self-exciting contributions across history.
     */
    private computeHawkesRatio(): number {
        const events = this.eventTimes;
        if (events.length < 2) return 0;

        const s1: number[] = [];
        const s2: number[] = [];
        for (let i = 0; i < events.length; i++) {
            if (i === 0) {
                // First buffered interaction = deliberate re-engagement (System 2).
                s2.push(events[i]);
                continue;
            }
            const gap = events[i] - events[i - 1];
            if (gap < this.hawkes.s1IntervalThreshold) s1.push(events[i]);
            else s2.push(events[i]);
        }

        const t = events[events.length - 1] + 1e-9; // evaluate just after the last event
        const lambdaS1 = s1.reduce(
            (acc, tk) => (tk < t ? acc + this.hawkes.alpha1 * Math.exp(-this.hawkes.beta1 * (t - tk)) : acc),
            0,
        );
        const lambdaS2 = s2.reduce(
            (acc, tm) => (tm < t ? acc + this.hawkes.alpha2 * Math.exp(-this.hawkes.beta2 * (t - tm)) : acc),
            0,
        );

        if (lambdaS2 <= 1e-12) return lambdaS1 > 0 ? Number.POSITIVE_INFINITY : 0;
        return lambdaS1 / lambdaS2;
    }

    private deriveFriction(): FrictionLevel {
        const ratio = this.getReserveRatio();
        let base: FrictionLevel;
        if (ratio < 0.2) base = 'block';
        else if (ratio < 0.35) base = 'high';
        else if (ratio < 0.6) base = 'mild';
        else base = 'none';

        // Optional escalation: sustained System-1 (impulsive) dominance nudges friction up
        // by one step, but Hawkes alone never forces a hard "block" — that requires genuine
        // reserve depletion.
        const system1Dominant =
            this.eventTimes.length >= HAWKES_MIN_EVENTS &&
            this.lastHawkesRatio >= HAWKES_DOMINANCE_THRESHOLD;

        if (!system1Dominant) return base;

        const baseIdx = LEVEL_ORDER.indexOf(base);
        const escalatedIdx = Math.min(baseIdx + 1, LEVEL_ORDER.indexOf('high'));
        return LEVEL_ORDER[Math.max(baseIdx, escalatedIdx)];
    }
}
