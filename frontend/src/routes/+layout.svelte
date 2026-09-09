<script lang="ts">
  import "../app.css";

  interface Props {
    children: import("svelte").Snippet;
  }

  let { children }: Props = $props();

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
