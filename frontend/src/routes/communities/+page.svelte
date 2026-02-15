<script lang="ts">
    import { api, type Community } from "$lib/api";
    import { currentUser, isLoggedIn } from "$lib/stores";
    import { onMount } from "svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import { goto } from "$app/navigation";

    let communities = $state<Community[]>([]);
    let myCommunityIds = $state<Set<number>>(new Set());
    let isLoading = $state(true);

    onMount(async () => {
        if (!$isLoggedIn) {
            goto("/auth/login");
            return;
        }
        await loadData();
    });

    async function loadData() {
        isLoading = true;
        try {
            const [all, mine] = await Promise.all([
                api.listCommunities(),
                api.getMyCommunities(),
            ]);
            communities = all;
            myCommunityIds = new Set(mine.map((c) => c.id_comunidade));
        } catch (err) {
            console.error("Error loading communities:", err);
        } finally {
            isLoading = false;
        }
    }

    async function toggleCommunity(id: number) {
        try {
            if (myCommunityIds.has(id)) {
                await api.leaveCommunity(id);
                const nextIds = new Set(myCommunityIds);
                nextIds.delete(id);
                myCommunityIds = nextIds;
            } else {
                await api.joinCommunity(id);
                const nextIds = new Set(myCommunityIds);
                nextIds.add(id);
                myCommunityIds = nextIds;
            }
        } catch (err) {
            console.error("Error toggling community:", err);
        }
    }
</script>

<svelte:head>
    <title>Communities | Be Productive</title>
</svelte:head>

<div class="flex min-h-screen bg-white text-black">
    <Sidebar />

    <main class="ml-64 flex-1 p-12">
        <header class="mb-16">
            <h1 class="text-4xl font-bold tracking-tighter uppercase">
                Discovery
            </h1>
            <p class="text-gray-400 text-sm mt-2">
                Find and join communities tailored to your interests.
            </p>
        </header>

        {#if isLoading}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {#each Array(6) as _}
                    <div
                        class="h-64 border border-gray-100 animate-pulse bg-gray-50"
                    ></div>
                {/each}
            </div>
        {:else if communities.length === 0}
            <div
                class="col-span-full py-32 text-center border border-dashed border-gray-200"
            >
                <p
                    class="text-[10px] font-bold text-gray-400 uppercase tracking-widest"
                >
                    No communities found. Create one to get started.
                </p>
            </div>
        {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {#each communities as community (community.id_comunidade)}
                    <div
                        class="border border-black p-8 flex flex-col justify-between group hover:bg-black hover:text-white transition-all"
                    >
                        <div>
                            <div
                                class="text-[10px] font-bold uppercase tracking-widest py-1 px-2 border border-current inline-block mb-6"
                            >
                                Community
                            </div>
                            <h3
                                class="text-2xl font-bold tracking-tighter mb-4"
                            >
                                {community.nome_comunidade}
                            </h3>
                            <p class="text-sm opacity-60 line-clamp-3 mb-8">
                                {community.regras_de_moderacao ||
                                    "A space for focused collaboration and shared growth."}
                            </p>
                        </div>

                        <button
                            class="w-full py-4 text-xs font-bold uppercase tracking-widest border border-current transition-colors
                                    {myCommunityIds.has(community.id_comunidade)
                                ? 'bg-black text-white group-hover:bg-white group-hover:text-black border-transparent'
                                : 'hover:bg-black hover:text-white group-hover:bg-white group-hover:text-black'}"
                            onclick={() =>
                                toggleCommunity(community.id_comunidade)}
                        >
                            {myCommunityIds.has(community.id_comunidade)
                                ? "Joined"
                                : "+ Join"}
                        </button>
                    </div>
                {/each}
            </div>
        {/if}
    </main>
</div>
