<script lang="ts">
  export let ok = false;
  export let text = 'offline';
</script>

<span class:ok aria-label={ok ? 'Artifact service available' : 'Artifact service unavailable'}>
  <i aria-hidden="true"></i>
  {text}
</span>

<style>
  span {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.55rem 0.75rem;
    border: 1px solid #e3dacb;
    border-radius: 999px;
    background: #fffdf9;
    color: #8a3b34;
    font-weight: 620;
    font-size: 0.78rem;
    white-space: nowrap;
  }

  i {
    width: 0.45rem;
    height: 0.45rem;
    border-radius: 50%;
    background: currentColor;
  }

  .ok {
    color: #2e7d55;
  }
</style>
