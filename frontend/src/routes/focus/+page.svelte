<script lang="ts">
    import { currentUser, isLoggedIn, ui } from "$lib/stores";
    import { api, type FocusGoal, type Session, type SessionReport, type Content } from "$lib/api";
    import { onMount } from "svelte";
    import { fade, slide } from "svelte/transition";
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

    // Feed for focus mode
    let focusFeed = $state<Content[]>([]);
    let isLoadingFeed = $state(false);
    let activeSlideIndex = $state(0);

    // Goal form
    let tempoProdutividade = $state(30);
    let tempoEntretenimento = $state(15);
    let modoAbsoluto = $state(false);
    let tempoTotal = $derived(tempoProdutividade + tempoEntretenimento);

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
            focusFeed = await api.getFeed($currentUser.id_usuario, currentCategory);
            activeSlideIndex = 0;
        } catch (err) {
            console.error("Error loading focus feed:", err);
        } finally {
            isLoadingFeed = false;
        }
    }

    async function loadGoals() {
        if (!$currentUser) return;
        isLoading = true;
        try {
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
        } finally {
            isLoading = false;
        }
    }

    async function createGoal() {
        if (!$currentUser || isSubmitting) return;
        if (tempoProdutividade === 0 && tempoEntretenimento === 0) {
            alert("Please set at least 1 minute.");
            return;
        }

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
</script>

<svelte:head>
    <title>Focus | Be Productive</title>
</svelte:head>

<div class="flex min-h-screen bg-white text-black overflow-hidden">
    {#if !$ui.focusMode && !showReport}
        <Sidebar />
    {/if}

    <main class="flex-1 transition-all duration-500 {!$ui.focusMode && !showReport ? 'ml-64 p-12' : 'p-0'}">
        {#if showReport}
            <!-- Report View -->
            <div class="h-screen flex items-center justify-center bg-gray-50 p-12" in:fade>
                <div class="max-w-xl w-full p-12 border border-black bg-white shadow-2xl space-y-12">
                    <header class="text-center">
                        <div class="inline-block border border-black px-4 py-1 text-[10px] font-bold uppercase tracking-widest mb-4">
                            Focus Report
                        </div>
                        <h2 class="text-5xl font-bold uppercase tracking-tighter">
                            {showReport.classification === 'concluido' ? 'Success' : 'Session End'}
                        </h2>
                        <p class="text-sm text-gray-500 mt-4 font-medium">{showReport.message}</p>
                    </header>

                    <div class="grid grid-cols-2 gap-12 border-y border-black py-12">
                        <div class="text-center">
                            <span class="text-[10px] font-bold uppercase tracking-widest text-gray-400">Productivity</span>
                            <div class="text-3xl font-bold mt-2">{showReport.session.tempo_produtividade_realizado}m</div>
                        </div>
                        <div class="text-center">
                            <span class="text-[10px] font-bold uppercase tracking-widest text-gray-400">Entertainment</span>
                            <div class="text-3xl font-bold mt-2">{showReport.session.tempo_entretenimento_realizado}m</div>
                        </div>
                    </div>

                    <button class="w-full bg-black text-white py-5 text-xs font-bold uppercase tracking-widest hover:bg-gray-800 transition-all" onclick={() => { showReport = null; goto("/feed"); }}>
                        Return to Workspace
                    </button>
                </div>
            </div>

        {:else if $ui.focusMode && activeSession}
            <!-- Immersive Focus Mode -->
            <div class="h-screen w-full relative flex flex-col">
                <!-- Slim Focus Top Bar -->
                <nav class="absolute top-0 left-0 w-full z-50 p-6 flex justify-between items-center pointer-events-none">
                    <div class="flex items-center gap-6 pointer-events-auto">
                        <div class="bg-black text-white px-4 py-2 rounded-full flex items-center gap-3 shadow-xl">
                            <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                            <span class="text-xs font-bold tracking-widest uppercase">{currentCategory}</span>
                            <span class="opacity-40">|</span>
                            <span class="text-xs font-mono">{elapsedMinutes}m / {currentCategory === 'PRODUTIVIDADE' ? tempoProdutividade : tempoEntretenimento}m</span>
                        </div>
                    </div>

                    <div class="flex items-center gap-4 pointer-events-auto">
                        {#if !modoAbsoluto || goalReached}
                            <button 
                                class="bg-white/90 backdrop-blur border border-black px-6 py-2 text-[10px] font-bold uppercase tracking-widest hover:bg-black hover:text-white transition-all shadow-lg"
                                onclick={() => endSession(5)}
                            >
                                {goalReached ? 'Finish Session' : 'Exit Early'}
                            </button>
                        {/if}
                    </div>
                </nav>

                <!-- Transition Overlay -->
                {#if isTransitioning}
                    <div class="absolute inset-0 z-[100] bg-white flex flex-col items-center justify-center space-y-12 animate-fadeIn" in:fade>
                        <h2 class="text-2xl font-bold uppercase tracking-[0.3em]">Deep Breath</h2>
                        <div class="w-48 h-48 rounded-full border-2 border-black flex items-center justify-center animate-pulse">
                            <div class="w-32 h-32 rounded-full bg-black/5 animate-ping"></div>
                        </div>
                        <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400">Transitioning to Rest Mode</p>
                    </div>
                {/if}

                <!-- Vertical Scroll Feed -->
                <div 
                    class="flex-1 overflow-y-scroll snap-y snap-mandatory no-scrollbar"
                    onscroll={handleScroll}
                >
                    {#if isLoadingFeed}
                        <div class="h-screen w-full flex items-center justify-center">
                            <div class="w-12 h-12 border-4 border-black border-t-transparent rounded-full animate-spin"></div>
                        </div>
                    {:else if focusFeed.length === 0}
                        <div class="h-screen w-full flex flex-col items-center justify-center space-y-6">
                            <span class="text-4xl">🌑</span>
                            <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400">No content available for this phase</p>
                            <button class="underline text-xs" onclick={() => endSession(null)}>Exit Session</button>
                        </div>
                    {:else}
                        {#each focusFeed as content, i}
                            <FocusSlide {content} active={activeSlideIndex === i} />
                        {/each}
                        
                        <!-- End of Feed Slide -->
                        <div class="h-screen w-full flex flex-col items-center justify-center snap-start bg-gray-50 space-y-8">
                            <div class="text-center space-y-4">
                                <h3 class="text-xl font-bold uppercase tracking-widest">End of Curated Flow</h3>
                                <p class="text-xs text-gray-500">You've seen everything we picked for this session.</p>
                            </div>
                            <button 
                                class="bg-black text-white px-12 py-4 text-[10px] font-bold uppercase tracking-widest"
                                onclick={() => endSession(5)}
                            >
                                Complete Session Now
                            </button>
                        </div>
                    {/if}
                </div>
            </div>

        {:else}
            <!-- Goal Configuration (Same as before) -->
            <div class="max-w-4xl mx-auto space-y-16 animate-fadeIn">
                <header>
                    <h1 class="text-6xl font-bold tracking-tighter uppercase leading-none">Focus<br/>Workspace</h1>
                    <p class="text-gray-400 text-lg mt-6 max-w-md">Design your attention boundaries. Real data, real focus.</p>
                </header>

                {#if goals.filter((g) => g.status === "ATIVA").length > 0}
                    <div class="border-2 border-black p-12 flex justify-between items-center bg-gray-50 group hover:bg-black hover:text-white transition-all cursor-pointer" onclick={() => startSession()}>
                        <div>
                            <h3 class="font-bold text-2xl uppercase tracking-tight">Active Meta Found</h3>
                            <p class="text-[10px] font-bold uppercase tracking-widest mt-2 opacity-60">
                                Resume session with {goals.filter((g) => g.status === "ATIVA").length} goals
                            </p>
                        </div>
                        <div class="text-4xl">→</div>
                    </div>
                {/if}

                <div class="space-y-12">
                    <div class="flex justify-between items-end border-b-2 border-black pb-6">
                        <h2 class="font-bold text-xl uppercase tracking-tighter">Session Architect</h2>
                        <button class="btn-minimal py-2 px-4" onclick={toggleGoalForm}>
                            {showGoalForm ? "Discard" : "+ New Meta"}
                        </button>
                    </div>

                    {#if showGoalForm}
                        <div class="p-12 border-2 border-black space-y-12 animate-slideUp">
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
                                <div class="space-y-6">
                                    <label for="p" class="text-[10px] font-bold uppercase tracking-widest text-gray-400">Productivity (Min)</label>
                                    <input type="number" id="p" bind:value={tempoProdutividade} class="text-6xl font-bold w-full bg-transparent outline-none focus:text-blue-600 transition-colors" />
                                </div>
                                <div class="space-y-6">
                                    <label for="e" class="text-[10px] font-bold uppercase tracking-widest text-gray-400">Rest (Min)</label>
                                    <input type="number" id="e" bind:value={tempoEntretenimento} class="text-6xl font-bold w-full bg-transparent outline-none focus:text-orange-600 transition-colors" />
                                </div>
                            </div>

                            <div class="pt-12 border-t border-black/10 flex items-start gap-6">
                                <input type="checkbox" id="abs" bind:checked={modoAbsoluto} class="w-6 h-6 mt-1 accent-black" />
                                <div class="space-y-2">
                                    <label for="abs" class="font-bold uppercase tracking-tight">Absolute Mode</label>
                                    <p class="text-xs text-gray-400 leading-relaxed uppercase">Commitment locking. Browsing outside current category will be restricted. No early exits allowed without penalty.</p>
                                </div>
                            </div>

                            <button class="w-full bg-black text-white py-6 text-sm font-bold uppercase tracking-widest hover:tracking-[0.3em] transition-all" onclick={createGoal} disabled={isSubmitting}>
                                {isSubmitting ? 'Architecting...' : 'Initialize Immersive Session'}
                            </button>
                        </div>
                    {/if}

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {#each goals as goal}
                            <div class="p-8 border border-black/10 hover:border-black transition-all group {goal.status === 'CONCLUIDA' ? 'opacity-20 grayscale' : ''}">
                                <div class="text-[8px] font-bold uppercase tracking-widest text-gray-400 mb-4">{goal.categoria}</div>
                                <div class="text-4xl font-bold tracking-tighter mb-2">{goal.duracao_definida}m</div>
                                <div class="text-[8px] font-bold uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">Ready to sync</div>
                            </div>
                        {/each}
                    </div>
                </div>
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
