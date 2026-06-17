<script lang="ts">
  export let reactants = 'COc1cc(CC=C)ccc1O\nCC(=O)O';
  export let candidates = 'CC(=O)Oc1ccc(CC=C)cc1OC';
  export let loading = false;
  export let onRun: () => void;
</script>

<section class="console">
  <div class="head">
    <h2>Score a candidate set</h2>
    <p>Paste one SMILES per line.</p>
  </div>

  <label for="reactant-smiles">Reactants</label>
  <textarea id="reactant-smiles" bind:value={reactants}></textarea>

  <label for="candidate-smiles">Candidates</label>
  <textarea id="candidate-smiles" bind:value={candidates}></textarea>

  <button type="button" onclick={onRun} disabled={loading}>{loading ? 'Scoring…' : 'Run score'}</button>
</section>

<style>
  .console {
    background: #fff;
    color: #191816;
    border: 1px solid #e9e1d4;
    border-radius: 22px;
    padding: 1rem;
    display: grid;
    gap: 0.75rem;
    box-shadow: 0 18px 50px rgba(58, 45, 24, 0.035);
  }

  .head {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: 1rem;
  }

  h2 {
    margin: 0;
    font-size: 1rem;
    letter-spacing: -0.02em;
  }

  p {
    margin: 0;
    color: #777064;
    font-size: 0.82rem;
  }

  label {
    display: block;
    color: #6e675e;
    font-size: 0.78rem;
    font-weight: 620;
  }

  textarea {
    min-height: 82px;
    background: #fffdf9;
    color: #191816;
    border: 1px solid #e6dfd3;
    border-radius: 14px;
    padding: 0.75rem;
    font: inherit;
    line-height: 1.45;
    resize: vertical;
    outline: none;
  }

  textarea:focus {
    border-color: #9c7b49;
    box-shadow: 0 0 0 3px rgba(156, 123, 73, 0.12);
  }

  button {
    justify-self: start;
    border: 0;
    border-radius: 999px;
    padding: 0.75rem 1rem;
    background: #191816;
    color: #fffdf9;
    font-weight: 620;
    font-size: 0.86rem;
    cursor: pointer;
  }

  button:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }
</style>
