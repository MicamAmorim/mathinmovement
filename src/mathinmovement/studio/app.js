const state = {
  contents: [],
  selected: null,
  jobs: [],
  jobsHistory: false,
  jobsLimit: 5,
  jobsOffset: 0,
  jobsTotal: 0,
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
  toggleJobHistory: $("toggleJobHistory"),
  jobsHistoryControls: $("jobsHistoryControls"),
  jobsPageSize: $("jobsPageSize"),
  jobsPrev: $("jobsPrev"),
  jobsNext: $("jobsNext"),
  jobsPageInfo: $("jobsPageInfo"),
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
    const processed = fragment.querySelector(".processed-pill");
    const title = fragment.querySelector(".card-title");
    const id = fragment.querySelector(".card-id");
    const tags = fragment.querySelector(".tag-list");
    const meta = fragment.querySelector(".card-meta");
    const button = fragment.querySelector(".select-button");

    type.textContent = item.type;
    status.textContent = item.status;
    status.classList.add(item.status);
    if (item.processed) {
      processed.classList.remove("hidden");
      const count = Number(item.processed_count || 0);
      const when = item.last_processed_at
        ? formatDate(item.last_processed_at)
        : "data desconhecida";
      processed.title = count > 1
        ? `${count} processamentos concluídos · último em ${when}`
        : `Processado em ${when}`;
    }
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
  const files = [...(elements.packageFile.files || [])];
  if (!files.length) {
    elements.importMessage.textContent = "Selecione um ou mais arquivos .demo ou .qenem.";
    elements.importMessage.className = "form-message import-message error";
    return;
  }

  const invalid = files.filter((file) => {
    const name = file.name.toLowerCase();
    return !name.endsWith(".demo") && !name.endsWith(".qenem");
  });
  if (invalid.length) {
    elements.importMessage.textContent = `Formato inválido: ${invalid.map((file) => file.name).join(", ")}`;
    elements.importMessage.className = "form-message import-message error";
    return;
  }

  const form = new FormData();
  files.forEach((file) => form.append("files", file));
  form.append("replace", elements.replacePackage.checked ? "true" : "false");

  elements.importPackage.disabled = true;
  elements.importMessage.textContent = `Validando e importando ${files.length} pacote${files.length === 1 ? "" : "s"}...`;
  elements.importMessage.className = "form-message import-message";

  try {
    const result = await request("/imports/batch", {
      method: "POST",
      body: form,
    });
    const imported = result.imported || [];
    const failed = result.failed || [];
    const parts = [`${imported.length} importado${imported.length === 1 ? "" : "s"}`];
    if (failed.length) {
      parts.push(`${failed.length} com erro`);
      parts.push(failed.map((item) => `${item.name}: ${item.error}`).join(" | "));
    }
    elements.importMessage.textContent = parts.join(" · ");
    elements.importMessage.className = failed.length
      ? "form-message import-message error"
      : "form-message import-message success";
    elements.packageFile.value = "";
    await loadContents();

    if (imported.length === 1) {
      const importedId = imported[0].content?.id;
      const item = state.contents.find((content) => content.id === importedId);
      if (item) selectContent(item);
    }
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

function renderJobHistoryControls() {
  elements.jobsHistoryControls.classList.toggle("hidden", !state.jobsHistory);
  elements.toggleJobHistory.textContent = state.jobsHistory
    ? "Voltar aos recentes"
    : "Todo histórico";

  if (!state.jobsHistory) return;

  const limit = state.jobsLimit;
  const page = Math.floor(state.jobsOffset / limit) + 1;
  const totalPages = Math.max(1, Math.ceil(state.jobsTotal / limit));
  elements.jobsPageInfo.textContent = `Página ${page} de ${totalPages} · ${state.jobsTotal} jobs`;
  elements.jobsPrev.disabled = state.jobsOffset <= 0;
  elements.jobsNext.disabled = state.jobsOffset + limit >= state.jobsTotal;
}

async function loadJobs() {
  try {
    if (state.jobsHistory) {
      const result = await request(
        `/jobs/history?limit=${state.jobsLimit}&offset=${state.jobsOffset}`
      );
      state.jobs = result.items || [];
      state.jobsTotal = Number(result.total || 0);
    } else {
      state.jobs = await request("/jobs?limit=5");
      state.jobsTotal = state.jobs.length;
      state.jobsLimit = 5;
      state.jobsOffset = 0;
    }
    renderJobs();
    renderJobHistoryControls();
  } catch (error) {
    elements.jobsBody.innerHTML = "";
    elements.jobsEmpty.classList.remove("hidden");
    elements.jobsEmpty.textContent = `Falha ao carregar jobs: ${error.message}`;
  }
}

async function toggleJobHistory() {
  state.jobsHistory = !state.jobsHistory;
  state.jobsOffset = 0;
  state.jobsLimit = state.jobsHistory
    ? Number(elements.jobsPageSize.value || 25)
    : 5;
  await loadJobs();
}

async function changeJobsPageSize() {
  state.jobsLimit = Number(elements.jobsPageSize.value || 25);
  state.jobsOffset = 0;
  await loadJobs();
}

async function changeJobsPage(direction) {
  const next = state.jobsOffset + direction * state.jobsLimit;
  state.jobsOffset = Math.max(0, next);
  await loadJobs();
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
elements.toggleJobHistory.addEventListener("click", toggleJobHistory);
elements.jobsPageSize.addEventListener("change", changeJobsPageSize);
elements.jobsPrev.addEventListener("click", () => changeJobsPage(-1));
elements.jobsNext.addEventListener("click", () => changeJobsPage(1));
elements.openMediaFolder.addEventListener("click", openMediaFolder);
elements.renderForm.addEventListener("submit", enqueue);

loadHealth();
loadContents();
loadJobs();
setInterval(loadJobs, 2500);
setInterval(loadHealth, 15000);
