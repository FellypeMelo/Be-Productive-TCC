<script lang="ts">
    import { currentUser, isLoggedIn } from "$lib/stores";
    import { api, type Content } from "$lib/api";
    import { onMount, onDestroy } from "svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import { animate, stagger } from "motion";
    import { EdgeFatigueEngine, type FrictionLevel } from "$lib/fatigue";
    import { LocalReserveAccumulator } from "$lib/sustainable-metrics";

    let feed = $state<Content[]>([]);
    let isLoading = $state(true);
    let error = $state("");
    let category = $state<string | null>(null);
    let selectedTopic = $state<number | null>(null);
    let topics = $state<any[]>([]);
    let gridRef: HTMLElement;
    let personalizationEnabled = $state(false);
    let fatigueEnabled = $state(false);
    let researchConsentEnabled = $state(false);
    let modelVersion = "unknown";
    let experiment = "none";
    let experimentID = "";
    let assignmentVersion = "";
    let variant = "not_eligible";
    let explanations = $state<Record<number, string[]>>({});

    // Friction state — computed 100% ON-DEVICE by the Edge fatigue engine.
    // Raw telemetry (v_scroll, v_alt) NEVER leaves the browser.
    let frictionLevel = $state<FrictionLevel>("none");

    // On-device fatigue inference (Ego-Depletion EDO + Hawkes dual-kernel).
    const fatigueEngine = new EdgeFatigueEngine();
    const reserveMetrics = new LocalReserveAccumulator();
    let fatigueInterval: ReturnType<typeof setInterval> | null = null;
    let lastScrollY = 0;
    let lastScrollTime = Date.now();
    let lastTickTime = Date.now();
    // Throttle so a scroll gesture (which fires many events) is sampled, not flooded.
    let lastScrollSampleTime = 0;
    let lastProtectionOrder = false;

    // Explicit-confirm gate for the "block" overlay (no one-click no-op dismissal).
    let blockAcknowledged = $state(false);
    let blockCountdown = $state(0);
    let blockCountdownInterval: ReturnType<typeof setInterval> | null = null;

    const TICK_MS = 1500;
    const SCROLL_SAMPLE_MS = 200;
    const BLOCK_WAIT_SECONDS = 5;
    const FATIGUE_STORAGE_KEY = "be-productive:fatigue:v1";
    const RESERVE_METRICS_STORAGE_KEY = "be-productive:metrics:reserve:v1";
    const REASON_LABELS: Record<string, string> = {
        matches_your_topics: "alinhado aos seus interesses",
        high_quality: "alta qualidade",
        positive_history: "útil para você antes",
        recent: "conteúdo recente",
        not_repetitive: "traz variedade",
        negative_history_penalty: "preferência ajustada",
        repetition_penalty: "repetição reduzida",
        balanced_candidate: "escolha equilibrada",
        safety_penalty: "alcance reduzido por segurança",
        protective_dense_content: "favorece atenção profunda",
        deliberative_state_boost: "apoia seu momento de foco",
        diversity_rerank: "amplia perspectivas",
    };

    function humanReasons(contentID: number): string[] {
        return (explanations[contentID] || [])
            .map((reason) => REASON_LABELS[reason])
            .filter((reason): reason is string => Boolean(reason))
            .slice(0, 3);
    }

    // Nomes de autores para o feed de demonstração (leitura apenas).
    const AUTHORS: Record<number, string> = {
        1: "Marina Alves",
        2: "Rafael Nogueira",
        3: "Bianca Costa",
        4: "Téo Ferraz",
        5: "Helena Prado",
        6: "Caio Menezes",
    };
    function authorName(id: number): string {
        return AUTHORS[id] ?? `Autor ${id}`;
    }
    function formatDate(d: string): string {
        try {
            return new Date(d).toLocaleDateString("pt-BR", {
                day: "2-digit",
                month: "short",
            });
        } catch {
            return d;
        }
    }

    // Feed de demonstração — usado como fallback quando o backend está indisponível.
    // Conteúdo rico em português para manter o app "vivo" mesmo offline.
    const mockFeed: Content[] = [
        {
            id_conteudo: 1,
            titulo: "O mito da multitarefa: por que o foco profundo rende mais",
            corpo: "Alternar entre tarefas cobra um imposto cognitivo silencioso. Cada troca de contexto deixa um resíduo de atenção na atividade anterior — e a conta chega no fim do dia como cansaço difuso. Este ensaio destrincha a ciência do trabalho profundo e propõe blocos de 90 minutos sem notificações.",
            categoria: "PRODUTIVIDADE",
            tipo_de_midia: "TEXTO",
            autor_id: 1,
            data_publicacao: "2026-02-06",
            score_de_qualidade: 0.94,
            tags_relevantes: "foco, atenção, deep work",
            topics: [
                { id_topico: 1, nome_topico: "Foco", descricao: "" },
                { id_topico: 3, nome_topico: "Hábitos", descricao: "" },
            ],
        },
        {
            id_conteudo: 2,
            titulo: "Ruído marrom: 45 minutos para uma concentração serena",
            corpo: "Uma paisagem sonora contínua, sem picos que roubam a atenção. Ideal para leitura, estudo ou escrita — o tipo de som que desaparece e deixa só o trabalho.",
            categoria: "PRODUTIVIDADE",
            tipo_de_midia: "AUDIO",
            autor_id: 2,
            data_publicacao: "2026-02-05",
            score_de_qualidade: 0.89,
            tags_relevantes: "som ambiente, concentração",
            topics: [{ id_topico: 1, nome_topico: "Foco", descricao: "" }],
        },
        {
            id_conteudo: 3,
            titulo: "Pomodoro na prática: um dia real de trabalho profundo",
            corpo: "Acompanhe uma jornada completa dividida em ciclos de 25 minutos, com pausas deliberadas e um ritual de encerramento que protege o descanso.",
            categoria: "PRODUTIVIDADE",
            tipo_de_midia: "VIDEO",
            autor_id: 3,
            data_publicacao: "2026-02-04",
            score_de_qualidade: 0.91,
            tags_relevantes: "pomodoro, rotina, produtividade",
            topics: [
                { id_topico: 3, nome_topico: "Hábitos", descricao: "" },
                { id_topico: 1, nome_topico: "Foco", descricao: "" },
            ],
        },
        {
            id_conteudo: 4,
            titulo: "Higiene do sono e desempenho cognitivo",
            corpo: "Dormir bem não é luxo — é infraestrutura da mente. Veja como luz, temperatura e horários regulares moldam sua clareza mental no dia seguinte.",
            categoria: "PRODUTIVIDADE",
            tipo_de_midia: "TEXTO",
            autor_id: 5,
            data_publicacao: "2026-02-03",
            score_de_qualidade: 0.96,
            tags_relevantes: "sono, saúde, cognição",
            topics: [{ id_topico: 2, nome_topico: "Bem-estar", descricao: "" }],
        },
        {
            id_conteudo: 5,
            titulo: "A nova onda do cinema brasileiro",
            corpo: "Diretores independentes estão reinventando a linguagem visual do país. Um passeio curado por filmes que equilibram lentidão e beleza.",
            categoria: "ENTRETENIMENTO",
            tipo_de_midia: "VIDEO",
            autor_id: 4,
            data_publicacao: "2026-02-02",
            score_de_qualidade: 0.83,
            tags_relevantes: "cinema, cultura, arte",
            topics: [{ id_topico: 4, nome_topico: "Cultura", descricao: "" }],
        },
        {
            id_conteudo: 6,
            titulo: "Contos curtos para uma pausa consciente",
            corpo: "Três narrativas breves, feitas para caber num intervalo de café. Ficção que relaxa sem prender você numa rolagem infinita.",
            categoria: "ENTRETENIMENTO",
            tipo_de_midia: "TEXTO",
            autor_id: 6,
            data_publicacao: "2026-02-01",
            score_de_qualidade: 0.8,
            tags_relevantes: "literatura, contos, pausa",
            topics: [{ id_topico: 4, nome_topico: "Cultura", descricao: "" }],
        },
        {
            id_conteudo: 7,
            titulo: "Jazz de fim de tarde: uma seleção calma",
            corpo: "Standards suaves e improvisos delicados para desacelerar o ritmo. A trilha certa para encerrar o dia sem estímulo em excesso.",
            categoria: "ENTRETENIMENTO",
            tipo_de_midia: "AUDIO",
            autor_id: 2,
            data_publicacao: "2026-01-31",
            score_de_qualidade: 0.86,
            tags_relevantes: "música, jazz, relaxar",
            topics: [{ id_topico: 2, nome_topico: "Bem-estar", descricao: "" }],
        },
        {
            id_conteudo: 8,
            titulo: "A arte lenta da cerâmica",
            corpo: "Um documentário meditativo sobre o tempo, as mãos e o barro. Um convite a valorizar o processo em vez do resultado imediato.",
            categoria: "ENTRETENIMENTO",
            tipo_de_midia: "VIDEO",
            autor_id: 3,
            data_publicacao: "2026-01-30",
            score_de_qualidade: 0.88,
            tags_relevantes: "documentário, artesanato, slow",
            topics: [{ id_topico: 4, nome_topico: "Cultura", descricao: "" }],
        },
    ];

    onMount(async () => {
        if (!$isLoggedIn) return;
        await loadPrivacySettings();
        await Promise.all([loadTopics(), loadFeed()]);
        if (fatigueEnabled) startFatigueMonitoring();
    });

    onDestroy(() => {
        stopFatigueMonitoring();
    });

    // On-device fatigue monitoring: measure scroll velocity + context switches locally,
    // feed them into the Edge engine, and derive friction locally. NOTHING is uploaded.
    function startFatigueMonitoring() {
        if (typeof window === "undefined" || typeof document === "undefined") return;

        lastScrollY = window.scrollY || document.documentElement.scrollTop;
        lastScrollTime = Date.now();
        lastTickTime = Date.now();

        window.addEventListener("scroll", handleScroll, { passive: true });
        document.addEventListener("visibilitychange", handleVisibility);

        fatigueInterval = setInterval(runFatigueTick, TICK_MS);
    }

    function stopFatigueMonitoring() {
        if (fatigueInterval) {
            clearInterval(fatigueInterval);
            fatigueInterval = null;
        }
        if (blockCountdownInterval) {
            clearInterval(blockCountdownInterval);
            blockCountdownInterval = null;
        }
        if (typeof window !== "undefined") {
            window.removeEventListener("scroll", handleScroll);
        }
        if (typeof document !== "undefined") {
            document.removeEventListener("visibilitychange", handleVisibility);
        }
    }

    // Sample scroll movement locally and hand raw deltas to the on-device engine only.
    function handleScroll() {
        try {
            const now = Date.now();
            if (now - lastScrollSampleTime < SCROLL_SAMPLE_MS) return;

            const currentScrollY =
                window.scrollY || document.documentElement.scrollTop;
            const dt = (now - lastScrollTime) / 1000;
            const delta = currentScrollY - lastScrollY;

            fatigueEngine.recordScroll(delta, dt);

            lastScrollY = currentScrollY;
            lastScrollTime = now;
            lastScrollSampleTime = now;
        } catch {
            // FAIL CLOSED — never drop below protective friction.
            escalateFrictionOnError();
        }
    }

    function handleVisibility() {
        try {
            if (typeof document !== "undefined" && document.hidden) {
                fatigueEngine.recordContextSwitch();
            }
        } catch {
            escalateFrictionOnError();
        }
    }

    function runFatigueTick() {
        try {
            const now = Date.now();
            const dt = (now - lastTickTime) / 1000;
            lastTickTime = now;

            const level = fatigueEngine.tick(dt);
            frictionLevel = level;
            localStorage.setItem(FATIGUE_STORAGE_KEY, JSON.stringify(fatigueEngine.snapshot()));
            reserveMetrics.observe(fatigueEngine.getReserveRatio(), dt);
            localStorage.setItem(RESERVE_METRICS_STORAGE_KEY, JSON.stringify(reserveMetrics.snapshot()));

            // Only this binary order leaves the device. A threshold crossing
            // refreshes the ranking without exposing scroll/context telemetry.
            const protectionOrder = isProtectionOrderActive();
            if (protectionOrder !== lastProtectionOrder) void loadFeed();

            if (level !== "block") {
                // User is no longer blocked — clear any pending acknowledgement gate.
                resetBlockGate();
            }
        } catch {
            escalateFrictionOnError();
        }
    }

    // Protective fallback: if anything in the fatigue path errors, default to at least
    // "mild" friction. We never silently drop to "none".
    function escalateFrictionOnError() {
        const order: FrictionLevel[] = ["none", "mild", "high", "block"];
        if (order.indexOf(frictionLevel) < order.indexOf("mild")) {
            frictionLevel = "mild";
        }
    }

    async function loadTopics() {
        if (!$currentUser) return;
        try {
            const userTopics = await api.getUserTopics($currentUser.id_usuario);
            topics = userTopics;
        } catch (err) {
            console.error("Error loading topics:", err);
            topics = [
                { id_topico: 1, nome_topico: "Focus" },
                { id_topico: 2, nome_topico: "Health" },
                { id_topico: 3, nome_topico: "Coding" },
            ];
        }
    }

    async function loadPrivacySettings() {
        if (!$currentUser) return;
        try {
            const settings = await api.getSettings($currentUser.id_usuario);
            personalizationEnabled = settings.personalizacao_ativa;
            fatigueEnabled = settings.sugestao_saudavel_ativa;
            researchConsentEnabled = settings.consentimento_pesquisa === true;
            if (fatigueEnabled) {
                const saved = localStorage.getItem(FATIGUE_STORAGE_KEY);
                if (saved) {
                    fatigueEngine.restore(JSON.parse(saved));
                    frictionLevel = fatigueEngine.frictionLevel();
                }
                const savedMetrics = localStorage.getItem(RESERVE_METRICS_STORAGE_KEY);
                if (savedMetrics) reserveMetrics.restore(JSON.parse(savedMetrics));
            }
        } catch {
            personalizationEnabled = false;
            fatigueEnabled = false;
        }
    }

    async function loadFeed() {
        isLoading = true;
        error = "";
        try {
            const userID = $currentUser?.id_usuario || 1;
            const protectionOrder = isProtectionOrderActive();
            lastProtectionOrder = protectionOrder;
            const result = await api.getFeed(
                userID,
                category || undefined,
                selectedTopic || undefined,
                20,
                false,
                undefined,
                protectionOrder,
            );

            feed = result.items;
            modelVersion = result.model_version;
            experiment = result.experiment;
            experimentID = result.experiment_id || "";
            assignmentVersion = result.assignment_version || "";
            variant = result.variant || "not_eligible";
            explanations = result.explanations || {};
            if (researchConsentEnabled && result.eligible &&
                (result.variant === "control" || result.variant === "treatment") &&
                result.experiment_id && result.assignment_version) {
                void api.recordExperimentExposure({
                    event_id: eventID(),
                    experiment_id: result.experiment_id,
                    variant: result.variant,
                    assignment_version: result.assignment_version,
                    algorithm_version: result.model_version,
                    request_id: eventID(),
                    eligible: true,
                    served: feed.length > 0,
                    fallback: result.fallback,
                    position_count: Math.min(feed.length, 50),
                }).catch(() => {
                    // Exposure recording must never block feed navigation.
                });
            }
            if (personalizationEnabled && !result.fallback) {
                void Promise.allSettled(feed.map((content, position) =>
                    recordEvent(content.id_conteudo, "impression", position)
                ));
            }
            // NOTE: friction is NOT read from the server anymore — it is computed
            // entirely on-device by the Edge fatigue engine (see runFatigueTick).

            // Animations
            setTimeout(() => {
                if (gridRef) {
                    animate(
                        "article",
                        { opacity: [0, 1], y: [10, 0] },
                        {
                            delay: stagger(0.05),
                            duration: 0.4,
                        },
                    );
                }
            }, 50);
        } catch (err) {
            // A local protection order is fail-closed even when the network is
            // unavailable: never replace a protected feed with demo content.
            feed = isProtectionOrderActive() ? [] : mockFeed;
            error = isProtectionOrderActive()
                ? "A proteção continua ativa, mas o servidor não respondeu. Mostrando uma pausa segura."
                : "Estamos usando uma seleção local enquanto reconectamos ao servidor.";
            // Do not reset friction here — it is owned by the on-device engine.
        } finally {
            isLoading = false;
        }
    }

    function eventID(): string {
        if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
            return crypto.randomUUID();
        }
        return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    }

    async function recordEvent(
        contentID: number,
        type: "impression" | "open" | "complete" | "hide",
        position: number,
    ) {
        if (!personalizationEnabled) return;
        try {
            if (type === "open") {
                sessionStorage.setItem("be-productive:ranking-context", JSON.stringify({
                    algorithm: modelVersion, experiment, position,
                }));
            }
            await api.recordContentEvent(contentID, {
                event_id: eventID(), type, dwell_seconds: 0, position,
                algorithm: modelVersion, experiment,
            });
        } catch {
            // Analytics must never block feed navigation.
        }
    }

    function isProtectionOrderActive(): boolean {
        if (!fatigueEnabled) return false;
        const level = fatigueEngine.frictionLevel();
        return level === "high" || level === "block";
    }

    function toggleCategory(cat: string | null) {
        category = cat;
        loadFeed();
    }

    function toggleTopic(id: number | null) {
        selectedTopic = id;
        loadFeed();
    }

    // HIGH-friction banner: a soft nudge; dismissing just hides the banner locally.
    // The engine keeps running, so if fatigue persists the banner returns on the next tick.
    function dismissFriction() {
        frictionLevel = "mild";
    }

    // BLOCK overlay: NOT a one-click no-op. The user must (a) tick the acknowledgement
    // checkbox AND (b) wait out a short reflective countdown before proceeding.
    function acknowledgeBlock() {
        blockAcknowledged = true;
        startBlockCountdown();
    }

    function startBlockCountdown() {
        if (blockCountdownInterval) return;
        blockCountdown = BLOCK_WAIT_SECONDS;
        blockCountdownInterval = setInterval(() => {
            blockCountdown = Math.max(0, blockCountdown - 1);
            if (blockCountdown <= 0 && blockCountdownInterval) {
                clearInterval(blockCountdownInterval);
                blockCountdownInterval = null;
            }
        }, 1000);
    }

    function resetBlockGate() {
        blockAcknowledged = false;
        blockCountdown = 0;
        if (blockCountdownInterval) {
            clearInterval(blockCountdownInterval);
            blockCountdownInterval = null;
        }
    }

    // Proceed only after the explicit confirm step is satisfied.
    function proceedPastBlock() {
        if (!blockAcknowledged || blockCountdown > 0) return;
        resetBlockGate();
        // Drop to "high" (still protective/grayscale) rather than a clean "none".
        frictionLevel = "high";
    }
</script>

<svelte:head>
    <title>Feed | Be Productive</title>
</svelte:head>

<!-- Filtro grayscale aplicado em fricção alta/bloqueio -->
<div class="flex min-h-screen {frictionLevel === 'high' || frictionLevel === 'block' ? 'feed-grayscale' : ''}">
    <Sidebar />

    <main class="flex-1 min-w-0 md:ml-64 pt-14 md:pt-0">
      <div class="p-5 sm:p-8 lg:p-12 max-w-6xl mx-auto">
        <!-- Banner de fricção ALTA — nudge suave (paleta warn) -->
        {#if frictionLevel === 'high'}
            <div class="mb-8 rounded-2xl border border-warn/25 bg-warn-wash p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center gap-4 animate-slideUp">
                <span class="shrink-0 w-10 h-10 rounded-xl bg-warn/12 text-warn flex items-center justify-center" style="background: color-mix(in srgb, var(--color-warn) 12%, transparent);">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                </span>
                <div class="flex-1">
                    <p class="font-semibold text-warn leading-tight">Você parece cansado. Que tal uma pausa?</p>
                    <p class="text-sm text-warn/80 mt-0.5" style="color: color-mix(in srgb, var(--color-warn) 80%, transparent);">Reduzimos os estímulos visuais para ajudar sua atenção a se recuperar.</p>
                </div>
                <button onclick={dismissFriction} class="btn btn-outline !border-warn/40 !text-warn shrink-0 self-start sm:self-auto">
                    Continuar navegando
                </button>
            </div>
        {/if}

        <!-- Overlay de BLOQUEIO — gate explícito (paleta danger) -->
        {#if frictionLevel === 'block'}
            <div
                class="fixed inset-0 z-[1000] flex items-center justify-center p-5 animate-fadeIn"
                style="background: color-mix(in srgb, var(--color-ink) 55%, transparent); backdrop-filter: blur(6px);"
                role="dialog" aria-modal="true" aria-labelledby="block-title"
            >
                <div class="card w-full max-w-md p-7 sm:p-9 text-center animate-scaleIn bg-surface">
                    <span class="mx-auto w-14 h-14 rounded-2xl bg-danger-wash text-danger flex items-center justify-center mb-5">
                        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg>
                    </span>
                    <h2 id="block-title" class="text-xl font-bold">Pausa recomendada</h2>
                    <p class="text-muted text-sm mt-2 leading-relaxed">
                        Sua reserva cognitiva está baixa. Recomendamos alguns minutos longe da tela antes de continuar.
                    </p>

                    <label class="flex items-start gap-3 text-left mt-6 p-4 rounded-xl bg-danger-wash cursor-pointer">
                        <input
                            type="checkbox"
                            checked={blockAcknowledged}
                            onchange={acknowledgeBlock}
                            disabled={blockAcknowledged}
                            class="mt-0.5 w-5 h-5 shrink-0 cursor-pointer accent-[var(--color-danger)]"
                        />
                        <span class="text-sm text-ink leading-snug">Entendo que ignorar a pausa pode aumentar meu cansaço.</span>
                    </label>

                    {#if blockAcknowledged && blockCountdown > 0}
                        <p class="text-sm text-subtle mt-4 tabular-nums">
                            Aguarde <span class="font-semibold text-danger">{blockCountdown}s</span> para refletir…
                        </p>
                    {/if}

                    <div class="mt-6 flex flex-col gap-2">
                        <button
                            class="btn w-full {(!blockAcknowledged || blockCountdown > 0) ? 'btn-outline' : ''}"
                            style={(!blockAcknowledged || blockCountdown > 0) ? '' : 'background: var(--color-danger); color: #fff; border-color: var(--color-danger);'}
                            onclick={proceedPastBlock}
                            disabled={!blockAcknowledged || blockCountdown > 0}
                        >
                            {#if !blockAcknowledged}
                                Marque a caixa para continuar
                            {:else if blockCountdown > 0}
                                Aguarde {blockCountdown}s…
                            {:else}
                                Continuar mesmo assim
                            {/if}
                        </button>
                        <p class="eyebrow">respire fundo · beba água · alongue-se</p>
                    </div>
                </div>
            </div>
        {/if}

        <!-- Cabeçalho -->
        <header class="mb-8 sm:mb-10">
            <p class="eyebrow mb-2">Seu feed · curadoria ética</p>
            <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-5">
                <div>
                    <h1 class="text-3xl sm:text-4xl font-bold tracking-tight">
                        Feito para sua atenção
                    </h1>
                    <p class="text-muted text-sm sm:text-base mt-2 max-w-md">
                        Conteúdo equilibrado entre produtividade e descanso — sem a rolagem infinita.
                    </p>
                </div>

                <div class="flex flex-wrap gap-2">
                    <button
                        onclick={() => toggleCategory(null)}
                        class="chip {category === null ? 'chip-active' : ''}"
                        aria-pressed={category === null}
                    >
                        Tudo
                    </button>
                    <button
                        onclick={() => toggleCategory("PRODUTIVIDADE")}
                        class="chip {category === 'PRODUTIVIDADE' ? 'chip-active' : ''}"
                        aria-pressed={category === 'PRODUTIVIDADE'}
                    >
                        <span class="w-1.5 h-1.5 rounded-full bg-accent"></span>
                        Produtividade
                    </button>
                    <button
                        onclick={() => toggleCategory("ENTRETENIMENTO")}
                        class="chip {category === 'ENTRETENIMENTO' ? 'chip-active' : ''}"
                        aria-pressed={category === 'ENTRETENIMENTO'}
                    >
                        <span class="w-1.5 h-1.5 rounded-full bg-subtle"></span>
                        Entretenimento
                    </button>
                </div>
            </div>
        </header>

        <div class="privacy-note mb-8" role="status">
            <span class="w-9 h-9 rounded-xl bg-surface text-accent flex items-center justify-center shrink-0">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>
            </span>
            <div class="min-w-0 flex-1">
                <div class="flex flex-col items-start sm:flex-row sm:items-center gap-1.5 sm:gap-2">
                    <p class="font-semibold text-sm">Proteção de atenção no seu dispositivo</p>
                    <span class="chip chip-accent !py-0.5 !text-[10px]">{fatigueEnabled ? "Ativa" : "Opcional"}</span>
                </div>
                <p class="text-xs sm:text-sm mt-1 leading-relaxed opacity-80">
                    Rolagem e trocas de contexto ficam neste navegador. O servidor recebe somente uma ordem de proteção quando necessário.
                </p>
            </div>
        </div>

        {#if error}
            <div class="mb-8 rounded-2xl border border-line bg-surface px-4 py-3 text-sm text-muted" role="status">
                <span class="font-semibold text-ink">Nota:</span> {error}
            </div>
        {/if}

        <!-- Navegador de tópicos -->
        <div class="mb-8">
            <p class="eyebrow mb-3">Explore seus interesses</p>
            <div class="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
                <button
                    onclick={() => toggleTopic(null)}
                    class="chip whitespace-nowrap {selectedTopic === null ? 'chip-active' : ''}"
                    aria-pressed={selectedTopic === null}
                >
                    Para você
                </button>
                {#each topics as topic}
                    <button
                        onclick={() => toggleTopic(topic.id_topico)}
                        class="chip whitespace-nowrap {selectedTopic === topic.id_topico ? 'chip-active' : ''}"
                        aria-pressed={selectedTopic === topic.id_topico}
                    >
                        {topic.nome_topico}
                    </button>
                {/each}
            </div>
        </div>

        <!-- Grid de conteúdo -->
        <div
            bind:this={gridRef}
            class="grid gap-5 grid-cols-1 sm:grid-cols-2 xl:grid-cols-3"
        >
            {#if isLoading}
                {#each Array(6) as _}
                    <div class="card p-0 overflow-hidden">
                        <div class="skeleton aspect-[16/10] rounded-none"></div>
                        <div class="p-5 space-y-3">
                            <div class="skeleton h-3 w-24"></div>
                            <div class="skeleton h-5 w-full"></div>
                            <div class="skeleton h-5 w-2/3"></div>
                            <div class="skeleton h-3 w-1/2 mt-1"></div>
                        </div>
                    </div>
                {/each}
            {:else}
                {#each feed as content (content.id_conteudo)}
                    {@const prod = content.categoria === "PRODUTIVIDADE"}
                    <a
                        href="/content/{content.id_conteudo}"
                        onclick={() => void recordEvent(content.id_conteudo, "open", feed.indexOf(content))}
                        class="group rounded-[14px] focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2"
                    >
                        <article class="card card-interactive card-reveal p-0 overflow-hidden h-full flex flex-col">
                            <!-- Mídia -->
                            <div class="relative aspect-[16/8] sm:aspect-[16/10] flex items-center justify-center overflow-hidden {prod ? 'bg-accent-wash' : 'bg-hairline'}">
                                <div class="{prod ? 'text-accent' : 'text-subtle'} transition-transform duration-300 group-hover:scale-110">
                                    {#if content.tipo_de_midia === "VIDEO"}
                                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg>
                                    {:else if content.tipo_de_midia === "AUDIO"}
                                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3z"/><path d="M3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>
                                    {:else}
                                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="13" y2="17"/></svg>
                                    {/if}
                                </div>

                                <!-- Etiqueta de categoria -->
                                <span class="absolute top-3 left-3 inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold border {prod ? 'bg-accent-wash text-accent-ink border-transparent' : 'bg-surface text-muted border-line'}">
                                    <span class="w-1.5 h-1.5 rounded-full {prod ? 'bg-accent' : 'bg-subtle'}"></span>
                                    {prod ? 'Produtividade' : 'Entretenimento'}
                                </span>

                                <!-- Score de qualidade -->
                                <span class="absolute top-3 right-3 inline-flex items-center gap-1 rounded-full px-2 py-1 text-[11px] font-semibold bg-surface text-accent-ink border border-line tabular-nums" title="Score de qualidade">
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/><path d="M2 21c0-3 1.85-5.36 5.08-6"/></svg>
                                    {Math.round(content.score_de_qualidade * 100)}
                                </span>

                                <span class="absolute bottom-3 right-3 eyebrow !text-subtle bg-surface/80 rounded px-1.5 py-0.5">{content.tipo_de_midia}</span>
                            </div>

                            <!-- Corpo -->
                            <div class="p-5 flex flex-col flex-1">
                                <h3 class="font-semibold text-[17px] leading-snug tracking-tight text-ink transition-colors group-hover:text-accent-ink line-clamp-2">
                                    {content.titulo}
                                </h3>
                                {#if content.corpo}
                                    <p class="text-sm text-muted mt-2 leading-relaxed line-clamp-2">
                                        {content.corpo}
                                    </p>
                                {/if}

                                {#if content.topics && content.topics.length > 0}
                                    <div class="flex flex-wrap gap-1.5 mt-3">
                                        {#each content.topics.slice(0, 3) as topic}
                                            <span class="text-[11px] font-medium text-subtle bg-hairline rounded-full px-2 py-0.5">
                                                {topic.nome_topico}
                                            </span>
                                        {/each}
                                    </div>
                                {/if}

                                {#if humanReasons(content.id_conteudo).length}
                                    <div class="flex flex-wrap gap-1.5 mt-3" aria-label="Motivos da recomendação">
                                        {#each humanReasons(content.id_conteudo) as reason}
                                            <span class="reason-pill">
                                                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 3v18M3 12h18"/></svg>
                                                {reason}
                                            </span>
                                        {/each}
                                    </div>
                                {/if}

                                <div class="mt-auto pt-4 flex items-center gap-2 text-xs text-subtle">
                                    <span class="w-5 h-5 rounded-full bg-ink text-paper flex items-center justify-center text-[9px] font-bold uppercase shrink-0">
                                        {authorName(content.autor_id).charAt(0)}
                                    </span>
                                    <span class="font-medium text-muted truncate">{authorName(content.autor_id)}</span>
                                    <span class="text-line">·</span>
                                    <span class="shrink-0">{formatDate(content.data_publicacao)}</span>
                                </div>
                            </div>
                        </article>
                    </a>
                {/each}
            {/if}
        </div>

        {#if !isLoading && feed.length === 0}
            <div class="py-24 sm:py-32 text-center card border-dashed">
                <p class="text-4xl mb-4">🍃</p>
                <p class="font-semibold text-ink">
                    {isProtectionOrderActive() ? "Uma pausa também é uma boa recomendação" : "Nada por aqui ainda"}
                </p>
                <p class="text-sm text-muted mt-1 max-w-md mx-auto">
                    {isProtectionOrderActive()
                        ? "O modo protetivo não encontrou conteúdo adequado para este momento. Respire, hidrate-se e volte quando quiser."
                        : "Não há conteúdo nesta seção no momento."}
                </p>
            </div>
        {/if}
      </div>
    </main>
</div>

<style>
    /* Filtro grayscale nos estados de fricção — reduz o estímulo visual */
    .feed-grayscale {
        filter: grayscale(70%);
        transition: filter 0.5s ease;
    }

    /* Revelação suave dos cartões (funciona com ou sem a lib de motion) */
    .card-reveal {
        animation: cardReveal 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
    }
    @keyframes cardReveal {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: none; }
    }

    /* Trilho horizontal sem barra de rolagem visível */
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
