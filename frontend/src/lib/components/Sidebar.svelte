<script lang="ts">
    import { auth, currentUser } from "$lib/stores";
    import { goto } from "$app/navigation";
    import { page } from "$app/stores";

    function isActive(path: string): boolean {
        // Handle exact matches and sub-paths for settings
        if (path === "/feed") return $page.url.pathname === "/feed";
        return $page.url.pathname.startsWith(path);
    }
</script>

<aside
    class="fixed top-0 left-0 w-64 h-screen bg-white border-r border-black flex flex-col p-6 z-50"
>
    <!-- Logo -->
    <a href="/" class="flex items-center gap-2 mb-12 group">
        <div
            class="w-8 h-8 bg-black flex items-center justify-center text-white transition-transform group-hover:scale-110"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
                ><circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" /></svg
            >
        </div>
        <span class="font-bold tracking-tighter text-lg uppercase"
            >Be Productive</span
        >
    </a>

    <!-- Navigation -->
    <nav class="space-y-1 flex-1">
        <p
            class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-4"
        >
            Navigation
        </p>

        <a
            href="/feed"
            class="flex items-center gap-3 px-3 py-2 text-sm font-medium transition-colors hover:bg-black hover:text-white {isActive(
                '/feed',
            )
                ? 'bg-black text-white'
                : ''}"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                ><path
                    d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"
                /><polyline points="9 22 9 12 15 12 15 22" /></svg
            >
            Feed
        </a>

        <a
            href="/focus"
            class="flex items-center gap-3 px-3 py-2 text-sm font-medium transition-colors hover:bg-black hover:text-white {isActive(
                '/focus',
            )
                ? 'bg-black text-white'
                : ''}"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                ><circle cx="12" cy="12" r="10" /><circle
                    cx="12"
                    cy="12"
                    r="6"
                /><circle cx="12" cy="12" r="2" /></svg
            >
            Focus
        </a>

        <a
            href="/communities"
            class="flex items-center gap-3 px-3 py-2 text-sm font-medium transition-colors hover:bg-black hover:text-white {isActive(
                '/communities',
            )
                ? 'bg-black text-white'
                : ''}"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                ><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle
                    cx="9"
                    cy="7"
                    r="4"
                /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path
                    d="M16 3.13a4 4 0 0 1 0 7.75"
                /></svg
            >
            Communities
        </a>

        <a
            href="/settings/wellbeing"
            class="flex items-center gap-3 px-3 py-2 text-sm font-medium transition-colors hover:bg-black hover:text-white {isActive(
                '/settings/wellbeing',
            )
                ? 'bg-black text-white'
                : ''}"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                ><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /></svg
            >
            Wellbeing
        </a>

        <div class="pt-8 space-y-1">
            <p
                class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-4"
            >
                Categories
            </p>
            <a
                href="/feed?cat=PRODUTIVIDADE"
                class="flex items-center gap-3 px-3 py-2 text-sm hover:underline"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    ><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" /><path
                        d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"
                    /></svg
                >
                Productivity
            </a>
            <a
                href="/feed?cat=ENTRETENIMENTO"
                class="flex items-center gap-3 px-3 py-2 text-sm hover:underline"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    ><rect x="2" y="6" width="20" height="12" rx="2" /><path
                        d="M6 12h.01M9 12h.01M15 12h.01M18 12h.01"
                    /></svg
                >
                Entertainment
            </a>
        </div>
    </nav>

    <!-- User Profil / Logout -->
    <div class="border-t border-black pt-6">
        {#if $currentUser}
            <button class="flex items-center gap-3 w-full text-left group">
                <div
                    class="w-8 h-8 rounded-full border border-black flex items-center justify-center font-bold text-xs uppercase bg-black text-white group-hover:bg-white group-hover:text-black transition-colors"
                >
                    {$currentUser.nome.charAt(0)}
                </div>
                <div class="flex-1 overflow-hidden">
                    <p class="text-xs font-bold truncate">
                        {$currentUser.nome}
                    </p>
                    <p class="text-[10px] text-gray-500 truncate lowercase">
                        {$currentUser.email}
                    </p>
                </div>
            </button>
        {:else}
            <a
                href="/auth/login"
                class="block w-full text-center border border-black py-2 text-xs font-bold uppercase transition-colors hover:bg-black hover:text-white"
            >
                Login
            </a>
        {/if}
    </div>
</aside>
