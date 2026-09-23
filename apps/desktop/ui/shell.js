"use strict";
const heading = document.getElementById("heading");
const status = document.getElementById("status");
const retry = document.getElementById("retry");
let busy = false;

async function start() {
  if (busy) return;
  busy = true;
  retry.hidden = true;
  heading.textContent = "Starting your workspace";
  status.textContent = "Checking Jarvis at 127.0.0.1:8000… Startup can take up to 35 seconds.";
  try {
    const result = await window.__TAURI__.core.invoke("start_jarvis");
    heading.textContent = "Jarvis is ready";
    status.textContent = result.owned
      ? "This desktop session started Jarvis and will stop it on exit."
      : "Connected to your existing Jarvis session. It will keep running when you exit.";
  } catch (error) {
    heading.textContent = "Jarvis could not start";
    status.textContent = String(error);
    retry.hidden = false;
  } finally {
    busy = false;
  }
}

retry.addEventListener("click", start);
start();
