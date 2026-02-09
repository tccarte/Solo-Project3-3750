
// --- Configuration ---
// Set to "" for local dev (same-origin with Flask), or full URL for split deployment
// e.g., "https://yourusername.pythonanywhere.com"
const API_BASE = "https://tccarter11.pythonanywhere.com";

const PAGE_SIZE = 10;

let editingId = null;
let currentView = "list";
let currentPage = 1;
let totalPages = 1;

// --- DOM References ---

const viewList = document.getElementById("view-list");
const viewForm = document.getElementById("view-form");
const viewStats = document.getElementById("view-stats");

const tabList = document.getElementById("tab-list");
const tabForm = document.getElementById("tab-form");
const tabStats = document.getElementById("tab-stats");

const tbody = document.getElementById("cardsTbody");
const emptyState = document.getElementById("emptyState");

const searchInput = document.getElementById("search");
const filterColor = document.getElementById("filterColor");
const newCardBtn = document.getElementById("newCardBtn");

const cardForm = document.getElementById("cardForm");
const formTitle = document.getElementById("formTitle");
const formError = document.getElementById("formError");

const cardIdInput = document.getElementById("cardId");
const nameInput = document.getElementById("name");
const setInput = document.getElementById("set");
const typeLineInput = document.getElementById("typeLine");
const manaValueInput = document.getElementById("manaValue");
const colorsInput = document.getElementById("colors");
const rarityInput = document.getElementById("rarity");
const quantityInput = document.getElementById("quantity");
const conditionInput = document.getElementById("condition");
const notesInput = document.getElementById("notes");

const cancelBtn = document.getElementById("cancelBtn");
const deleteBtn = document.getElementById("deleteBtn");

const statTotal = document.getElementById("statTotal");
const statAvgMv = document.getElementById("statAvgMv");
const statTopColor = document.getElementById("statTopColor");
const colorBars = document.getElementById("colorBars");
const rarityBreakdown = document.getElementById("rarityBreakdown");

const prevPageBtn = document.getElementById("prevPage");
const nextPageBtn = document.getElementById("nextPage");
const pageIndicator = document.getElementById("pageIndicator");

// --- API Helpers ---

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Request failed: ${res.status}`);
  }
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Request failed: ${res.status}`);
  }
  return res.json();
}

async function apiPut(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Request failed: ${res.status}`);
  }
  return res.json();
}

async function apiDelete(path) {
  const res = await fetch(`${API_BASE}${path}`, { method: "DELETE" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Request failed: ${res.status}`);
  }
  return res.json();
}

// --- Utility Functions ---

function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function colorLabel(c) {
  const map = { W: "W", U: "U", B: "B", R: "R", G: "G", C: "C", M: "M" };
  return map[c] || c;
}

// --- Validation (client-side pre-check) ---

function validateForm(data) {
  if (!data.name.trim()) return "Card Name is required.";
  if (!data.set.trim()) return "Set Code is required.";
  if (!data.typeLine.trim()) return "Type Line is required.";
  if (!data.colors) return "Colors is required.";
  if (!data.rarity) return "Rarity is required.";
  if (!data.condition) return "Condition is required.";

  if (!Number.isInteger(data.manaValue) || data.manaValue < 0 || data.manaValue > 20) {
    return "Mana Value must be an integer from 0 to 20.";
  }
  if (!Number.isInteger(data.quantity) || data.quantity < 1 || data.quantity > 99) {
    return "Quantity must be an integer from 1 to 99.";
  }

  return null;
}

function showError(msg) {
  formError.textContent = msg;
  formError.classList.remove("hidden");
}
function clearError() {
  formError.textContent = "";
  formError.classList.add("hidden");
}

// --- View Navigation ---

function setActiveTab(tabEl) {
  [tabList, tabForm, tabStats].forEach(t => t.classList.remove("active"));
  tabEl.classList.add("active");
}

async function showView(name) {
  currentView = name;

  viewList.classList.add("hidden");
  viewForm.classList.add("hidden");
  viewStats.classList.add("hidden");

  if (name === "list") {
    setActiveTab(tabList);
    viewList.classList.remove("hidden");
    await renderList();
  } else if (name === "form") {
    setActiveTab(tabForm);
    viewForm.classList.remove("hidden");
  } else {
    setActiveTab(tabStats);
    viewStats.classList.remove("hidden");
    await renderStats();
  }
}

// --- Paging ---

function updatePagingControls() {
  pageIndicator.textContent = `Page ${currentPage} of ${totalPages}`;
  prevPageBtn.disabled = currentPage <= 1;
  nextPageBtn.disabled = currentPage >= totalPages;
}

// --- List Rendering ---

async function renderList() {
  const q = searchInput.value.trim();
  const color = filterColor.value;

  const params = new URLSearchParams();
  params.set("page", currentPage);
  if (q) params.set("search", q);
  if (color) params.set("color", color);

  try {
    const data = await apiGet(`/api/cards?${params.toString()}`);
    const cards = data.cards;
    totalPages = data.totalPages;
    currentPage = data.page;

    updatePagingControls();

    tbody.innerHTML = "";
    if (cards.length === 0) {
      emptyState.textContent = "No cards match your filters.";
      emptyState.classList.remove("hidden");
      return;
    }
    emptyState.classList.add("hidden");

    for (const c of cards) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${escapeHtml(c.name)}</strong></td>
        <td>${escapeHtml(c.set)}</td>
        <td>${escapeHtml(c.typeLine)}</td>
        <td class="center">${escapeHtml(c.manaValue)}</td>
        <td class="center">${escapeHtml(c.quantity)}</td>
        <td>${escapeHtml(colorLabel(c.colors))}</td>
        <td class="right">
          <button type="button" data-action="edit" data-id="${c.id}">Edit</button>
          <button type="button" class="danger" data-action="delete" data-id="${c.id}">Delete</button>
        </td>
      `;
      tbody.appendChild(tr);
    }
  } catch (err) {
    console.error("Failed to load cards:", err);
    tbody.innerHTML = "";
    emptyState.textContent = "Failed to load cards. Check your connection.";
    emptyState.classList.remove("hidden");
  }
}

// --- Stats Rendering ---

async function renderStats() {
  try {
    const stats = await apiGet("/api/stats");

    statTotal.textContent = String(stats.totalRecords);
    statAvgMv.textContent = stats.averageManaValue.toFixed(2);

    statTopColor.textContent = stats.totalRecords === 0
      ? "\u2014"
      : `${stats.mostCommonColor} (${stats.mostCommonColorCount})`;

    colorBars.innerHTML = "";
    const colorCounts = stats.colorCounts;
    const max = Math.max(1, ...Object.values(colorCounts));
    for (const key of ["W", "U", "B", "R", "G", "C", "M"]) {
      const count = colorCounts[key] || 0;
      const pct = (count / max) * 100;
      const row = document.createElement("div");
      row.className = "barRow";
      row.innerHTML = `
        <div class="muted">${key}</div>
        <div class="barTrack"><div class="barFill" style="width:${pct}%;"></div></div>
        <div class="muted right">${count}</div>
      `;
      colorBars.appendChild(row);
    }

    rarityBreakdown.innerHTML = "";
    const rarityCounts = stats.rarityCounts;
    for (const r of ["Common", "Uncommon", "Rare", "Mythic"]) {
      const pill = document.createElement("div");
      pill.className = "pill";
      pill.textContent = `${r}: ${rarityCounts[r] || 0}`;
      rarityBreakdown.appendChild(pill);
    }
  } catch (err) {
    console.error("Failed to load stats:", err);
    statTotal.textContent = "Error";
  }
}

// --- Form Handling ---

function resetForm() {
  editingId = null;
  cardIdInput.value = "";
  formTitle.textContent = "Add Card";
  deleteBtn.classList.add("hidden");
  cardForm.reset();
  clearError();
}

async function loadFormForEdit(id) {
  try {
    const data = await apiGet(`/api/cards/${id}`);
    const card = data.card;

    editingId = id;
    cardIdInput.value = id;
    formTitle.textContent = "Edit Card";
    deleteBtn.classList.remove("hidden");
    clearError();

    nameInput.value = card.name;
    setInput.value = card.set;
    typeLineInput.value = card.typeLine;
    manaValueInput.value = card.manaValue;
    colorsInput.value = card.colors;
    rarityInput.value = card.rarity;
    quantityInput.value = card.quantity;
    conditionInput.value = card.condition;
    notesInput.value = card.notes || "";
  } catch (err) {
    alert("Could not load card: " + err.message);
  }
}

// --- Event Listeners ---

tabList.addEventListener("click", () => showView("list"));
tabForm.addEventListener("click", () => { resetForm(); showView("form"); });
tabStats.addEventListener("click", () => showView("stats"));

newCardBtn.addEventListener("click", () => {
  resetForm();
  showView("form");
});

let searchTimeout;
searchInput.addEventListener("input", () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    currentPage = 1;
    renderList();
  }, 300);
});

filterColor.addEventListener("change", () => {
  currentPage = 1;
  renderList();
});

prevPageBtn.addEventListener("click", () => {
  if (currentPage > 1) {
    currentPage--;
    renderList();
  }
});

nextPageBtn.addEventListener("click", () => {
  if (currentPage < totalPages) {
    currentPage++;
    renderList();
  }
});

tbody.addEventListener("click", async (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;

  const action = btn.dataset.action;
  const id = btn.dataset.id;
  if (!id) return;

  if (action === "edit") {
    await loadFormForEdit(id);
    showView("form");
  }

  if (action === "delete") {
    const row = btn.closest("tr");
    const name = row ? row.querySelector("td strong").textContent : "this card";
    const ok = confirm(`Delete "${name}"? This cannot be undone.`);
    if (ok) {
      try {
        await apiDelete(`/api/cards/${id}`);
        await renderList();
      } catch (err) {
        alert("Delete failed: " + err.message);
      }
    }
  }
});

cancelBtn.addEventListener("click", () => {
  resetForm();
  showView("list");
});

deleteBtn.addEventListener("click", async () => {
  if (!editingId) return;
  const name = nameInput.value || "this card";
  const ok = confirm(`Delete "${name}"? This cannot be undone.`);
  if (!ok) return;

  try {
    await apiDelete(`/api/cards/${editingId}`);
    resetForm();
    await showView("list");
  } catch (err) {
    alert("Delete failed: " + err.message);
  }
});

cardForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();

  const data = {
    name: nameInput.value,
    set: setInput.value,
    typeLine: typeLineInput.value,
    manaValue: Number(manaValueInput.value),
    colors: colorsInput.value,
    rarity: rarityInput.value,
    quantity: Number(quantityInput.value),
    condition: conditionInput.value,
    notes: notesInput.value.trim(),
  };

  const err = validateForm(data);
  if (err) {
    showError(err);
    return;
  }

  try {
    if (editingId) {
      await apiPut(`/api/cards/${editingId}`, data);
    } else {
      await apiPost("/api/cards", data);
      currentPage = 1;
    }
    resetForm();
    await showView("list");
  } catch (apiErr) {
    showError(apiErr.message);
  }
});

// --- Initialize ---
showView("list");
