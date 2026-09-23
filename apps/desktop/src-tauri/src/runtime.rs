use std::{io::{ErrorKind, Read}, net::{SocketAddr, TcpStream}, os::windows::process::CommandExt, path::PathBuf, process::Command, thread, time::{Duration, Instant}};
use reqwest::blocking::Client;
use tauri::Manager;
use serde::{Deserialize, Serialize};
use windows::Win32::System::Threading::CREATE_NO_WINDOW;
use crate::process::{listener_pid, OwnedLauncher};

pub const ORIGIN: &str = "http://127.0.0.1:8000";
pub const ASSISTANT: &str = "http://127.0.0.1:8000/assistant";

pub fn client() -> Result<Client, String> {
    Client::builder().no_proxy().redirect(reqwest::redirect::Policy::none())
        .connect_timeout(Duration::from_secs(2)).timeout(Duration::from_secs(3))
        .build().map_err(|e| e.to_string())
}

pub fn allowed_url(url: &tauri::Url) -> bool {
    url.scheme() == "http" && url.host_str() == Some("127.0.0.1")
        && url.port() == Some(8000) && url.username().is_empty() && url.password().is_none()
}

#[derive(Deserialize)]
struct Health { status: String, app: String, mode: String, version: String }

pub enum HealthState { Ready, Absent }

pub fn health(client: &Client) -> Result<HealthState, String> {
    let address = SocketAddr::from(([127, 0, 0, 1], 8000));
    match TcpStream::connect_timeout(&address, Duration::from_secs(1)) {
        Ok(stream) => drop(stream),
        Err(error) if error.kind() == ErrorKind::ConnectionRefused => {
            if listener_pid()?.is_some() {
                return Err("Port 8000 is occupied but is not accepting connections. No process was changed.".into());
            }
            return Ok(HealthState::Absent);
        }
        Err(_) => return Err("Port 8000 could not be checked safely. No existing process was changed.".into()),
    }
    let response = client.get(format!("{ORIGIN}/health")).send()
        .map_err(|_| "Port 8000 is occupied, but Jarvis health did not respond. Close the conflicting service or wait for it to become ready, then retry.".to_string())?;
    if response.status() != reqwest::StatusCode::OK {
        return Err("Port 8000 did not return valid Jarvis health. Startup was blocked.".into());
    }
    let mut body = Vec::new();
    response.take(8193).read_to_end(&mut body).map_err(|e| e.to_string())?;
    if body.len() > 8192 { return Err("The health response exceeded the allowed size.".into()); }
    let payload: Health = serde_json::from_slice(&body)
        .map_err(|_| "Port 8000 returned an invalid health identity. Startup was blocked.".to_string())?;
    if payload.status != "ok" || payload.app != "Jarvis PC Local" || payload.mode != "local" || payload.version.trim().is_empty() {
        return Err("Port 8000 belongs to an unknown or unhealthy app. Startup was blocked; no existing process was changed.".into());
    }
    Ok(HealthState::Ready)
}

pub struct RuntimeLayout {
    pub resources: PathBuf,
    pub runtime: PathBuf,
    pub installed: bool,
}

impl RuntimeLayout {
    pub fn python(&self) -> PathBuf { self.runtime.join(".venv/Scripts/python.exe") }

    pub fn mode(&self) -> &'static str {
        if self.installed { "installed" } else { "repository" }
    }

    pub fn environment(&self) -> std::collections::BTreeMap<std::ffi::OsString, std::ffi::OsString> {
        // Windows environment keys are case-insensitive. Override inherited mode
        // explicitly; no resource, runtime, or data path comes from the UI/env.
        let mut environment = std::collections::BTreeMap::new();
        for (key, value) in std::env::vars_os() {
            environment.insert(std::ffi::OsString::from(key.to_string_lossy().to_uppercase()), value);
        }
        environment.insert("JARVIS_DESKTOP_LAYOUT".into(), self.mode().into());
        environment.insert("PYTHONDONTWRITEBYTECODE".into(), "1".into());
        environment
    }
}

fn valid_resources(root: &std::path::Path) -> bool {
    ["apps/desktop/launcher_adapter.py", "apps/desktop/runtime_layout.py",
     "scripts/jarvis_launcher.py", "scripts/jarvis_bootstrap.py", "requirements.txt",
     "services/jarvis-core/src/jarvis_core/app.py"]
        .iter().all(|relative| root.join(relative).is_file())
}

pub fn resolve_layout(app: &tauri::AppHandle) -> Result<RuntimeLayout, String> {
    // Preserve repository-local operation even when Tauri has staged resources
    // alongside a development executable. Never search cwd or an environment path.
    let executable = std::env::current_exe().map_err(|e| e.to_string())?;
    for ancestor in executable.ancestors().skip(1) {
        if ancestor.join(".git").exists()
            && ancestor.join("apps/desktop/src-tauri/Cargo.toml").is_file()
            && valid_resources(ancestor)
        {
            return Ok(RuntimeLayout {
                resources: ancestor.to_path_buf(), runtime: ancestor.to_path_buf(), installed: false,
            });
        }
    }
    let resources = app.path().resource_dir().map_err(|e| e.to_string())?.join("jarvis-resources");
    let marker = std::fs::read_to_string(resources.join("desktop-resources.version"))
        .map_err(|_| "Packaged Jarvis resources are missing. Restore the complete application.".to_string())?;
    if marker.trim() != "jarvis-desktop-resources-v1" || !valid_resources(&resources) {
        return Err("Packaged Jarvis resources are incomplete or unsupported.".into());
    }
    // Stable across application versions and installation directories. Preparation
    // creates missing directories only; upgrades never copy or clear user data.
    let user_root = app.path().app_local_data_dir().map_err(|e| e.to_string())?;
    let runtime = user_root.join("runtime");
    use std::os::windows::fs::MetadataExt;
    for path in [&user_root, &runtime, &runtime.join(".venv"),
                 &runtime.join(".venv/Scripts"), &runtime.join(".venv/Scripts/python.exe")] {
        match std::fs::symlink_metadata(path) {
            Ok(metadata) if metadata.file_attributes() & 0x400 != 0 =>
                return Err("Jarvis runtime paths must not be redirected.".into()),
            Err(error) if error.kind() != ErrorKind::NotFound => return Err(error.to_string()),
            _ => {}
        }
    }
    Ok(RuntimeLayout { resources, runtime, installed: true })
}

#[derive(Clone, Deserialize, Serialize)]
pub struct MissingPrerequisite {
    pub code: String,
    pub message: String,
}

#[derive(Clone, Deserialize, Serialize)]
pub struct Preflight {
    pub ready: bool,
    pub missing: Vec<MissingPrerequisite>,
    pub python_executable: PathBuf,
    pub runtime_active: bool,
}

pub fn preflight(layout: &RuntimeLayout) -> Result<Preflight, String> {
    let root = &layout.resources;
    let script = root.join("scripts/jarvis_bootstrap.py");
    if !script.is_file() {
        return Err("The Jarvis bootstrap resource is missing.".into());
    }
    let mut last_error = String::from("Python 3.10 or newer could not be launched.");
    // Reuse the prepared interpreter first; fall back to system Python for setup.
    let candidates = [
        (layout.python(), &[][..]),
        (PathBuf::from("python.exe"), &[][..]),
        (PathBuf::from("py.exe"), &["-3"][..]),
    ];
    for (program, launcher_args) in candidates {
        let output = Command::new(program)
            .args(launcher_args)
            .arg("-I").arg("-B").arg(&script).arg("--preflight-json")
            .current_dir(root).env_clear().envs(layout.environment())
            .creation_flags(CREATE_NO_WINDOW.0)
            .output();
        let Ok(output) = output else { continue };
        if !output.status.success() {
            last_error = String::from_utf8_lossy(&output.stderr).trim().to_string();
            continue;
        }
        if output.stdout.len() > 65536 {
            return Err("The preflight response exceeded the desktop size limit.".into());
        }
        let report: Preflight = serde_json::from_slice(&output.stdout)
            .map_err(|_| "The bootstrap returned invalid preflight data.".to_string())?;
        if report.missing.iter().any(|item| item.code == "python") {
            last_error = report.missing.iter().find(|item| item.code == "python")
                .map(|item| item.message.clone()).unwrap_or_default();
            continue;
        }
        return Ok(report);
    }
    Err(format!("{last_error} Install Python 3.10 or newer, then retry."))
}
pub fn connect(app: &tauri::AppHandle) -> Result<Option<OwnedLauncher>, String> {
    let client = client()?;
    if matches!(health(&client)?, HealthState::Ready) { return Ok(None); }
    let owned = OwnedLauncher::spawn(&resolve_layout(app)?)?;
    let deadline = Instant::now() + Duration::from_secs(35);
    loop {
        match health(&client)? {
            HealthState::Ready => {
                if owned.owns_listener()? { return Ok(Some(owned)); }
                // Another instance won startup. Drop only our job; the adapter
                // never configures the winner. Recheck before calling it reused.
                drop(owned);
                return match health(&client)? {
                    HealthState::Ready => Ok(None),
                    HealthState::Absent => Err("Jarvis exited during startup. Retry startup.".into()),
                };
            }
            HealthState::Absent => {}
        }
        if !owned.running() {
            return Err("The Jarvis launcher exited before readiness. Prepare or repair the local environment with the existing launcher, then retry.".into());
        }
        if Instant::now() >= deadline {
            return Err("Jarvis did not become ready within 35 seconds. The desktop-owned launcher was stopped. Retry startup.".into());
        }
        thread::sleep(Duration::from_millis(400));
    }
}
