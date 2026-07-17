const els = {
  healthStatus: document.querySelector("#healthStatus"),
  scannerStatus: document.querySelector("#scannerStatus"),
  detectForm: document.querySelector("#detectForm"),
  fileInput: document.querySelector(".file-input"),
  dropzone: document.querySelector("#dropzone"),
  scanButton: document.querySelector(".scan-button"),
  resetFileButton: document.querySelector("#resetFileButton"),
  resultPanel: document.querySelector("#resultPanel"),
  resultIndicator: document.querySelector("#resultIndicator"),
  verdictMark: document.querySelector("#verdictMark"),
  verdictKicker: document.querySelector("#verdictKicker"),
  resultTitle: document.querySelector("#resultTitle"),
  resultText: document.querySelector("#resultText"),
  scanState: document.querySelector("#scanState"),
  scanStage: document.querySelector("#scanStage"),
  scanProgressBar: document.querySelector("#scanProgressBar"),
  riskScore: document.querySelector("#riskScore"),
  marginScore: document.querySelector("#marginScore"),
  riskBar: document.querySelector("#riskBar"),
  marginBar: document.querySelector("#marginBar"),
  resultFacts: document.querySelector("#resultFacts"),
  insightBlock: document.querySelector("#insightBlock"),
  insightList: document.querySelector("#insightList"),
  reviewLabel: document.querySelector("#reviewLabel"),
  previewPanel: document.querySelector("#previewPanel"),
  previewImage: document.querySelector("#previewImage"),
  selectedFileName: document.querySelector("#selectedFileName"),
};

const SCAN_STAGES = [
  "Đang kiểm tra cấu trúc ảnh",
  "Đang định vị khuôn mặt",
  "Đang chạy detector face-swap",
  "Đang đo tín hiệu chất lượng",
  "Đang tổng hợp kết luận",
];
const MIN_SCAN_MS = 1800;
let previewUrl = null;
let scanTimer = null;

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : { error: await response.text() };
  if (!response.ok) {
    const detail = Array.isArray(payload.detail)
      ? payload.detail.map((item) => item.msg || item.message || String(item)).join("; ")
      : payload.detail;
    throw new Error(payload.error || detail || `Yêu cầu thất bại (${response.status})`);
  }
  return payload;
}

async function getJson(url) {
  return parseResponse(await fetch(url));
}

async function postForm(url, formData) {
  return parseResponse(await fetch(url, { method: "POST", body: formData }));
}

function delay(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function percent(value) {
  return `${Math.round(Number(value || 0) * 100)}%`;
}

function riskIndex(value) {
  return `${Math.round(Number(value || 0) * 100)} / 100`;
}

function setBusy(isBusy) {
  els.scanButton.disabled = isBusy;
  els.scanButton.classList.toggle("is-loading", isBusy);
  els.scannerStatus.textContent = isBusy ? "Đang quét" : "Sẵn sàng";
}

function renderFacts(rows = null) {
  const facts = rows || [
    ["Kết luận", "--"],
    ["Mức rủi ro", "--"],
    ["Khuôn mặt", "--"],
    ["Phiên quét", "--"],
  ];
  els.resultFacts.innerHTML = facts
    .map(
      ([key, value, className]) =>
        `<div><dt>${escapeHtml(key)}</dt><dd class="${escapeHtml(className || "")}">${escapeHtml(value)}</dd></div>`,
    )
    .join("");
}

function resetVerdict() {
  stopScanFeedback();
  els.resultPanel.classList.remove("is-real", "is-fake", "is-uncertain", "is-error", "is-scanning");
  els.resultIndicator.textContent = "Chờ quét";
  els.verdictMark.textContent = "FT";
  els.verdictKicker.textContent = "Chưa có dữ liệu";
  els.resultTitle.textContent = "Chọn ảnh để bắt đầu";
  els.resultText.textContent = "Kết quả sẽ xuất hiện sau khi detector hoàn tất phân tích.";
  els.riskScore.textContent = "--";
  els.marginScore.textContent = "--";
  els.riskBar.style.width = "0";
  els.marginBar.style.width = "0";
  els.insightBlock.hidden = true;
  renderFacts();
}

function startScanFeedback() {
  let stageIndex = 0;
  let progress = 10;
  els.resultPanel.classList.remove("is-real", "is-fake", "is-uncertain", "is-error");
  els.resultPanel.classList.add("is-scanning");
  els.resultIndicator.textContent = "Đang quét";
  els.verdictMark.textContent = "";
  els.verdictKicker.textContent = "Đang phân tích";
  els.resultTitle.textContent = "Hệ thống đang kiểm định ảnh";
  els.resultText.textContent = "Detector đang phân tích vùng mặt và các tín hiệu pháp chứng.";
  els.riskScore.textContent = "--";
  els.marginScore.textContent = "--";
  els.riskBar.style.width = "0";
  els.marginBar.style.width = "0";
  els.scanState.hidden = false;
  els.scanStage.textContent = SCAN_STAGES[stageIndex];
  els.scanProgressBar.style.width = `${progress}%`;
  els.insightBlock.hidden = true;
  renderFacts([
    ["Kết luận", "Đang xử lý"],
    ["Mức rủi ro", "Đang tính"],
    ["Khuôn mặt", "Đang quét"],
    ["Phiên quét", "Đang tạo"],
  ]);
  scanTimer = window.setInterval(() => {
    stageIndex = Math.min(stageIndex + 1, SCAN_STAGES.length - 1);
    progress = Math.min(progress + 16, 92);
    els.scanStage.textContent = SCAN_STAGES[stageIndex];
    els.scanProgressBar.style.width = `${progress}%`;
  }, 520);
}

function stopScanFeedback() {
  if (scanTimer) window.clearInterval(scanTimer);
  scanTimer = null;
  els.scanState.hidden = true;
  els.scanProgressBar.style.width = "0";
  els.resultPanel.classList.remove("is-scanning");
}

function setError(message) {
  stopScanFeedback();
  els.resultPanel.classList.remove("is-real", "is-fake", "is-uncertain");
  els.resultPanel.classList.add("is-error");
  els.resultIndicator.textContent = "Cần thử lại";
  els.verdictMark.textContent = "!";
  els.verdictKicker.textContent = "Không thể hoàn tất";
  els.resultTitle.textContent = "Ảnh chưa được phân tích";
  els.resultText.textContent = message;
  els.riskScore.textContent = "--";
  els.marginScore.textContent = "--";
  els.riskBar.style.width = "0";
  els.marginBar.style.width = "0";
  els.insightBlock.hidden = true;
  renderFacts();
}

function renderInsights(presentation) {
  const signals = presentation.signals || [];
  els.reviewLabel.textContent = presentation.review_label || "Phân tích mô hình";
  els.insightList.innerHTML = signals
    .map(
      (item) =>
        `<li class="insight-item insight-${escapeHtml(item.kind)}"><strong>${escapeHtml(item.title)}</strong><span>${escapeHtml(item.detail)}</span></li>`,
    )
    .join("");
  els.insightBlock.hidden = signals.length === 0;
}

function verdictMeta(verdict) {
  if (verdict === "fake") return { className: "is-fake", chip: "Nghi vấn fake", mark: "F", labelClass: "label-fake" };
  if (verdict === "real") return { className: "is-real", chip: "Khả năng real", mark: "R", labelClass: "label-real" };
  return { className: "is-uncertain", chip: "Chưa chắc", mark: "?", labelClass: "label-uncertain" };
}

function renderResult(result) {
  stopScanFeedback();
  const presentation = result.presentation || {};
  const verdict = presentation.verdict || result.label || "uncertain";
  const meta = verdictMeta(verdict);
  els.resultPanel.classList.remove("is-real", "is-fake", "is-uncertain", "is-error");
  els.resultPanel.classList.add(meta.className);
  els.resultIndicator.textContent = meta.chip;
  els.verdictMark.textContent = meta.mark;
  els.verdictKicker.textContent = presentation.kicker || "Đã hoàn tất phân tích";
  els.resultTitle.textContent = presentation.title || "Kết luận: chưa đủ bằng chứng";
  els.resultText.textContent = presentation.summary || "Hệ thống đã hoàn tất kiểm định ảnh.";
  els.riskScore.textContent = riskIndex(presentation.fake_risk_index);
  els.marginScore.textContent = percent(presentation.decision_margin);
  els.riskBar.style.width = percent(presentation.fake_risk_index);
  els.marginBar.style.width = percent(presentation.decision_margin);
  renderFacts([
    ["Kết luận", presentation.verdict_label || meta.chip, meta.labelClass],
    ["Mức rủi ro", presentation.risk_band || "--"],
    ["Khuôn mặt", result.face_detected ? "Đã định vị" : "Chưa rõ"],
    ["Phiên quét", result.scan_id || "--"],
  ]);
  renderInsights(presentation);
}

function clearPreview() {
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = null;
  els.previewPanel.hidden = true;
  els.dropzone.hidden = false;
  els.previewImage.removeAttribute("src");
  els.selectedFileName.textContent = "Ảnh đã chọn";
}

function setUploadFile(file) {
  clearPreview();
  if (file) {
    previewUrl = URL.createObjectURL(file);
    els.previewImage.src = previewUrl;
    els.selectedFileName.textContent = file.name;
    els.previewPanel.hidden = false;
    els.dropzone.hidden = true;
  }
  resetVerdict();
}

async function loadHealth() {
  try {
    const payload = await getJson("/api/health");
    els.healthStatus.textContent = "Online";
    document.body.classList.add("system-online");
  } catch {
    els.healthStatus.textContent = "Offline";
    document.body.classList.add("system-offline");
  }
}

function bindUpload() {
  els.fileInput.addEventListener("change", () => setUploadFile(els.fileInput.files?.[0]));
  for (const eventName of ["dragenter", "dragover"]) {
    els.dropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      els.dropzone.classList.add("is-dragging");
    });
  }
  for (const eventName of ["dragleave", "drop"]) {
    els.dropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      els.dropzone.classList.remove("is-dragging");
    });
  }
  els.dropzone.addEventListener("drop", (event) => {
    const file = event.dataTransfer?.files?.[0];
    if (!file) return;
    const transfer = new DataTransfer();
    transfer.items.add(file);
    els.fileInput.files = transfer.files;
    setUploadFile(file);
  });
  els.resetFileButton.addEventListener("click", () => {
    els.fileInput.value = "";
    clearPreview();
    resetVerdict();
  });
}

async function runAnalysis() {
  if (!els.fileInput.files?.length) {
    throw new Error("Vui lòng chọn một ảnh trước khi bắt đầu kiểm định.");
  }
  const formData = new FormData(els.detectForm);
  return postForm("/api/detect", formData);
}

function bindDetectForm() {
  els.detectForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    startScanFeedback();
    setBusy(true);
    try {
      const [result] = await Promise.all([runAnalysis(), delay(MIN_SCAN_MS)]);
      renderResult(result);
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy(false);
    }
  });
}

bindUpload();
bindDetectForm();
resetVerdict();
loadHealth();
