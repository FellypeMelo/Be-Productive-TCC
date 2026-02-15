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
    <title>Be-Productive | Focus & Balance</title>
</svelte:head>

<main
    class="min-h-screen bg-white text-black selection:bg-black selection:text-white"
>
    <!-- Navigation Header -->
    <header class="border-b border-black">
        <div
            class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between"
        >
            <div
                class="flex items-center gap-2 font-bold text-xl tracking-tighter"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    ><circle cx="12" cy="12" r="10" /><path
                        d="M12 6v6l4 2"
                    /></svg
                >
                BE PRODUCTIVE
            </div>
            <div class="flex items-center gap-8 text-sm font-medium">
                <a href="/auth/login" class="hover:underline">Login</a>
                <a
                    href="/auth/register"
                    class="bg-black text-white px-4 py-2 hover:bg-gray-800 transition-colors"
                    >Get Started</a
                >
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section bind:this={heroRef} class="max-w-7xl mx-auto px-6 py-32 opacity-0">
        <div class="max-w-3xl">
            <h1 class="text-7xl font-bold leading-[1.1] mb-8">
                Content for a <br /> balanced mind.
            </h1>
            <p class="text-xl text-gray-600 mb-12 leading-relaxed">
                A minimalist platform designed to help you balance productivity
                and entertainment without the noise.
            </p>
            <div class="flex items-center gap-4">
                <a
                    href="/feed"
                    class="bg-black text-white px-8 py-4 text-lg font-bold hover:bg-gray-800 transition-colors"
                >
                    Explore Feed
                </a>
            </div>
        </div>
    </section>

    <!-- Features Grid -->
    <section
        bind:this={featuresRef}
        class="max-w-7xl mx-auto px-6 py-24 border-t border-black opacity-0"
    >
        <div class="grid grid-cols-1 md:grid-cols-3 gap-16">
            <div class="space-y-4">
                <div
                    class="w-12 h-12 border border-black flex items-center justify-center"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        ><circle cx="12" cy="12" r="10" /><polyline
                            points="12 6 12 12 16 14"
                        /></svg
                    >
                </div>
                <h3 class="font-bold text-xl uppercase tracking-wider">
                    Intelligent Focus
                </h3>
                <p class="text-gray-600">
                    Set precise time goals for your productive and leisure
                    moments.
                </p>
            </div>

            <div class="space-y-4">
                <div
                    class="w-12 h-12 border border-black flex items-center justify-center"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        ><path
                            d="M20.42 4.58a5.4 5.4 0 0 0-7.65 0l-.77.78-.77-.78a5.4 5.4 0 0 0-7.65 10.8l8.42 8.42 8.42-8.42a5.4 5.4 0 0 0 0-7.65z"
                        /></svg
                    >
                </div>
                <h3 class="font-bold text-xl uppercase tracking-wider">
                    Mental Wellness
                </h3>
                <p class="text-gray-600">
                    Proactive reminders for breaks and healthy content
                    suggestions.
                </p>
            </div>

            <div class="space-y-4">
                <div
                    class="w-12 h-12 border border-black flex items-center justify-center"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        ><polygon
                            points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
                        /></svg
                    >
                </div>
                <h3 class="font-bold text-xl uppercase tracking-wider">
                    Ethical Algorithm
                </h3>
                <p class="text-gray-600">
                    A recommendation system that prioritizes your peace of mind
                    over engagement.
                </p>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-black py-12">
        <div
            class="max-w-7xl mx-auto px-6 flex justify-between items-center text-xs uppercase tracking-widest text-gray-500"
        >
            <div>&copy; 2026 Be Productive</div>
            <div class="flex gap-8">
                <a href="/" class="hover:text-black">Privacy</a>
                <a href="/" class="hover:text-black">Terms</a>
            </div>
        </div>
    </footer>
</main>
