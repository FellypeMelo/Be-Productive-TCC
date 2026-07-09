<script lang="ts">
    import { api, type UserSettings } from "$lib/api";
    import { currentUser, isLoggedIn } from "$lib/stores";
    import { onMount } from "svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import { goto } from "$app/navigation";

    let settings = $state<UserSettings | null>(null);
    let isLoading = $state(true);
    let saveStatus = $state<"idle" | "saving" | "success" | "error">("idle");

    onMount(async () => {
        if (!$isLoggedIn || !$currentUser) {
            goto("/auth/login");
            return;
        }
        await loadSettings();
    });

    async function loadSettings() {
        if (!$currentUser) return;
        isLoading = true;
        try {
            settings = await api.getSettings($currentUser.id_usuario);
        } catch (err) {
            console.error("Error loading settings:", err);
        } finally {
            isLoading = false;
        }
    }

    async function saveSettings() {
        if (!$currentUser || !settings) return;
        saveStatus = "saving";
        try {
            await api.updateSettings($currentUser.id_usuario, settings);
            saveStatus = "success";
            setTimeout(() => {
                saveStatus = "idle";
            }, 3000);
        } catch (err) {
            console.error("Error saving settings:", err);
            saveStatus = "error";
        }
    }
</script>

<svelte:head>
    <title>Wellbeing Settings | Be Productive</title>
</svelte:head>

<div class="flex min-h-screen">
    <Sidebar />

    <main class="flex-1 md:ml-64 pt-14 md:pt-0">
      <div class="p-5 sm:p-8 lg:p-12 max-w-3xl mx-auto">
        <header class="mb-8 sm:mb-10">
            <p class="eyebrow mb-2">Preferências</p>
            <h1 class="text-3xl sm:text-4xl font-bold tracking-tight">Bem-estar</h1>
            <p class="text-muted text-sm sm:text-base mt-2 max-w-md">
                Ajuste como o Be Productive cuida da sua atenção e do seu descanso.
            </p>
        </header>

        {#if isLoading}
            <div class="space-y-4">
                {#each Array(3) as _}
                    <div class="card p-6 flex items-center justify-between">
                        <div class="space-y-2 flex-1">
                            <div class="skeleton h-4 w-40"></div>
                            <div class="skeleton h-3 w-64 max-w-full"></div>
                        </div>
                        <div class="skeleton w-11 h-6 rounded-full"></div>
                    </div>
                {/each}
            </div>
        {:else if settings}
            <div class="space-y-4">
                <label class="card p-5 sm:p-6 flex items-center justify-between gap-5 cursor-pointer hover:border-ink transition-colors">
                    <div class="flex items-start gap-4">
                        <span class="w-10 h-10 rounded-xl bg-accent-wash text-accent flex items-center justify-center shrink-0">
                            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        </span>
                        <div>
                            <h3 class="font-semibold text-ink">Detecção de fadiga</h3>
                            <p class="text-sm text-muted mt-0.5">Sugerir pausas após períodos longos de foco.</p>
                        </div>
                    </div>
                    <span class="relative inline-flex shrink-0">
                        <input type="checkbox" bind:checked={settings.sugestao_saudavel_ativa} class="sr-only peer" />
                        <span class="w-11 h-6 rounded-full bg-line transition-colors peer-checked:bg-accent peer-focus-visible:ring-2 peer-focus-visible:ring-accent peer-focus-visible:ring-offset-2 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:w-5 after:h-5 after:rounded-full after:bg-white after:shadow after:transition-transform peer-checked:after:translate-x-5"></span>
                    </span>
                </label>

                <label class="card p-5 sm:p-6 flex items-center justify-between gap-5 cursor-pointer hover:border-ink transition-colors">
                    <div class="flex items-start gap-4">
                        <span class="w-10 h-10 rounded-xl bg-accent-wash text-accent flex items-center justify-center shrink-0">
                            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20a8 8 0 1 0 0-16 8 8 0 0 0 0 16z"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2"/></svg>
                        </span>
                        <div>
                            <h3 class="font-semibold text-ink">Personalização inteligente</h3>
                            <p class="text-sm text-muted mt-0.5">Ajustar o feed com base na sua atividade recente.</p>
                        </div>
                    </div>
                    <span class="relative inline-flex shrink-0">
                        <input type="checkbox" bind:checked={settings.personalizacao_ativa} class="sr-only peer" />
                        <span class="w-11 h-6 rounded-full bg-line transition-colors peer-checked:bg-accent peer-focus-visible:ring-2 peer-focus-visible:ring-accent peer-focus-visible:ring-offset-2 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:w-5 after:h-5 after:rounded-full after:bg-white after:shadow after:transition-transform peer-checked:after:translate-x-5"></span>
                    </span>
                </label>

                <label class="card p-5 sm:p-6 flex items-center justify-between gap-5 cursor-pointer hover:border-ink transition-colors">
                    <div class="flex items-start gap-4">
                        <span class="w-10 h-10 rounded-xl bg-accent-wash text-accent flex items-center justify-center shrink-0">
                            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9z"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                        </span>
                        <div>
                            <h3 class="font-semibold text-ink">Notificações de foco</h3>
                            <p class="text-sm text-muted mt-0.5">Avisar quando você atingir suas metas de foco.</p>
                        </div>
                    </div>
                    <span class="relative inline-flex shrink-0">
                        <input type="checkbox" bind:checked={settings.notificacao_foco_ativa} class="sr-only peer" />
                        <span class="w-11 h-6 rounded-full bg-line transition-colors peer-checked:bg-accent peer-focus-visible:ring-2 peer-focus-visible:ring-accent peer-focus-visible:ring-offset-2 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:w-5 after:h-5 after:rounded-full after:bg-white after:shadow after:transition-transform peer-checked:after:translate-x-5"></span>
                    </span>
                </label>

                <div class="pt-6 mt-2 border-t border-hairline flex flex-wrap items-center gap-4">
                    <button
                        class="btn btn-primary"
                        onclick={saveSettings}
                        disabled={saveStatus === "saving"}
                    >
                        {saveStatus === "saving" ? "Salvando..." : "Salvar preferências"}
                    </button>

                    {#if saveStatus === "success"}
                        <span class="inline-flex items-center gap-1.5 text-sm font-medium text-accent animate-fadeIn">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                            Alterações salvas com sucesso.
                        </span>
                    {:else if saveStatus === "error"}
                        <span class="text-sm font-medium text-danger animate-fadeIn">Erro ao salvar. Tente novamente.</span>
                    {/if}
                </div>
            </div>
        {/if}
      </div>
    </main>
</div>
