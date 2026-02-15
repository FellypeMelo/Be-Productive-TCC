<script lang="ts">
  import "../app.css";
  import { onMount } from "svelte";
  import { auth } from "$lib/stores";

  interface Props {
    children: import("svelte").Snippet;
  }

  let { children }: Props = $props();

  onMount(() => {
    auth.init();
  });
</script>

<div class="app">
  {@render children()}
</div>

<style>
  .app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
</style>
