<script lang="ts">
    import { currentUser, isLoggedIn, ui } from "$lib/stores";
    import { api, type FocusGoal, type Session } from "$lib/api";
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import { animate } from "motion";

    let goals = $state<FocusGoal[]>([]);
    let activeSession = $state<Session | null>(null);
    let isLoading = $state(true);
    let showGoalForm = $state(false);
    let showReport = $state<SessionReport | null>(null);
    let lastActiveElement = $state<HTMLElement | null>(null);

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

    // Fatigue & Transitions (UC12, UC16)
    let showBreakSuggestion = $state(false);
    let transitionWarning = $state(false);
    let goalReached = $state(false);
    let showTransitionConfirm = $state(false);

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

    // UC09: Create Goal & Immediate Start
    async function createGoal() {
        if (!$currentUser) return;
        
        // Validation (RN001)
        if (tempoProdutividade === 0 && tempoEntretenimento === 0) {
            alert("Please set at least 1 minute for productivity or entertainment.");
            return;
        }

        try {
            const newGoals = await api.createGoal({
                user_id: $currentUser.id_usuario,
                tempo_produtividade: tempoProdutividade,
                tempo_entretenimento: tempoEntretenimento,
                modo_absoluto: modoAbsoluto,
            });
            
            showGoalForm = false;
            if (lastActiveElement) lastActiveElement.focus();
            
            // UC09.7: Start session immediately
            await startSession(newGoals);
        } catch (err) {
            console.error("Error creating goal:", err);
        }
    }

    function toggleGoalForm() {
        if (!showGoalForm) {
            lastActiveElement = document.activeElement as HTMLElement;
            showGoalForm = true;
        } else {
            showGoalForm = false;
            if (lastActiveElement) lastActiveElement.focus();
        }
    }

    async function startSession(specificGoals?: FocusGoal[]) {
        if (!$currentUser) return;
        
        const goalsToUse = specificGoals || goals.filter(g => g.status === 'ATIVA');
        if (goalsToUse.length === 0) return;

        const goalIds = goalsToUse.map(g => g.id_meta);

        try {
            activeSession = await api.startSession($currentUser.id_usuario, goalIds);
            currentCategory = 'PRODUTIVIDADE';
            ui.enterFocusMode();
            startTimer();
            ariaAnnouncement = "Focus session started. Productivity mode active.";
        } catch (err) {
            console.error("Error starting session:", err);
        }
    }

    function startTimer() {
        elapsedMinutes = 0;
        goalReached = false;
        showBreakSuggestion = false;
        transitionWarning = false;

        timerInterval = setInterval(() => {
            elapsedMinutes++;
            checkFocusHealth();
        }, 60000);
    }

    function checkFocusHealth() {
        const target = currentCategory === 'PRODUTIVIDADE' ? tempoProdutividade : tempoEntretenimento;

        // UC12.1: 30-second warning (simplified to 1 min before for this mock logic)
        if (elapsedMinutes === target - 1 && !transitionWarning) {
            transitionWarning = true;
            ariaAnnouncement = "Transition imminent. 1 minute remaining.";
        }

        if (elapsedMinutes >= target && !goalReached) {
            handleTransition();
        }

        // Fatigue Detection
        if (currentCategory === 'PRODUTIVIDADE' && elapsedMinutes >= 50 && !showBreakSuggestion) {
            showBreakSuggestion = true;
        }
    }

    function playTransitionSound() {
        // Simple Web Audio beep (UC12.3)
        try {
            const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.type = "sine";
            osc.frequency.setValueAtTime(440, ctx.currentTime);
            gain.gain.setValueAtTime(0.1, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.5);
            osc.start();
            osc.stop(ctx.currentTime + 0.5);
        } catch (e) { /* Audio fallback */ }
    }

    function handleTransition() {
        playTransitionSound();
        transitionWarning = false;
        
        if (currentCategory === 'PRODUTIVIDADE' && tempoEntretenimento > 0) {
            currentCategory = 'ENTRETENIMENTO';
            elapsedMinutes = 0;
            showTransitionConfirm = true;
            ariaAnnouncement = "Productivity goal reached. Switching to Entertainment.";
        } else {
            goalReached = true;
            ariaAnnouncement = "Session complete.";
            const timerCircle = document.querySelector(".timer-circle");
            if (timerCircle) {
                animate(timerCircle, { scale: [1, 1.05, 1], borderColor: ["#000", "#22c55e", "#000"] } as any, { duration: 1 });
            }
        }
    }

    async function endSession(feedback: number | null = null) {
        if (!activeSession) return;
        
        // UC10: Prevent early exit in Absolute Mode
        if (modoAbsoluto && !goalReached && !confirm("Absolute Mode is active. Are you sure you want to break your commitment?")) {
            return;
        }

        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }

        try {
            // In a real app, we'd calculate real stats here
            await api.endSession(activeSession.id_sessao, {
                tempo_produtividade_realizado: currentCategory === 'PRODUTIVIDADE' ? elapsedMinutes : tempoProdutividade,
                tempo_entretenimento_realizado: currentCategory === 'ENTRETENIMENTO' ? elapsedMinutes : 0,
                feedback,
            });

            // UC13: Get Report
            const report = await api.getSessionReport(activeSession.id_sessao);
            showReport = report;
            ui.exitFocusMode();
        } catch (err) {
            console.error("Error ending session:", err);
            ui.exitFocusMode();
            goto("/feed");
        }
    }

    function formatTime(minutes: number): string {
        const h = Math.floor(minutes / 60);
        const m = minutes % 60;
        return h > 0 ? `${h}h ${m}m` : `${m}m`;
    }
</script>

<svelte:head>
    <title>Focus | Be Productive</title>
</svelte:head>

<!-- ARIA Live region for accessibility announcements -->
<div class="sr-only" aria-live="polite">{ariaAnnouncement}</div>

<div class="flex min-h-screen bg-white text-black">
    {#if !$ui.focusMode && !showReport}
        <Sidebar />
    {/if}

    <main
        class="flex-1 {$ui.focusMode || showReport
            ? 'p-0 flex items-center justify-center'
            : 'ml-64 p-12'}"
    >
        {#if showReport}
            <!-- UC13: Session Report -->
            <div class="max-w-xl w-full p-12 animate-slideUp border border-black bg-white shadow-2xl">
                <header class="text-center mb-12">
                    <div class="inline-block border border-black px-4 py-1 text-[10px] font-bold uppercase tracking-widest mb-4">
                        Session Report
                    </div>
                    <h2 class="text-4xl font-bold uppercase tracking-tighter">
                        {showReport.classification === 'progresso' ? 'Session Success' : 'Session Ended'}
                    </h2>
                    <p class="text-sm text-gray-500 mt-2">{showReport.message}</p>
                </header>

                <div class="grid grid-cols-2 gap-8 mb-12 border-y border-black py-8">
                    <div>
                        <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-1">Productivity</p>
                        <p class="text-2xl font-bold">{formatTime(showReport.session.tempo_produtividade_realizado)}</p>
                    </div>
                    <div>
                        <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-1">Entertainment</p>
                        <p class="text-2xl font-bold">{formatTime(showReport.session.tempo_entretenimento_realizado)}</p>
                    </div>
                </div>

                <button 
                    class="w-full bg-black text-white py-4 text-xs font-bold uppercase tracking-widest hover:bg-gray-800 transition-colors"
                    onclick={() => { showReport = null; goto("/feed"); }}
                >
                    Back to Feed
                </button>
            </div>
        {:else if $ui.focusMode && activeSession}
            <div class="text-center max-w-lg w-full p-12 animate-fadeIn">
                <div class="mb-16">
                    <div
                        class="timer-circle w-64 h-64 rounded-full border-4 border-black mx-auto flex flex-col items-center justify-center mb-12 shadow-[0_0_60px_rgba(0,0,0,0.05)] transition-all duration-500 {transitionWarning ? 'border-yellow-500 animate-pulse' : ''}"
                    >
                        <span class="text-6xl font-bold tracking-tighter"
                            >{formatTime(elapsedMinutes)}</span
                        >
                        <span
                            class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mt-2"
                        >
                            {currentCategory} MODE
                        </span>
                    </div>

                    {#if transitionWarning}
                        <div class="mb-8 text-yellow-600 text-[10px] font-bold uppercase tracking-widest animate-bounce">
                            Transition Imminent
                        </div>
                    {/if}

                    {#if showBreakSuggestion}
                        <div
                            class="mb-12 p-8 border border-black bg-gray-50 animate-bounce cursor-default"
                        >
                            <span
                                class="text-[10px] font-bold uppercase tracking-widest block mb-2"
                                >Health Tip</span
                            >
                            <h3
                                class="text-lg font-bold uppercase leading-tight"
                            >
                                Focusing for a while? Maybe it's time for a
                                short break.
                            </h3>
                        </div>
                    {/if}

                    {#if showTransitionConfirm}
                        <div
                            class="mb-12 p-8 border border-green-600 bg-green-50 animate-slideUp"
                        >
                            <span
                                class="text-[10px] font-bold uppercase tracking-widest block mb-2 text-green-700"
                                >Productivity Meta Reached</span
                            >
                            <h3
                                class="text-lg font-bold uppercase leading-tight"
                            >
                                Nice work. Starting your entertainment period.
                            </h3>
                            <div class="flex gap-4 mt-6 justify-center">
                                <button
                                    class="bg-black text-white px-6 py-3 text-[10px] font-bold uppercase tracking-widest hover:bg-gray-800 transition-colors"
                                    onclick={() =>
                                        goto("/feed?cat=ENTRETENIMENTO")}
                                >
                                    View Rest Content
                                </button>
                                <button
                                    class="text-[10px] font-bold uppercase tracking-widest underline"
                                    onclick={() =>
                                        (showTransitionConfirm = false)}
                                >
                                    Dismiss
                                </button>
                            </div>
                        </div>
                    {/if}

                    <h2 class="text-2xl font-bold uppercase tracking-tighter">
                        {currentCategory === 'PRODUTIVIDADE' ? 'You are in the zone.' : 'Time to recharge.'}
                    </h2>
                </div>

                <div class="flex flex-col gap-4">
                    {#if !modoAbsoluto || goalReached}
                        <button
                            class="w-full bg-black text-white py-4 text-xs font-bold uppercase tracking-widest hover:bg-gray-800 transition-colors {goalReached
                                ? 'animate-pulse bg-green-600'
                                : ''}"
                            onclick={() => endSession(5)}
                        >
                            {goalReached ? "Finish & View Report" : "End Session Early"}
                        </button>
                    {:else}
                        <div class="py-4 border border-dashed border-gray-300">
                            <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400">
                                Absolute Mode Active - Session Locked
                            </p>
                        </div>
                    {/if}
                    
                    {#if !modoAbsoluto && !goalReached}
                        <button
                            class="text-[10px] font-bold uppercase tracking-widest text-gray-400 hover:text-black transition-colors"
                            onclick={() => endSession(null)}
                        >
                            Pause & Exit
                        </button>
                    {/if}
                </div>
            </div>
        {:else}
            <header class="mb-16">
                <h1 class="text-4xl font-bold tracking-tighter uppercase">
                    Focus Goals
                </h1>
                <p class="text-gray-400 text-sm mt-2">
                    Define your balance between work and rest.
                </p>
            </header>

            {#if goals.filter((g) => g.status === "ATIVA").length > 0}
                <div
                    class="border border-black p-8 mb-16 flex justify-between items-center bg-gray-50"
                >
                    <div>
                        <h3 class="font-bold text-lg uppercase tracking-tight">
                            Resume Session?
                        </h3>
                        <p
                            class="text-xs text-gray-500 uppercase tracking-widest mt-1"
                        >
                            You have {goals.filter((g) => g.status === "ATIVA")
                                .length} active goal(s)
                        </p>
                    </div>
                    <button
                        class="bg-black text-white px-8 py-4 text-xs font-bold uppercase tracking-widest hover:bg-gray-800 transition-colors"
                        onclick={() => startSession()}
                    >
                        Resume Active Meta
                    </button>
                </div>
            {/if}

            <div class="space-y-8">
                <div
                    class="flex justify-between items-center border-b border-black pb-4"
                >
                    <h2 class="font-bold text-sm uppercase tracking-widest">
                        Saved Goals
                    </h2>
                    <button
                        class="text-[10px] font-bold uppercase tracking-widest underline hover:no-underline"
                        onclick={toggleGoalForm}
                    >
                        {showGoalForm ? "Cancel" : "+ New Goal"}
                    </button>
                </div>

                {#if showGoalForm}
                    <div
                        class="border border-black p-8 space-y-8 animate-slideUp"
                        role="dialog"
                        aria-labelledby="goal-form-title"
                    >
                        <div class="flex justify-between items-center">
                            <h3 id="goal-form-title" class="font-bold uppercase tracking-widest text-xs">
                                New Focus Goal
                            </h3>
                            <div class="text-[10px] font-bold bg-black text-white px-2 py-1">
                                TOTAL: {formatTime(tempoTotal)}
                            </div>
                        </div>

                        <div class="space-y-4">
                            <label
                                for="tempoProdutividade"
                                class="block text-[10px] font-bold uppercase tracking-widest text-gray-400"
                            >
                                Productivity: {formatTime(tempoProdutividade)}
                            </label>
                            <input
                                type="range"
                                id="tempoProdutividade"
                                min="0"
                                max="120"
                                step="5"
                                class="w-full accent-black cursor-pointer"
                                bind:value={tempoProdutividade}
                            />
                        </div>

                        <div class="space-y-4">
                            <label
                                for="tempoEntretenimento"
                                class="block text-[10px] font-bold uppercase tracking-widest text-gray-400"
                            >
                                Entertainment: {formatTime(tempoEntretenimento)}
                            </label>
                            <input
                                type="range"
                                id="tempoEntretenimento"
                                min="0"
                                max="60"
                                step="5"
                                class="w-full accent-black cursor-pointer"
                                bind:value={tempoEntretenimento}
                            />
                        </div>

                        <div class="space-y-4 border-t border-black pt-6">
                            <div class="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    id="modoAbsoluto"
                                    bind:checked={modoAbsoluto}
                                    class="accent-black w-4 h-4"
                                />
                                <label
                                    for="modoAbsoluto"
                                    class="text-[10px] font-bold uppercase tracking-widest cursor-pointer"
                                >
                                    Activate Absolute Mode (UC10)
                                </label>
                            </div>
                            
                            {#if modoAbsoluto}
                                <p class="text-[10px] text-gray-500 uppercase leading-relaxed animate-fadeIn">
                                    Warning: In Absolute Mode, you cannot pause or cancel the session.
                                    The application will restrict navigation until the goal is met.
                                </p>
                            {/if}
                        </div>

                        <button
                            class="w-full bg-black text-white py-4 text-xs font-bold uppercase tracking-widest hover:bg-gray-800 transition-colors"
                            onclick={createGoal}
                        >
                            Confirm & Start Session immediately
                        </button>
                    </div>
                {/if}

                {#if isLoading}
                    <div class="flex gap-8 overflow-x-auto pb-4">
                        {#each Array(3) as _}
                            <div
                                class="w-64 h-48 border border-gray-100 animate-pulse bg-gray-50"
                            ></div>
                        {/each}
                    </div>
                {:else if goals.length === 0}
                    <div
                        class="py-24 text-center border border-dashed border-gray-200"
                    >
                        <p
                            class="text-[10px] font-bold text-gray-400 uppercase tracking-widest"
                        >
                            No goals defined yet.
                        </p>
                    </div>
                {:else}
                    <div
                        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
                    >
                        {#each goals as goal (goal.id_meta)}
                            <div
                                class="border border-black p-8 group transition-all hover:bg-black hover:text-white {goal.status ===
                                'CONCLUIDA'
                                    ? 'opacity-30'
                                    : ''}"
                            >
                                <div
                                    class="flex justify-between items-start mb-6"
                                >
                                    <div
                                        class="text-[10px] font-bold uppercase tracking-widest py-1 px-2 border border-current"
                                    >
                                        {goal.categoria}
                                    </div>
                                    <div
                                        class="text-[10px] font-bold uppercase tracking-widest opacity-50"
                                    >
                                        {goal.status}
                                    </div>
                                </div>
                                <div
                                    class="text-4xl font-bold tracking-tighter mb-2"
                                >
                                    {formatTime(goal.duracao_definida)}
                                </div>
                                <div
                                    class="text-[10px] font-bold uppercase tracking-widest opacity-50"
                                >
                                    Target Duration
                                </div>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        {/if}
    </main>
</div>
