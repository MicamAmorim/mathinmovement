const state = {
  contents: [],
  selected: null,
  jobs: [],
};

const $ = (id) => document.getElementById(id);

const elements = {
  health: $("healthBadge"),
  packageFile: $("packageFile"),
  replacePackage: $("replacePackage"),
  importPackage: $("importPackage"),
  importMessage: $("importMessage"),
  search: $("search"),
  typeFilter: $("typeFilter"),
  statusFilter: $("statusFilter"),
  yearFilter: $("yearFilter"),
  tagFilter: $("tagFilter"),
  formatFilter: $("formatFilter"),
  narrationFilter: $("narrationFilter"),
  catalog: $("catalog"),
  catalogEmpty: $("catalogEmpty"),
  catalogCount: $("catalogCount"),
  refreshCatalog: $("refreshCatalog"),
  composerEmpty: $("composerEmpty"),
  renderForm: $("renderForm"),
  selectedTitle: $("selectedTitle"),
  selectedId: $("selectedId"),
  selectedType: $("selectedType"),
  renderFormat: $("renderFormat"),
  renderQuality: $("renderQuality"),
  voice: $("voice"),
  musicFile: $("musicFile"),
  musicPath: $("musicPath"),
  musicHint: $("musicHint"),
  musicVolume: $("musicVolume"),
  fadeIn: $("fadeIn"),
  fadeOut: $("fadeOut"),
  dryRun: $("dryRun"),
  fastPreview: $("fastPreview"),
  skipVoice: $("skipVoice"),
  forceVoice: $("forceVoice"),
  ducking: $("ducking"),
  normalizeAudio: $("normalizeAudio"),
  enqueueButton: $("enqueueButton"),
  formMessage: $("formMessage"),
  jobsBody: $("jobsBody"),
  jobsEmpty: $("jobsEmpty"),
  refreshJobs: $("refreshJobs"),
  openMediaFolder: $("openMediaFolder"),
  folderMessage: $("folderMessage"),
  cardTemplate: $("contentCardTemplate"),
};

async function request(url, options = {}) {
  const isFormData = options.body instanceof FormData;
  const response = await fetch(url, {
    ...options,
    headers: isFormData
      ? { ...(options.headers || {}) }
      : { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch (_) {}
    throw new Error(message);
  }
  return response.json();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function filteredContents() {
  const term = elements.search.value.trim().toLowerCase();
  const type = elements.typeFilter.value;
  const status = elements.statusFilter.value;
  const year = elements.yearFilter.value;
  const tag = elements.tagFilter.value;
  const format = elements.formatFilter.value;
  const narration = elements.narrationFilter.value;
  return state.contents.filter((item) => {
    const haystack = [
      item.id,
      item.title,
      ...(item.tags || []),
      item.year || "",
    ].join(" ").toLowerCase();
    const formats = item.production_formats || item.render?.formats || ["vertical"];
    const hasNarration = Boolean(item.narration?.enabled);
    return (!term || haystack.includes(term))
      && (!type || item.type === type)
      && (!status || item.status === status)
      && (!year || String(item.year || "") === year)
      && (!tag || (item.tags || []).includes(tag))
      && (!format || formats.includes(format))
      && (!narration || (narration === "yes" ? hasNarration : !hasNarration));
  });
}

function populateFilterOptions() {
  const currentYear = elements.yearFilter.value;
  const currentTag = elements.tagFilter.value;

  const years = [...new Set(
    state.contents.map((item) => item.year).filter(Boolean)
  )].sort((a, b) => b - a);
  const tags = [...new Set(
    state.contents.flatMap((item) => item.tags || [])
  )].sort((a, b) => a.localeCompare(b, "pt-BR"));

  elements.yearFilter.innerHTML = '<option value="">Todos</option>';
  years.forEach((year) => {
    const option = document.createElement("option");
    option.value = String(year);
    option.textContent = String(year);
    elements.yearFilter.appendChild(option);
  });

  elements.tagFilter.innerHTML = '<option value="">Todas</option>';
  tags.forEach((tag) => {
    const option = document.createElement("option");
    option.value = tag;
    option.textContent = tag;
    elements.tagFilter.appendChild(option);
  });

  if (years.map(String).includes(currentYear)) {
    elements.yearFilter.value = currentYear;
  }
  if (tags.includes(currentTag)) {
    elements.tagFilter.value = currentTag;
  }
}

function renderCatalog() {
  const items = filteredContents();
  elements.catalog.innerHTML = "";
  elements.catalogEmpty.classList.toggle("hidden", items.length !== 0);
  elements.catalogCount.textContent = `${items.length} conteúdo${items.length === 1 ? "" : "s"}`;

  items.forEach((item) => {
    const fragment = elements.cardTemplate.content.cloneNode(true);
    const card = fragment.querySelector(".content-card");
    const type = fragment.querySelector(".card-type");
    const status = fragment.querySelector(".card-status");
    const title = fragment.querySelector(".card-title");
    const id = fragment.querySelector(".card-id");
    const tags = fragment.querySelector(".tag-list");
    const meta = fragment.querySelector(".card-meta");
    const button = fragment.querySelector(".select-button");

    type.textContent = item.type;
    status.textContent = item.status;
    status.classList.add(item.status);
    title.textContent = item.title;
    id.textContent = item.id;
    const formats = item.production_formats || item.render?.formats || ["vertical"];
    meta.textContent = [
      item.year ? String(item.year) : "sem ano",
      formats.map((value) => value === "horizontal" ? "16:9" : "9:16").join(" / "),
    ].join(" · ");

    (item.tags || []).slice(0, 5).forEach((tag) => {
      const node = document.createElement("span");
      node.className = "tag";
      node.textContent = tag;
      tags.appendChild(node);
    });

    if (state.selected?.id === item.id) {
      card.classList.add("selected");
    }

    button.addEventListener("click", () => selectContent(item));
    card.addEventListener("dblclick", () => selectContent(item));
    elements.catalog.appendChild(fragment);
  });
}

function selectContent(item) {
  state.selected = item;
  elements.composerEmpty.classList.add("hidden");
  elements.renderForm.classList.remove("hidden");
  elements.selectedTitle.textContent = item.title;
  elements.selectedId.textContent = item.id;
  elements.selectedType.textContent = item.type;
  elements.formMessage.textContent = "";
  elements.formMessage.className = "form-message";

  const formats = item.production_formats || item.render?.formats || ["vertical"];
  [...elements.renderFormat.options].forEach((option) => {
    option.disabled = !formats.includes(option.value);
  });
  elements.renderFormat.value = formats.includes("vertical")
    ? "vertical"
    : formats[0];

  renderCatalog();
  if (window.innerWidth < 1050) {
    $("composer").scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

async function importPackage() {
  const file = elements.packageFile.files?.[0];
  if (!file) {
    elements.importMessage.textContent = "Selecione um arquivo .demo ou .qenem.";
    elements.importMessage.className = "form-message import-message error";
    return;
  }

  const suffix = file.name.toLowerCase();
  if (!suffix.endsWith(".demo") && !suffix.endsWith(".qenem")) {
    elements.importMessage.textContent = "O arquivo deve terminar em .demo ou .qenem.";
    elements.importMessage.className = "form-message import-message error";
    return;
  }

  const form = new FormData();
  form.append("file", file);
  form.append("replace", elements.replacePackage.checked ? "true" : "false");

  elements.importPackage.disabled = true;
  elements.importMessage.textContent = "Validando e importando pacote...";
  elements.importMessage.className = "form-message import-message";

  try {
    const result = await request("/imports", {
      method: "POST",
      body: form,
    });
    elements.importMessage.textContent = `${result.content.id} importado com sucesso.`;
    elements.importMessage.className = "form-message import-message success";
    elements.packageFile.value = "";
    await loadContents();
    const imported = state.contents.find((item) => item.id === result.content.id);
    if (imported) selectContent(imported);
  } catch (error) {
    elements.importMessage.textContent = error.message;
    elements.importMessage.className = "form-message import-message error";
  } finally {
    elements.importPackage.disabled = false;
  }
}

async function uploadSelectedMusic() {
  const file = elements.musicFile.files?.[0];
  if (!file) {
    return elements.musicPath.value.trim() || null;
  }

  const form = new FormData();
  form.append("file", file);
  elements.musicHint.textContent = `Enviando ${file.name}...`;

  const result = await request("/uploads/music", {
    method: "POST",
    body: form,
  });
  elements.musicHint.textContent = `${result.name} · upload concluído`;
  return result.path;
}

async function loadHealth() {
  try {
    await request("/health");
    elements.health.className = "health ok";
    elements.health.innerHTML = '<span class="health-dot"></span><span>API online</span>';
  } catch (error) {
    elements.health.className = "health error";
    elements.health.innerHTML = '<span class="health-dot"></span><span>API indisponível</span>';
  }
}

async function loadContents() {
  try {
    state.contents = await request("/contents");
    populateFilterOptions();
    renderCatalog();
  } catch (error) {
    elements.catalog.innerHTML = "";
    elements.catalogEmpty.classList.remove("hidden");
    elements.catalogEmpty.textContent = `Falha ao carregar catálogo: ${error.message}`;
  }
}

function formatDate(value) {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "medium",
    }).format(new Date(value));
  } catch (_) {
    return value;
  }
}

function jobConfig(job) {
  const parts = [
    job.payload?.format || "vertical",
    job.payload?.quality || "draft",
  ];
  if (job.payload?.dry_run) parts.push("dry-run");
  if (job.payload?.music) parts.push("música");
  return parts.join(" · ");
}

function renderJobs() {
  elements.jobsBody.innerHTML = "";
  elements.jobsEmpty.classList.toggle("hidden", state.jobs.length !== 0);

  state.jobs.forEach((job) => {
    const row = document.createElement("tr");

    const status = document.createElement("td");
    status.innerHTML = `<span class="job-status ${job.status}">${escapeHtml(job.status)}</span>`;

    const target = document.createElement("td");
    target.innerHTML = `<strong>${escapeHtml(job.payload?.target || "—")}</strong><br><span class="content-id">${escapeHtml(job.id.slice(0, 12))}</span>`;

    const config = document.createElement("td");
    config.textContent = jobConfig(job);

    const created = document.createElement("td");
    created.textContent = formatDate(job.created_at);

    const result = document.createElement("td");
    const path = job.result?.output || job.error || "—";
    result.innerHTML = `<div class="result-path" title="${escapeHtml(path)}">${escapeHtml(path)}</div>`;

    const action = document.createElement("td");
    if (job.status === "queued") {
      const cancel = document.createElement("button");
      cancel.className = "cancel-button";
      cancel.textContent = "Cancelar";
      cancel.addEventListener("click", () => cancelJob(job.id));
      action.appendChild(cancel);
    }

    [status, target, config, created, result, action].forEach((cell) => row.appendChild(cell));
    elements.jobsBody.appendChild(row);
  });
}

async function loadJobs() {
  try {
    state.jobs = await request("/jobs?limit=30");
    renderJobs();
  } catch (error) {
    elements.jobsBody.innerHTML = "";
    elements.jobsEmpty.classList.remove("hidden");
    elements.jobsEmpty.textContent = `Falha ao carregar jobs: ${error.message}`;
  }
}

async function openMediaFolder() {
  elements.openMediaFolder.disabled = true;
  elements.folderMessage.textContent = "Abrindo pasta...";
  elements.folderMessage.className = "form-message footer-message";

  try {
    const result = await request("/system/open-media-folder", {
      method: "POST",
    });
    elements.folderMessage.textContent = result.opened;
    elements.folderMessage.className = "form-message footer-message success";
  } catch (error) {
    elements.folderMessage.textContent = error.message;
    elements.folderMessage.className = "form-message footer-message error";
  } finally {
    elements.openMediaFolder.disabled = false;
  }
}

async function cancelJob(id) {
  try {
    await request(`/jobs/${id}/cancel`, { method: "POST" });
    await loadJobs();
  } catch (error) {
    window.alert(`Não foi possível cancelar: ${error.message}`);
  }
}

async function enqueue(event) {
  event.preventDefault();
  if (!state.selected) return;

  const payload = {
    target: state.selected.id,
    format: elements.renderFormat.value,
    quality: elements.renderQuality.value,
    music_volume: Number(elements.musicVolume.value || 0.12),
    fade_in: Number(elements.fadeIn.value || 0),
    fade_out: Number(elements.fadeOut.value || 0),
    dry_run: elements.dryRun.checked,
    fast: elements.fastPreview.checked,
    skip_voice: elements.skipVoice.checked,
    force_voice: elements.forceVoice.checked,
    no_ducking: !elements.ducking.checked,
    no_normalize: !elements.normalizeAudio.checked,
  };

  const voice = elements.voice.value.trim();
  if (voice) payload.voice = voice;

  elements.enqueueButton.disabled = true;
  elements.formMessage.textContent = "Preparando job...";
  elements.formMessage.className = "form-message";

  try {
    const music = await uploadSelectedMusic();
    if (music) payload.music = music;

    elements.formMessage.textContent = "Enfileirando...";
    const job = await request("/jobs", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    elements.formMessage.textContent = `Job ${job.id.slice(0, 12)} criado com sucesso.`;
    elements.formMessage.className = "form-message success";
    await loadJobs();
  } catch (error) {
    elements.formMessage.textContent = error.message;
    elements.formMessage.className = "form-message error";
  } finally {
    elements.enqueueButton.disabled = false;
  }
}

[
  elements.search,
  elements.typeFilter,
  elements.statusFilter,
  elements.yearFilter,
  elements.tagFilter,
  elements.formatFilter,
  elements.narrationFilter,
].forEach((node) => {
  node.addEventListener("input", renderCatalog);
  node.addEventListener("change", renderCatalog);
});

elements.importPackage.addEventListener("click", importPackage);
elements.refreshCatalog.addEventListener("click", loadContents);
elements.refreshJobs.addEventListener("click", loadJobs);
elements.openMediaFolder.addEventListener("click", openMediaFolder);
elements.renderForm.addEventListener("submit", enqueue);

loadHealth();
loadContents();
loadJobs();
setInterval(loadJobs, 2500);
setInterval(loadHealth, 15000);
