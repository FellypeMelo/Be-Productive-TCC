<script lang="ts">
    import { api } from "$lib/api";
    import { auth } from "$lib/stores";
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import { animate } from "motion";

    let nome = $state("");
    let email = $state("");
    let senha = $state("");
    let confirmarSenha = $state("");
    let error = $state("");
    let isLoading = $state(false);
    let cardRef = $state<HTMLElement | null>(null);

    onMount(() => {
        if (cardRef)
            animate(
                cardRef,
                { opacity: [0, 1], y: [10, 0] },
                { duration: 0.4 },
            );
    });

    async function handleRegister(e: Event) {
        e.preventDefault();
        error = "";

        if (senha !== confirmarSenha) {
            error = "Passwords do not match";
            return;
        }

        if (senha.length < 8) {
            error = "Password must be at least 8 characters";
            return;
        }

        isLoading = true;

        try {
            const user = await api.register(nome, email, senha);
            const { token } = await api.login(email, senha);
            auth.login(user, token);
            goto("/feed");
        } catch (err) {
            error = err instanceof Error ? err.message : "Creation failed";
        } finally {
            isLoading = false;
        }
    }
</script>

<svelte:head>
    <title>Create Account | Be Productive</title>
</svelte:head>

<main
    class="min-h-screen bg-white flex items-center justify-center p-6 selection:bg-black selection:text-white"
>
    <div
        bind:this={cardRef}
        class="w-full max-w-sm border border-black p-10 opacity-0"
    >
        <header class="mb-10 text-center">
            <a
                href="/"
                class="inline-block mb-8 hover:scale-110 transition-transform"
                aria-label="Home"
            >
                <div
                    class="w-12 h-12 bg-black flex items-center justify-center text-white"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        ><circle cx="12" cy="12" r="10" /><path
                            d="M12 6v6l4 2"
                        /></svg
                    >
                </div>
            </a>
            <h1 class="text-2xl font-bold uppercase tracking-tighter">
                Register
            </h1>
            <p
                class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-2"
            >
                Join the minimalist community
            </p>
        </header>

        <form onsubmit={handleRegister} class="space-y-4">
            {#if error}
                <div
                    class="border border-black p-3 text-[10px] font-bold uppercase text-black bg-gray-50"
                >
                    {error}
                </div>
            {/if}

            <div class="space-y-1">
                <label
                    for="nome"
                    class="text-[10px] font-bold uppercase tracking-widest text-gray-400"
                    >Full Name</label
                >
                <input
                    type="text"
                    id="nome"
                    class="w-full border border-black p-3 text-sm focus:outline-none focus:bg-gray-50 transition-colors"
                    placeholder="John Doe"
                    bind:value={nome}
                    required
                />
            </div>

            <div class="space-y-1">
                <label
                    for="email"
                    class="text-[10px] font-bold uppercase tracking-widest text-gray-400"
                    >Email Address</label
                >
                <input
                    type="email"
                    id="email"
                    class="w-full border border-black p-3 text-sm focus:outline-none focus:bg-gray-50 transition-colors"
                    placeholder="email@example.com"
                    bind:value={email}
                    required
                />
            </div>

            <div class="space-y-1">
                <label
                    for="senha"
                    class="text-[10px] font-bold uppercase tracking-widest text-gray-400"
                    >Password</label
                >
                <input
                    type="password"
                    id="senha"
                    class="w-full border border-black p-3 text-sm focus:outline-none focus:bg-gray-50 transition-colors"
                    placeholder="••••••••"
                    bind:value={senha}
                    required
                    minlength="8"
                />
            </div>

            <div class="space-y-1">
                <label
                    for="confirmarSenha"
                    class="text-[10px] font-bold uppercase tracking-widest text-gray-400"
                    >Confirm Password</label
                >
                <input
                    type="password"
                    id="confirmarSenha"
                    class="w-full border border-black p-3 text-sm focus:outline-none focus:bg-gray-50 transition-colors"
                    placeholder="••••••••"
                    bind:value={confirmarSenha}
                    required
                />
            </div>

            <button
                type="submit"
                class="w-full bg-black text-white py-4 text-xs font-bold uppercase tracking-widest hover:bg-gray-800 transition-colors disabled:opacity-50 mt-4"
                disabled={isLoading}
            >
                {isLoading ? "Creating..." : "Create Account"}
            </button>
        </form>

        <div
            class="mt-10 text-center text-[10px] font-bold uppercase tracking-widest text-gray-400"
        >
            Already have an account? <a
                href="/auth/login"
                class="text-black hover:underline">Login</a
            >
        </div>
    </div>
</main>
