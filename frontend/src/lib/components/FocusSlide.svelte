<script lang="ts">
    import { api, type Content } from "$lib/api";
    import { currentUser } from "$lib/stores";
    import { fade, slide } from "svelte/transition";

    interface Props {
        content: Content;
        active: boolean;
        index?: number;
        total?: number;
    }

    let { content, active, index = 0, total = 1 }: Props = $props();

    let showReportModal = $state(false);
    let feedbackGiven = $state<string | null>(null);
    let reportReason = $state("não é relevante para mim");
    let reportDetails = $state("");
    let reportStatus = $state<"idle" | "sending" | "success" | "error">("idle");

    const mediaLabels: Record<Content["tipo_de_midia"], string> = {
        TEXTO: "Leitura",
        VIDEO: "Vídeo",
        AUDIO: "Áudio",
    };

    function categoryLabel(category: Content["categoria"]): string {
        return category === "PRODUTIVIDADE" ? "Produtividade" : "Descanso";
    }

    async function handleFeedback(type: string) {
        if (!$currentUser) return;
        try {
            await api.submitFeedback(content.id_conteudo, $currentUser.id_usuario, type);
            feedbackGiven = type;
        } catch (err) {
            console.error("Error submitting feedback:", err);
        }
    }

    async function submitReport() {
        if (!$currentUser || reportStatus === "sending") return;
        reportStatus = "sending";
        try {
            await api.reportContent(
                content.id_conteudo,
                $currentUser.id_usuario,
                reportReason,
                reportDetails.trim(),
            );
            reportStatus = "success";
        } catch (err) {
            console.error("Error reporting content:", err);
            reportStatus = "error";
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

<section class="focus-slide h-[100svh] min-h-[620px] w-full flex flex-col items-center justify-center relative snap-start bg-paper overflow-hidden border-b border-line" aria-label="Conteúdo {index + 1} de {total}">
    <!-- Background Type Decoration (Subtle) -->
    <div class="absolute inset-0 flex items-center justify-center opacity-[0.02] pointer-events-none select-none">
        <span class="text-[40vh] font-bold uppercase tracking-tighter">
            {content.tipo_de_midia}
        </span>
    </div>

    <!-- Main Content Container -->
    <div class="max-w-5xl w-full h-full flex flex-col px-5 pt-24 pb-7 sm:px-8 sm:pt-28 sm:pb-8 lg:px-12 relative z-10">
        <!-- Metadata Top -->
        <header class="flex justify-between items-start gap-4 mb-5 sm:mb-7">
            <div class="space-y-2">
                <div class="flex flex-wrap items-center gap-2">
                    <span class="chip chip-accent !cursor-default !text-[10px] uppercase tracking-[.12em]">
                        {categoryLabel(content.categoria)}
                    </span>
                    <span class="text-[10px] font-semibold text-subtle uppercase tracking-[.12em]">
                        {mediaLabels[content.tipo_de_midia]}
                    </span>
                </div>
                <h2 class="text-2xl sm:text-4xl lg:text-5xl font-bold tracking-tight leading-[1.04] max-w-3xl">
                    {content.titulo}
                </h2>
                {#if content.tags_relevantes}
                    <p class="text-xs text-muted truncate max-w-xl">
                        {content.tags_relevantes.split(',').slice(0, 3).map((tag) => `#${tag.trim()}`).join(' · ')}
                    </p>
                {/if}
            </div>
        </header>

        <!-- Dynamic Media Area -->
        <div class="flex-1 flex items-center justify-center w-full min-h-0 rounded-3xl bg-surface border border-line shadow-soft group relative overflow-hidden">
            {#if content.tipo_de_midia === 'VIDEO'}
                <iframe
                    title={content.titulo}
                    src={getEmbedUrl(content.midia_url)}
                    class="w-full h-full"
                    allow="autoplay; encrypted-media"
                    allowfullscreen
                ></iframe>
            {:else if content.tipo_de_midia === 'AUDIO'}
                <div class="w-full h-full flex flex-col items-center justify-center p-6 sm:p-12 gap-7">
                    <div class="w-24 h-24 sm:w-32 sm:h-32 rounded-full bg-accent-wash text-accent border border-accent/20 flex items-center justify-center animate-spin-slow">
                        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3z"/><path d="M3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>
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
                <div class="w-full h-full overflow-y-auto p-6 sm:p-10 lg:p-14 max-w-none">
                    <div class="text-base sm:text-lg leading-[1.75] font-serif text-ink space-y-6 max-w-3xl mx-auto">
                        {content.corpo}
                    </div>
                </div>
            {/if}
        </div>

        <!-- Interactions Footer -->
        <footer class="mt-5 sm:mt-7 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
            <div class="flex items-center justify-between sm:justify-start gap-3 sm:gap-6">
                <div class="flex gap-1.5 sm:gap-2" aria-label="Avaliar conteúdo">
                    <button 
                        class="interaction-btn {feedbackGiven === 'util' ? 'active' : ''}"
                        onclick={() => handleFeedback('util')}
                        aria-pressed={feedbackGiven === 'util'}
                    >
                        <span class="text-sm">Útil</span>
                    </button>
                    <button 
                        class="interaction-btn {feedbackGiven === 'relaxante' ? 'active' : ''}"
                        onclick={() => handleFeedback('relaxante')}
                        aria-pressed={feedbackGiven === 'relaxante'}
                    >
                        <span class="text-sm">Relaxante</span>
                    </button>
                </div>
                
                <button 
                    class="btn btn-ghost !px-2 !text-xs"
                    onclick={() => (showReportModal = true)}
                >
                    Sinalizar
                </button>
            </div>

            <div class="text-xs font-medium text-subtle tabular-nums">
                Conteúdo {index + 1} de {total}
            </div>
        </footer>
    </div>
</section>

{#if showReportModal}
    <div class="fixed inset-0 z-[200] flex items-center justify-center p-5 bg-ink/45 backdrop-blur-sm" role="presentation" onclick={(event) => event.target === event.currentTarget && (showReportModal = false)}>
        <div class="card w-full max-w-md p-6 sm:p-7 animate-scaleIn" role="dialog" aria-modal="true" aria-labelledby="report-title">
            {#if reportStatus === "success"}
                <div class="text-center py-3">
                    <span class="mx-auto w-12 h-12 rounded-2xl bg-accent-wash text-accent flex items-center justify-center mb-4">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 4 4L19 6"/></svg>
                    </span>
                    <h2 class="text-lg font-bold" id="report-title">Obrigado pelo sinal</h2>
                    <p class="text-sm text-muted mt-2">Vamos revisar este conteúdo para manter o espaço útil e seguro.</p>
                    <button class="btn btn-primary w-full mt-6" onclick={() => { showReportModal = false; reportStatus = "idle"; }}>Fechar</button>
                </div>
            {:else}
                <div class="flex items-start justify-between gap-4">
                    <div>
                        <p class="eyebrow mb-1">Cuidar do espaço</p>
                        <h2 class="text-xl font-bold" id="report-title">O que aconteceu?</h2>
                    </div>
                    <button class="btn btn-ghost !p-2" aria-label="Fechar sinalização" onclick={() => (showReportModal = false)}>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
                    </button>
                </div>
                <label class="block text-sm font-medium mt-6" for="report-reason">Motivo</label>
                <select id="report-reason" class="input mt-2" bind:value={reportReason}>
                    <option>não é relevante para mim</option>
                    <option>informação incorreta</option>
                    <option>conteúdo inadequado</option>
                    <option>problema técnico</option>
                </select>
                <label class="block text-sm font-medium mt-4" for="report-details">Detalhes <span class="font-normal text-subtle">(opcional)</span></label>
                <textarea id="report-details" class="input mt-2 min-h-24 resize-y" bind:value={reportDetails} placeholder="Conte um pouco mais, se quiser."></textarea>
                {#if reportStatus === "error"}
                    <p class="text-sm text-danger mt-3" role="alert">Não foi possível enviar agora. Tente novamente.</p>
                {/if}
                <div class="flex flex-col-reverse sm:flex-row sm:justify-end gap-2 mt-6">
                    <button class="btn btn-ghost" onclick={() => (showReportModal = false)}>Cancelar</button>
                    <button class="btn btn-primary" onclick={submitReport} disabled={reportStatus === "sending"}>
                        {reportStatus === "sending" ? "Enviando…" : "Enviar sinal"}
                    </button>
                </div>
            {/if}
        </div>
    </div>
{/if}

<style>
    .focus-slide {
        scroll-snap-align: start;
        scroll-snap-stop: always;
    }

    .interaction-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 2.625rem;
        padding: 0.5rem 0.75rem;
        border: 1px solid var(--color-line);
        border-radius: 999px;
        color: var(--color-muted);
        background: var(--color-surface);
        transition: all 0.2s ease;
        cursor: pointer;
    }

    .interaction-btn:hover {
        color: var(--color-ink);
        border-color: var(--color-ink);
    }

    .interaction-btn.active {
        color: var(--color-accent-ink);
        border-color: color-mix(in srgb, var(--color-accent) 35%, transparent);
        background: var(--color-accent-wash);
    }

    .animate-spin-slow {
        animation: spin 8s linear infinite;
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    @media (prefers-reduced-motion: reduce) {
        .animate-spin-slow { animation: none; }
    }

</style>
