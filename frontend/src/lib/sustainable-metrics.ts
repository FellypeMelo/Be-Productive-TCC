/** Privacy-safe participant metric accumulator.
 * It receives only normalized reserve computed by EdgeFatigueEngine.
 */
export interface LocalReserveAggregate {
    version: 1;
    observed_seconds: number;
    normalized_reserve_auc: number;
    updated_at: number;
}

export class LocalReserveAccumulator {
    private observedSeconds = 0;
    private auc = 0;

    observe(normalizedReserve: number, dtSeconds: number): void {
        if (!Number.isFinite(normalizedReserve) || !Number.isFinite(dtSeconds) || dtSeconds <= 0) return;
        const reserve = Math.max(0, Math.min(1, normalizedReserve));
        this.auc += reserve * dtSeconds;
        this.observedSeconds += dtSeconds;
    }

    snapshot(now = Date.now()): LocalReserveAggregate {
        return {
            version: 1,
            observed_seconds: this.observedSeconds,
            normalized_reserve_auc: this.observedSeconds > 0 ? this.auc / this.observedSeconds : 0,
            updated_at: now,
        };
    }

    restore(snapshot: LocalReserveAggregate): boolean {
        if (snapshot?.version !== 1 || !Number.isFinite(snapshot.observed_seconds) ||
            !Number.isFinite(snapshot.normalized_reserve_auc) || snapshot.observed_seconds < 0 ||
            snapshot.normalized_reserve_auc < 0 || snapshot.normalized_reserve_auc > 1) return false;
        this.observedSeconds = snapshot.observed_seconds;
        this.auc = snapshot.normalized_reserve_auc * snapshot.observed_seconds;
        return true;
    }
}
