const input = document.getElementById("q");
const searchArea = document.getElementById("search-area");
const countEl = document.getElementById("count");
const elapsedEl = document.getElementById("elapsed");
const relatedEl = document.getElementById("related-concepts");
const featuredEl = document.getElementById("featured-section");
const recentEl = document.getElementById("recent-searches");
const exportBar = document.getElementById("export-bar");
const sortAdvanced = document.getElementById("sort-advanced");
const autocompleteDropdown = document.getElementById("autocomplete-dropdown");
const statsSection = document.getElementById("stats-bar-section");
const filterBar = document.getElementById("filter-bar");
const limitSelect = document.getElementById("limit");
const chapterToggle = document.getElementById("chapter-toggle");
const chapterDropdown = document.getElementById("chapter-dropdown");
const chapterGroups = document.getElementById("chapter-groups");
const chapterSearchInput = document.getElementById("chapter-search");
const chapterCountBadge = document.getElementById("chapter-count-badge");

let lastSearchResults = [];
let currentLimit = 20;
let allChapterData = [];
let totalChapterCount = 0;

const SWMM_TERMS = [
  'Manning roughness','dynamic wave routing','kinematic wave','infiltration',
  'Green-Ampt','Horton','curve number','pump curve','LID controls','bioretention',
  'rain garden','permeable pavement','RDII','groundwater','snowmelt','conduit',
  'junction','outfall','storage','divider','subcatchment','time series',
  'control rules','weir','orifice','outlet','inflow','rainfall','hyetograph',
  'rain gage','runoff','impervious','pervious','overland flow','hydrograph',
  'peak flow','Saint-Venant','hydraulic','pipe','cross section','diameter',
  'slope','wet well','force main','lift station','buildup','washoff',
  'water quality','concentration','treatment','EMC','aquifer','percolation',
  'water table','baseflow','lateral flow','surcharge','ponding','overflow',
  'depth','volume','node','snow pack','cold content','melt coefficient',
  'detention','stage','calibration','validation','sensitivity','parameters',
  'transverse','side flow','V-notch','trapezoidal','manhole','invert',
  'head','pressure','velocity','energy','friction','losses',
  'Preissmann slot','inertial damping','variable time step','normal flow',
  'force main','dual drainage','surface flooding','rating curve','storage curve'
];

function escapeHtml(s) {
  return (s || "").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function showToast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2000);
}

function copyShareLink() {
  const url = window.location.href;
  navigator.clipboard.writeText(url).then(() => showToast("Link copied to clipboard")).catch(() => showToast("Could not copy link"));
}

function toggleSourcePreview() {
  const el = document.getElementById("source-preview");
  el.style.display = el.style.display === "block" ? "none" : "block";
}

function copyPassage(text) {
  navigator.clipboard.writeText(text).then(() => showToast("Passage copied to clipboard"));
}

let acActiveIndex = -1;

function setupAutocomplete() {
  if (!input || !autocompleteDropdown) return;

  input.addEventListener("input", function() {
    const value = this.value.toLowerCase().trim();
    if (value.length < 2) { closeAutocomplete(); return; }
    const lastTerm = value.split(",").pop().trim();
    if (lastTerm.length < 2) { closeAutocomplete(); return; }
    const suggestions = searchEnhancer.getSuggestions(lastTerm);
    const termMatches = SWMM_TERMS
      .filter(term => term.toLowerCase().includes(lastTerm))
      .filter(term => !suggestions.some(s => s.text === term))
      .slice(0, 4)
      .map(t => ({ text: t, source: 'term' }));
    const allMatches = [...suggestions, ...termMatches].slice(0, 8);
    if (allMatches.length === 0) { closeAutocomplete(); return; }
    acActiveIndex = -1;
    autocompleteDropdown.innerHTML = allMatches.map((m, i) => {
      const safeText = escapeHtml(m.text);
      const highlighted = safeText.replace(new RegExp('(' + lastTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'), '<mark>$1</mark>');
      const icon = m.source === 'history' ? '<span class="ac-icon">&#128336;</span>' : '';
      return `<div class="autocomplete-item${m.source === 'history' ? ' ac-history' : ''}" data-index="${i}" data-value="${safeText}">${icon}${highlighted}</div>`;
    }).join("");
    autocompleteDropdown.classList.add("open");

    autocompleteDropdown.querySelectorAll(".autocomplete-item").forEach(item => {
      item.addEventListener("mousedown", function(e) {
        e.preventDefault();
        selectAutocomplete(this.dataset.value);
      });
    });
  });

  input.addEventListener("keydown", function(e) {
    if (!autocompleteDropdown.classList.contains("open")) return;
    const items = autocompleteDropdown.querySelectorAll(".autocomplete-item");
    if (e.key === "ArrowDown") {
      e.preventDefault();
      acActiveIndex = Math.min(acActiveIndex + 1, items.length - 1);
      updateAcHighlight(items);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      acActiveIndex = Math.max(acActiveIndex - 1, -1);
      updateAcHighlight(items);
    } else if (e.key === "Enter" && acActiveIndex >= 0) {
      e.preventDefault();
      selectAutocomplete(items[acActiveIndex].dataset.value);
    } else if (e.key === "Escape") {
      closeAutocomplete();
    }
  });

  input.addEventListener("blur", function() {
    setTimeout(closeAutocomplete, 150);
  });
}

function updateAcHighlight(items) {
  items.forEach((it, i) => it.classList.toggle("active", i === acActiveIndex));
}

function selectAutocomplete(value) {
  const parts = input.value.split(",");
  parts[parts.length - 1] = " " + value;
  input.value = parts.join(",").replace(/^,?\s*/, "");
  closeAutocomplete();
  input.focus();
}

function closeAutocomplete() {
  if (autocompleteDropdown) {
    autocompleteDropdown.classList.remove("open");
    autocompleteDropdown.innerHTML = "";
    acActiveIndex = -1;
  }
}

function exportResults(format) {
  if (!lastSearchResults || lastSearchResults.length === 0) {
    showToast("No results to export");
    return;
  }
  if (format === 'csv') {
    const header = '"Title","Section","URL","Snippet"';
    const rows = lastSearchResults.map(r => {
      const snippet = (r.snippet || "").replace(/<[^>]*>/g, "").replace(/"/g, '""');
      return `"${(r.title||"").replace(/"/g,'""')}","${(r.section||"").replace(/"/g,'""')}","${r.url}","${snippet}"`;
    });
    const csv = header + "\n" + rows.join("\n");
    downloadFile(csv, "swmm-search-results.csv", "text/csv");
  } else if (format === 'pdf') {
    const query = input.value.trim();
    let html = '<html><head><title>SWMM Search Results</title>';
    html += '<style>body{font-family:system-ui,sans-serif;margin:2rem;color:#1e293b}';
    html += 'h1{font-size:1.3rem;color:#2563eb}h2{font-size:.9rem;margin-top:1.5rem;border-bottom:1px solid #e2e8f0;padding-bottom:.3rem}';
    html += '.snippet{color:#64748b;font-size:.85rem;margin:.3rem 0 .8rem}.url{color:#2563eb;font-size:.75rem}';
    html += '.meta{color:#94a3b8;font-size:.7rem;margin-top:.2rem}</style></head><body>';
    html += `<h1>SWMM5 Manual Search Results</h1>`;
    html += `<p style="color:#64748b;font-size:.85rem;">Query: "${escapeHtml(query)}" &mdash; ${lastSearchResults.length} results</p>`;
    lastSearchResults.forEach((r, i) => {
      const snippet = (r.snippet || "").replace(/<[^>]*>/g, "");
      html += `<h2>${i+1}. ${escapeHtml(r.title || r.section || "Untitled")}</h2>`;
      if (r.section) html += `<div class="meta">${escapeHtml(r.section)}</div>`;
      html += `<div class="snippet">${escapeHtml(snippet)}</div>`;
      html += `<div class="url">${escapeHtml(r.url)}</div>`;
    });
    html += `<p style="margin-top:2rem;font-size:.7rem;color:#94a3b8;">Generated from SWMM5 Manual Search &mdash; Data: EPA SWMM 5.2 &mdash; Source: swmm-manual.netlify.app</p>`;
    html += '</body></html>';
    const printWin = window.open('', '_blank');
    printWin.document.write(html);
    printWin.document.close();
    printWin.focus();
    setTimeout(() => { printWin.print(); }, 500);
  }
}

function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType || "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast(`Downloaded ${filename}`);
}

const syntaxBtn = document.getElementById("syntax-help-btn");
const syntaxPopup = document.getElementById("syntax-popup");
if (syntaxBtn) {
  syntaxBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    syntaxPopup.classList.toggle("open");
  });
  document.addEventListener("click", (e) => {
    if (!syntaxBtn.contains(e.target)) syntaxPopup.classList.remove("open");
  });
}

class SearchEnhancer {
  constructor() {
    this.history = [];
    try { this.history = JSON.parse(localStorage.getItem('swmm_search_history') || '[]'); } catch {}
    this.maxHistory = 15;
    this.suggestions = [
      'Manning roughness', 'dynamic wave routing', 'kinematic wave',
      'Green-Ampt infiltration', 'Horton infiltration', 'curve number',
      'LID controls', 'bioretention', 'rain garden', 'green roof',
      'permeable pavement', 'RDII', 'pump curve', 'weir', 'orifice',
      'conduit', 'junction', 'outfall', 'storage unit', 'subcatchment',
      'time series', 'control rules', 'groundwater', 'aquifer',
      'snowmelt', 'pollutant buildup', 'washoff', 'Preissmann slot',
      'inertial damping', 'force main', 'variable time step',
      'surcharge', 'flooding', 'ponding', 'dry weather flow',
      'inlet capture', 'street cross section', 'irregular channel'
    ];
  }

  addToHistory(query) {
    if (!query || !query.trim()) return;
    this.history = this.history.filter(h => h.toLowerCase() !== query.toLowerCase());
    this.history.unshift(query.trim());
    this.history = this.history.slice(0, this.maxHistory);
    try { localStorage.setItem('swmm_search_history', JSON.stringify(this.history)); } catch {}
    this.renderHistory();
  }

  getSuggestions(inputVal) {
    if (inputVal.length < 2) return [];
    const lower = inputVal.toLowerCase();
    const historyMatches = this.history
      .filter(h => h.toLowerCase().includes(lower))
      .map(h => ({ text: h, source: 'history' }));
    const termMatches = this.suggestions
      .filter(s => s.toLowerCase().includes(lower))
      .filter(s => !this.history.includes(s))
      .map(s => ({ text: s, source: 'suggestion' }));
    return [...historyMatches, ...termMatches].slice(0, 8);
  }

  renderHistory() {
    if (!recentEl) return;
    if (this.history.length === 0) { recentEl.style.display = 'none'; return; }
    recentEl.style.display = 'flex';
    recentEl.innerHTML = '';
    const label = document.createElement('span');
    label.className = 'label';
    label.textContent = 'Recent:';
    recentEl.appendChild(label);
    this.history.slice(0, 5).forEach(q => {
      const chip = document.createElement('button');
      chip.className = 'history-chip';
      chip.textContent = q;
      chip.addEventListener('click', () => searchFor(q));
      recentEl.appendChild(chip);
    });
    const clearBtn = document.createElement('button');
    clearBtn.className = 'history-clear';
    clearBtn.textContent = 'Clear';
    clearBtn.addEventListener('click', () => this.clearHistory());
    recentEl.appendChild(clearBtn);
  }

  clearHistory() {
    this.history = [];
    try { localStorage.removeItem('swmm_search_history'); } catch {}
    this.renderHistory();
  }
}

const searchEnhancer = new SearchEnhancer();

function buildChapterLabel(title) {
  if (!title) return "";
  const name = title.replace("SWMM Manual ", "");
  if (/^Chapter(\d+)/.test(name)) {
    const chNum = name.match(/^Chapter(\d+)/)[1];
    const subTopic = name.replace(/^Chapter\d+-?/, "").replace(/([A-Z])/g, ' $1').trim();
    return `Chapter ${chNum}${subTopic ? ' — ' + subTopic : ''}`;
  } else if (/^Appendix/.test(name)) {
    return name;
  }
  return name;
}

function renderInpPanel(refs) {
  if (!refs || refs.length === 0) return "";
  let html = '<div class="inp-panel"><h3>INP File Reference</h3>';
  refs.forEach(ref => {
    html += '<div class="inp-section">';
    html += `<div class="inp-section-title">[${escapeHtml(ref.section)}]</div>`;
    html += `<div class="inp-section-desc">${escapeHtml(ref.description || "")}</div>`;
    const fields = ref.fields || [];
    if (fields.length > 0) {
      html += '<div class="inp-table-wrap"><table class="inp-field-table"><thead><tr><th>Field</th><th>Description</th><th>Unit</th></tr></thead><tbody>';
      fields.forEach(f => {
        html += `<tr><td><strong>${escapeHtml(f.name)}</strong></td><td>${escapeHtml(f.description)}</td><td>${escapeHtml(f.unit || f.type || "")}</td></tr>`;
      });
      html += '</tbody></table></div>';
    }
    if (ref.methods) {
      Object.entries(ref.methods).forEach(([method, data]) => {
        html += `<div style="margin-top:.4rem;font-size:.78rem;font-weight:600;color:var(--inp-header);">${escapeHtml(method)} method:</div>`;
        if (data.fields && data.fields.length > 0) {
          html += '<div class="inp-table-wrap"><table class="inp-field-table"><thead><tr><th>Field</th><th>Description</th><th>Unit</th></tr></thead><tbody>';
          data.fields.forEach(f => {
            html += `<tr><td><strong>${escapeHtml(f.name)}</strong></td><td>${escapeHtml(f.description)}</td><td>${escapeHtml(f.unit || f.type || "")}</td></tr>`;
          });
          html += '</tbody></table></div>';
        }
        if (data.example) {
          html += `<div class="inp-example">${escapeHtml(data.example)}</div>`;
        }
      });
    } else if (ref.example) {
      html += `<div class="inp-syntax-block"><div class="inp-syntax-header"><span>INP Syntax</span><button onclick="copyPassage(\`${ref.example.replace(/`/g,"'").replace(/\\/g,"\\\\")}\`)">Copy</button></div><pre><code>${escapeHtml(ref.example)}</code></pre></div>`;
    }
    if (ref.layers) {
      html += '<div style="margin-top:.4rem;font-size:.78rem;font-weight:600;color:var(--inp-header);">Layers:</div>';
      Object.entries(ref.layers).forEach(([layer, params]) => {
        html += `<div style="font-size:.72rem;margin-top:.2rem;"><strong>${escapeHtml(layer)}:</strong> ${params.map(p => escapeHtml(p)).join(", ")}</div>`;
      });
    }
    html += '<div class="inp-cross-links">';
    html += `<span class="inp-cross-link" onclick="searchFor('${escapeHtml(ref.section)}')">Search manual for ${escapeHtml(ref.section)}</span>`;
    html += '</div>';
    html += '</div>';
  });
  html += '</div>';
  return html;
}

let offlineDocs = null;
let isOffline = !navigator.onLine;

window.addEventListener("online", () => { isOffline = false; updateOfflineIndicator(); });
window.addEventListener("offline", () => { isOffline = true; updateOfflineIndicator(); });

function updateOfflineIndicator() {
  const el = document.getElementById("offline-indicator");
  if (el) el.style.display = isOffline ? "flex" : "none";
}

async function loadOfflineDocs() {
  try {
    const cached = localStorage.getItem("swmm_offline_docs");
    if (cached) { offlineDocs = JSON.parse(cached); return; }
  } catch {}
  try {
    const res = await fetch("/offline-docs");
    if (res.ok) {
      const data = await res.json();
      offlineDocs = data.docs || [];
      try { localStorage.setItem("swmm_offline_docs", JSON.stringify(offlineDocs)); } catch {}
    }
  } catch {}
}

function offlineSearch(q, limit, chapter) {
  if (!offlineDocs || offlineDocs.length === 0) return null;
  const t0 = performance.now();
  const terms = q.toLowerCase().split(",").map(t => t.trim()).filter(Boolean);
  const words = [];
  terms.forEach(t => t.split(/\s+/).filter(Boolean).forEach(w => { if (w.length >= 2) words.push(w); }));
  if (words.length === 0) return null;

  let docs = offlineDocs;
  if (chapter) {
    docs = docs.filter(d => d.t.toLowerCase().includes(chapter.toLowerCase().replace("SWMM Manual ", "")));
  }

  const scored = [];
  docs.forEach(d => {
    const text = (d.t + " " + d.s + " " + d.c).toLowerCase();
    let score = 0;
    words.forEach(w => {
      const idx = text.indexOf(w);
      if (idx !== -1) {
        score += 10;
        const regex = new RegExp(w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
        const matches = text.match(regex);
        if (matches) score += matches.length;
      }
    });
    if (score > 0) {
      const snippet = extractSmartSnippet(d.c, q);
      scored.push({ ...d, score, snippet });
    }
  });

  scored.sort((a, b) => b.score - a.score);
  const total = scored.length;
  const results = scored.slice(0, parseInt(limit) || 20).map(d => ({
    url: d.u, title: d.t, section: d.s, snippet: d.snippet || d.c.substring(0, 200)
  }));
  const elapsed = ((performance.now() - t0) / 1000).toFixed(3);
  return { results, total, elapsed, offline: true, related: [], inp_references: [] };
}

function getAdvancedFilters() {
  const scope = document.getElementById("search-scope");
  const filterSections = document.getElementById("filter-sections");
  const filterTables = document.getElementById("filter-tables");
  const filterInp = document.getElementById("filter-inp");
  return {
    scope: scope ? scope.value : "all",
    showSections: filterSections ? filterSections.checked : true,
    showTables: filterTables ? filterTables.checked : true,
    showInp: filterInp ? filterInp.checked : false,
  };
}

function applyAdvancedFilters(items, inpRefs, filters) {
  let filtered = items;
  if (filters.scope === "inp") {
    filtered = filtered.filter(it => {
      const s = ((it.snippet || "") + " " + (it.section || "")).toLowerCase();
      return s.includes("[") || s.includes("inp") || s.includes("syntax");
    });
  } else if (filters.scope === "tables") {
    filtered = filtered.filter(it => {
      const s = ((it.snippet || "") + " " + (it.section || "")).toLowerCase();
      return s.includes("table") || s.includes("column") || s.includes("row");
    });
  } else if (filters.scope === "text") {
    filtered = filtered.filter(it => {
      const s = ((it.snippet || "") + " " + (it.section || "")).toLowerCase();
      return !s.includes("[") || s.length > 100;
    });
  }
  if (!filters.showSections && !filters.showTables) {
    filtered = [];
  }
  return filtered;
}

const CHAPTER_GROUP_MAP = [
  { label: "Getting Started", match: t => /^(Intro|Chapter1($|-)|TitlePage|Abstract|Disclaimer|Acknowledgments|TableOfContents)/.test(t) },
  { label: "Hydrology", match: t => /^Chapter2($|-)/.test(t) },
  { label: "SWMM Modeling", match: t => /^Chapter3($|-)/.test(t) },
  { label: "Infiltration & Runoff", match: t => /^Chapter4($|-)/.test(t) },
  { label: "Hydraulics", match: t => /^Chapter5($|-)/.test(t) },
  { label: "LID & Special Features", match: t => /^Chapter6($|-)/.test(t) },
  { label: "Advanced Features", match: t => /^Chapter7($|-)/.test(t) },
  { label: "Options & Usage", match: t => /^(Chapter8|Chapter9|Chapter10|Chapter11|Chapter12)($|-)/.test(t) },
  { label: "Appendices", match: t => /^Appendix/.test(t) },
  { label: "Reference", match: t => /^(Glossary|References|ListOf|Acronyms)/.test(t) },
];

function classifyChapter(title) {
  const name = title.replace("SWMM Manual ", "");
  for (const g of CHAPTER_GROUP_MAP) {
    if (g.match(name)) return g.label;
  }
  return "Other";
}

async function loadChapters() {
  try {
    const res = await fetch("/chapters");
    if (!res.ok) return;
    const json = await res.json();
    if (json.error) return;
    allChapterData = json.chapters || [];
    totalChapterCount = allChapterData.length;
    renderChapterGroups();
  } catch(e) {}
}

function renderChapterGroups() {
  if (!chapterGroups) return;
  const grouped = {};
  allChapterData.forEach(ch => {
    const group = classifyChapter(ch.title);
    if (!grouped[group]) grouped[group] = [];
    grouped[group].push(ch);
  });

  let html = '';
  const groupOrder = CHAPTER_GROUP_MAP.map(g => g.label).concat(['Other']);
  groupOrder.forEach(groupName => {
    const items = grouped[groupName];
    if (!items || items.length === 0) return;
    html += `<div class="chapter-group" data-group="${escapeHtml(groupName)}">`;
    html += `<div class="group-label">${escapeHtml(groupName)}</div>`;
    items.forEach(ch => {
      const label = buildChapterLabel(ch.title);
      html += `<label data-title="${escapeHtml(ch.title)}">
        <input type="checkbox" value="${escapeHtml(ch.title)}" checked />
        <span>${escapeHtml(label)}</span>
        <span class="ch-sections">(${ch.sections})</span>
      </label>`;
    });
    html += '</div>';
  });
  chapterGroups.innerHTML = html;

  chapterGroups.querySelectorAll('input[type="checkbox"]').forEach(cb => {
    cb.addEventListener("change", () => {
      updateChapterBadge();
      const query = input.value.trim();
      if (query) run(query, currentLimit);
    });
  });

  updateChapterBadge();
}

function getSelectedChapters() {
  if (!chapterGroups) return [];
  const checked = chapterGroups.querySelectorAll('input[type="checkbox"]:checked');
  return Array.from(checked).map(cb => cb.value);
}

function getChapterFilterString() {
  const selected = getSelectedChapters();
  if (selected.length === 0 || selected.length === totalChapterCount) return "";
  return selected.join("|");
}

function updateChapterBadge() {
  if (!chapterCountBadge) return;
  const selected = getSelectedChapters();
  if (selected.length === totalChapterCount || selected.length === 0) {
    chapterCountBadge.textContent = "All";
  } else {
    chapterCountBadge.textContent = `${selected.length}/${totalChapterCount}`;
  }
}

function setupChapterFilter() {
  if (!chapterToggle || !chapterDropdown) return;

  chapterToggle.addEventListener("click", (e) => {
    e.stopPropagation();
    const isOpen = chapterDropdown.classList.contains("open");
    if (isOpen) {
      chapterDropdown.classList.remove("open");
      chapterToggle.classList.remove("open");
    } else {
      chapterDropdown.classList.add("open");
      chapterToggle.classList.add("open");
      if (chapterSearchInput) {
        chapterSearchInput.value = "";
        chapterSearchInput.focus();
        filterChapterList("");
      }
    }
  });

  document.addEventListener("click", (e) => {
    const filter = document.getElementById("chapter-filter");
    if (filter && !filter.contains(e.target) && chapterDropdown && chapterToggle) {
      chapterDropdown.classList.remove("open");
      chapterToggle.classList.remove("open");
    }
  });

  if (chapterSearchInput) {
    chapterSearchInput.addEventListener("input", () => {
      filterChapterList(chapterSearchInput.value);
    });
    chapterSearchInput.addEventListener("keydown", (e) => {
      e.stopPropagation();
    });
  }

  const selectAllBtn = document.getElementById("ch-select-all");
  const clearAllBtn = document.getElementById("ch-clear-all");
  if (selectAllBtn) {
    selectAllBtn.addEventListener("click", () => {
      chapterGroups.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = true);
      updateChapterBadge();
      const query = input.value.trim();
      if (query) run(query, currentLimit);
    });
  }
  if (clearAllBtn) {
    clearAllBtn.addEventListener("click", () => {
      chapterGroups.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
      updateChapterBadge();
      const query = input.value.trim();
      if (query) run(query, currentLimit);
    });
  }
}

function filterChapterList(term) {
  if (!chapterGroups) return;
  const lower = term.toLowerCase().trim();
  chapterGroups.querySelectorAll('.chapter-group').forEach(group => {
    let visibleCount = 0;
    group.querySelectorAll('label').forEach(label => {
      const text = label.textContent.toLowerCase();
      const match = !lower || text.includes(lower);
      label.classList.toggle("hidden", !match);
      if (match) visibleCount++;
    });
    const groupLabel = group.querySelector('.group-label');
    if (groupLabel) groupLabel.style.display = visibleCount === 0 ? 'none' : '';
  });
}

async function run(q, limit) {
  if (!q.trim()) {
    searchArea.innerHTML = "";
    if (countEl) countEl.textContent = "";
    if (elapsedEl) elapsedEl.textContent = "";
    if (relatedEl) relatedEl.innerHTML = "";
    if (exportBar) exportBar.style.display = "none";
    if (statsSection) statsSection.style.display = "none";
    const summaryEl = document.getElementById('resultsSummary');
    if (summaryEl) summaryEl.style.display = 'none';
    return;
  }
  if (countEl) countEl.innerHTML = '<strong>Searching...</strong>';
  if (elapsedEl) elapsedEl.textContent = "";
  if (statsSection) statsSection.style.display = "flex";
  const chapter = getChapterFilterString();
  let url = `/search?q=${encodeURIComponent(q)}&limit=${limit}`;
  if (chapter) url += `&chapter=${encodeURIComponent(chapter)}`;
  let json;
  try {
    const res = await fetch(url);
    json = await res.json();
    if (json.offline) throw new Error("offline signal");
  } catch(e) {
    json = offlineSearch(q, limit, chapter);
    if (!json) {
      if (countEl) countEl.textContent = isOffline ? "Offline — no cached data available yet." : "Search failed. Please try again.";
      return;
    }
  }
  if (json.error && json.error !== "offline") {
    if (countEl) countEl.textContent = json.error === "index_missing" ? "Index not built yet." : "Search error.";
    return;
  }
  let items = json.results || [];
  const total = json.total || items.length;
  const related = json.related || [];
  const inpRefs = json.inp_references || [];
  const elapsed = json.elapsed;

  const sortMode = sortAdvanced ? sortAdvanced.value : 'relevance';
  if (sortMode === 'chapter' && items.length > 0) {
    items = [...items].sort((a, b) => (a.chapter_order || 0) - (b.chapter_order || 0));
  } else if (sortMode === 'alpha' && items.length > 0) {
    items = [...items].sort((a, b) => (a.title || "").localeCompare(b.title || ""));
  }

  const filters = getAdvancedFilters();
  items = applyAdvancedFilters(items, inpRefs, filters);

  lastSearchResults = items;

  searchEnhancer.addToHistory(q);

  if (exportBar) exportBar.style.display = items.length > 0 ? "flex" : "none";

  if (items.length === 0) {
    const selectedCount = getSelectedChapters().length;
    const chapterName = chapter ? ` in ${selectedCount} selected chapter${selectedCount !== 1 ? 's' : ''}` : "";
    if (countEl) countEl.textContent = "";
    if (elapsedEl) elapsedEl.textContent = "";
    searchArea.innerHTML = `
      <div class="empty-state">
        <h3>No results for "${escapeHtml(q)}"${chapterName}</h3>
        <p>Try these suggestions:</p>
        <ul>
          ${chapter ? `<li>Remove the chapter filter to search all chapters</li>` : ""}
          <li>Use fewer or broader search terms</li>
          <li>Check spelling (e.g., "Preissmann" not "Preissman")</li>
          <li>Try related terms: <span class="suggestion-link" onclick="searchFor('${escapeHtml(q.split(/\s+/)[0])}')">${escapeHtml(q.split(/\s+/)[0])}</span></li>
        </ul>
      </div>`;
    if (relatedEl) relatedEl.innerHTML = "";
    updateUrl(q, limit, chapter);
    return;
  }

  const offlineBadge = json.offline ? ' <span style="font-size:.72rem;background:var(--featured-border);color:var(--featured-text);padding:.1rem .4rem;border-radius:4px;margin-left:.3rem;">offline</span>' : '';
  const selectedChapters = getSelectedChapters();
  const chapterFilterLabel = (selectedChapters.length === totalChapterCount || selectedChapters.length === 0) ? 'All Chapters' : `${selectedChapters.length} chapter${selectedChapters.length !== 1 ? 's' : ''}`;
  const resultCountText = total > items.length
    ? `<strong>${total} total result${total === 1 ? '' : 's'}</strong> &mdash; showing ${items.length}`
    : `<strong>${items.length} result${items.length === 1 ? '' : 's'}</strong>`;

  const summaryEl = document.getElementById('resultsSummary');
  if (summaryEl) {
    summaryEl.style.display = 'flex';
    summaryEl.innerHTML = `
      <div class="summary-left">
        ${resultCountText} for
        "<span class="query-echo">${escapeHtml(q)}</span>"
        <span class="filter-active">in ${escapeHtml(chapterFilterLabel)}</span>
        ${offlineBadge}
        ${elapsed !== undefined ? `<span class="elapsed-badge">${elapsed}s</span>` : ''}
      </div>
      <div class="summary-right">
        <select class="sort-select" id="summary-sort">
          <option value="relevance"${sortMode === 'relevance' ? ' selected' : ''}>Sort: Relevance</option>
          <option value="chapter"${sortMode === 'chapter' ? ' selected' : ''}>Sort: Chapter Order</option>
          <option value="alpha"${sortMode === 'alpha' ? ' selected' : ''}>Sort: Alphabetical</option>
        </select>
        <button class="summary-btn export-btn" id="summary-export" title="Export results as CSV">Export CSV</button>
        <button class="summary-btn share-btn" id="summary-share" title="Copy shareable link">Share &#128279;</button>
      </div>
    `;
    const summarySort = document.getElementById('summary-sort');
    if (summarySort) summarySort.addEventListener('change', function() {
      if (sortAdvanced) sortAdvanced.value = this.value;
      run(q, currentLimit);
    });
    const summaryExport = document.getElementById('summary-export');
    if (summaryExport) summaryExport.addEventListener('click', () => exportResults('csv'));
    const summaryShare = document.getElementById('summary-share');
    if (summaryShare) summaryShare.addEventListener('click', copyShareLink);
  }

  if (countEl) countEl.innerHTML = resultCountText + ` for "<span class="query-text">${escapeHtml(q)}</span>"`;
  if (elapsed !== undefined && elapsedEl) {
    elapsedEl.textContent = `${elapsed}s`;
  }

  const currentQuery = q;
  let resultsHtml = items.map(it => {
    const rawSnippet = it.snippet || "";
    const highlightedSnippet = highlightMatches(rawSnippet, currentQuery);
    const cleanSnippet = rawSnippet.replace(/<[^>]*>/g, "").replace(/&[^;]+;/g, " ");
    const chapterLabel = buildChapterLabel(it.title);
    const inpMatch = inpRefs.find(r => it.section && it.section.toLowerCase().includes(r.section.toLowerCase()));
    return `
    <div class="result-card">
      <div class="result-chapter">${escapeHtml(chapterLabel)}</div>
      <h3 class="result-title">
        <a href="${it.url}" target="_blank" rel="noopener">${escapeHtml(it.section || it.title || it.url)}</a>
      </h3>
      <p class="result-snippet">${highlightedSnippet}</p>
      <div class="result-meta">
        <a href="${it.url}" target="_blank" rel="noopener">View in manual &rarr;</a>
        <button class="copy-btn" onclick="copyPassage(\`${cleanSnippet.replace(/`/g, "'").replace(/\\/g, "\\\\")}\`)">Copy passage</button>
        ${inpMatch ? `<span class="inp-badge">INP: [${escapeHtml(inpMatch.section)}]</span>` : ''}
      </div>
    </div>`;
  }).join("");

  if (inpRefs.length > 0) {
    searchArea.innerHTML = `<div class="dual-pane"><div>${resultsHtml}</div>${renderInpPanel(inpRefs)}</div>`;
  } else {
    searchArea.innerHTML = resultsHtml;
  }

  if (related.length > 0 && relatedEl) {
    relatedEl.innerHTML = `
      <div class="related-box">
        <h4>Related Concepts</h4>
        <div class="related-tags">
          ${related.map(r => `<span class="related-tag" onclick="searchFor('${escapeHtml(r)}')">${escapeHtml(r)}</span>`).join("")}
        </div>
      </div>`;
  } else if (relatedEl) {
    relatedEl.innerHTML = "";
  }

  updateUrl(q, limit, chapter);
}

function updateUrl(q, limit, chapter) {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (limit && parseInt(limit) !== 20) params.set("results", limit);
  if (chapter) params.set("chapter", chapter);
  const newUrl = params.toString() ? `?${params.toString()}` : window.location.pathname;
  history.replaceState(null, "", newUrl);
}

function searchFor(term) {
  input.value = term;
  run(term, currentLimit);
  const tabs = document.querySelectorAll(".tab");
  const contents = document.querySelectorAll(".tab-content");
  tabs.forEach(t => t.classList.remove("active"));
  contents.forEach(c => c.classList.remove("active"));
  tabs[0].classList.add("active");
  document.getElementById("tab-search").classList.add("active");
  input.scrollIntoView({ behavior: "smooth", block: "start" });
}

if (input) {
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && acActiveIndex < 0) {
      e.preventDefault();
      run(input.value.trim(), currentLimit);
    }
  });
}

if (limitSelect) {
  limitSelect.addEventListener("change", () => {
    currentLimit = parseInt(limitSelect.value) || 20;
    const query = input.value.trim();
    if (query) run(query, currentLimit);
  });
}

if (sortAdvanced) {
  sortAdvanced.addEventListener("change", () => {
    const query = input.value.trim();
    if (query) run(query, currentLimit);
  });
}

["search-scope", "filter-sections", "filter-tables", "filter-inp"].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener("change", () => {
    const query = input.value.trim();
    if (query) run(query, currentLimit);
  });
});

document.querySelectorAll(".example-chip").forEach(chip => {
  chip.addEventListener("click", () => {
    searchFor(chip.dataset.query);
  });
});

document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    tab.classList.add("active");
    const target = document.getElementById("tab-" + tab.dataset.tab);
    if (target) target.classList.add("active");
    if (tab.dataset.tab === "toc" && !tocLoaded) loadToc();
    if (tab.dataset.tab === "glossary" && !glossaryLoaded) loadGlossary();
    if (tab.dataset.tab === "docs" && !docsLoaded) loadDocs();
  });
});

async function loadFeatured() {
  try {
    const res = await fetch("/featured-search");
    const json = await res.json();
    if (json.error) return;
    const items = json.results || [];
    if (items.length === 0) return;
    const featuredQuery = json.query;
    const featuredTotal = json.total || items.length;
    featuredEl.innerHTML = `
      <div class="featured-box">
        <h3>Featured Search of the Day</h3>
        <span class="featured-query" onclick="searchFor('${escapeHtml(featuredQuery)}')">"${escapeHtml(featuredQuery)}"</span>
        <div class="featured-meta">${items.length} of ${featuredTotal} results shown</div>
        <div style="margin-top: .4rem;">
          ${items.slice(0, 3).map(it => `
            <div class="featured-result">
              <a href="${it.url}" target="_blank" rel="noopener">${escapeHtml(it.title || it.section || it.url)}</a>
              ${it.section ? `<div style="font-size:.75rem;color:var(--text-muted);">${escapeHtml(it.section)}</div>` : ``}
              <div class="result-snippet" style="font-size:.78rem;">${highlightMatches(it.snippet || "", featuredQuery)}</div>
            </div>
          `).join("")}
        </div>
        <span class="see-all-link" onclick="searchFor('${escapeHtml(featuredQuery)}')">See all ${featuredTotal} results &rarr;</span>
      </div>`;
  } catch(e) {}
}

let tocLoaded = false;
async function loadToc() {
  try {
    document.getElementById("toc-loading").textContent = "Loading table of contents (53 chapters)...";
    const res = await fetch("/toc");
    const json = await res.json();
    if (json.error) { document.getElementById("toc-loading").textContent = "Table of contents not available. Build the index first."; return; }
    tocLoaded = true;
    const toc = json.toc || [];
    const maxWords = Math.max(...toc.map(t => t.word_count));
    document.getElementById("toc-loading").style.display = "none";
    let html = `
      <div class="toc-stats">
        <span class="toc-stat">${toc.length} documents</span>
        <span class="toc-stat">${json.total_documents} sections</span>
        <span class="toc-stat">${toc.reduce((sum, t) => sum + t.word_count, 0).toLocaleString()} total words</span>
      </div>
      <div class="toc-container">`;
    toc.forEach((item, idx) => {
      const isLargest = item.word_count === maxWords;
      html += `
        <div class="toc-item">
          <div class="toc-header" onclick="document.getElementById('toc-sec-${idx}').classList.toggle('open')">
            <span class="toc-title">${escapeHtml(item.title)}${isLargest ? '<span class="largest-badge">largest</span>' : ''}</span>
            <span class="toc-meta">${item.section_count} sections &middot; ${item.word_count.toLocaleString()} words</span>
          </div>
          <div class="toc-sections" id="toc-sec-${idx}">
            ${item.sections.filter(s => s).map(s => `<div class="toc-section-item" onclick="searchFor('${escapeHtml(s.replace(/'/g, ""))}')">${escapeHtml(s)}</div>`).join("")}
          </div>
        </div>`;
    });
    html += '</div>';
    document.getElementById("toc-content").innerHTML = html;
  } catch(e) {
    document.getElementById("toc-loading").textContent = "Failed to load table of contents.";
  }
}

let glossaryLoaded = false;
async function loadGlossary() {
  try {
    document.getElementById("glossary-loading").textContent = "Loading glossary terms...";
    const res = await fetch("/glossary");
    const json = await res.json();
    if (json.error) { document.getElementById("glossary-loading").textContent = "Glossary not available. Build the index first."; return; }
    glossaryLoaded = true;
    const glossary = json.glossary || {};
    const letters = Object.keys(glossary).sort();
    document.getElementById("glossary-loading").style.display = "none";
    let html = `
      <div style="margin-bottom:.4rem; font-size:.82rem; color:var(--text-muted);">
        ${json.total_terms} terms auto-extracted from the SWMM manual. Click any term to search.
      </div>
      <div style="margin-bottom:.6rem; font-size:.8rem;">
        ${letters.map(l => `<a href="#glossary-${l}" style="margin-right:.35rem; color:var(--primary); font-weight:600; text-decoration:none;">${l}</a>`).join("")}
      </div>
      <div class="glossary-container">`;
    letters.forEach(letter => {
      const terms = glossary[letter] || [];
      html += `<div class="glossary-letter" id="glossary-${letter}">${letter}</div>`;
      terms.forEach(t => {
        html += `<span class="glossary-term" onclick="searchFor('${escapeHtml(t.term.replace(/'/g, ""))}')" title="${t.count} occurrence${t.count !== 1 ? 's' : ''}">${escapeHtml(t.term)}<span class="glossary-count">(${t.count})</span></span>`;
      });
    });
    html += '</div>';
    document.getElementById("glossary-content").innerHTML = html;
  } catch(e) {
    document.getElementById("glossary-loading").textContent = "Failed to load glossary.";
  }
}

let docsLoaded = false;
async function loadDocs() {
  try {
    document.getElementById("docs-loading").textContent = "Loading application source files...";
    const res = await fetch("/docs-files");
    const json = await res.json();
    if (!json.ok) { document.getElementById("docs-loading").textContent = "Could not load docs."; return; }
    docsLoaded = true;
    const groups = json.groups || [];
    document.getElementById("docs-loading").style.display = "none";

    let totalLines = 0;
    let totalFiles = 0;
    groups.forEach(g => g.files.forEach(f => { totalLines += f.lines; totalFiles++; }));

    const container = document.getElementById("docs-content");
    const overview = document.createElement('div');
    overview.className = 'docs-overview';
    overview.textContent = `${totalFiles} source files \u2022 ${totalLines.toLocaleString()} total lines of code \u2022 Click any file to view its source`;
    container.appendChild(overview);

    groups.forEach(grp => {
      const groupDiv = document.createElement('div');
      groupDiv.className = 'docs-group';
      const titleDiv = document.createElement('div');
      titleDiv.className = 'docs-group-title';
      const iconSpan = document.createElement('span');
      iconSpan.className = 'docs-group-icon';
      iconSpan.innerHTML = grp.icon;
      titleDiv.appendChild(iconSpan);
      titleDiv.appendChild(document.createTextNode(grp.group));
      groupDiv.appendChild(titleDiv);

      grp.files.forEach(file => {
        const card = document.createElement('div');
        card.className = 'docs-file-card';

        const header = document.createElement('div');
        header.className = 'docs-file-header';

        const info = document.createElement('div');
        info.className = 'docs-file-info';
        const nameEl = document.createElement('span');
        nameEl.className = 'docs-file-name';
        nameEl.textContent = file.path;
        const descEl = document.createElement('span');
        descEl.className = 'docs-file-desc';
        descEl.textContent = file.desc;
        info.appendChild(nameEl);
        info.appendChild(descEl);

        const meta = document.createElement('div');
        meta.className = 'docs-file-meta';
        const linesSpan = document.createElement('span');
        linesSpan.textContent = file.lines.toLocaleString() + ' lines';
        const sizeSpan = document.createElement('span');
        const sizeKb = (file.size / 1024).toFixed(1);
        sizeSpan.textContent = sizeKb + ' KB';
        const extSpan = document.createElement('span');
        extSpan.textContent = file.ext.toUpperCase();
        meta.appendChild(linesSpan);
        meta.appendChild(sizeSpan);
        meta.appendChild(extSpan);

        const arrow = document.createElement('span');
        arrow.className = 'docs-expand-icon';
        arrow.textContent = '\u25B6';

        header.appendChild(info);
        const rightSide = document.createElement('div');
        rightSide.style.cssText = 'display:flex;align-items:center;gap:.6rem;';
        rightSide.appendChild(meta);
        rightSide.appendChild(arrow);
        header.appendChild(rightSide);

        const body = document.createElement('div');
        body.className = 'docs-file-body';

        let bodyBuilt = false;
        header.addEventListener('click', () => {
          card.classList.toggle('expanded');
          body.classList.toggle('open');
          if (!bodyBuilt) {
            bodyBuilt = true;
            const copyBtn = document.createElement('button');
            copyBtn.className = 'docs-copy-btn';
            copyBtn.textContent = 'Copy';
            copyBtn.addEventListener('click', (e) => {
              e.stopPropagation();
              navigator.clipboard.writeText(file.content).then(() => {
                copyBtn.textContent = 'Copied!';
                setTimeout(() => copyBtn.textContent = 'Copy', 1500);
              });
            });
            body.appendChild(copyBtn);
            const pre = document.createElement('pre');
            const codeDiv = document.createElement('div');
            codeDiv.className = 'line-numbers';
            const lines = file.content.split('\n');
            lines.forEach(line => {
              const lineSpan = document.createElement('span');
              lineSpan.className = 'line';
              lineSpan.textContent = line;
              codeDiv.appendChild(lineSpan);
            });
            pre.appendChild(codeDiv);
            body.appendChild(pre);
          }
        });

        card.appendChild(header);
        card.appendChild(body);
        groupDiv.appendChild(card);
      });

      container.appendChild(groupDiv);
    });
  } catch(e) {
    document.getElementById("docs-loading").textContent = "Failed to load documentation files.";
  }
}

async function handleUrlParams() {
  const params = new URLSearchParams(window.location.search);
  const q = params.get("q");
  const results = params.get("results");
  const chapter = params.get("chapter");
  if (results) {
    currentLimit = parseInt(results) || 20;
    if (limitSelect) limitSelect.value = currentLimit;
  }
  if (chapter && chapterGroups) {
    const chapterTitles = chapter.split('|').map(c => c.trim());
    chapterGroups.querySelectorAll('input[type="checkbox"]').forEach(cb => {
      cb.checked = chapterTitles.includes(cb.value);
    });
    updateChapterBadge();
  }
  if (q) {
    input.value = q;
    run(q, currentLimit);
  }
}

document.addEventListener("keydown", (e) => {
  if (e.key === "/" && !["INPUT","TEXTAREA","SELECT"].includes(document.activeElement.tagName)) {
    e.preventDefault();
    input.focus();
  }
  if ((e.ctrlKey || e.metaKey) && e.key === "k") {
    e.preventDefault();
    input.focus();
    input.select();
  }
});

function escapeRegex(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function parseQueryTerms(query) {
  const terms = [];
  const phraseRegex = /"([^"]+)"/g;
  let match;
  while ((match = phraseRegex.exec(query)) !== null) {
    terms.push(match[1]);
  }
  const remaining = query.replace(/"[^"]+"/g, '').trim();
  remaining.split(/[\s,]+/)
    .filter(t => !['OR', 'AND'].includes(t.toUpperCase()) && t.length > 1)
    .forEach(t => terms.push(t));
  return terms;
}

function highlightMatches(snippet, query) {
  if (!query) return snippet;
  const terms = parseQueryTerms(query);
  if (terms.length === 0) return snippet;
  const escaped = terms.map(t => escapeRegex(t));
  escaped.sort((a, b) => b.length - a.length);
  const pattern = new RegExp('(' + escaped.join('|') + ')', 'gi');
  const parts = snippet.split(/(<[^>]*>)/);
  return parts.map(part => {
    if (part.startsWith('<') && part.endsWith('>')) return part;
    return part.replace(pattern, '<mark class="search-highlight">$1</mark>');
  }).join('');
}

function extractSmartSnippet(fullText, query, options = {}) {
  const {
    maxLength = 250,
    contextBefore = 60,
    contextAfter = 150,
    ellipsis = '...'
  } = options;
  const terms = parseQueryTerms(query);
  const lowerText = fullText.toLowerCase();
  let bestPos = -1;
  bestPos = lowerText.indexOf(query.toLowerCase());
  if (bestPos === -1) {
    for (const term of terms) {
      bestPos = lowerText.indexOf(term.toLowerCase());
      if (bestPos !== -1) break;
    }
  }
  if (bestPos === -1) {
    return fullText.slice(0, maxLength) + (fullText.length > maxLength ? ellipsis : '');
  }
  let start = Math.max(0, bestPos - contextBefore);
  let end = Math.min(fullText.length, bestPos + query.length + contextAfter);
  while (start > 0 && fullText[start - 1] !== ' ') start--;
  while (end < fullText.length && fullText[end] !== ' ' && fullText[end] !== '.') end++;
  const nextPeriod = fullText.indexOf('.', end);
  if (nextPeriod !== -1 && nextPeriod - end < 30) {
    end = nextPeriod + 1;
  }
  let snippet = fullText.slice(start, end).trim();
  if (start > 0) snippet = ellipsis + snippet;
  if (end < fullText.length) snippet = snippet + ellipsis;
  return snippet;
}

function showWelcomePopup() {
  try {
    if (localStorage.getItem("swmm_welcome_dismissed")) return;
  } catch {}
  const overlay = document.getElementById("welcome-overlay");
  if (!overlay) return;
  overlay.classList.add("open");

  function closeWelcome() {
    overlay.classList.remove("open");
    try {
      const check = document.getElementById("welcome-dont-show-check");
      if (check && check.checked) {
        localStorage.setItem("swmm_welcome_dismissed", "1");
      }
    } catch {}
    input.focus();
  }

  document.getElementById("welcome-close").addEventListener("click", closeWelcome);
  document.getElementById("welcome-start-btn").addEventListener("click", closeWelcome);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeWelcome();
  });
  document.addEventListener("keydown", function escHandler(e) {
    if (e.key === "Escape") {
      closeWelcome();
      document.removeEventListener("keydown", escHandler);
    }
  });
}

function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js', { scope: '/' })
      .then((reg) => {
        reg.addEventListener('updatefound', () => {
          const newSw = reg.installing;
          if (newSw) {
            newSw.addEventListener('statechange', () => {
              if (newSw.state === 'activated') {
                showToast("App updated for offline use");
              }
            });
          }
        });
      })
      .catch(() => {});
  }
}

function updateOfflineStatus(status) {
  const el = document.getElementById("offline-status");
  if (!el) return;
  if (status === 'ready') {
    el.innerHTML = '<span style="color:var(--inp-header);">Ready for offline use</span>';
  } else if (status === 'downloading') {
    el.innerHTML = '<span style="color:var(--text-muted);">Downloading for offline...</span>';
  }
}

async function init() {
  showWelcomePopup();
  registerServiceWorker();
  setupAutocomplete();
  setupChapterFilter();
  await loadChapters();
  handleUrlParams();
  loadFeatured();
  loadOfflineDocs();
  searchEnhancer.renderHistory();
  updateOfflineIndicator();
}

init();
