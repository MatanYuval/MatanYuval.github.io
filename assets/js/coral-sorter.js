
const GENERA = ["Acropora","Agaricia","Colpophyllia","Dendrogyra","Dichocoenia","Diploria","Eusmilia","Favia","Helioseris","Isophyllia","Madracis","Manicina","Meandrina","Millepora","Montastraea","Mussa","Mycetophyllia","Oculina","Orbicella","Porites","Pseudodiploria","Scolymia","Siderastrea","Solenastrea","Stephanocoenia"];
const SPECIAL = ["Unsure","Other coral","Not coral"];
function validClass(value) {
  return typeof value === "string" &&
    (SPECIAL.includes(value) || /^[A-Z][a-z]{2,35}$/.test(value));
}
function cleanAssignments(input, models) {
  const clean = Object.create(null);
  const ids = new Set(models.map(m => m.serialize));
  if (!input || typeof input !== "object") return clean;
  for (const [id, entry] of Object.entries(input)) {
    if (ids.has(id) && entry && validClass(entry.className)) {
      clean[id] = {
        className: entry.className,
        assignedAt: typeof entry.assignedAt === "string" ? entry.assignedAt.slice(0,40) : ""
      };
    }
  }
  return clean;
}
function nextUnsorted(models, assignments, afterId) {
  if (!models.length) return null;
  const start = models.findIndex(m => m.serialize === afterId);
  for (let offset = 1; offset <= models.length; offset++) {
    const model = models[(start + offset + models.length) % models.length];
    if (!assignments[model.serialize]) return model;
  }
  return null;
}

(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const KEY = "adopt-a-coral-sorter-v1";
  const models = JSON.parse($("coral-data").textContent);
  const byId = new Map(models.map(m => [m.serialize,m]));
  let state = { assignments: Object.create(null), history: [], currentId: null };
  let current = null;
  let locked = false;
  let lockTimer;
  let persistent = true;
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const saved = JSON.parse(raw);
      state.assignments = cleanAssignments(saved.assignments, models);
      state.currentId = byId.has(saved.currentId) ? saved.currentId : null;
      state.history = Array.isArray(saved.history) ? saved.history.filter(h =>
        h && byId.has(h.id) && (h.previous === null || validClass(h.previous?.className))
      ).slice(-100) : [];
    }
  } catch {
    persistent = false;
  }
  function storageMessage() {
    $("storage-note").textContent = persistent
      ? "Progress saves in this browser only. Download your results to keep a backup or share them."
      : "Browser saving is unavailable. Your choices remain in this open tab; download results before closing it.";
  }
  function persist() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); persistent = true; }
    catch { persistent = false; }
    storageMessage();
  }
  function el(tag, text, cls) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (cls) node.className = cls;
    return node;
  }
  function urlFor(model) {
    return "?model=" + encodeURIComponent(model.serialize);
  }
  function embedFor(model) {
    return "https://www.kiriengine.app/share/embed/" + model.serialize +
      "?userId=1592778&bg_theme=bright&btn=1";
  }
  function progress() {
    const n = Object.keys(state.assignments).length;
    $("progress-text").textContent = n + " / " + models.length + " sorted";
    $("progress-bar").max = models.length;
    $("progress-bar").value = n;
    $("undo").disabled = !state.history.length;
    $("download").disabled = n === 0;
  }
  function go(model, replace = false) {
    history[replace ? "replaceState" : "pushState"]({}, "", model ? urlFor(model) : "?view=complete");
    render();
  }
  function render() {
    // Remove the previous viewer before mounting the next one.
    $("model-viewer").replaceChildren();
    current = null;
    progress();
    const params = new URLSearchParams(location.search);
    const view = params.get("view");
    $("workspace").hidden = true;
    $("groups-view").hidden = true;
    $("complete-view").hidden = true;
    if (view === "groups") { renderGroups(); return; }
    const requested = byId.get(params.get("model"));
    const next = requested || nextUnsorted(models, state.assignments, null);
    if (!next) {
      $("complete-view").hidden = false;
      $("complete-title").textContent = "All " + models.length + " models have a class.";
      document.title = "Sorting complete · Adopt-a-Coral";
      $("complete-title").focus();
      return;
    }
    current = next;
    state.currentId = current.serialize;
    persist();
    $("workspace").hidden = false;
    $("model-name").textContent = current.name;
    const assignment = state.assignments[current.serialize];
    $("current-class").textContent = assignment
      ? "Current class: " + assignment.className + ". Choose again to change it."
      : "Choose a genus. Your choice saves and opens the next unsorted model.";
    $("external").href = embedFor(current);
    $("custom-genus").value = "";
    $("custom-error").textContent = "";
    $("choice-panel").querySelectorAll("button[data-class]").forEach(button => {
      button.setAttribute("aria-pressed", String(button.dataset.class === assignment?.className));
      button.disabled = locked;
    });
    $("custom-submit").disabled = locked;
    const frame = document.createElement("iframe");
    frame.src = embedFor(current);
    frame.title = current.name + " interactive 3D model";
    frame.allow = "autoplay; fullscreen";
    frame.allowFullscreen = true;
    $("model-viewer").append(frame);
    document.title = current.name + " · Coral sorter";
    $("model-name").focus();
  }
  function choose(className) {
    if (!current || locked || !validClass(className)) return;
    const id = current.serialize;
    state.history.push({ id, previous: state.assignments[id] ? {...state.assignments[id]} : null });
    state.history = state.history.slice(-100);
    state.assignments[id] = { className, assignedAt: new Date().toISOString() };
    persist();
    $("announcement").textContent = current.name + " saved to " + className + ".";
    locked = true;
    clearTimeout(lockTimer);
    go(nextUnsorted(models, state.assignments, id));
    lockTimer = setTimeout(() => {
      locked = false;
      $("choice-panel").querySelectorAll("button").forEach(b => b.disabled = false);
    }, 700);
  }
  for (const name of GENERA) {
    const button = el("button", name, "genus-choice");
    button.type = "button";
    button.dataset.class = name;
    button.addEventListener("click", () => choose(name));
    $("genus-choices").append(button);
  }
  for (const name of SPECIAL) {
    const button = el("button", name, "special-choice");
    button.type = "button";
    button.dataset.class = name;
    button.addEventListener("click", () => choose(name));
    $("special-choices").append(button);
  }
  $("custom-form").addEventListener("submit", event => {
    event.preventDefault();
    const raw = $("custom-genus").value.trim();
    const genus = raw.charAt(0).toUpperCase() + raw.slice(1).toLowerCase();
    if (!validClass(genus)) {
      $("custom-error").textContent = "Enter one genus name, using letters only.";
      return;
    }
    choose(genus);
  });
  $("skip").addEventListener("click", () => {
    if (!current) return;
    const next = nextUnsorted(models, state.assignments, current.serialize);
    if (next?.serialize === current.serialize) {
      $("announcement").textContent = "This is the last unsorted model. Choose a class or Unsure.";
    } else go(next);
  });
  $("reload-model").addEventListener("click", render);
  $("undo").addEventListener("click", () => {
    const last = state.history.pop();
    if (!last) return;
    if (last.previous) state.assignments[last.id] = last.previous;
    else delete state.assignments[last.id];
    persist();
    go(byId.get(last.id));
    $("announcement").textContent = "Last choice undone.";
  });
  function renderGroups() {
    $("groups-view").hidden = false;
    const container = $("group-list");
    container.replaceChildren();
    const groups = new Map();
    for (const model of models) {
      const name = state.assignments[model.serialize]?.className || "Unsorted";
      if (!groups.has(name)) groups.set(name, []);
      groups.get(name).push(model);
    }
    for (const [name, items] of [...groups].sort((a,b) => a[0].localeCompare(b[0]))) {
      const details = document.createElement("details");
      details.append(el("summary", name + " (" + items.length + ")"));
      const list = document.createElement("ul");
      for (const model of items) {
        const li = document.createElement("li");
        const link = el("a", model.name);
        link.href = urlFor(model);
        link.addEventListener("click", event => { event.preventDefault(); go(model); });
        li.append(link); list.append(li);
      }
      details.append(list); container.append(details);
    }
    document.title = "Sorted groups · Adopt-a-Coral";
    $("groups-title").focus();
  }
  $("show-groups").addEventListener("click", () => {
    history.pushState({}, "", "?view=groups"); render();
  });
  document.querySelectorAll("[data-resume]").forEach(button => {
    button.addEventListener("click", () => go(nextUnsorted(models, state.assignments, null)));
  });
  $("download").addEventListener("click", () => {
    const output = {
      schemaVersion: 1,
      exportedAt: new Date().toISOString(),
      total: models.length,
      sorted: Object.keys(state.assignments).length,
      assignments: state.assignments,
      models: models.map(model => ({
        ...model,
        className: state.assignments[model.serialize]?.className || null,
        genus: state.assignments[model.serialize] && !SPECIAL.includes(state.assignments[model.serialize].className)
          ? state.assignments[model.serialize].className : null,
        assignedAt: state.assignments[model.serialize]?.assignedAt || null,
        embedUrl: embedFor(model)
      }))
    };
    const url = URL.createObjectURL(new Blob([JSON.stringify(output,null,2)], { type:"application/json" }));
    const link = document.createElement("a");
    link.href = url; link.download = "coral-classifications.json";
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 30000);
  });
  $("import-results").addEventListener("click", () => $("results-file").click());
  $("results-file").addEventListener("change", async event => {
    const file = event.target.files[0];
    if (!file) return;
    try {
      const data = JSON.parse(await file.text());
      if (data.schemaVersion !== 1 || !data.assignments || typeof data.assignments !== "object")
        throw new Error("Choose a coral-classifications.json backup from this sorter.");
      const clean = cleanAssignments(data.assignments, models);
      const conflicts = Object.entries(clean).filter(([id,a]) =>
        state.assignments[id] && state.assignments[id].className !== a.className).length;
      if (conflicts && !confirm("Replace " + conflicts + " existing choices with the imported choices?")) return;
      Object.assign(state.assignments, clean);
      state.history = [];
      persist();
      go(nextUnsorted(models, state.assignments, null));
      $("announcement").textContent = "Imported " + Object.keys(clean).length + " assignments.";
    } catch(error) { $("announcement").textContent = "Import failed: " + error.message; }
    finally { event.target.value = ""; }
  });
  window.addEventListener("popstate", render);
  window.addEventListener("storage", event => {
    if (event.key !== KEY || !event.newValue) return;
    try {
      const saved = JSON.parse(event.newValue);
      state.assignments = cleanAssignments(saved.assignments, models);
      state.history = [];
      progress();
      if (current) {
        const assignment = state.assignments[current.serialize];
        $("current-class").textContent = assignment
          ? "Current class: " + assignment.className + ". Choose again to change it."
          : "Choose a genus. Your choice saves and opens the next unsorted model.";
      }
      if (!$("groups-view").hidden) renderGroups();
    } catch {}
  });
  storageMessage();
  const params = new URLSearchParams(location.search);
  if (!params.has("model") && !params.has("view")) {
    const resume = state.currentId && !state.assignments[state.currentId]
      ? byId.get(state.currentId) : nextUnsorted(models, state.assignments, null);
    go(resume, true);
  } else render();
})();
