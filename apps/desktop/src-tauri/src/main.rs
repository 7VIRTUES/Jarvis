#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

#[cfg(not(windows))]
compile_error!("Jarvis desktop currently supports Windows only.");

#[cfg(windows)]
mod process;
#[cfg(windows)]
mod runtime;
#[cfg(windows)]
mod webview;

use std::sync::{Arc, Mutex};
use serde::Serialize;
use tauri::Manager;

#[derive(Default)]
struct Lifecycle {
    busy: bool,
    exiting: bool,
    connected: bool,
    owned: Option<process::OwnedLauncher>,
    preparation: Option<Arc<process::OwnedPreparation>>,
    progress: String,
}

#[derive(Serialize)]
struct Connection { owned: bool }

fn startup_caller(window: &tauri::WebviewWindow) -> Result<(), String> {
    if window.label() != "startup" || !webview::shell_url(&window.url().map_err(|e| e.to_string())?) {
        return Err("This command is only available to the local startup screen.".into());
    }
    Ok(())
}

#[tauri::command]
async fn inspect_startup(window: tauri::WebviewWindow) -> Result<runtime::Preflight, String> {
    startup_caller(&window)?;
    tauri::async_runtime::spawn_blocking(|| {
        let client = runtime::client()?;
        if matches!(runtime::health(&client)?, runtime::HealthState::Ready) {
            return Ok(runtime::Preflight {
                ready: true, missing: Vec::new(), python_executable: Default::default(),
            });
        }
        runtime::preflight(&runtime::repository_root()?)
    }).await.map_err(|e| format!("Preflight could not complete: {e}"))?
}

#[tauri::command]
fn preparation_status(app: tauri::AppHandle, window: tauri::WebviewWindow) -> Result<String, String> {
    startup_caller(&window)?;
    let state = app.state::<Mutex<Lifecycle>>();
    let state = state.lock().map_err(|_| "Desktop lifecycle is unavailable.")?;
    Ok(state.progress.clone())
}

#[tauri::command]
async fn prepare_jarvis(app: tauri::AppHandle, window: tauri::WebviewWindow) -> Result<(), String> {
    startup_caller(&window)?;
    {
        let state = app.state::<Mutex<Lifecycle>>();
        let mut state = state.lock().map_err(|_| "Desktop lifecycle is unavailable.")?;
        if state.exiting || state.busy || state.connected {
            return Err("Desktop startup or preparation is already active.".into());
        }
        state.busy = true;
        state.progress = "Checking local prerequisites...".into();
    }
    let worker_app = app.clone();
    let result = tauri::async_runtime::spawn_blocking(move || {
        let client = runtime::client()?;
        if matches!(runtime::health(&client)?, runtime::HealthState::Ready) {
            return Ok(());
        }
        let root = runtime::repository_root()?;
        let preflight = runtime::preflight(&root)?;
        if preflight.ready { return Ok(()); }
        let child = Arc::new(process::OwnedPreparation::spawn(&root, &preflight.python_executable)?);
        {
            let state = worker_app.state::<Mutex<Lifecycle>>();
            let mut state = state.lock().map_err(|_| "Desktop lifecycle is unavailable.")?;
            if state.exiting {
                child.terminate();
                return Err("Desktop is closing.".into());
            }
            state.preparation = Some(child.clone());
        }
        child.run(|message| {
            let state = worker_app.state::<Mutex<Lifecycle>>();
            if let Ok(mut state) = state.lock() {
                state.progress = message.to_string();
            }
        })?;
        let state = worker_app.state::<Mutex<Lifecycle>>();
        if state.lock().map_err(|_| "Desktop lifecycle is unavailable.")?.exiting {
            return Err("Desktop is closing.".into());
        }
        if matches!(runtime::health(&client)?, runtime::HealthState::Ready) {
            return Err("Another Jarvis instance started during preparation. No instance was reconfigured.".into());
        }
        let remaining = runtime::preflight(&root)?;
        if !remaining.ready {
            return Err(remaining.missing.into_iter().map(|item| item.message)
                .collect::<Vec<_>>().join("\n"));
        }
        Ok(())
    }).await.map_err(|e| format!("Preparation could not complete: {e}"))?;
    let state = app.state::<Mutex<Lifecycle>>();
    let mut state = state.lock().map_err(|_| "Desktop lifecycle is unavailable.")?;
    state.busy = false;
    if result.is_err() {
        if let Some(child) = state.preparation.take() { child.terminate(); }
    }
    result
}

#[tauri::command]
async fn start_jarvis(app: tauri::AppHandle, window: tauri::WebviewWindow) -> Result<Connection, String> {
    startup_caller(&window)?;
    {
        let state = app.state::<Mutex<Lifecycle>>();
        let mut state = state.lock().map_err(|_| "Desktop lifecycle is unavailable.")?;
        if state.exiting || state.busy || state.connected { return Err("Desktop startup is already active.".into()); }
        state.busy = true;
    }
    let worker_app = app.clone();
    let result = tauri::async_runtime::spawn_blocking(move || {
        let owned = runtime::connect()?;
        let owns_runtime = owned.is_some();
        {
            let state = worker_app.state::<Mutex<Lifecycle>>();
            let mut state = state.lock().map_err(|_| "Desktop lifecycle is unavailable.")?;
            if state.exiting { return Err("Desktop is closing.".to_string()); }
            state.owned = owned;
        }
        webview::assistant(&worker_app)?;
        Ok(Connection { owned: owns_runtime })
    }).await.map_err(|e| format!("Desktop startup could not complete: {e}"))
        .and_then(|result| result);
    let state = app.state::<Mutex<Lifecycle>>();
    let mut state = state.lock().map_err(|_| "Desktop lifecycle is unavailable.")?;
    state.busy = false;
    state.connected = result.is_ok();
    if result.is_err() { state.owned.take(); }
    result
}

fn main() {
    tauri::Builder::default()
        .manage(Mutex::new(Lifecycle::default()))
        .invoke_handler(tauri::generate_handler![inspect_startup, preparation_status, prepare_jarvis, start_jarvis])
        .setup(|app| { webview::startup(app.handle())?; Ok(()) })
        .on_window_event(|window, event| {
            if matches!(event, tauri::WindowEvent::CloseRequested { .. }) {
                window.app_handle().exit(0);
            }
        })
        .build(tauri::generate_context!())
        .expect("Could not create the Jarvis desktop window")
        .run(|app, event| {
            if matches!(event, tauri::RunEvent::ExitRequested { .. } | tauri::RunEvent::Exit) {
                let state = app.state::<Mutex<Lifecycle>>();
                if let Ok(mut state) = state.lock() {
                    state.exiting = true;
                    if let Some(child) = state.preparation.take() { child.terminate(); }
                    state.owned.take();
                };
            }
        });
}
