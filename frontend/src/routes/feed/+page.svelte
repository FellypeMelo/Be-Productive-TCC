<script lang="ts">
    import { currentUser, isLoggedIn } from "$lib/stores";
    import { api, type Content } from "$lib/api";
    import { onMount, onDestroy } from "svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import { animate, stagger } from "motion";
    import { EdgeFatigueEngine, type FrictionLevel } from "$lib/fatigue";

    let feed = $state<Content[]>([]);
    let isLoading = $state(true);
    let error = $state("");
    let category = $state<string | null>(null);
    let selectedTopic = $state<number | null>(null);
    let topics = $state<any[]>([]);
    let gridRef: HTMLElement;

    // Friction state — computed 100% ON-DEVICE by the Edge fatigue engine.
    // Raw telemetry (v_scroll, v_alt) NEVER leaves the browser.
    let frictionLevel = $state<FrictionLevel>("none");

    // On-device fatigue inference (Ego-Depletion EDO + Hawkes dual-kernel).
    const fatigueEngine = new EdgeFatigueEngine();
    let fatigueInterval: ReturnType<typeof setInterval> | null = null;
    let lastScrollY = 0;
    let lastScrollTime = Date.now();
    let lastTickTime = Date.now();
    // Throttle so a scroll gesture (which fires many events) is sampled, not flooded.
    let lastScrollSampleTime = 0;

    // Explicit-confirm gate for the "block" overlay (no one-click no-op dismissal).
    let blockAcknowledged = $state(false);
    let blockCountdown = $state(0);
    let blockCountdownInterval: ReturnType<typeof setInterval> | null = null;

    const TICK_MS = 1500;
    const SCROLL_SAMPLE_MS = 200;
    const BLOCK_WAIT_SECONDS = 5;

    // Preserving original mock data for fallback/demo
    const mockFeed: Content[] = [
        {
            id_conteudo: 1,
            titulo: "Deep Focus Strategies",
            categoria: "PRODUTIVIDADE",
            tipo_de_midia: "VIDEO",
            autor_id: 1,
            data_publicacao: "2026-02-01",
            score_de_qualidade: 0.92,
            corpo: "",
            tags_relevantes: "",
        },
        {
            id_conteudo: 2,
            titulo: "Ambient Study Session",
            categoria: "PRODUTIVIDADE",
            tipo_de_midia: "AUDIO",
            autor_id: 2,
            data_publicacao: "2026-02-01",
            score_de_qualidade: 0.88,
            corpo: "",
            tags_relevantes: "",
        },
        {
            id_conteudo: 3,
            titulo: "Modern Minimalist Design",
            categoria: "ENTRETENIMENTO",
            tipo_de_midia: "VIDEO",
            autor_id: 3,
            data_publicacao: "2026-01-30",
            score_de_qualidade: 0.85,
            corpo: "",
            tags_relevantes: "",
        },
        {
            id_conteudo: 4,
            titulo: "Daily Meditation Guide",
            categoria: "PRODUTIVIDADE",
            tipo_de_midia: "VIDEO",
            autor_id: 1,
            data_publicacao: "2026-01-29",
            score_de_qualidade: 0.95,
            corpo: "",
            tags_relevantes: "",
        },
        {
            id_conteudo: 5,
            titulo: "Cinema: The New Wave",
            categoria: "ENTRETENIMENTO",
            tipo_de_midia: "VIDEO",
            autor_id: 4,
            data_publicacao: "2026-01-28",
            score_de_qualidade: 0.78,
            corpo: "",
            tags_relevantes: "",
        },
    ];

    onMount(async () => {
        if (!$isLoggedIn) return;
        loadTopics();
        loadFeed();
        startFatigueMonitoring();
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

    async function loadFeed() {
        isLoading = true;
        try {
            const userID = $currentUser?.id_usuario || 1;
            const result = await api.getFeed(
                userID,
                category || undefined,
                selectedTopic || undefined,
            );

            feed = result.items;
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
            feed = mockFeed;
            // Do not reset friction here — it is owned by the on-device engine.
        } finally {
            isLoading = false;
        }
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

<!-- Grayscale filter on high friction -->
<div class="flex min-h-screen bg-white {frictionLevel === 'high' || frictionLevel === 'block' ? 'feed-grayscale' : ''}">
    <Sidebar />

    <main class="flex-1 ml-64 p-12">
        <!-- Friction banners -->
        {#if frictionLevel === 'high'}
            <div class="friction-banner">
                <p>Você parece cansado. Que tal fazer uma pausa?</p>
                <button onclick={dismissFriction}>Continuar navegando</button>
            </div>
        {/if}

        {#if frictionLevel === 'block'}
            <div class="friction-overlay" role="dialog" aria-modal="true" aria-labelledby="block-title">
                <h2 id="block-title">Pausa recomendada</h2>
                <p>Sua reserva cognitiva está baixa. Recomendamos uma pausa de alguns minutos.</p>

                <label class="block-confirm">
                    <input
                        type="checkbox"
                        checked={blockAcknowledged}
                        onchange={acknowledgeBlock}
                        disabled={blockAcknowledged}
                    />
                    <span>Entendo que ignorar a pausa pode aumentar meu cansaço.</span>
                </label>

                {#if blockAcknowledged && blockCountdown > 0}
                    <p class="block-countdown">
                        Aguarde {blockCountdown}s para refletir…
                    </p>
                {/if}

                <button
                    class="block-proceed"
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
            </div>
        {/if}

        <!-- Header -->
        <header class="flex justify-between items-end mb-16">
            <div>
                <h1 class="text-4xl font-bold tracking-tighter uppercase">
                    Your Feed
                </h1>
                <p class="text-gray-400 text-sm mt-2">
                    Curated for your mental balance.
                </p>
            </div>

            <div class="flex gap-4">
                <button
                    onclick={() => toggleCategory(null)}
                    class="text-xs font-bold uppercase tracking-widest px-4 py-2 border {category ===
                    null
                        ? 'bg-black text-white border-black'
                        : 'border-gray-200 hover:border-black'} transition-colors"
                >
                    All
                </button>
                <button
                    onclick={() => toggleCategory("PRODUTIVIDADE")}
                    class="text-xs font-bold uppercase tracking-widest px-4 py-2 border {category ===
                    'PRODUTIVIDADE'
                        ? 'bg-black text-white border-black'
                        : 'border-gray-200 hover:border-black'} transition-colors"
                >
                    Productivity
                </button>
                <button
                    onclick={() => toggleCategory("ENTRETENIMENTO")}
                    class="text-xs font-bold uppercase tracking-widest px-4 py-2 border {category ===
                    'ENTRETENIMENTO'
                        ? 'bg-black text-white border-black'
                        : 'border-gray-200 hover:border-black'} transition-colors"
                >
                    Entertainment
                </button>
            </div>
        </header>

        <!-- Topic Browser (Discovery Module) -->
        <div class="mb-12">
            <p
                class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-4"
            >
                Browse your interests
            </p>
            <div class="flex gap-4 overflow-x-auto pb-4 no-scrollbar">
                <button
                    onclick={() => toggleTopic(null)}
                    class="px-6 py-3 text-[10px] font-bold uppercase tracking-widest border border-black transition-all
                           {selectedTopic === null
                        ? 'bg-black text-white'
                        : 'border-gray-200 hover:border-black'}"
                >
                    All For You
                </button>
                {#each topics as topic}
                    <button
                        onclick={() => toggleTopic(topic.id_topico)}
                        class="px-6 py-3 text-[10px] font-bold uppercase tracking-widest border border-black transition-all whitespace-nowrap
                               {selectedTopic === topic.id_topico
                            ? 'bg-black text-white'
                            : 'border-gray-200 hover:border-black'}"
                    >
                        {topic.nome_topico}
                    </button>
                {/each}
            </div>
        </div>

        <!-- Grid -->
        <div
            bind:this={gridRef}
            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-16"
        >
            {#if isLoading}
                {#each Array(6) as _}
                    <div class="space-y-4 animate-pulse">
                        <div
                            class="aspect-video bg-gray-100 border border-black/5"
                        ></div>
                        <div class="h-4 bg-gray-100 w-3/4"></div>
                        <div class="h-3 bg-gray-100 w-1/2"></div>
                    </div>
                {/each}
            {:else}
                {#each feed as content (content.id_conteudo)}
                    <a
                        href="/content/{content.id_conteudo}"
                        class="block group"
                    >
                        <article class="opacity-0">
                            <div
                                class="aspect-video border border-black bg-white mb-4 relative overflow-hidden flex items-center justify-center"
                            >
                                <div
                                    class="absolute inset-0 bg-black opacity-0 group-hover:opacity-5 transition-opacity"
                                ></div>

                                <!-- Content Type Icon (Minimalist) -->
                                <div
                                    class="text-black/20 group-hover:text-black transition-colors"
                                >
                                    {#if content.tipo_de_midia === "VIDEO"}
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            width="48"
                                            height="48"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            stroke-width="1.5"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            ><polygon
                                                points="5 3 19 12 5 21 5 3"
                                            /></svg
                                        >
                                    {:else if content.tipo_de_midia === "AUDIO"}
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            width="48"
                                            height="48"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            stroke-width="1.5"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            ><path
                                                d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"
                                            /><path
                                                d="M19 10v2a7 7 0 0 1-14 0v-2"
                                            /><line
                                                x1="12"
                                                y1="19"
                                                x2="12"
                                                y2="23"
                                            /><line
                                                x1="8"
                                                y1="23"
                                                x2="16"
                                                y2="23"
                                            /></svg
                                        >
                                    {:else}
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            width="48"
                                            height="48"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            stroke-width="1.5"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            ><path
                                                d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                                            /><polyline
                                                points="14 2 14 8 20 8"
                                            /></svg
                                        >
                                    {/if}
                                </div>

                                <!-- Metadata Badge -->
                                <div
                                    class="absolute bottom-2 right-2 bg-black text-white text-[8px] font-bold uppercase px-1 tracking-tighter"
                                >
                                    {content.tipo_de_midia}
                                </div>
                            </div>

                            <h3
                                class="font-bold text-lg leading-tight group-hover:underline uppercase tracking-tight"
                            >
                                {content.titulo}
                            </h3>
                            <div
                                class="flex items-center gap-2 mt-2 text-[10px] font-bold text-gray-400 uppercase tracking-widest"
                            >
                                <span>Author #{content.autor_id}</span>
                                <span>•</span>
                                <span
                                    class={content.categoria === "PRODUTIVIDADE"
                                        ? "text-black"
                                        : ""}>{content.categoria}</span
                                >
                            </div>

                            {#if content.topics && content.topics.length > 0}
                                <div class="flex flex-wrap gap-1 mt-3">
                                    {#each content.topics as topic}
                                        <span class="px-1 bg-black text-white text-[8px] font-bold uppercase tracking-tighter">
                                            {topic.nome_topico}
                                        </span>
                                    {/each}
                                </div>
                            {/if}
                        </article>
                    </a>
                {/each}
            {/if}
        </div>

        {#if !isLoading && feed.length === 0}
            <div class="py-32 text-center border border-dashed border-gray-200">
                <p
                    class="text-sm font-bold text-gray-400 uppercase tracking-widest"
                >
                    No content available in this section.
                </p>
            </div>
        {/if}
    </main>
</div>

<style>
    /* Grayscale filter for friction states — reduces visual stimulation */
    .feed-grayscale {
        filter: grayscale(70%);
        transition: filter 0.5s ease;
    }

    /* Friction banner (HIGH friction) */
    .friction-banner {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .friction-banner p {
        color: #856404;
        font-weight: 600;
        margin: 0;
    }

    .friction-banner button {
        background: transparent;
        border: 1px solid #ffc107;
        border-radius: 4px;
        padding: 0.25rem 0.75rem;
        cursor: pointer;
        font-size: 0.75rem;
        color: #856404;
    }

    /* Friction overlay (BLOCK friction) */
    .friction-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        text-align: center;
        padding: 2rem;
    }

    .friction-overlay h2 {
        margin-bottom: 0.5rem;
        font-size: 1.5rem;
    }

    .friction-overlay p {
        margin-bottom: 1rem;
        opacity: 0.8;
    }

    .friction-overlay button {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 4px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        color: white;
        font-size: 0.8rem;
    }

    /* Explicit-confirm gate on the BLOCK overlay */
    .block-confirm {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        max-width: 26rem;
        margin: 0.5rem 0 1rem;
        font-size: 0.85rem;
        text-align: left;
        cursor: pointer;
    }

    .block-confirm input {
        margin-top: 0.15rem;
        cursor: pointer;
    }

    .block-countdown {
        font-size: 0.8rem;
        opacity: 0.7;
        margin-bottom: 0.75rem;
    }

    .friction-overlay button.block-proceed:disabled {
        opacity: 0.4;
        cursor: not-allowed;
    }
</style>
