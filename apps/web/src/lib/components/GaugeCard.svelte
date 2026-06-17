<script lang="ts">
  export let label = '';
  export let value: number | undefined | null = null;
  export let suffix = '';
  export let detail = '';
</script>

<section class="gauge">
  <p>{label}</p>
  <strong>{value == null ? '—' : value.toFixed(3)}{suffix}</strong>
  <span>{detail}</span>
</section>

<style>
  .gauge {
    background: #fffdf9;
    border: 1px solid #e9e1d4;
    border-radius: 18px;
    padding: 1rem;
    box-shadow: 0 18px 50px rgba(58, 45, 24, 0.04);
  }

  p {
    margin: 0;
    color: #7c7265;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 620;
  }

  strong {
    display: block;
    margin: 0.5rem 0 0.35rem;
    font-size: 1.7rem;
    line-height: 1;
    color: #191816;
    letter-spacing: -0.04em;
  }

  span {
    color: #71685d;
    font-size: 0.84rem;
    line-height: 1.4;
  }
</style>
