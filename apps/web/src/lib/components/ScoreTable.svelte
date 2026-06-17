<script lang="ts">
  export let title = 'Scores';
  export let rows: any[] = [];
</script>

<section class="scores">
  <h2>{title}</h2>

  {#if rows.length}
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Physics</th>
          <th>Stability</th>
          <th>Uncertainty</th>
          <th>Source</th>
        </tr>
      </thead>
      <tbody>
        {#each rows as r}
          <tr>
            <td>{r.id ?? r.candidate_id}</td>
            <td>{Number(r.p_physics ?? r.physics_support ?? 0).toFixed(3)}</td>
            <td>{Number(r.stability_support ?? 0).toFixed(3)}</td>
            <td>{Number(r.uncertainty ?? 0).toFixed(3)}</td>
            <td>{r.score_source ?? r.reactant_set_id ?? 'artifact'}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {:else}
    <p>No rows yet.</p>
  {/if}
</section>

<style>
  .scores {
    background: #fff;
    color: #191816;
    border: 1px solid #e9e1d4;
    border-radius: 18px;
    padding: 1rem;
    overflow: auto;
    box-shadow: 0 18px 50px rgba(58, 45, 24, 0.035);
  }

  h2 {
    margin: 0 0 0.75rem;
    font-size: 1rem;
    letter-spacing: -0.02em;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
  }

  th {
    text-align: left;
    color: #777064;
    font-weight: 620;
  }

  td,
  th {
    padding: 0.65rem;
    border-bottom: 1px solid #f0e8dc;
  }

  td:nth-child(2) {
    font-weight: 720;
    color: #4d3c22;
  }

  p {
    color: #777064;
    font-size: 0.84rem;
    margin: 0;
  }
</style>
