<script lang="ts">
    import { auth, isLoggedIn } from "$lib/stores";
    import { onMount } from "svelte";
    import { animate } from "motion";

    let heroRef: HTMLElement;
    let featuresRef: HTMLElement;

    onMount(() => {
        auth.init();

        // Minimalist entrance animations
        if (heroRef)
            animate(heroRef, { opacity: [0, 1], y: [20, 0] } as any, {
                duration: 0.8,
                ease: "easeOut",
            });
        if (featuresRef)
            animate(featuresRef, { opacity: [0, 1] } as any, {
                duration: 1,
                delay: 0.4,
            });
    });
</script>

<svelte:head>
    <title>Be Productive | Atenção como recurso a proteger</title>
</svelte:head>

<main class="min-h-screen bg-paper text-ink">
    <!-- Navegação -->
    <header
        class="sticky top-0 z-40 border-b border-line"
        style="background: color-mix(in srgb, var(--color-paper) 85%, transparent); backdrop-filter: blur(8px);"
    >
        <div class="max-w-6xl mx-auto px-5 sm:px-8 h-16 flex items-center justify-between">
            <a href="/" class="flex items-center gap-2.5 group">
                <span
                    class="w-9 h-9 rounded-xl bg-ink text-paper flex items-center justify-center transition-transform group-hover:scale-105 group-hover:rotate-3"
                >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" /></svg>
                </span>
                <span class="font-bold tracking-tight text-lg leading-none hidden sm:inline">Be Productive</span>
            </a>
            <nav class="flex items-center gap-2 sm:gap-3">
                <a href="/auth/login" class="btn btn-ghost">Entrar</a>
                <a href="/auth/register" class="btn btn-primary">Começar agora</a>
            </nav>
        </div>
    </header>

    <!-- Hero -->
    <section
        bind:this={heroRef}
        class="max-w-6xl mx-auto px-5 sm:px-8 pt-16 sm:pt-24 lg:pt-32 pb-16 sm:pb-24 opacity-0"
    >
        <div class="max-w-3xl">
            <p class="eyebrow mb-5">Rede social · saúde mental · curadoria ética</p>
            <h1 class="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.05]">
                A atenção é um recurso.
                <span class="text-accent">Nós a protegemos.</span>
            </h1>
            <p class="text-lg sm:text-xl text-muted mt-7 leading-relaxed max-w-2xl">
                Uma recomendação ética que preserva a sua reserva cognitiva —
                equilibrando produtividade e descanso, sem a rolagem infinita
                nem os gatilhos que esgotam a sua mente.
            </p>
            <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mt-10">
                <a href="/auth/register" class="btn btn-accent !px-7 !py-3.5 text-base">
                    Criar minha conta
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                </a>
                <a href="/feed" class="btn btn-outline !px-7 !py-3.5 text-base">
                    Explorar o feed
                </a>
            </div>
        </div>
    </section>

    <!-- Manifesto -->
    <section class="border-y border-line bg-surface">
        <div class="max-w-6xl mx-auto px-5 sm:px-8 py-14 sm:py-20">
            <blockquote class="max-w-3xl">
                <p class="text-2xl sm:text-3xl font-semibold tracking-tight leading-snug text-ink">
                    “Todo produto disputa a sua atenção. O nosso escolhe
                    <span class="text-accent-ink">devolvê-la</span> quando você já teve o suficiente.”
                </p>
                <footer class="eyebrow mt-6">O princípio por trás do algoritmo</footer>
            </blockquote>
        </div>
    </section>

    <!-- Pilares -->
    <section
        bind:this={featuresRef}
        class="max-w-6xl mx-auto px-5 sm:px-8 py-16 sm:py-24 opacity-0"
    >
        <p class="eyebrow mb-3">Como funciona</p>
        <h2 class="text-2xl sm:text-3xl font-bold tracking-tight max-w-xl">
            Três compromissos com a sua mente
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mt-10">
            <div class="card p-7 flex flex-col">
                <span class="w-11 h-11 rounded-xl bg-accent-wash text-accent flex items-center justify-center mb-5">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>
                </span>
                <h3 class="text-lg font-semibold tracking-tight">Foco com limites reais</h3>
                <p class="text-sm text-muted leading-relaxed mt-2">
                    Defina metas de tempo para produzir e para descansar. O Pacto
                    de Ulisses tranca o compromisso quando você mais precisa.
                </p>
            </div>

            <div class="card p-7 flex flex-col">
                <span class="w-11 h-11 rounded-xl bg-accent-wash text-accent flex items-center justify-center mb-5">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /></svg>
                </span>
                <h3 class="text-lg font-semibold tracking-tight">Fadiga detectada no seu aparelho</h3>
                <p class="text-sm text-muted leading-relaxed mt-2">
                    A leitura da sua fadiga acontece localmente. Quando a reserva
                    cai, reduzimos os estímulos e sugerimos uma pausa.
                </p>
            </div>

            <div class="card p-7 flex flex-col">
                <span class="w-11 h-11 rounded-xl bg-accent-wash text-accent flex items-center justify-center mb-5">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" /></svg>
                </span>
                <h3 class="text-lg font-semibold tracking-tight">Algoritmo do seu lado</h3>
                <p class="text-sm text-muted leading-relaxed mt-2">
                    A recomendação prioriza a sua paz de espírito acima do
                    engajamento — conteúdo de qualidade, não vício.
                </p>
            </div>
        </div>
    </section>

    <!-- CTA final -->
    <section class="border-t border-line">
        <div class="max-w-6xl mx-auto px-5 sm:px-8 py-16 sm:py-24 text-center">
            <h2 class="text-3xl sm:text-4xl font-bold tracking-tight max-w-2xl mx-auto leading-tight">
                Comece a proteger a sua atenção hoje.
            </h2>
            <p class="text-muted mt-4 max-w-md mx-auto">
                Grátis para começar. Sem rolagem infinita, sem culpa.
            </p>
            <div class="flex flex-col sm:flex-row justify-center gap-3 mt-8">
                <a href="/auth/register" class="btn btn-primary !px-7 !py-3.5 text-base">Criar minha conta</a>
                <a href="/feed" class="btn btn-outline !px-7 !py-3.5 text-base">Explorar o feed</a>
            </div>
        </div>
    </section>

    <!-- Rodapé -->
    <footer class="border-t border-line">
        <div class="max-w-6xl mx-auto px-5 sm:px-8 py-8 flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-subtle">
            <div class="flex items-center gap-2">
                <span class="w-6 h-6 rounded-lg bg-ink text-paper flex items-center justify-center">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" /></svg>
                </span>
                <span>&copy; 2026 Be Productive</span>
            </div>
            <div class="flex gap-6">
                <a href="/" class="hover:text-ink transition-colors">Privacidade</a>
                <a href="/" class="hover:text-ink transition-colors">Termos</a>
            </div>
        </div>
    </footer>
</main>
