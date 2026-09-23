#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

#[cfg(not(windows))]
compile_error!("Jarvis desktop currently supports Windows only.");

#[cfg(windows)]
mod process;
#[cfg(windows)]
mod runtime;
#[cfg(windows)]
mod webview;

use std::sync::Mutex;
use serde::Serialize;
use tauri::Manager;

#[derive(Default)]
struct Lifecycle {
    busy: bool,
    exiting: bool,
    connected: bool,
    owned: Option<process::OwnedLauncher>,
}

#[derive(Serialize)]
struct Connection { owned: bool }

#[tauri::command]
async fn start_jarvis(app: tauri::AppHandle, window: tauri::WebviewWindow) -> Result<Connection, String> {
    // App commands need an explicit caller check as well as remote capability
    // isolation. The assistant has no command or native plugin permissions.
    if window.label() != "startup" || !webview::shell_url(&window.url().map_err(|e| e.to_string())?) {
        return Err("This command is only available to the local startup screen.".into());
    }
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
        .invoke_handler(tauri::generate_handler![start_jarvis])
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
                    state.owned.take();
                };
            }
        });
}
