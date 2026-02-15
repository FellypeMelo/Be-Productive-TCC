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

<div class="flex min-h-screen bg-white text-black">
    <Sidebar />

    <main class="ml-64 flex-1 p-12">
        <header class="mb-16">
            <h1 class="text-4xl font-bold tracking-tighter uppercase">
                Wellbeing
            </h1>
            <p class="text-gray-400 text-sm mt-2">
                Personalize your healthy usage experience.
            </p>
        </header>

        {#if isLoading}
            <div class="space-y-8 animate-pulse">
                {#each Array(3) as _}
                    <div class="h-24 bg-gray-50 border border-gray-100"></div>
                {/each}
            </div>
        {:else if settings}
            <div class="max-w-2xl space-y-12">
                <section class="space-y-8">
                    <div
                        class="flex items-center justify-between p-8 border border-black hover:bg-gray-50 transition-colors"
                    >
                        <div>
                            <h3
                                class="font-bold uppercase tracking-tight text-lg"
                            >
                                Fatigue Detection
                            </h3>
                            <p
                                class="text-xs text-gray-500 uppercase tracking-widest mt-1"
                            >
                                Suggest breaks after 50 minutes of focus.
                            </p>
                        </div>
                        <input
                            type="checkbox"
                            bind:checked={settings.sugestao_saudavel_ativa}
                            class="w-6 h-6 accent-black cursor-pointer"
                        />
                    </div>

                    <div
                        class="flex items-center justify-between p-8 border border-black hover:bg-gray-50 transition-colors"
                    >
                        <div>
                            <h3
                                class="font-bold uppercase tracking-tight text-lg"
                            >
                                Smart Personalization
                            </h3>
                            <p
                                class="text-xs text-gray-500 uppercase tracking-widest mt-1"
                            >
                                Adjust feed based on your recent activity.
                            </p>
                        </div>
                        <input
                            type="checkbox"
                            bind:checked={settings.personalizacao_ativa}
                            class="w-6 h-6 accent-black cursor-pointer"
                        />
                    </div>

                    <div
                        class="flex items-center justify-between p-8 border border-black hover:bg-gray-50 transition-colors"
                    >
                        <div>
                            <h3
                                class="font-bold uppercase tracking-tight text-lg"
                            >
                                Focus Notifications
                            </h3>
                            <p
                                class="text-xs text-gray-500 uppercase tracking-widest mt-1"
                            >
                                Alerts when you reach your focus goals.
                            </p>
                        </div>
                        <input
                            type="checkbox"
                            bind:checked={settings.notificacao_foco_ativa}
                            class="w-6 h-6 accent-black cursor-pointer"
                        />
                    </div>
                </section>

                <div class="pt-8 border-t border-black flex items-center gap-8">
                    <button
                        class="bg-black text-white px-12 py-4 text-xs font-bold uppercase tracking-widest hover:bg-gray-800 transition-colors disabled:opacity-50"
                        onclick={saveSettings}
                        disabled={saveStatus === "saving"}
                    >
                        {saveStatus === "saving"
                            ? "Saving..."
                            : "Save Preferences"}
                    </button>

                    {#if saveStatus === "success"}
                        <span
                            class="text-[10px] font-bold uppercase tracking-widest text-green-600 animate-fadeIn"
                            >Changes saved successfully.</span
                        >
                    {:else if saveStatus === "error"}
                        <span
                            class="text-[10px] font-bold uppercase tracking-widest text-red-600 animate-fadeIn"
                            >Error saving changes.</span
                        >
                    {/if}
                </div>
            </div>
        {/if}
    </main>
</div>
