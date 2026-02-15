<script lang="ts">
    import type { Content } from "$lib/api";

    interface Props {
        content: Content;
        onFeedback?: (type: string) => void;
    }

    let { content, onFeedback }: Props = $props();

    let showFeedback = $state(false);

    function formatDate(dateStr: string): string {
        const date = new Date(dateStr);
        return date.toLocaleDateString("pt-BR", {
            day: "2-digit",
            month: "short",
        });
    }

    function getCategoryColor(category: string): string {
        return category === "PRODUTIVIDADE"
            ? "var(--color-secondary)"
            : "var(--color-accent)";
    }

    function getMediaIcon(type: string): string {
        switch (type) {
            case "VIDEO":
                return "🎬";
            case "AUDIO":
                return "🎧";
            default:
                return "📄";
        }
    }

    function handleFeedback(type: string) {
        if (onFeedback) onFeedback(type);
        showFeedback = false;
    }
</script>

<article class="content-card">
    <div class="card-header">
        <span class="media-type">{getMediaIcon(content.tipo_de_midia)}</span>
        <span
            class="category-badge"
            style="background: {getCategoryColor(content.categoria)}"
        >
            {content.categoria === "PRODUTIVIDADE" ? "🎯" : "🎮"}
            {content.categoria}
        </span>
    </div>

    <h3 class="card-title">{content.titulo}</h3>

    <p class="card-body">
        {content.corpo.length > 200
            ? content.corpo.slice(0, 200) + "..."
            : content.corpo}
    </p>

    {#if content.tags_relevantes}
        <div class="tags">
            {#each content.tags_relevantes.split(",").slice(0, 3) as tag}
                <span class="tag">#{tag.trim()}</span>
            {/each}
        </div>
    {/if}

    <div class="card-footer">
        <span class="date">{formatDate(content.data_publicacao)}</span>

        <div class="actions">
            <button
                class="action-btn"
                title="Dar feedback"
                onclick={() => (showFeedback = !showFeedback)}
            >
                💭
            </button>
            <button class="action-btn" title="Reportar"> ⚠️ </button>
        </div>
    </div>

    {#if showFeedback}
        <div class="feedback-panel animate-fadeIn">
            <p>Como você avalia este conteúdo?</p>
            <div class="feedback-buttons">
                <button
                    class="feedback-btn positive"
                    onclick={() => handleFeedback("util")}
                >
                    👍 Útil
                </button>
                <button
                    class="feedback-btn neutral"
                    onclick={() => handleFeedback("relaxante")}
                >
                    😌 Relaxante
                </button>
                <button
                    class="feedback-btn negative"
                    onclick={() => handleFeedback("nao_relevante")}
                >
                    👎 Não relevante
                </button>
            </div>
        </div>
    {/if}
</article>

<style>
    .content-card {
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: var(--space-lg);
        transition:
            transform var(--transition-base),
            box-shadow var(--transition-base);
    }

    .content-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--space-md);
    }

    .media-type {
        font-size: 1.5rem;
    }

    .category-badge {
        display: flex;
        align-items: center;
        gap: var(--space-xs);
        padding: var(--space-xs) var(--space-sm);
        border-radius: var(--radius-full);
        font-size: var(--font-size-xs);
        font-weight: 500;
        color: white;
    }

    .card-title {
        font-size: var(--font-size-lg);
        margin-bottom: var(--space-sm);
        line-height: 1.4;
    }

    .card-body {
        font-size: var(--font-size-sm);
        color: var(--color-text-secondary);
        line-height: 1.6;
        margin-bottom: var(--space-md);
    }

    .tags {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-xs);
        margin-bottom: var(--space-md);
    }

    .tag {
        font-size: var(--font-size-xs);
        color: var(--color-primary);
        background: rgba(99, 102, 241, 0.1);
        padding: var(--space-xs) var(--space-sm);
        border-radius: var(--radius-sm);
    }

    .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: var(--space-md);
        border-top: 1px solid var(--color-border);
    }

    .date {
        font-size: var(--font-size-xs);
        color: var(--color-text-muted);
    }

    .actions {
        display: flex;
        gap: var(--space-sm);
    }

    .action-btn {
        background: transparent;
        border: none;
        font-size: 1rem;
        cursor: pointer;
        padding: var(--space-xs);
        border-radius: var(--radius-sm);
        transition: background var(--transition-fast);
    }

    .action-btn:hover {
        background: var(--color-bg-tertiary);
    }

    .feedback-panel {
        margin-top: var(--space-md);
        padding: var(--space-md);
        background: var(--color-bg-secondary);
        border-radius: var(--radius-md);
    }

    .feedback-panel p {
        font-size: var(--font-size-sm);
        margin-bottom: var(--space-sm);
    }

    .feedback-buttons {
        display: flex;
        gap: var(--space-sm);
        flex-wrap: wrap;
    }

    .feedback-btn {
        padding: var(--space-xs) var(--space-md);
        border-radius: var(--radius-full);
        font-size: var(--font-size-xs);
        border: 1px solid var(--color-border);
        background: transparent;
        color: var(--color-text-secondary);
        cursor: pointer;
        transition: all var(--transition-fast);
    }

    .feedback-btn:hover {
        transform: scale(1.05);
    }

    .feedback-btn.positive:hover {
        background: rgba(16, 185, 129, 0.2);
        border-color: var(--color-secondary);
    }

    .feedback-btn.neutral:hover {
        background: rgba(99, 102, 241, 0.2);
        border-color: var(--color-primary);
    }

    .feedback-btn.negative:hover {
        background: rgba(239, 68, 68, 0.2);
        border-color: var(--color-error);
    }
</style>
