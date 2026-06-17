<script lang="ts">
  export let rows: any[] = [];
  const target = 'sapt_all';
</script>

<section class="panel">
  <div class="title">
    <div>
      <h2>Prediction samples</h2>
      <p>Stored DESS predictions from the artifact.</p>
    </div>
  </div>

  <div class="tape">
    {#each rows as r}
      <article>
        <div class="row-head">
          <b>k={r.k_index}</b>
          <em>{r.rank_score == null ? 'rank —' : `rank ${r.rank_score.toFixed(3)}`}</em>
        </div>
        <span>predicted {target}: {r.y_pred[target]?.toFixed(3)}</span>
        <small>true {target}: {r.y_true[target]?.toFixed(3)}</small>
      </article>
    {/each}
  </div>
</section>

<style>
  .panel {
    background: #fff;
    color: #191816;
    border-radius: 22px;
    padding: 1rem;
    border: 1px solid #e9e1d4;
    box-shadow: 0 18px 50px rgba(58, 45, 24, 0.035);
  }

  .title {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
  }

  .title h2 {
    margin: 0;
    font-size: 1rem;
    letter-spacing: -0.02em;
  }

  .title p {
    margin: 0.25rem 0 0;
    color: #777064;
    font-size: 0.82rem;
  }

  .tape {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
    gap: 0.75rem;
    margin-top: 1rem;
  }

  article {
    background: #fffdf9;
    border: 1px solid #eee5d8;
    border-radius: 16px;
    padding: 0.8rem;
    display: grid;
    gap: 0.35rem;
  }

  .row-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
  }

  b {
    color: #191816;
  }

  span {
    color: #4d3c22;
    font-weight: 650;
    font-size: 0.84rem;
  }

  small {
    color: #777064;
  }

  em {
    color: #8a6d38;
    font-style: normal;
    font-weight: 620;
    font-size: 0.75rem;
  }
</style>
