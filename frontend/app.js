/**
 * PolyPi Pure — Dashboard JavaScript
 * Communicates with the FastAPI backend at /api/*
 */

const API = window.location.origin;

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------
const $ = (id) => document.getElementById(id);

function appendConsole(text) {
  const el = $('console-output');
  if (el.textContent === 'Run a proof above to see output here…') {
    el.textContent = '';
  }
  el.textContent += text + '\n';
  el.scrollTop = el.scrollHeight;
}

function setCodeBlock(id, text) {
  $(id).textContent = text;
}

// ---------------------------------------------------------------------------
// Runtime status
// ---------------------------------------------------------------------------
async function refreshRuntime() {
  try {
    const r = await fetch(`${API}/api/runtime`);
    const data = await r.json();
    setCodeBlock('runtime-info', JSON.stringify(data, null, 2));
  } catch (e) {
    setCodeBlock('runtime-info', `Error: ${e.message}\nIs the backend running? uvicorn backend.app:app --reload`);
  }
}

// ---------------------------------------------------------------------------
// Proofs of Work
// ---------------------------------------------------------------------------
async function loadProofs() {
  try {
    const r = await fetch(`${API}/api/proofs`);
    const proofs = await r.json();
    const grid = $('proof-grid');
    grid.innerHTML = '';
    proofs.forEach((p) => {
      const card = document.createElement('div');
      card.className = 'proof-card';
      card.id = `proof-card-${p.id}`;
      card.innerHTML = `
        <span class="proof-id">#${p.id}</span>
        <h3>${p.name}</h3>
        <small class="sub">${p.file}</small>
        <button class="btn" id="btn-run-${p.id}">Run Proof</button>
      `;
      grid.appendChild(card);
      document.getElementById(`btn-run-${p.id}`).addEventListener('click', () => runProof(p.id));
    });
  } catch (e) {
    $('proof-grid').innerHTML = `<p style="color:#f85149">Backend offline: ${e.message}</p>`;
  }
}

async function runProof(id) {
  const card = $(`proof-card-${id}`);
  const btn = $(`btn-run-${id}`);
  card.classList.add('running');
  card.classList.remove('done');
  btn.disabled = true;
  btn.textContent = 'Running…';
  appendConsole(`\n▶ Running Proof #${id}…`);

  try {
    const r = await fetch(`${API}/api/proofs/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ proof: id }),
    });
    const data = await r.json();
    if (data.error) {
      appendConsole(`❌ Error: ${data.error}`);
      if (data.output) appendConsole(data.output);
    } else {
      appendConsole(data.output || '(no output)');
      appendConsole(`✅ Proof #${id} complete.`);
      card.classList.add('done');
    }
  } catch (e) {
    appendConsole(`❌ Fetch error: ${e.message}`);
  } finally {
    card.classList.remove('running');
    btn.disabled = false;
    btn.textContent = 'Run Proof';
  }
}

// ---------------------------------------------------------------------------
// Re-init Runtime
// ---------------------------------------------------------------------------
async function reinitRuntime() {
  const mode = $('sel-mode').value;
  const ide = $('sel-ide').value;
  const target = $('sel-target').value || null;

  try {
    const r = await fetch(`${API}/api/runtime/init`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode, ide, target }),
    });
    const data = await r.json();
    setCodeBlock('init-result', JSON.stringify(data, null, 2));
    await refreshRuntime();
  } catch (e) {
    setCodeBlock('init-result', `Error: ${e.message}`);
  }
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', async () => {
  await refreshRuntime();
  await loadProofs();

  $('btn-refresh-runtime').addEventListener('click', refreshRuntime);
  $('btn-clear').addEventListener('click', () => {
    $('console-output').textContent = 'Run a proof above to see output here…';
  });
  $('btn-init').addEventListener('click', reinitRuntime);
});
