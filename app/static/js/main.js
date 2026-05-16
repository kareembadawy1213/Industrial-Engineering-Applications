/* ── Global utilities used across all pages ────────────────────────────── */

"use strict";

/* Sidebar toggle for mobile */
document.addEventListener('DOMContentLoaded', () => {
  const toggle  = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
  }

  // Mark active nav link
  const links = document.querySelectorAll('#sidebar .nav-link');
  links.forEach(link => {
    if (link.href === window.location.href ||
        window.location.pathname.startsWith(new URL(link.href, location).pathname.replace(/\/$/, ''))) {
      link.classList.add('active');
    }
  });

  // Auto-dismiss flash messages after 4 s
  document.querySelectorAll('.flash-msg').forEach(el => {
    setTimeout(() => el.style.display = 'none', 4000);
  });
});

/* ── Spinner helpers ──────────────────────────────────────────────────── */
function showSpinner() {
  const el = document.getElementById('spin-overlay');
  if (el) el.classList.add('active');
}
function hideSpinner() {
  const el = document.getElementById('spin-overlay');
  if (el) el.classList.remove('active');
}

/* ── Generic POST helper returning JSON ──────────────────────────────── */
async function postJSON(url, payload) {
  const res = await fetch(url, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Server error');
  return data;
}

/* ── Render recommendations ──────────────────────────────────────────── */
function renderRecs(recs, containerId) {
  const el = document.getElementById(containerId);
  if (!el || !recs) return;
  const icons = { success: 'fa-check-circle', info: 'fa-info-circle',
                  warning: 'fa-exclamation-triangle', danger: 'fa-times-circle' };
  el.innerHTML = recs.map(r => `
    <div class="rec-card ${r.type}">
      <i class="fas ${icons[r.type] || 'fa-lightbulb'} mt-1"></i>
      <div>
        <div class="rec-title">${r.title}</div>
        <div class="rec-message">${r.message}</div>
      </div>
    </div>`).join('');
}

/* ── Format number with commas ───────────────────────────────────────── */
function fmt(n, decimals = 2) {
  return Number(n).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/* ── Dynamic row builder ─────────────────────────────────────────────── */
function addRow(containerId, templateFn) {
  const container = document.getElementById(containerId);
  const idx       = container.querySelectorAll('.dynamic-row').length;
  const div       = document.createElement('div');
  div.className   = 'dynamic-row';
  div.innerHTML   = templateFn(idx);
  container.appendChild(div);
}

function removeRow(btn) {
  btn.closest('.dynamic-row').remove();
}

/* ── Chart default config ────────────────────────────────────────────── */
const CHART_DEFAULTS = {
  responsive:          true,
  maintainAspectRatio: true,
  plugins: {
    legend: { labels: { color: '#94a3b8', font: { size: 12 } } },
    tooltip: { backgroundColor: '#1e293b', titleColor: '#e2e8f0', bodyColor: '#94a3b8',
               borderColor: '#334155', borderWidth: 1 },
  },
  scales: {
    x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(51,65,85,.5)' } },
    y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(51,65,85,.5)' } },
  },
};

function lineChart(ctx, labels, datasets, options = {}) {
  return new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: { ...CHART_DEFAULTS, ...options },
  });
}

function barChart(ctx, labels, datasets, options = {}) {
  return new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets },
    options: { ...CHART_DEFAULTS, ...options },
  });
}
