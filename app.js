const form = document.querySelector('#relay-form');
const org = document.querySelector('#organization');
const goal = document.querySelector('#goal');
const messages = document.querySelector('#messages');
const actions = document.querySelector('#actions');
const summary = document.querySelector('#summary');
const reviewed = document.querySelector('#reviewed');
const template = document.querySelector('#action-template');

function localPlan() {
  const rows = messages.value.split('\n').map(line => line.trim()).filter(Boolean);
  const urgent = rows.filter(row => /urgent|can't|cannot|broken|today/i.test(row));
  return {
    brief: { messages_reviewed: rows.length, coverage_risk: urgent.length, themes: [['availability', Math.max(1, rows.length - urgent.length)]] },
    actions: rows.slice(0, 5).map((message, index) => ({
      priority: /urgent|can't|cannot|broken/i.test(message) ? 'NOW' : 'NEXT',
      title: index === 0 ? 'Confirm the coverage handoff' : `Route update ${index + 1}`,
      detail: message,
      draft: `Hi — thanks for the update. Before we change anything, could you confirm the next step for: ${goal.value}`,
    })),
  };
}

function render(data) {
  const { brief, actions: queue } = data;
  reviewed.textContent = `${brief.messages_reviewed} UPDATES`;
  const theme = brief.themes?.[0]?.[0]?.toUpperCase?.() || 'COORDINATION';
  summary.innerHTML = `<p class="card-kicker">SITUATION READ</p><h3>${brief.coverage_risk ? `${brief.coverage_risk} coverage risk${brief.coverage_risk > 1 ? 's' : ''},<br />action ready.` : 'No urgent coverage gap.<br />Keep the relay moving.'}</h3><div class="signal-row"><span>Coverage risk</span><b>${String(brief.coverage_risk).padStart(2,'0')}</b></div><div class="signal-row"><span>Strongest theme</span><b>${theme}</b></div>`;
  actions.replaceChildren();
  queue.forEach((item, index) => {
    const fragment = template.content.cloneNode(true);
    const card = fragment.querySelector('.action-card');
    card.style.animationDelay = `${index * 80}ms`;
    fragment.querySelector('.priority').textContent = item.priority;
    fragment.querySelector('h3').textContent = item.title;
    fragment.querySelector('.detail').textContent = item.detail;
    fragment.querySelector('.draft').textContent = item.draft || 'No outreach draft needed.';
    fragment.querySelector('.copy-draft').addEventListener('click', async event => {
      await navigator.clipboard?.writeText(item.draft || '');
      event.currentTarget.textContent = 'COPIED';
      setTimeout(() => { event.currentTarget.textContent = 'COPY DRAFT'; }, 1400);
    });
    actions.append(fragment);
  });
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  button.querySelector('span').textContent = 'Mapping the handoff…';
  const payload = { organization: org.value, goal: goal.value, messages: messages.value.split('\n').map(line => line.trim()).filter(Boolean) };
  try {
    const response = await fetch('http://localhost:8000/api/plan', { method: 'POST', headers: { 'Content-Type':'application/json' }, body: JSON.stringify(payload) });
    if (!response.ok) throw new Error('Local agent unavailable');
    render(await response.json());
  } catch {
    render(localPlan());
  } finally {
    button.disabled = false;
    button.querySelector('span').textContent = 'Build the review queue';
  }
});
document.querySelector('#load-demo').addEventListener('click', () => { messages.value = 'Maya — I can cover the 5pm food pickup, but I will need a ride back after 7.\nLuis: urgent — my car has broken down, so I can\'t bring the pantry kits tonight.\nNora here. I can drive an extra route if we confirm before 3pm.\nSam: I have 30 extra hygiene kits in storage and can drop them off this afternoon.'; form.requestSubmit(); });
form.requestSubmit();
