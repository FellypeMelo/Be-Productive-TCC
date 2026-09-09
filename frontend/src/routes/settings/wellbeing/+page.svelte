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
    <title>Bem-estar | Be Productive</title>
</svelte:head>

<div class="flex min-h-screen">
    <Sidebar />

    <main class="flex-1 min-w-0 md:ml-64 pt-14 md:pt-0">
      <div class="p-5 sm:p-8 lg:p-12 max-w-3xl mx-auto">
        <header class="mb-8 sm:mb-10">
            <p class="eyebrow mb-2">Preferências</p>
            <h1 class="text-3xl sm:text-4xl font-bold tracking-tight">Bem-estar</h1>
            <p class="text-muted text-sm sm:text-base mt-2 max-w-md">
                Ajuste como o Be Productive cuida da sua atenção e do seu descanso.
            </p>
        </header>

        <div class="privacy-note mb-6">
            <span class="w-9 h-9 rounded-xl bg-surface text-accent flex items-center justify-center shrink-0">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </span>
            <div>
                <p class="font-semibold text-sm">Privacidade por padrão</p>
                <p class="text-xs sm:text-sm mt-1 leading-relaxed opacity-80">A detecção de fadiga usa apenas este navegador. Velocidade de rolagem, trocas de contexto e reserva cognitiva não são salvas no servidor.</p>
            </div>
        </div>

        {#if isLoading}
            <div class="space-y-4">
                {#each Array(4) as _}
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
                <label class="card p-5 sm:p-6 flex items-center justify-between gap-5 cursor-pointer hover:border-ink transition-colors border-accent/40 bg-accent-wash/20">
                    <div class="flex items-start gap-4">
                        <span class="w-10 h-10 rounded-xl bg-accent text-white flex items-center justify-center shrink-0">
                            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18M3 12h18"/><circle cx="12" cy="12" r="9"/></svg>
                        </span>
                        <div>
                            <h3 class="font-semibold text-ink">Participar do estudo de atenção sustentável</h3>
                            <p class="text-sm text-muted mt-0.5">Ajude a avaliar duas formas de organizar o feed. É opcional, separado da personalização e pode ser revogado a qualquer momento.</p>
                            <p class="text-xs text-muted mt-2">Enviamos apenas resultados agregados do experimento; rolagem e sinais brutos permanecem neste navegador.</p>
                        </div>
                    </div>
                    <span class="relative inline-flex shrink-0">
                        <input type="checkbox" bind:checked={settings.consentimento_pesquisa} class="sr-only peer" />
                        <span class="w-11 h-6 rounded-full bg-line transition-colors peer-checked:bg-accent peer-focus-visible:ring-2 peer-focus-visible:ring-accent peer-focus-visible:ring-offset-2 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:w-5 after:h-5 after:rounded-full after:bg-white after:shadow after:transition-transform peer-checked:after:translate-x-5"></span>
                    </span>
                </label>

                <label class="card p-5 sm:p-6 flex items-center justify-between gap-5 cursor-pointer hover:border-ink transition-colors">
                    <div class="flex items-start gap-4">
                        <span class="w-10 h-10 rounded-xl bg-accent-wash text-accent flex items-center justify-center shrink-0">
                            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        </span>
                        <div>
                            <h3 class="font-semibold text-ink">Detecção de fadiga</h3>
                            <p class="text-sm text-muted mt-0.5">Perceber desgaste localmente e sugerir pausas no momento certo.</p>
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
                            <p class="text-sm text-muted mt-0.5">Usar impressões e escolhas de conteúdo para ajustar suas preferências.</p>
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
