<script lang="ts">
    import { auth, currentUser } from "$lib/stores";
    import { goto } from "$app/navigation";
    import { page } from "$app/stores";

    let open = $state(false);

    function isActive(path: string): boolean {
        if (path === "/feed") return $page.url.pathname === "/feed";
        return $page.url.pathname.startsWith(path);
    }

    // Fecha o drawer ao navegar (mobile).
    $effect(() => {
        $page.url.pathname;
        open = false;
    });

    function logout() {
        auth.logout?.();
        goto("/auth/login");
    }

    const primary = [
        { href: "/feed", label: "Feed", d: "m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z|9 22 9 12 15 12 15 22" },
        { href: "/focus", label: "Foco", d: "circle" },
        { href: "/communities", label: "Comunidades", d: "M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2|9 7 4|M23 21v-2a4 4 0 0 0-3-3.87|M16 3.13a4 4 0 0 1 0 7.75" },
        { href: "/settings/wellbeing", label: "Bem-estar", d: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" },
    ];
</script>

<!-- Barra superior (mobile) -->
<header
    class="md:hidden fixed top-0 inset-x-0 h-14 z-40 flex items-center justify-between px-4 border-b border-line"
    style="background: color-mix(in srgb, var(--color-paper) 88%, transparent); backdrop-filter: blur(8px);"
>
    <a href="/" class="flex items-center gap-2">
        <span class="w-7 h-7 rounded-lg bg-ink text-paper flex items-center justify-center">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
        </span>
        <span class="font-bold tracking-tight text-sm uppercase">Be Productive</span>
    </a>
    <button onclick={() => (open = true)} aria-label="Abrir menu" class="btn-ghost h-9 w-9 !p-0 rounded-lg">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
    </button>
</header>

<!-- Backdrop (mobile) -->
{#if open}
    <button
        class="md:hidden fixed inset-0 z-40 animate-fadeIn"
        style="background: color-mix(in srgb, var(--color-ink) 28%, transparent);"
        onclick={() => (open = false)}
        aria-label="Fechar menu"
    ></button>
{/if}

<!-- Sidebar / drawer -->
<aside
    class="fixed top-0 left-0 w-64 h-screen z-50 bg-surface border-r border-line flex flex-col p-6
           transition-transform duration-300 ease-out {open ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0"
>
    <a href="/" class="flex items-center gap-2.5 mb-10 group">
        <span class="w-9 h-9 rounded-xl bg-ink text-paper flex items-center justify-center transition-transform group-hover:scale-105 group-hover:rotate-3">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
        </span>
        <span class="font-bold tracking-tight text-lg leading-none">Be Productive<br/><span class="eyebrow">atenção sustentável</span></span>
    </a>

    <nav class="flex-1 flex flex-col gap-1 overflow-y-auto -mx-1 px-1">
        <p class="eyebrow mb-2 px-3">Navegação</p>
        {#each primary as item}
            <a
                href={item.href}
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
                       {isActive(item.href) ? 'bg-ink text-paper' : 'text-muted hover:text-ink hover:bg-hairline'}"
            >
                {#if item.d === 'circle'}
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
                {:else}
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        {#each item.d.split('|') as seg}
                            {#if seg.startsWith('M') || seg.startsWith('m')}<path d={seg}/>{:else if seg === '9 7 4'}<circle cx="9" cy="7" r="4"/>{:else}<polyline points={seg}/>{/if}
                        {/each}
                    </svg>
                {/if}
                {item.label}
            </a>
        {/each}

        <p class="eyebrow mt-6 mb-2 px-3">Categorias</p>
        <a href="/feed?cat=PRODUTIVIDADE" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-muted hover:text-accent-ink hover:bg-accent-wash transition-colors">
            <span class="w-1.5 h-1.5 rounded-full bg-accent"></span> Produtividade
        </a>
        <a href="/feed?cat=ENTRETENIMENTO" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-muted hover:text-ink hover:bg-hairline transition-colors">
            <span class="w-1.5 h-1.5 rounded-full bg-subtle"></span> Entretenimento
        </a>
    </nav>

    <div class="border-t border-line pt-4 mt-2">
        {#if $currentUser}
            <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-full bg-ink text-paper flex items-center justify-center font-bold text-xs uppercase shrink-0">
                    {$currentUser.nome?.charAt(0) ?? "?"}
                </div>
                <div class="flex-1 overflow-hidden">
                    <p class="text-sm font-semibold truncate leading-tight">{$currentUser.nome}</p>
                    <p class="text-xs text-subtle truncate lowercase">{$currentUser.email}</p>
                </div>
                <button onclick={logout} aria-label="Sair" class="btn-ghost h-8 w-8 !p-0 rounded-lg shrink-0">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                </button>
            </div>
        {:else}
            <a href="/auth/login" class="btn btn-primary w-full">Entrar</a>
        {/if}
    </div>
</aside>
