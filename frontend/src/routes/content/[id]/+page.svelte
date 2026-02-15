<script lang="ts">
  import { page } from "$app/stores";
  import { currentUser } from "$lib/stores";
  import { api, type Content } from "$lib/api";
  import { onMount } from "svelte";
  import Sidebar from "$lib/components/Sidebar.svelte";

  let id = $derived($page.params.id);
  let content = $state<Content | null>(null);
  let isLoading = $state(true);
  let feedbackSent = $state(false);

  onMount(() => {
    loadContent();
  });

  async function loadContent() {
    isLoading = true;
    try {
      content = await api.getContent(parseInt(id || "0"));
    } catch (err) {
      console.error("Failed to load content:", err);
      // Mock fallback for development if API fails
      content = {
        id_conteudo: parseInt(id || "0"),
        titulo: "The Art of Focused Work",
        corpo:
          "Deep work is the ability to focus without distraction on a cognitively demanding task. It's a skill that allows you to quickly master complicated information and produce better results in less time. In today's economy, this ability is becoming increasingly rare and valuable.\n\nTo practice deep work, one must eliminate all distractions and dedicate a fixed block of time to a single task. This minimalist approach to productivity is the core of Be Productive.",
        tipo_de_midia: "TEXTO",
        categoria: "PRODUTIVIDADE",
        autor_id: 1,
        data_publicacao: "2026-02-07",
        score_de_qualidade: 0.98,
        tags_relevantes: "focus, productivity",
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
</script>

<svelte:head>
  <title>{content?.titulo || "Content"} | Be Productive</title>
</svelte:head>

<div class="flex min-h-screen bg-white">
  <Sidebar />

  <main class="flex-1 ml-64 p-24">
    <div class="max-w-3xl mx-auto">
      {#if isLoading}
        <div class="space-y-8 animate-pulse">
          <div class="h-12 bg-gray-100 w-full"></div>
          <div class="aspect-video bg-gray-50 border border-black/5"></div>
          <div class="space-y-4">
            <div class="h-4 bg-gray-100 w-full"></div>
            <div class="h-4 bg-gray-100 w-full"></div>
            <div class="h-4 bg-gray-100 w-3/4"></div>
          </div>
        </div>
      {:else if content}
        <article class="animate-slideUp">
          <header class="mb-12">
            <div
              class="flex items-center gap-4 mb-6 text-[10px] font-bold uppercase tracking-widest text-gray-500"
            >
              <a
                href="/feed"
                class="hover:text-black hover:underline inline-flex items-center gap-1"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="10"
                  height="10"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="3"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  ><path d="M19 12H5M12 19l-7-7 7-7" /></svg
                >
                Back to Feed
              </a>
              <span>•</span>
              <span>{content.categoria}</span>
              <span>•</span>
              <span
                >{new Date(content.data_publicacao).toLocaleDateString()}</span
              >
            </div>
            <h1
              class="text-6xl font-bold tracking-tighter uppercase leading-none mb-8"
            >
              {content.titulo}
            </h1>

            {#if content.topics && content.topics.length > 0}
              <div class="flex flex-wrap gap-2 mb-12">
                {#each content.topics as topic}
                  <span
                    class="px-3 py-1 bg-black text-white text-[10px] font-bold uppercase tracking-widest"
                  >
                    {topic.nome_topico}
                  </span>
                {/each}
              </div>
            {/if}
          </header>

          {#if content.tipo_de_midia === "VIDEO"}
            <div
              class="aspect-video bg-black border border-black mb-12 flex flex-col items-center justify-center text-white relative group overflow-hidden"
            >
              {#if content.midia_url}
                <iframe
                  src={content.midia_url}
                  class="absolute inset-0 w-full h-full border-0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen
                  title={content.titulo}
                ></iframe>
              {:else}
                <div
                  class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"
                ></div>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="64"
                  height="64"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="relative z-10 hover:scale-110 transition-transform cursor-pointer"
                  ><polygon points="5 3 19 12 5 21 5 3" /></svg
                >
                <div
                  class="absolute bottom-6 left-6 text-[10px] font-bold uppercase tracking-widest opacity-70 flex items-center gap-2"
                >
                  <div
                    class="w-2 h-2 bg-red-600 rounded-full animate-pulse"
                  ></div>
                  Live Video Stream (Placeholder)
                </div>
              {/if}
            </div>
          {:else if content.tipo_de_midia === "AUDIO"}
            {#if content.midia_url}
              <div class="mb-12 border border-black overflow-hidden bg-black">
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
              <div
                class="bg-black border border-black p-12 mb-12 flex items-center gap-12 text-white relative overflow-hidden group"
              >
                <div
                  class="w-16 h-16 border border-white/20 flex items-center justify-center"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="32"
                    height="32"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    ><path
                      d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"
                    /><path d="M19 10v2a7 7 0 0 1-14 0v-2" /><line
                      x1="12"
                      y1="19"
                      x2="12"
                      y2="23"
                    /><line x1="8" y1="23" x2="16" y2="23" /></svg
                  >
                </div>
                <div class="flex-1 space-y-4">
                  <div class="h-1 bg-white/10 w-full relative">
                    <div
                      class="absolute top-0 left-0 h-full bg-white w-1/3"
                    ></div>
                  </div>
                  <div
                    class="flex justify-between text-[10px] font-bold uppercase tracking-widest opacity-50"
                  >
                    <span>02:45</span>
                    <span>08:12</span>
                  </div>
                </div>
              </div>
            {/if}
          {/if}

          <div class="prose prose-black max-w-none">
            <div
              class="text-2xl leading-[1.6] text-black font-serif whitespace-pre-wrap selection:bg-black selection:text-white"
            >
              {content.corpo}
            </div>
          </div>

          <footer
            class="mt-24 pt-12 border-t border-black flex flex-col gap-12"
          >
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-4">
                <div
                  class="w-10 h-10 bg-black text-white flex items-center justify-center font-bold text-sm"
                >
                  A
                </div>
                <div>
                  <p
                    class="text-[10px] font-bold uppercase tracking-widest text-gray-400"
                  >
                    Published by
                  </p>
                  <p class="font-bold text-sm uppercase">
                    Author #{content.autor_id}
                  </p>
                </div>
              </div>

              <div class="flex gap-4">
                <button
                  class="px-6 py-2 border border-black text-[10px] font-bold uppercase tracking-widest hover:bg-black hover:text-white transition-colors"
                >
                  Share
                </button>
                <button
                  class="px-6 py-2 bg-black text-white text-[10px] font-bold uppercase tracking-widest hover:bg-gray-800 transition-colors"
                >
                  Save
                </button>
              </div>
            </div>

            <!-- Feedback Section (UC15) -->
            <div class="bg-gray-50 border border-black/5 p-8">
              <h4
                class="text-[10px] font-bold uppercase tracking-widest mb-6 text-gray-400 text-center"
              >
                How was this content?
              </h4>
              <div class="flex justify-center gap-4">
                <button
                  onclick={() => submitFeedback("util")}
                  class="px-6 py-3 border border-black text-[10px] font-bold uppercase tracking-widest hover:bg-black hover:text-white transition-all transform active:scale-95"
                >
                  Useful
                </button>
                <button
                  onclick={() => submitFeedback("relaxante")}
                  class="px-6 py-3 border border-black text-[10px] font-bold uppercase tracking-widest hover:bg-black hover:text-white transition-all transform active:scale-95"
                >
                  Relaxing
                </button>
                <button
                  onclick={() => submitFeedback("nao_relevante")}
                  class="px-6 py-3 border border-black text-[10px] font-bold uppercase tracking-widest hover:bg-black hover:text-white transition-all transform active:scale-95"
                >
                  Not Relevant
                </button>
              </div>

              {#if feedbackSent}
                <p
                  class="text-[10px] font-bold uppercase tracking-widest text-center mt-6 animate-pulse"
                >
                  Thanks for your feedback! It helps improve your feed.
                </p>
              {/if}
            </div>
          </footer>
        </article>
      {/if}
    </div>
  </main>
</div>
