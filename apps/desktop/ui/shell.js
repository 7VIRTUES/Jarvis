"use strict";
const heading = document.getElementById("heading");
const status = document.getElementById("status");
const missing = document.getElementById("missing");
const prepare = document.getElementById("prepare");
const retry = document.getElementById("retry");
let busy = false;

function showMissing(items) {
  missing.replaceChildren();
  for (const item of items) {
    const line = document.createElement("li");
    line.textContent = item.message;
    missing.append(line);
  }
  missing.hidden = items.length === 0;
}

function showError(error, canPrepare = false) {
  heading.textContent = "Jarvis needs attention";
  status.textContent = String(error);
  prepare.hidden = !canPrepare;
  retry.hidden = false;
}

async function launch() {
  heading.textContent = "Starting your workspace";
  status.textContent = "Checking Jarvis at 127.0.0.1:8000… Startup can take up to 35 seconds.";
  prepare.hidden = true;
  retry.hidden = true;
  showMissing([]);
  try {
    const result = await window.__TAURI__.core.invoke("start_jarvis");
    heading.textContent = "Jarvis is ready";
    status.textContent = result.owned
      ? "This desktop session started Jarvis and will stop it on exit."
      : "Connected to your existing Jarvis session. It will keep running when you exit.";
  } catch (error) {
    showError(error);
  }
}

async function inspect() {
  if (busy) return;
  busy = true;
  prepare.hidden = true;
  retry.hidden = true;
  showMissing([]);
  heading.textContent = "Checking your workspace";
  status.textContent = "Reading local prerequisites…";
  try {
    const result = await window.__TAURI__.core.invoke("inspect_startup");
    if (result.ready) {
      await launch();
    } else {
      heading.textContent = "Prepare Jarvis";
      status.textContent = "These local prerequisites are missing. Preparation will create the Python environment and may install Ollama and download the listed models.";
      showMissing(result.missing);
      prepare.hidden = false;
      retry.hidden = false;
    }
  } catch (error) {
    showError(error);
  } finally {
    busy = false;
  }
}

async function runPreparation() {
  if (busy) return;
  busy = true;
  prepare.hidden = true;
  retry.hidden = true;
  heading.textContent = "Preparing Jarvis";
  status.textContent = "Checking local prerequisites…";
  let poll;
  try {
    poll = setInterval(async () => {
      try {
        const progress = await window.__TAURI__.core.invoke("preparation_status");
        if (progress) status.textContent = progress;
      } catch (_) {
        // The preparation command reports the actionable failure.
      }
    }, 500);
    await window.__TAURI__.core.invoke("prepare_jarvis");
    clearInterval(poll);
    status.textContent = "Preparation complete. Starting Jarvis…";
    await launch();
  } catch (error) {
    clearInterval(poll);
    showError(error, true);
  } finally {
    busy = false;
  }
}

retry.addEventListener("click", inspect);
prepare.addEventListener("click", runPreparation);
inspect();
