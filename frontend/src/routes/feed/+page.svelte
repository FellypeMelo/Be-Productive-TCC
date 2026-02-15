<script lang="ts">
    import { currentUser, isLoggedIn } from "$lib/stores";
    import { api, type Content } from "$lib/api";
    import { onMount } from "svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import { animate, stagger } from "motion";

    let feed = $state<Content[]>([]);
    let isLoading = $state(true);
    let error = $state("");
    let category = $state<string | null>(null);
    let selectedTopic = $state<number | null>(null);
    let topics = $state<any[]>([]);
    let gridRef: HTMLElement;

    // Preserving original mock data for fallback/demo
    const mockFeed: Content[] = [
        {
            id_conteudo: 1,
            titulo: "Deep Focus Strategies",
            categoria: "PRODUTIVIDADE",
            tipo_de_midia: "VIDEO",
            autor_id: 1,
            data_publicacao: "2026-02-01",
            score_de_qualidade: 0.92,
            corpo: "",
            tags_relevantes: "",
        },
        {
            id_conteudo: 2,
            titulo: "Ambient Study Session",
            categoria: "PRODUTIVIDADE",
            tipo_de_midia: "AUDIO",
            autor_id: 2,
            data_publicacao: "2026-02-01",
            score_de_qualidade: 0.88,
            corpo: "",
            tags_relevantes: "",
        },
        {
            id_conteudo: 3,
            titulo: "Modern Minimalist Design",
            categoria: "ENTRETENIMENTO",
            tipo_de_midia: "VIDEO",
            autor_id: 3,
            data_publicacao: "2026-01-30",
            score_de_qualidade: 0.85,
            corpo: "",
            tags_relevantes: "",
        },
        {
            id_conteudo: 4,
            titulo: "Daily Meditation Guide",
            categoria: "PRODUTIVIDADE",
            tipo_de_midia: "VIDEO",
            autor_id: 1,
            data_publicacao: "2026-01-29",
            score_de_qualidade: 0.95,
            corpo: "",
            tags_relevantes: "",
        },
        {
            id_conteudo: 5,
            titulo: "Cinema: The New Wave",
            categoria: "ENTRETENIMENTO",
            tipo_de_midia: "VIDEO",
            autor_id: 4,
            data_publicacao: "2026-01-28",
            score_de_qualidade: 0.78,
            corpo: "",
            tags_relevantes: "",
        },
    ];

    onMount(async () => {
        if (!$isLoggedIn) return;
        loadTopics();
        loadFeed();
    });

    async function loadTopics() {
        if (!$currentUser) return;
        try {
            // Reusing getMyCommunities as it also implies interests,
            // but let's check if there's a direct topic list for user.
            // In current repo, UserRepository has GetTopics.
            // Let's assume api.getUserTopics exists or similar.
            // Since I didn't add it to api.ts yet, I'll add it now.
            const userTopics = await api.getUserTopics($currentUser.id_usuario);
            topics = userTopics;
        } catch (err) {
            console.error("Error loading topics:", err);
            // Fallback topics
            topics = [
                { id_topico: 1, nome_topico: "Focus" },
                { id_topico: 2, nome_topico: "Health" },
                { id_topico: 3, nome_topico: "Coding" },
            ];
        }
    }

    async function loadFeed() {
        isLoading = true;
        try {
            const userID = $currentUser?.id_usuario || 1;
            feed = await api.getFeed(
                userID,
                category || undefined,
                selectedTopic || undefined,
            );

            // Animations
            setTimeout(() => {
                if (gridRef) {
                    animate(
                        "article",
                        { opacity: [0, 1], y: [10, 0] },
                        {
                            delay: stagger(0.05),
                            duration: 0.4,
                        },
                    );
                }
            }, 50);
        } catch (err) {
            feed = mockFeed;
        } finally {
            isLoading = false;
        }
    }

    function toggleCategory(cat: string | null) {
        category = cat;
        loadFeed();
    }

    function toggleTopic(id: number | null) {
        selectedTopic = id;
        loadFeed();
    }
</script>

<svelte:head>
    <title>Feed | Be Productive</title>
</svelte:head>

<div class="flex min-h-screen bg-white">
    <Sidebar />

    <main class="flex-1 ml-64 p-12">
        <!-- Header -->
        <header class="flex justify-between items-end mb-16">
            <div>
                <h1 class="text-4xl font-bold tracking-tighter uppercase">
                    Your Feed
                </h1>
                <p class="text-gray-400 text-sm mt-2">
                    Curated for your mental balance.
                </p>
            </div>

            <div class="flex gap-4">
                <button
                    onclick={() => toggleCategory(null)}
                    class="text-xs font-bold uppercase tracking-widest px-4 py-2 border {category ===
                    null
                        ? 'bg-black text-white border-black'
                        : 'border-gray-200 hover:border-black'} transition-colors"
                >
                    All
                </button>
                <button
                    onclick={() => toggleCategory("PRODUTIVIDADE")}
                    class="text-xs font-bold uppercase tracking-widest px-4 py-2 border {category ===
                    'PRODUTIVIDADE'
                        ? 'bg-black text-white border-black'
                        : 'border-gray-200 hover:border-black'} transition-colors"
                >
                    Productivity
                </button>
                <button
                    onclick={() => toggleCategory("ENTRETENIMENTO")}
                    class="text-xs font-bold uppercase tracking-widest px-4 py-2 border {category ===
                    'ENTRETENIMENTO'
                        ? 'bg-black text-white border-black'
                        : 'border-gray-200 hover:border-black'} transition-colors"
                >
                    Entertainment
                </button>
            </div>
        </header>

        <!-- Topic Browser (Discovery Module) -->
        <div class="mb-12">
            <p
                class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-4"
            >
                Browse your interests
            </p>
            <div class="flex gap-4 overflow-x-auto pb-4 no-scrollbar">
                <button
                    onclick={() => toggleTopic(null)}
                    class="px-6 py-3 text-[10px] font-bold uppercase tracking-widest border border-black transition-all
                           {selectedTopic === null
                        ? 'bg-black text-white'
                        : 'border-gray-200 hover:border-black'}"
                >
                    All For You
                </button>
                {#each topics as topic}
                    <button
                        onclick={() => toggleTopic(topic.id_topico)}
                        class="px-6 py-3 text-[10px) font-bold uppercase tracking-widest border border-black transition-all whitespace-nowrap
                               {selectedTopic === topic.id_topico
                            ? 'bg-black text-white'
                            : 'border-gray-200 hover:border-black'}"
                    >
                        {topic.nome_topico}
                    </button>
                {/each}
            </div>
        </div>

        <!-- Grid -->
        <div
            bind:this={gridRef}
            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-16"
        >
            {#if isLoading}
                {#each Array(6) as _}
                    <div class="space-y-4 animate-pulse">
                        <div
                            class="aspect-video bg-gray-100 border border-black/5"
                        ></div>
                        <div class="h-4 bg-gray-100 w-3/4"></div>
                        <div class="h-3 bg-gray-100 w-1/2"></div>
                    </div>
                {/each}
            {:else}
                {#each feed as content (content.id_conteudo)}
                    <a
                        href="/content/{content.id_conteudo}"
                        class="block group"
                    >
                        <article class="opacity-0">
                            <div
                                class="aspect-video border border-black bg-white mb-4 relative overflow-hidden flex items-center justify-center"
                            >
                                <div
                                    class="absolute inset-0 bg-black opacity-0 group-hover:opacity-5 transition-opacity"
                                ></div>

                                <!-- Content Type Icon (Minimalist) -->
                                <div
                                    class="text-black/20 group-hover:text-black transition-colors"
                                >
                                    {#if content.tipo_de_midia === "VIDEO"}
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            width="48"
                                            height="48"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            stroke-width="1.5"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            ><polygon
                                                points="5 3 19 12 5 21 5 3"
                                            /></svg
                                        >
                                    {:else if content.tipo_de_midia === "AUDIO"}
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            width="48"
                                            height="48"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            stroke-width="1.5"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            ><path
                                                d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"
                                            /><path
                                                d="M19 10v2a7 7 0 0 1-14 0v-2"
                                            /><line
                                                x1="12"
                                                y1="19"
                                                x2="12"
                                                y2="23"
                                            /><line
                                                x1="8"
                                                y1="23"
                                                x2="16"
                                                y2="23"
                                            /></svg
                                        >
                                    {:else}
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            width="48"
                                            height="48"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            stroke-width="1.5"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            ><path
                                                d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                                            /><polyline
                                                points="14 2 14 8 20 8"
                                            /></svg
                                        >
                                    {/if}
                                </div>

                                <!-- Metadata Badge -->
                                <div
                                    class="absolute bottom-2 right-2 bg-black text-white text-[8px] font-bold uppercase px-1 tracking-tighter"
                                >
                                    {content.tipo_de_midia}
                                </div>
                            </div>

                            <h3
                                class="font-bold text-lg leading-tight group-hover:underline uppercase tracking-tight"
                            >
                                {content.titulo}
                            </h3>
                            <div
                                class="flex items-center gap-2 mt-2 text-[10px] font-bold text-gray-400 uppercase tracking-widest"
                            >
                                <span>Author #{content.autor_id}</span>
                                <span>•</span>
                                <span
                                    class={content.categoria === "PRODUTIVIDADE"
                                        ? "text-black"
                                        : ""}>{content.categoria}</span
                                >
                            </div>
                        </article>
                    </a>
                {/each}
            {/if}
        </div>

        {#if !isLoading && feed.length === 0}
            <div class="py-32 text-center border border-dashed border-gray-200">
                <p
                    class="text-sm font-bold text-gray-400 uppercase tracking-widest"
                >
                    No content available in this section.
                </p>
            </div>
        {/if}
    </main>
</div>
