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
    <title>Comunidades | Be Productive</title>
</svelte:head>

<div class="flex min-h-screen">
    <Sidebar />

    <main class="flex-1 min-w-0 md:ml-64 pt-14 md:pt-0">
      <div class="p-5 sm:p-8 lg:p-12 max-w-6xl mx-auto">
        <header class="mb-8 sm:mb-10 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-5">
            <div>
                <p class="eyebrow mb-2">Descobrir</p>
                <h1 class="text-3xl sm:text-4xl font-bold tracking-tight">Comunidades</h1>
                <p class="text-muted text-sm sm:text-base mt-2 max-w-md">
                    Encontre grupos alinhados aos seus interesses e cresça em boa companhia.
                </p>
            </div>
            {#if !isLoading}
                <div class="calm-panel px-4 py-3 min-w-40">
                    <p class="eyebrow">Sua rede</p>
                    <p class="text-sm font-semibold mt-1">{myCommunityIds.size} {myCommunityIds.size === 1 ? "grupo escolhido" : "grupos escolhidos"}</p>
                </div>
            {/if}
        </header>

        {#if isLoading}
            <div class="grid gap-5 grid-cols-1 sm:grid-cols-2 xl:grid-cols-3">
                {#each Array(6) as _}
                    <div class="card p-6 space-y-4">
                        <div class="skeleton w-11 h-11 rounded-xl"></div>
                        <div class="skeleton h-5 w-2/3"></div>
                        <div class="skeleton h-3 w-full"></div>
                        <div class="skeleton h-3 w-4/5"></div>
                        <div class="skeleton h-10 w-full rounded-lg mt-2"></div>
                    </div>
                {/each}
            </div>
        {:else if communities.length === 0}
            <div class="py-24 sm:py-32 text-center card border-dashed">
                <p class="text-4xl mb-4">🌱</p>
                <p class="font-semibold text-ink">Nenhuma comunidade ainda</p>
                <p class="text-sm text-muted mt-1">Crie a primeira e comece a construir.</p>
            </div>
        {:else}
            <div class="grid gap-5 grid-cols-1 sm:grid-cols-2 xl:grid-cols-3">
                {#each communities as community (community.id_comunidade)}
                    {@const joined = myCommunityIds.has(community.id_comunidade)}
                    <div class="card card-interactive p-6 flex flex-col animate-fadeIn min-h-[17rem]">
                        <div class="flex items-start justify-between gap-3 mb-4">
                            <span class="w-11 h-11 rounded-xl bg-accent-wash text-accent-ink flex items-center justify-center font-bold uppercase shrink-0">
                                {community.nome_comunidade?.charAt(0) ?? "#"}
                            </span>
                            {#if joined}
                                <span class="chip chip-accent">Membro</span>
                            {/if}
                        </div>
                        <h3 class="text-lg font-semibold tracking-tight text-ink">
                            {community.nome_comunidade}
                        </h3>
                        <p class="text-sm text-muted leading-relaxed line-clamp-3 mt-2 flex-1">
                            {community.regras_de_moderacao ||
                                "Um espaço para colaboração focada e crescimento compartilhado."}
                        </p>

                        <button
                            class="btn w-full mt-5 {joined ? 'btn-outline' : 'btn-accent'}"
                            onclick={() => toggleCommunity(community.id_comunidade)}
                        >
                            {#if joined}
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                                Participando
                            {:else}
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                                Participar
                            {/if}
                        </button>
                    </div>
                {/each}
            </div>
        {/if}
      </div>
    </main>
</div>
