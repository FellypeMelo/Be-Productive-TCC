<script lang="ts">
  import { page } from "$app/stores";
  import { currentUser } from "$lib/stores";
  import { api, type Content } from "$lib/api";
  import { onDestroy, onMount } from "svelte";
  import Sidebar from "$lib/components/Sidebar.svelte";

  let id = $derived($page.params.id);
  let content = $state<Content | null>(null);
  let isLoading = $state(true);
  let feedbackSent = $state(false);
  let trackingEnabled = false;
  let openedAt = Date.now();
  let rankingContext = {
    algorithm: "unknown", experiment: "none", position: 0,
  };

  onMount(async () => {
    openedAt = Date.now();
    try {
      rankingContext = {
        ...rankingContext,
        ...JSON.parse(sessionStorage.getItem("be-productive:ranking-context") || "{}"),
      };
    } catch {
      // Missing ranking context is valid for direct links.
    }
    await Promise.all([loadContent(), loadTrackingPreference()]);
  });

  onDestroy(() => {
    const dwellSeconds = Math.floor((Date.now() - openedAt) / 1000);
    if (!trackingEnabled || !content || dwellSeconds < 15) return;
    void api.recordContentEvent(content.id_conteudo, {
      event_id: eventID(), type: "complete", dwell_seconds: dwellSeconds,
      position: rankingContext.position, algorithm: rankingContext.algorithm,
      experiment: rankingContext.experiment,
    }).catch(() => undefined);
  });

  async function loadTrackingPreference() {
    if (!$currentUser) return;
    try {
      trackingEnabled = (await api.getSettings($currentUser.id_usuario)).personalizacao_ativa;
    } catch {
      trackingEnabled = false;
    }
  }

  function eventID(): string {
    if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
    return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  async function loadContent() {
    isLoading = true;
    try {
      content = await api.getContent(parseInt(id || "0"));
    } catch (err) {
      console.error("Failed to load content:", err);
      // Mock fallback for development if API fails
      content = {
        id_conteudo: parseInt(id || "0"),
        titulo: "A arte do trabalho focado",
        corpo:
          "O trabalho profundo é a capacidade de se concentrar sem distração em uma tarefa cognitivamente exigente. É uma habilidade que permite dominar informações complexas com rapidez e produzir resultados melhores em menos tempo. Na economia de hoje, essa capacidade está se tornando cada vez mais rara e valiosa.\n\nPara praticar o trabalho profundo, é preciso eliminar as distrações e dedicar um bloco fixo de tempo a uma única tarefa. Essa abordagem minimalista da produtividade é o núcleo do Be Productive.",
        tipo_de_midia: "TEXTO",
        categoria: "PRODUTIVIDADE",
        autor_id: 1,
        data_publicacao: "2026-02-07",
        score_de_qualidade: 0.98,
        tags_relevantes: "foco, produtividade",
      };
    } finally {
      isLoading = false;
    }
  }

  async function submitFeedback(type: "util" | "nao_relevante" | "relaxante") {
    if (!content || !$currentUser) return;
    try {
      await api.submitFeedback(
        content.id_conteudo,
        $currentUser.id_usuario,
        type,
      );
      feedbackSent = true;
      setTimeout(() => {
        feedbackSent = false;
      }, 3000);
    } catch (err) {
      console.error("Error submitting feedback:", err);
    }
  }

  function formatDate(d: string): string {
    try {
      return new Date(d).toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "long",
        year: "numeric",
      });
    } catch {
      return d;
    }
  }
</script>

<svelte:head>
  <title>{content?.titulo || "Conteúdo"} | Be Productive</title>
</svelte:head>

<div class="flex min-h-screen">
  <Sidebar />

  <main class="flex-1 min-w-0 md:ml-64 pt-14 md:pt-0">
    <div class="p-5 sm:p-8 lg:p-12 max-w-2xl mx-auto">
      {#if isLoading}
        <div class="space-y-6">
          <div class="skeleton h-3 w-40"></div>
          <div class="skeleton h-10 w-full"></div>
          <div class="skeleton h-10 w-2/3"></div>
          <div class="skeleton aspect-[16/9] w-full rounded-xl mt-4"></div>
          <div class="space-y-3 mt-4">
            <div class="skeleton h-4 w-full"></div>
            <div class="skeleton h-4 w-full"></div>
            <div class="skeleton h-4 w-3/4"></div>
          </div>
        </div>
      {:else if content}
        {@const prod = content.categoria === "PRODUTIVIDADE"}
        <article class="animate-slideUp">
          <a
            href="/feed"
            class="inline-flex items-center gap-1.5 text-sm font-medium text-muted hover:text-ink transition-colors mb-8"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7" /></svg>
            Voltar ao feed
          </a>

          <header class="mb-8">
            <div class="flex flex-wrap items-center gap-2.5 mb-5">
              <span
                class="chip {prod ? 'chip-accent' : ''}"
              >
                <span class="w-1.5 h-1.5 rounded-full {prod ? 'bg-accent' : 'bg-subtle'}"></span>
                {prod ? "Produtividade" : "Entretenimento"}
              </span>
              <span class="text-sm text-subtle">{formatDate(content.data_publicacao)}</span>
              <span
                class="ml-auto inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-semibold bg-accent-wash text-accent-ink tabular-nums"
                title="Score de qualidade"
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z" /><path d="M2 21c0-3 1.85-5.36 5.08-6" /></svg>
                {Math.round(content.score_de_qualidade * 100)}
              </span>
            </div>

            <h1 class="text-3xl sm:text-4xl lg:text-[2.75rem] font-bold tracking-tight leading-[1.1]">
              {content.titulo}
            </h1>

            {#if content.topics && content.topics.length > 0}
              <div class="flex flex-wrap gap-1.5 mt-5">
                {#each content.topics as topic}
                  <span class="text-[11px] font-medium text-subtle bg-hairline rounded-full px-2.5 py-1">
                    {topic.nome_topico}
                  </span>
                {/each}
              </div>
            {/if}
          </header>

          {#if content.tipo_de_midia === "VIDEO"}
            <div class="aspect-video rounded-xl overflow-hidden border border-line mb-10 relative group bg-ink flex items-center justify-center text-paper">
              {#if content.midia_url}
                <iframe
                  src={content.midia_url}
                  class="absolute inset-0 w-full h-full border-0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen
                  title={content.titulo}
                ></iframe>
              {:else}
                <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" class="opacity-90 group-hover:scale-110 transition-transform"><circle cx="12" cy="12" r="10" /><polygon points="10 8 16 12 10 16 10 8" /></svg>
                <span class="absolute bottom-4 left-4 eyebrow !text-paper/70">Prévia de vídeo</span>
              {/if}
            </div>
          {:else if content.tipo_de_midia === "AUDIO"}
            {#if content.midia_url}
              <div class="mb-10 rounded-xl overflow-hidden border border-line bg-ink">
                <iframe
                  width="100%"
                  height="166"
                  scrolling="no"
                  frameborder="no"
                  allow="autoplay"
                  src={content.midia_url}
                  title={content.titulo}
                ></iframe>
              </div>
            {:else}
              <div class="card mb-10 p-6 sm:p-7 flex items-center gap-5 sm:gap-6">
                <span class="w-14 h-14 rounded-2xl bg-accent-wash text-accent flex items-center justify-center shrink-0">
                  <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" /><path d="M19 10v2a7 7 0 0 1-14 0v-2" /><line x1="12" y1="19" x2="12" y2="23" /><line x1="8" y1="23" x2="16" y2="23" /></svg>
                </span>
                <div class="flex-1 space-y-3">
                  <div class="h-1.5 rounded-full bg-hairline w-full relative overflow-hidden">
                    <div class="absolute inset-y-0 left-0 rounded-full bg-accent w-1/3"></div>
                  </div>
                  <div class="flex justify-between text-xs font-medium text-subtle tabular-nums">
                    <span>02:45</span>
                    <span>08:12</span>
                  </div>
                </div>
              </div>
            {/if}
          {/if}

          <div
            class="text-lg leading-[1.8] text-ink/90 whitespace-pre-wrap [&>*+*]:mt-6"
          >
            {content.corpo}
          </div>

          <footer class="mt-14 pt-8 border-t border-hairline space-y-10">
            <div class="flex flex-wrap items-center justify-between gap-5">
              <div class="flex items-center gap-3">
                <span class="w-10 h-10 rounded-full bg-ink text-paper flex items-center justify-center font-bold text-sm uppercase shrink-0">
                  A
                </span>
                <div>
                  <p class="eyebrow">Publicado por</p>
                  <p class="font-semibold text-ink text-sm mt-0.5">Autor #{content.autor_id}</p>
                </div>
              </div>

              <div class="flex gap-2.5">
                <button class="btn btn-outline">Compartilhar</button>
                <button class="btn btn-primary">Salvar</button>
              </div>
            </div>

            <!-- Feedback (UC15) -->
            <div class="card bg-accent-wash border-transparent p-6 sm:p-7 text-center">
              <p class="eyebrow mb-1">Sua opinião afina o feed</p>
              <h4 class="font-semibold text-ink">Como foi este conteúdo?</h4>
              <div class="flex flex-wrap justify-center gap-2.5 mt-5">
                <button onclick={() => submitFeedback("util")} class="btn btn-outline bg-surface">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3z"/><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>
                  Útil
                </button>
                <button onclick={() => submitFeedback("relaxante")} class="btn btn-outline bg-surface">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9z"/></svg>
                  Relaxante
                </button>
                <button onclick={() => submitFeedback("nao_relevante")} class="btn btn-outline bg-surface">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  Não relevante
                </button>
              </div>

              {#if feedbackSent}
                <p class="inline-flex items-center gap-1.5 text-sm font-medium text-accent mt-5 animate-fadeIn">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                  Obrigado! Isso ajuda a melhorar o seu feed.
                </p>
              {/if}
            </div>
          </footer>
        </article>
      {/if}
    </div>
  </main>
</div>
