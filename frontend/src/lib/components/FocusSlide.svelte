<script lang="ts">
    import { api, type Content } from "$lib/api";
    import { currentUser } from "$lib/stores";
    import { fade, slide } from "svelte/transition";

    interface Props {
        content: Content;
        active: boolean;
    }

    let { content, active }: Props = $props();

    let showReportModal = $state(false);
    let feedbackGiven = $state<string | null>(null);

    async function handleFeedback(type: string) {
        if (!$currentUser) return;
        try {
            await api.submitFeedback(content.id_conteudo, $currentUser.id_usuario, type);
            feedbackGiven = type;
        } catch (err) {
            console.error("Error submitting feedback:", err);
        }
    }

    function getEmbedUrl(url: string | undefined) {
        if (!url) return "";
        // Simple YouTube/SoundCloud check for mock data
        if (url.includes("youtube.com") || url.includes("youtu.be")) {
            const id = url.split("v=")[1] || url.split("/").pop();
            return `https://www.youtube.com/embed/${id}?autoplay=${active ? 1 : 0}&mute=0&controls=1`;
        }
        return url;
    }
</script>

<section class="focus-slide h-screen w-full flex flex-col items-center justify-center relative snap-start bg-white overflow-hidden border-b border-black/5">
    <!-- Background Type Decoration (Subtle) -->
    <div class="absolute inset-0 flex items-center justify-center opacity-[0.02] pointer-events-none select-none">
        <span class="text-[40vh] font-bold uppercase tracking-tighter">
            {content.tipo_de_midia}
        </span>
    </div>

    <!-- Main Content Container -->
    <div class="max-w-4xl w-full h-full flex flex-col p-12 md:p-24 relative z-10">
        <!-- Metadata Top -->
        <header class="flex justify-between items-start mb-8">
            <div class="space-y-2">
                <div class="flex items-center gap-3">
                    <span class="px-2 py-0.5 bg-black text-white text-[10px] font-bold uppercase tracking-widest">
                        {content.categoria}
                    </span>
                    <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                        #{content.tags_relevantes?.split(',')[0]}
                    </span>
                </div>
                <h2 class="text-3xl md:text-5xl font-bold tracking-tighter uppercase leading-none max-w-2xl">
                    {content.titulo}
                </h2>
            </div>
        </header>

        <!-- Dynamic Media Area -->
        <div class="flex-1 flex items-center justify-center w-full min-h-0 bg-gray-50 border border-black/10 group relative">
            {#if content.tipo_de_midia === 'VIDEO'}
                <iframe
                    title={content.titulo}
                    src={getEmbedUrl(content.midia_url)}
                    class="w-full h-full"
                    allow="autoplay; encrypted-media"
                    allowfullscreen
                ></iframe>
            {:else if content.tipo_de_midia === 'AUDIO'}
                <div class="w-full h-full flex flex-col items-center justify-center p-12 space-y-8">
                    <div class="w-32 h-32 rounded-full border-2 border-black flex items-center justify-center animate-spin-slow">
                        <span class="text-4xl">🎧</span>
                    </div>
                    <iframe
                        title={content.titulo}
                        src={getEmbedUrl(content.midia_url)}
                        width="100%"
                        height="166"
                        scrolling="no"
                        frameborder="no"
                        allow="autoplay"
                    ></iframe>
                </div>
            {:else}
                <!-- TEXT Content -->
                <div class="w-full h-full overflow-y-auto p-12 md:p-16 prose prose-black max-w-none">
                    <div class="text-xl leading-relaxed font-serif text-gray-800 space-y-6">
                        {content.corpo}
                    </div>
                </div>
            {/if}
        </div>

        <!-- Interactions Footer -->
        <footer class="mt-8 flex justify-between items-center">
            <div class="flex items-center gap-8">
                <div class="flex gap-4">
                    <button 
                        class="interaction-btn {feedbackGiven === 'util' ? 'active' : ''}"
                        onclick={() => handleFeedback('util')}
                    >
                        <span class="text-lg">🎯</span>
                        <span class="text-[10px] font-bold uppercase tracking-widest">Useful</span>
                    </button>
                    <button 
                        class="interaction-btn {feedbackGiven === 'relaxante' ? 'active' : ''}"
                        onclick={() => handleFeedback('relaxante')}
                    >
                        <span class="text-lg">😌</span>
                        <span class="text-[10px] font-bold uppercase tracking-widest">Relaxing</span>
                    </button>
                </div>
                
                <button 
                    class="text-[10px] font-bold uppercase tracking-widest text-gray-400 hover:text-red-600 transition-colors"
                    onclick={() => (showReportModal = true)}
                >
                    Report Issue
                </button>
            </div>

            <div class="text-[10px] font-bold uppercase tracking-widest text-gray-300">
                Author ID: {content.autor_id}
            </div>
        </footer>
    </div>
</section>

<style>
    .focus-slide {
        scroll-snap-align: start;
        scroll-snap-stop: always;
    }

    .interaction-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem;
        border: 1px solid transparent;
        transition: all 0.2s ease;
        opacity: 0.6;
    }

    .interaction-btn:hover {
        opacity: 1;
        background: #f9f9f9;
    }

    .interaction-btn.active {
        opacity: 1;
        border-color: black;
        background: white;
    }

    .animate-spin-slow {
        animation: spin 8s linear infinite;
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    /* Hide scrollbar for clean look */
    .prose::-webkit-scrollbar {
        width: 4px;
    }
    .prose::-webkit-scrollbar-track {
        background: transparent;
    }
    .prose::-webkit-scrollbar-thumb {
        background: #eee;
    }
    .prose::-webkit-scrollbar-thumb:hover {
        background: #ccc;
    }
</style>
