<script lang="ts">
    import { currentUser, isLoggedIn, ui } from "$lib/stores";
    import { api, type FocusGoal, type Session, type SessionReport, type Content } from "$lib/api";
    import { onMount } from "svelte";
    import { fade } from "svelte/transition";
    import { goto } from "$app/navigation";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import FocusSlide from "$lib/components/FocusSlide.svelte";

    let goals = $state<FocusGoal[]>([]);
    let activeSession = $state<Session | null>(null);
    let isLoading = $state(true);
    let isSubmitting = $state(false);
    let showGoalForm = $state(false);
    let showReport = $state<SessionReport | null>(null);
    let lastActiveElement = $state<HTMLElement | null>(null);
    let loadError = $state("");
    let formError = $state("");

    // Feed for focus mode
    let focusFeed = $state<Content[]>([]);
    let isLoadingFeed = $state(false);
    let activeSlideIndex = $state(0);
    let focusFeedRef = $state<HTMLElement>();

    // Goal form
    let tempoProdutividade = $state(30);
    let tempoEntretenimento = $state(15);
    let modoAbsoluto = $state(false);
    let tempoTotal = $derived(tempoProdutividade + tempoEntretenimento);
    let activeGoalCount = $derived(goals.filter((g) => g.status === "ATIVA").length);

    // Timer & Session State
    let elapsedMinutes = $state(0);
    let timerInterval: any = null;
    let currentCategory = $state<'PRODUTIVIDADE' | 'ENTRETENIMENTO'>('PRODUTIVIDADE');
    let ariaAnnouncement = $state("");
    let sessionCooldown = $state(false);

    // Fatigue & Transitions
    let showBreakSuggestion = $state(false);
    let transitionWarning = $state(false);
    let goalReached = $state(false);
    let showTransitionConfirm = $state(false);
    let isTransitioning = $state(false);

    onMount(() => {
        if (!$isLoggedIn) {
            goto("/auth/login");
            return;
        }
        loadGoals();
        
        const handleBeforeUnload = (e: BeforeUnloadEvent) => {
            if ($ui.focusMode && modoAbsoluto) {
                e.preventDefault();
                return (e.returnValue = "Absolute Mode is active. Breaking this session is registered as a broken commitment.");
            }
        };
        window.addEventListener("beforeunload", handleBeforeUnload);

        return () => {
            if (timerInterval) clearInterval(timerInterval);
            window.removeEventListener("beforeunload", handleBeforeUnload);
        };
    });

    async function loadFocusFeed() {
        if (!$currentUser) return;
        isLoadingFeed = true;
        try {
            const feedResult = await api.getFeed($currentUser.id_usuario, currentCategory);
            focusFeed = feedResult.items;
            activeSlideIndex = 0;
        } catch (err) {
            console.error("Error loading focus feed:", err);
            focusFeed = [];
        } finally {
            isLoadingFeed = false;
        }
    }

    async function loadGoals() {
        if (!$currentUser) return;
        isLoading = true;
        try {
            loadError = "";
            goals = await api.listGoals($currentUser.id_usuario);
            
            const sessions = await api.listActiveSessions($currentUser.id_usuario);
            if (sessions && sessions.length > 0) {
                activeSession = sessions[0];
                ui.enterFocusMode();
                
                const sessionGoals = await api.getSessionGoals(activeSession.id_sessao);
                const prodGoal = sessionGoals.find(g => g.categoria === 'PRODUTIVIDADE');
                const entGoal = sessionGoals.find(g => g.categoria === 'ENTRETENIMENTO');
                
                tempoProdutividade = prodGoal?.duracao_definida || 0;
                tempoEntretenimento = entGoal?.duracao_definida || 0;
                
                const start = new Date(activeSession.hora_inicio);
                const now = new Date();
                const totalElapsed = Math.floor((now.getTime() - start.getTime()) / 60000);
                
                if (totalElapsed < tempoProdutividade) {
                    currentCategory = 'PRODUTIVIDADE';
                    elapsedMinutes = totalElapsed;
                } else {
                    currentCategory = 'ENTRETENIMENTO';
                    elapsedMinutes = totalElapsed - tempoProdutividade;
                    if (elapsedMinutes >= tempoEntretenimento) {
                        goalReached = true;
                        elapsedMinutes = tempoEntretenimento;
                    }
                }
                
                loadFocusFeed();
                startTimer(false);
            }
        } catch (err) {
            console.error("Error loading goals:", err);
            loadError = "Não foi possível carregar suas metas agora. Tente atualizar a página.";
        } finally {
            isLoading = false;
        }
    }

    async function createGoal() {
        if (!$currentUser || isSubmitting) return;
        const produtividade = Math.max(0, Math.round(Number(tempoProdutividade) || 0));
        const entretenimento = Math.max(0, Math.round(Number(tempoEntretenimento) || 0));
        if (produtividade === 0 && entretenimento === 0) {
            formError = "Defina pelo menos 1 minuto para começar.";
            return;
        }
        formError = "";
        tempoProdutividade = produtividade;
        tempoEntretenimento = entretenimento;

        isSubmitting = true;
        try {
            const newGoals = await api.createGoal({
                user_id: $currentUser.id_usuario,
                tempo_produtividade: tempoProdutividade,
                tempo_entretenimento: tempoEntretenimento,
                modo_absoluto: modoAbsoluto,
            });
            goals = [...goals, ...newGoals];
            showGoalForm = false;
            await startSession(newGoals);
        } catch (err) {
            console.error("Error creating goal:", err);
            formError = "Não foi possível criar a meta. Verifique sua conexão e tente novamente.";
        } finally {
            isSubmitting = false;
        }
    }

    async function startSession(specificGoals?: FocusGoal[]) {
        if (!$currentUser || isSubmitting) return;
        const goalsToUse = specificGoals || goals.filter(g => g.status === 'ATIVA');
        if (goalsToUse.length === 0) return;

        isSubmitting = true;
        sessionCooldown = true;

        const prodGoal = goalsToUse.find(g => g.categoria === 'PRODUTIVIDADE');
        const entGoal = goalsToUse.find(g => g.categoria === 'ENTRETENIMENTO');
        tempoProdutividade = prodGoal?.duracao_definida || 0;
        tempoEntretenimento = entGoal?.duracao_definida || 0;

        try {
            activeSession = await api.startSession($currentUser.id_usuario, goalsToUse.map(g => g.id_meta), modoAbsoluto);
            currentCategory = tempoProdutividade > 0 ? 'PRODUTIVIDADE' : 'ENTRETENIMENTO';
            ui.enterFocusMode();
            setTimeout(() => { sessionCooldown = false; }, 2000);
            loadFocusFeed();
            startTimer(true);
        } catch (err) {
            console.error("Error starting session:", err);
            loadError = "Não foi possível iniciar a sessão. Tente novamente.";
            sessionCooldown = false;
        } finally {
            isSubmitting = false;
        }
    }

    function startTimer(reset: boolean = true) {
        if (reset) {
            elapsedMinutes = 0;
            goalReached = false;
            showBreakSuggestion = false;
            transitionWarning = false;
            showTransitionConfirm = false;
        }
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(() => {
            elapsedMinutes++;
            checkFocusHealth();
        }, 60000);
    }

    function checkFocusHealth() {
        if (!activeSession) return;
        const target = currentCategory === 'PRODUTIVIDADE' ? tempoProdutividade : tempoEntretenimento;
        if (elapsedMinutes === target - 1 && !transitionWarning) {
            transitionWarning = true;
        }
        if (elapsedMinutes >= target && !goalReached) {
            handleTransition();
        }
    }

    function handleTransition() {
        transitionWarning = false;
        if (currentCategory === 'PRODUTIVIDADE' && tempoEntretenimento > 0) {
            isTransitioning = true;
            setTimeout(() => {
                currentCategory = 'ENTRETENIMENTO';
                elapsedMinutes = 0;
                showTransitionConfirm = true;
                isTransitioning = false;
                loadFocusFeed();
            }, 5000); // 5 second breathing exercise interstitial
        } else {
            goalReached = true;
        }
    }

    async function endSession(feedback: number | null = null) {
        if (!activeSession || isSubmitting || sessionCooldown) return;
        if (!goalReached) {
            const msg = modoAbsoluto 
                ? "Absolute Mode active. Break commitment?" 
                : "End session early?";
            if (!confirm(msg)) return;
        }
        if (timerInterval) clearInterval(timerInterval);
        isSubmitting = true;
        try {
            const prodRealized = currentCategory === 'PRODUTIVIDADE' ? elapsedMinutes : tempoProdutividade;
            const entRealized = currentCategory === 'ENTRETENIMENTO' ? elapsedMinutes : (goalReached ? tempoEntretenimento : 0);
            await api.endSession(activeSession.id_sessao, {
                tempo_produtividade_realizado: prodRealized,
                tempo_entretenimento_realizado: entRealized,
                feedback,
            });
            showReport = await api.getSessionReport(activeSession.id_sessao);
            activeSession = null;
            ui.exitFocusMode();
        } catch (err) {
            console.error("Error ending session:", err);
            ui.exitFocusMode();
            goto("/feed");
        } finally {
            isSubmitting = false;
        }
    }

    function handleScroll(e: Event) {
        const target = e.target as HTMLElement;
        activeSlideIndex = Math.round(target.scrollTop / window.innerHeight);
    }

    function applyPreset(productivity: number, rest: number) {
        tempoProdutividade = productivity;
        tempoEntretenimento = rest;
        formError = "";
    }

    function handleFocusKeydown(event: KeyboardEvent) {
        if (!$ui.focusMode || !focusFeedRef || focusFeed.length === 0) return;
        const target = event.target as HTMLElement | null;
        if (target && ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName)) return;
        const direction = event.key === "ArrowDown" || event.key === "PageDown"
            ? 1
            : event.key === "ArrowUp" || event.key === "PageUp"
                ? -1
                : 0;
        if (direction === 0) return;
        event.preventDefault();
        const nextIndex = Math.max(0, Math.min(focusFeed.length, activeSlideIndex + direction));
        const nextSlide = focusFeedRef.children[nextIndex] as HTMLElement | undefined;
        nextSlide?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
</script>

<svelte:window onkeydown={handleFocusKeydown} />

<svelte:head>
    <title>Foco | Be Productive</title>
</svelte:head>

<div class="flex min-h-screen bg-paper text-ink">
    {#if !$ui.focusMode && !showReport}
        <Sidebar />
    {/if}

    <main class="flex-1 min-w-0 {!$ui.focusMode && !showReport ? 'md:ml-64 pt-14 md:pt-0' : ''}">
        {#if showReport}
            <!-- Relatório da sessão -->
            {@const concluido = showReport.classification === 'concluido'}
            <div class="min-h-screen flex items-center justify-center p-5 sm:p-8" in:fade>
                <div class="card w-full max-w-lg p-8 sm:p-10 text-center animate-scaleIn">
                    <span class="mx-auto w-14 h-14 rounded-2xl flex items-center justify-center mb-6 {concluido ? 'bg-accent-wash text-accent' : 'bg-hairline text-muted'}">
                        {#if concluido}
                            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                        {:else}
                            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        {/if}
                    </span>
                    <p class="eyebrow mb-2">Relatório de foco</p>
                    <h2 class="text-3xl sm:text-4xl font-bold tracking-tight">
                        {concluido ? 'Meta concluída' : 'Sessão encerrada'}
                    </h2>
                    <p class="text-muted text-sm mt-3 max-w-sm mx-auto leading-relaxed">{showReport.message}</p>

                    <div class="grid grid-cols-2 gap-4 my-8">
                        <div class="rounded-2xl bg-accent-wash p-5">
                            <p class="eyebrow !text-accent-ink/70">Produtividade</p>
                            <p class="text-3xl font-bold mt-1.5 tabular-nums text-accent-ink">
                                {showReport.session.tempo_produtividade_realizado}<span class="text-base font-semibold text-muted ml-0.5">min</span>
                            </p>
                        </div>
                        <div class="rounded-2xl bg-hairline p-5">
                            <p class="eyebrow">Descanso</p>
                            <p class="text-3xl font-bold mt-1.5 tabular-nums">
                                {showReport.session.tempo_entretenimento_realizado}<span class="text-base font-semibold text-muted ml-0.5">min</span>
                            </p>
                        </div>
                    </div>

                    <button class="btn btn-primary w-full !py-3.5" onclick={() => { showReport = null; goto("/feed"); }}>
                        Voltar ao workspace
                    </button>
                </div>
            </div>

        {:else if $ui.focusMode && activeSession}
            <!-- Modo de foco imersivo -->
            {@const target = currentCategory === 'PRODUTIVIDADE' ? tempoProdutividade : tempoEntretenimento}
            {@const pct = target > 0 ? Math.min(100, Math.round((elapsedMinutes / target) * 100)) : 0}
            <div class="h-[100svh] w-full relative flex flex-col bg-paper">
                <!-- Barra de status superior -->
                <nav class="absolute top-0 left-0 w-full z-50 p-4 sm:p-6 flex justify-between items-start gap-3 pointer-events-none" aria-label="Controles da sessão">
                    <div class="focus-hud card !rounded-2xl pointer-events-auto overflow-hidden max-w-[72vw]" aria-live="polite">
                        <div class="px-3.5 py-2.5 sm:px-4 flex items-center gap-2.5">
                            <span class="w-2 h-2 rounded-full bg-accent animate-pulse shrink-0"></span>
                            <span class="text-xs font-semibold tracking-tight truncate">{currentCategory === 'PRODUTIVIDADE' ? 'Bloco de produtividade' : 'Bloco de descanso'}</span>
                            <span class="text-xs font-medium text-muted tabular-nums shrink-0">{elapsedMinutes} / {target} min</span>
                        </div>
                        <div class="h-1.5 bg-hairline" role="progressbar" aria-label="Progresso da sessão" aria-valuemin="0" aria-valuemax="100" aria-valuenow={pct}>
                            <div class="h-full bg-accent transition-all duration-500" style="width: {pct}%"></div>
                        </div>
                    </div>

                    {#if !modoAbsoluto || goalReached}
                        <button
                            class="btn btn-outline bg-surface shrink-0 pointer-events-auto"
                            onclick={() => endSession(5)}
                            aria-label={goalReached ? "Concluir sessão" : "Sair da sessão"}
                        >
                            {goalReached ? 'Concluir sessão' : 'Sair agora'}
                        </button>
                    {:else}
                        <span class="chip chip-accent pointer-events-auto shrink-0 self-center">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                            Pacto ativo
                        </span>
                    {/if}
                </nav>

                <!-- Interstício de respiração -->
                {#if isTransitioning}
                    <div class="absolute inset-0 z-[100] bg-paper flex flex-col items-center justify-center gap-10 animate-fadeIn" in:fade>
                        <p class="eyebrow">Transição para o descanso</p>
                        <div class="relative w-44 h-44 flex items-center justify-center">
                            <span class="absolute inset-0 rounded-full bg-accent-wash animate-ping"></span>
                            <span class="relative w-32 h-32 rounded-full border-2 border-accent flex items-center justify-center text-accent-ink font-semibold">
                                Respire
                            </span>
                        </div>
                        <p class="text-muted text-sm">Inspire… e expire lentamente.</p>
                    </div>
                {/if}

                <!-- Feed vertical -->
                <div
                    bind:this={focusFeedRef}
                    class="flex-1 overflow-y-scroll snap-y snap-mandatory no-scrollbar"
                    onscroll={handleScroll}
                >
                    {#if isLoadingFeed}
                        <div class="h-full w-full flex flex-col items-center justify-center gap-4">
                            <div class="w-10 h-10 border-[3px] border-line border-t-accent rounded-full animate-spin"></div>
                            <p class="text-sm text-muted">Preparando uma sequência tranquila…</p>
                        </div>
                    {:else if focusFeed.length === 0}
                        <div class="h-full w-full flex flex-col items-center justify-center gap-5 p-6 text-center">
                            <span class="w-14 h-14 rounded-2xl bg-accent-wash text-accent flex items-center justify-center">
                                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18M3 12h18"/></svg>
                            </span>
                            <div>
                                <p class="font-semibold">Nada novo para esta fase</p>
                                <p class="text-muted text-sm max-w-xs mt-1">Sua atenção não precisa ser preenchida agora. Você pode encerrar quando quiser.</p>
                            </div>
                            <button class="btn btn-outline" onclick={() => endSession(null)}>Encerrar sessão</button>
                        </div>
                    {:else}
                        {#each focusFeed as content, i}
                            <FocusSlide {content} active={activeSlideIndex === i} index={i} total={focusFeed.length} />
                        {/each}

                        <!-- Fim do fluxo -->
                        <div class="h-screen w-full flex flex-col items-center justify-center snap-start bg-surface gap-6 p-6 text-center">
                            <span class="w-14 h-14 rounded-2xl bg-accent-wash text-accent flex items-center justify-center">
                                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
                            </span>
                            <div class="space-y-2">
                                <h3 class="text-xl font-bold tracking-tight">Fim do fluxo curado</h3>
                                <p class="text-sm text-muted max-w-xs">Você viu tudo o que selecionamos para esta sessão.</p>
                            </div>
                            <button class="btn btn-primary !px-8" onclick={() => endSession(5)}>
                                Concluir sessão agora
                            </button>
                        </div>
                    {/if}
                </div>
                {#if focusFeed.length > 0 && activeSlideIndex === 0 && !isLoadingFeed}
                    <div class="absolute bottom-5 left-1/2 -translate-x-1/2 pointer-events-none hidden sm:flex items-center gap-2 rounded-full bg-surface/90 border border-line px-3 py-1.5 text-[11px] font-medium text-muted shadow-soft" aria-hidden="true">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m7 13 5 5 5-5M12 18V6"/></svg>
                        Deslize ou use ↑ ↓
                    </div>
                {/if}
            </div>

        {:else}
            <!-- Configuração de metas -->
            <div class="p-5 sm:p-8 lg:p-12 max-w-4xl mx-auto animate-fadeIn">
                {#if isLoading}
                    <div class="space-y-4" aria-label="Carregando foco">
                        <div class="skeleton h-3 w-28"></div>
                        <div class="skeleton h-10 w-3/4"></div>
                        <div class="skeleton h-4 w-2/3"></div>
                        <div class="card p-7 mt-10 space-y-4"><div class="skeleton h-5 w-1/3"></div><div class="skeleton h-16 w-full"></div></div>
                    </div>
                {:else}
                <header class="mb-8 sm:mb-10">
                    <p class="eyebrow mb-2">Espaço de foco</p>
                    <h1 class="text-3xl sm:text-4xl font-bold tracking-tight">Desenhe os limites da sua atenção</h1>
                    <p class="text-muted text-sm sm:text-base mt-2 max-w-md">
                        Defina quanto tempo dedicar a produzir e a descansar. Dados reais, foco real.
                    </p>
                </header>

                {#if loadError}
                    <div class="privacy-note !bg-danger-wash !text-danger mb-8" role="alert">
                        <span class="shrink-0 mt-0.5">!</span>
                        <p class="text-sm">{loadError}</p>
                    </div>
                {/if}

                {#if activeGoalCount > 0}
                    <button
                        type="button"
                        onclick={() => startSession()}
                        class="card card-interactive w-full text-left p-6 sm:p-7 flex items-center justify-between gap-5 mb-10 group"
                    >
                        <div class="flex items-center gap-4">
                            <span class="w-11 h-11 rounded-xl bg-accent-wash text-accent flex items-center justify-center shrink-0">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                            </span>
                            <div>
                                <h3 class="font-semibold text-lg tracking-tight">
                                    {activeGoalCount === 1 ? "Você tem uma meta ativa" : `Você tem ${activeGoalCount} metas ativas`}
                                </h3>
                                <p class="text-sm text-muted mt-0.5">
                                    {activeGoalCount === 1 ? "Retome seu compromisso de onde parou." : "Retome seus compromissos de onde parou."}
                                </p>
                            </div>
                        </div>
                        <span class="text-accent transition-transform group-hover:translate-x-1">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                        </span>
                    </button>
                {/if}

                <div class="flex items-end justify-between gap-4 pb-4 border-b border-hairline mb-8">
                    <div>
                        <p class="eyebrow mb-1">Arquiteto de sessão</p>
                        <h2 class="text-xl font-bold tracking-tight">Nova meta de foco</h2>
                    </div>
                    <button class="btn {showGoalForm ? 'btn-ghost' : 'btn-outline'}" onclick={() => showGoalForm = !showGoalForm}>
                        {#if showGoalForm}
                            Descartar
                        {:else}
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                            Nova meta
                        {/if}
                    </button>
                </div>

                {#if showGoalForm}
                    <div class="card p-6 sm:p-8 space-y-8 animate-slideUp mb-10">
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                            <div class="rounded-2xl border border-line p-5">
                                <label for="p" class="flex items-center gap-2 text-sm font-medium text-ink">
                                    <span class="w-1.5 h-1.5 rounded-full bg-accent"></span> Produtividade
                                </label>
                                <div class="flex items-baseline gap-2 mt-3">
                                    <input type="number" id="p" min="0" max="240" step="5" inputmode="numeric" bind:value={tempoProdutividade} class="input !text-4xl !font-bold !p-0 !border-0 !bg-transparent w-24 tabular-nums focus:!ring-0 focus:!shadow-none" />
                                    <span class="text-sm font-medium text-subtle">min</span>
                                </div>
                            </div>
                            <div class="rounded-2xl border border-line p-5">
                                <label for="e" class="flex items-center gap-2 text-sm font-medium text-ink">
                                    <span class="w-1.5 h-1.5 rounded-full bg-subtle"></span> Descanso
                                </label>
                                <div class="flex items-baseline gap-2 mt-3">
                                    <input type="number" id="e" min="0" max="240" step="5" inputmode="numeric" bind:value={tempoEntretenimento} class="input !text-4xl !font-bold !p-0 !border-0 !bg-transparent w-24 tabular-nums focus:!ring-0 focus:!shadow-none" />
                                    <span class="text-sm font-medium text-subtle">min</span>
                                </div>
                            </div>
                        </div>

                        <div>
                            <p class="text-xs font-semibold text-muted mb-2">Comece por um ritmo</p>
                            <div class="flex flex-wrap gap-2">
                                <button type="button" class="chip" onclick={() => applyPreset(25, 5)}>25 + 5 min</button>
                                <button type="button" class="chip" onclick={() => applyPreset(50, 10)}>50 + 10 min</button>
                                <button type="button" class="chip" onclick={() => applyPreset(90, 15)}>90 + 15 min</button>
                            </div>
                        </div>

                        <p class="text-sm text-muted text-center tabular-nums">
                            Sessão total de <span class="font-semibold text-ink">{tempoTotal} min</span>
                        </p>

                        <!-- Pacto de Ulisses (modo absoluto) -->
                        <label
                            for="abs"
                            class="block rounded-2xl border-2 p-5 sm:p-6 cursor-pointer transition-colors {modoAbsoluto ? 'border-accent bg-accent-wash' : 'border-line hover:border-ink'}"
                        >
                            <div class="flex items-start justify-between gap-4">
                                <div class="flex items-start gap-4">
                                    <span class="w-11 h-11 rounded-xl flex items-center justify-center shrink-0 {modoAbsoluto ? 'bg-accent text-white' : 'bg-hairline text-muted'}">
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                                    </span>
                                    <div>
                                        <div class="flex items-center gap-2">
                                            <h3 class="font-semibold text-ink tracking-tight">Pacto de Ulisses</h3>
                                            <span class="chip {modoAbsoluto ? 'chip-accent' : ''} !py-0.5 !text-[10px]">Compromisso trancado</span>
                                        </div>
                                        <p class="text-sm text-muted mt-1 leading-relaxed">
                                            Ao ativar, você tranca o foco: sair antes da hora conta como compromisso rompido. Sem saídas fáceis.
                                        </p>
                                    </div>
                                </div>
                                <span class="relative inline-flex shrink-0 mt-0.5">
                                    <input type="checkbox" id="abs" bind:checked={modoAbsoluto} class="sr-only peer" />
                                    <span class="w-11 h-6 rounded-full bg-line transition-colors peer-checked:bg-accent peer-focus-visible:ring-2 peer-focus-visible:ring-accent peer-focus-visible:ring-offset-2 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:w-5 after:h-5 after:rounded-full after:bg-white after:shadow after:transition-transform peer-checked:after:translate-x-5"></span>
                                </span>
                            </div>
                        </label>

                        {#if formError}
                            <p class="text-sm text-danger -mt-4" role="alert">{formError}</p>
                        {/if}

                        <button class="btn btn-accent w-full !py-3.5" onclick={createGoal} disabled={isSubmitting || tempoTotal <= 0}>
                            {isSubmitting ? 'Preparando…' : 'Iniciar sessão imersiva'}
                        </button>
                    </div>
                {/if}

                {#if goals.length > 0}
                    <p class="eyebrow mb-3">Suas metas</p>
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {#each goals as goal}
                            {@const prod = goal.categoria === 'PRODUTIVIDADE'}
                            <div class="card p-5 {goal.status === 'CONCLUIDA' ? 'opacity-50' : ''}">
                                <div class="flex items-center justify-between">
                                    <span class="inline-flex items-center gap-1.5 text-xs font-semibold text-muted">
                                        <span class="w-1.5 h-1.5 rounded-full {prod ? 'bg-accent' : 'bg-subtle'}"></span>
                                        {prod ? 'Produtividade' : 'Descanso'}
                                    </span>
                                    {#if goal.status === 'CONCLUIDA'}
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="text-accent"><polyline points="20 6 9 17 4 12"/></svg>
                                    {/if}
                                </div>
                                <div class="text-3xl font-bold tracking-tight tabular-nums mt-3">
                                    {goal.duracao_definida}<span class="text-base font-semibold text-muted ml-0.5">min</span>
                                </div>
                            </div>
                        {/each}
                    </div>
                {/if}
                {/if}
            </div>
        {/if}
    </main>
</div>

<style>
    .no-scrollbar::-webkit-scrollbar {
        display: none;
    }
    .no-scrollbar {
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
</style>
