<script lang="ts">
  import { api } from "$lib/api";
  import { auth } from "$lib/stores";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { animate } from "motion";

  let email = $state("");
  let senha = $state("");
  let error = $state("");
  let isLoading = $state(false);
  let cardRef = $state<HTMLElement | null>(null);

  onMount(() => {
    if (cardRef)
      animate(cardRef, { opacity: [0, 1], y: [10, 0] }, { duration: 0.4 });
  });

  async function handleLogin(e: Event) {
    e.preventDefault();
    error = "";
    isLoading = true;

    try {
      const { token, user } = await api.login(email, senha);
      auth.login(user, token);
      goto("/feed");
    } catch (err) {
      error = err instanceof Error ? err.message : "Login failed";
    } finally {
      isLoading = false;
    }
  }
</script>

<svelte:head>
  <title>Entrar | Be Productive</title>
</svelte:head>

<main class="min-h-screen bg-paper flex items-center justify-center p-5 sm:p-6">
  <div bind:this={cardRef} class="w-full max-w-sm opacity-0">
    <a
      href="/"
      class="flex items-center justify-center gap-2.5 mb-8 group"
      aria-label="Início"
    >
      <span
        class="w-10 h-10 rounded-xl bg-ink text-paper flex items-center justify-center transition-transform group-hover:scale-105 group-hover:rotate-3"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" /></svg>
      </span>
      <span class="font-bold tracking-tight text-lg leading-none">Be Productive</span>
    </a>

    <div class="card p-7 sm:p-8">
      <header class="mb-7 text-center">
        <p class="eyebrow mb-2">Bem-vindo de volta</p>
        <h1 class="text-2xl font-bold tracking-tight">Entrar na sua conta</h1>
        <p class="text-sm text-muted mt-1.5">Continue de onde parou — sem ruído.</p>
      </header>

      <form onsubmit={handleLogin} class="space-y-4">
        {#if error}
          <div
            class="rounded-lg bg-danger-wash border border-danger/20 px-3.5 py-2.5 text-sm font-medium text-danger animate-fadeIn"
          >
            {error}
          </div>
        {/if}

        <div class="space-y-1.5">
          <label for="email" class="block text-sm font-medium text-ink">E-mail</label>
          <input
            type="email"
            id="email"
            class="input"
            placeholder="voce@exemplo.com"
            bind:value={email}
            required
          />
        </div>

        <div class="space-y-1.5">
          <label for="senha" class="block text-sm font-medium text-ink">Senha</label>
          <input
            type="password"
            id="senha"
            class="input"
            placeholder="••••••••"
            bind:value={senha}
            required
          />
        </div>

        <button type="submit" class="btn btn-primary w-full !py-3 mt-2" disabled={isLoading}>
          {isLoading ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>

    <p class="mt-6 text-center text-sm text-muted">
      Novo por aqui?
      <a href="/auth/register" class="font-semibold text-accent-ink hover:underline">Crie uma conta</a>
    </p>
  </div>
</main>
