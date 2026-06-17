<script lang="ts">
  import { onMount } from 'svelte';
  import {
    getHealth,
    getMetrics,
    getPredictions,
    scoreLab,
    explainScore,
    type Health,
    type Metrics,
    type PredictionList,
    type ScoreResponse,
    type ExplainResponse
  } from '$lib/api/client';
  import GaugeCard from '$lib/components/GaugeCard.svelte';
  import StatusPill from '$lib/components/StatusPill.svelte';
  import PredictionTape from '$lib/components/PredictionTape.svelte';
  import MetricsBoard from '$lib/components/MetricsBoard.svelte';
  import LabConsole from '$lib/components/LabConsole.svelte';
  import ScoreTable from '$lib/components/ScoreTable.svelte';

  let health: Health | null = null;
  let metrics: Metrics | null = null;
  let predictions: PredictionList | null = null;
  let score: ScoreResponse | null = null;
  let reactants = 'COc1cc(CC=C)ccc1O\nCC(=O)O';
  let candidates = 'CC(=O)Oc1ccc(CC=C)cc1OC';
  let error = '';
  let loadingScore = false;
  let explanation: ExplainResponse | null = null;
  let loadingExplanation = false;
  let explanationCopied = false;

  onMount(async () => {
    try {
      [health, metrics, predictions] = await Promise.all([getHealth(), getMetrics(), getPredictions(24)]);
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
    }
  });

  async function runScore() {
    loadingScore = true;
    error = '';
    try {
      score = await scoreLab(
        reactants.split(/\n+/).map((x) => x.trim()).filter(Boolean),
        candidates.split(/\n+/).map((x) => x.trim()).filter(Boolean)
      );
      explanation = null;
      explanationCopied = false;
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
    } finally {
      loadingScore = false;
    }
  }

  async function explainRun() {
    if (!score) return;
    loadingExplanation = true;
    error = '';
    try {
      explanation = await explainScore(score, 'Explain for a scientist or formulator reviewing a candidate screen.');
      explanationCopied = false;
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
    } finally {
      loadingExplanation = false;
    }
  }

  async function copyExplanation() {
    if (!explanation?.markdown) return;
    await navigator.clipboard.writeText(explanation.markdown);
    explanationCopied = true;
    setTimeout(() => {
      explanationCopied = false;
    }, 1600);
  }

</script>

<svelte:head><title>DESS Bridge Physics Lab</title></svelte:head>

<main class="shell">
  <aside class="rail">
    <div class="brand">
      <svg viewBox="0 0 36 36" aria-hidden="true">
        <rect x="5" y="6" width="26" height="24" rx="9" />
        <path d="M12 22h12M12 15h7M21 15h3" />
      </svg>
      <span>DESS Bridge</span>
    </div>

    <StatusPill ok={health?.ok ?? false} text={health ? `${health.model_version} · QC ${health.qc_ok ? 'pass' : 'review'}` : 'loading'} />

    <div class="meta">
      <p>Artifact</p>
      <strong>{health?.artifact_version ?? '—'}</strong>
    </div>
    <div class="meta">
      <p>Schema</p>
      <strong>{health?.schema_version ?? '—'}</strong>
    </div>
  </aside>

  <section class="workspace">
    <header class="topbar">
      <div>
        <p class="eyebrow">Physics-backed candidate scoring</p>
        <h1>DESS Bridge Physics Lab</h1>
      </div>
    </header>

    {#if error}<section class="error">{error}</section>{/if}

    <section class="summary-grid" aria-label="Artifact summary">
      <GaugeCard label="Raw predictions" value={health?.rows?.raw_predictions} detail="stored system rows" />
      <GaugeCard label="Best epoch" value={health?.best_epoch} detail="selected checkpoint" />
      <GaugeCard label="Test raw MSE" value={health?.test_raw_mse} detail="model error" />
      <GaugeCard label="Candidate ranks" value={health?.rows?.candidate_rank_scores} detail="rank records" />
    </section>

    <section class="workbench">
      <LabConsole bind:reactants bind:candidates loading={loadingScore} onRun={runScore} />
      <MetricsBoard {metrics} />
    </section>

    {#if score}
      <section class="results-head">
        <div>
          <p class="eyebrow">Run output</p>
          <h2>Candidate scoring results</h2>
        </div>
        <div class="result-actions">
          <span>{score.note}</span>
          <button type="button" onclick={explainRun} disabled={loadingExplanation}>
            {loadingExplanation ? 'Explaining…' : 'Explain results'}
          </button>
        </div>
      </section>

      <section class="score-grid">
        <ScoreTable title="Reactants" rows={score.reactant_scores} />
        <ScoreTable title="Candidates" rows={score.candidate_scores} />
        <ScoreTable title="Rank policy" rows={score.rank_scores} />
      </section>

      {#if explanation}
        <section class="explanation-card">
          <div class="explanation-head">
            <div>
              <p class="eyebrow">{explanation.ai_mode}</p>
              <h2>Result explanation</h2>
            </div>
            <button type="button" class="secondary" onclick={copyExplanation}>
              {explanationCopied ? 'Copied' : 'Copy explanation'}
            </button>
          </div>

          <p class="explanation-summary">{explanation.summary}</p>

          <div class="explanation-grid">
            <section>
              <h3>How to read this run</h3>
              <ul>{#each explanation.interpretation as item}<li>{item}</li>{/each}</ul>
            </section>
            <section>
              <h3>Next steps</h3>
              <ul>{#each explanation.recommended_next_steps as item}<li>{item}</li>{/each}</ul>
            </section>
            <section>
              <h3>Caveats</h3>
              <ul>{#each explanation.caveats as item}<li>{item}</li>{/each}</ul>
            </section>
          </div>
        </section>
      {/if}
    {/if}

    <PredictionTape rows={predictions?.rows ?? []} />
  </section>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #fbfaf7;
    color: #191816;
    font-size: 14px;
  }

  .shell {
    min-height: 100vh;
    display: grid;
    grid-template-columns: 244px minmax(0, 1fr);
  }

  .rail {
    position: sticky;
    top: 0;
    height: 100vh;
    box-sizing: border-box;
    background: #fffdf9;
    border-right: 1px solid #e8dfcf;
    padding: 22px 18px;
    display: flex;
    flex-direction: column;
    gap: 18px;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 680;
    letter-spacing: -0.03em;
  }

  .brand svg {
    width: 32px;
    height: 32px;
  }

  .brand rect {
    fill: #191816;
  }

  .brand path {
    fill: none;
    stroke: #fffdf9;
    stroke-width: 2;
    stroke-linecap: round;
  }

  .meta {
    border-top: 1px solid #eee6da;
    padding-top: 14px;
  }

  .meta p {
    margin: 0 0 0.35rem;
    color: #7c7265;
    font-size: 0.75rem;
  }

  .meta strong {
    font-size: 0.9rem;
    word-break: break-word;
  }

  .workspace {
    padding: 26px 28px 36px;
    display: grid;
    gap: 1rem;
  }

  .topbar {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
  }

  .eyebrow {
    margin: 0 0 0.45rem;
    color: #8a6d38;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.68rem;
    font-weight: 650;
  }

  h1 {
    margin: 0;
    font-size: clamp(2rem, 4vw, 3.3rem);
    line-height: 0.98;
    letter-spacing: -0.065em;
    font-weight: 690;
  }

  h2 {
    margin: 0;
    font-size: 1.05rem;
    letter-spacing: -0.02em;
  }

  .summary-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.85rem;
  }

  .workbench {
    display: grid;
    grid-template-columns: minmax(380px, 0.95fr) minmax(0, 1.05fr);
    gap: 0.9rem;
    align-items: start;
  }

  .score-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.9rem;
  }

  .results-head {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: 1rem;
    margin-top: 0.25rem;
  }

  .results-head span {
    color: #71685d;
    font-size: 0.84rem;
    max-width: 560px;
    text-align: right;
  }

  .error {
    background: #fff7f4;
    color: #8a3b34;
    border: 1px solid #f0c8bd;
    padding: 0.9rem 1rem;
    border-radius: 16px;
    font-size: 0.9rem;
  }


  .result-actions {
    display: flex;
    align-items: flex-end;
    justify-content: flex-end;
    gap: 0.75rem;
    max-width: 680px;
  }

  .result-actions button,
  .explanation-head button {
    border: 0;
    background: #191816;
    color: #fffdf9;
    border-radius: 999px;
    padding: 0.65rem 0.9rem;
    font-size: 0.82rem;
    cursor: pointer;
    white-space: nowrap;
  }

  .result-actions button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .explanation-card {
    background: #fff;
    border: 1px solid #e9e1d4;
    border-radius: 20px;
    padding: 1rem;
    box-shadow: 0 18px 50px rgba(58, 45, 24, 0.035);
  }

  .explanation-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.8rem;
  }

  .explanation-head .secondary {
    background: #fffdf9;
    color: #191816;
    border: 1px solid #ded2c2;
  }

  .explanation-summary {
    margin: 0 0 1rem;
    color: #514a40;
    font-size: 0.92rem;
    line-height: 1.55;
    max-width: 920px;
  }

  .explanation-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.9rem;
  }

  .explanation-grid section {
    background: #fffdf9;
    border: 1px solid #eee6da;
    border-radius: 16px;
    padding: 0.9rem;
  }

  .explanation-grid h3 {
    margin: 0 0 0.65rem;
    font-size: 0.88rem;
  }

  .explanation-grid ul {
    margin: 0;
    padding-left: 1.1rem;
  }

  .explanation-grid li {
    color: #625a50;
    font-size: 0.84rem;
    line-height: 1.5;
    margin-bottom: 0.45rem;
  }

  @media (max-width: 1100px) {
    .shell { grid-template-columns: 1fr; }
    .rail { position: static; height: auto; }
    .summary-grid,
    .score-grid { grid-template-columns: 1fr 1fr; }
    .workbench { grid-template-columns: 1fr; }
    .results-head { display: grid; }
    .results-head span { text-align: left; }
    .result-actions { justify-content: flex-start; align-items: flex-start; display: grid; }
    .explanation-grid { grid-template-columns: 1fr; }
  }

  @media (max-width: 720px) {
    .workspace { padding: 1rem; }
    .summary-grid,
    .score-grid { grid-template-columns: 1fr; }
  }
</style>
