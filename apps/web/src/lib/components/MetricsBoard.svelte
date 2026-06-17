<script lang="ts">
  export let metrics: any = null;
</script>

<section class="board">
  <div class="head">
    <h2>Model error by target</h2>
    <p>Lower RMSE is better.</p>
  </div>

  {#if metrics}
    <div class="grid">
      {#each Object.entries(metrics.test_rmse_per_target ?? {}) as [k, v]}
        <div>
          <span>{k}</span>
          <b>{Number(v).toFixed(3)}</b>
        </div>
      {/each}
    </div>
  {:else}
    <p class="empty">Metrics have not loaded yet.</p>
  {/if}
</section>

<style>
  .board {
    background: #fff;
    border: 1px solid #e9e1d4;
    border-radius: 22px;
    padding: 1rem;
    color: #191816;
    box-shadow: 0 18px 50px rgba(58, 45, 24, 0.035);
  }

  .head {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  h2 {
    margin: 0;
    font-size: 1rem;
    letter-spacing: -0.02em;
  }

  .head p,
  .empty {
    margin: 0;
    color: #777064;
    font-size: 0.82rem;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.65rem;
  }

  .grid div {
    background: #fffdf9;
    border: 1px solid #eee5d8;
    border-radius: 14px;
    padding: 0.75rem;
  }

  span {
    display: block;
    color: #7c7265;
    font-size: 0.74rem;
    margin-bottom: 0.35rem;
  }

  b {
    font-size: 1.15rem;
    letter-spacing: -0.03em;
  }

  @media (max-width: 800px) {
    .grid { grid-template-columns: 1fr 1fr; }
  }
</style>
