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
    pub local_data: PathBuf,
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
    let local_data = app.path().local_data_dir().map_err(|e| e.to_string())?;
    let executable = std::env::current_exe().map_err(|e| e.to_string())?;
    for ancestor in executable.ancestors().skip(1) {
        if ancestor.join(".git").exists()
            && ancestor.join("apps/desktop/src-tauri/Cargo.toml").is_file()
            && valid_resources(ancestor)
        {
            return Ok(RuntimeLayout {
                resources: ancestor.to_path_buf(), runtime: ancestor.to_path_buf(), installed: false,
                local_data,
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
    Ok(RuntimeLayout { resources, runtime, installed: true, local_data })
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

fn path_executables(name: &str) -> Vec<PathBuf> {
    std::env::var_os("PATH").map(|path| {
        std::env::split_paths(&path).filter(|directory| directory.is_absolute())
            .map(|directory| directory.join(name)).collect()
    }).unwrap_or_default()
}

fn python_candidates(layout: &RuntimeLayout) -> Vec<(PathBuf, bool)> {
    let mut candidates = vec![(layout.python(), false)];
    candidates.extend(path_executables("python.exe").into_iter().map(|path| (path, false)));
    candidates.extend(path_executables("py.exe").into_iter().map(|path| (path, true)));
    // Winget's current-user Python install is discoverable immediately, even
    // though this desktop process still has the PATH from before installation.
    let user_python = layout.local_data.join("Programs/Python");
    candidates.push((user_python.join("Python312/python.exe"), false));
    candidates.push((user_python.join("Launcher/py.exe"), true));
    if let Some(windows) = std::env::var_os("SystemRoot").map(PathBuf::from).filter(|path| path.is_absolute()) {
        candidates.push((windows.join("py.exe"), true));
    }
    // Also reuse runtimes already installed by Python Install Manager directly,
    // without invoking its WindowsApps aliases.
    let mut roots = vec![user_python, layout.local_data.join("Python")];
    for variable in ["ProgramFiles", "ProgramFiles(x86)"] {
        if let Some(path) = std::env::var_os(variable).map(PathBuf::from).filter(|path| path.is_absolute()) {
            roots.push(path);
        }
    }
    // Only immediate, conventionally named Python installation directories.
    for root in roots {
        if let Ok(entries) = std::fs::read_dir(root) {
            let mut paths: Vec<_> = entries.flatten()
                .filter(|entry| entry.file_name().to_string_lossy().to_ascii_lowercase().starts_with("python"))
                .map(|entry| entry.path().join("python.exe")).collect();
            paths.sort();
            candidates.extend(paths.into_iter().map(|path| (path, false)));
        }
    }
    candidates
}

fn find_python(layout: &RuntimeLayout) -> Option<PathBuf> {
    let mut seen = std::collections::HashSet::new();
    for (program, launcher) in python_candidates(layout) {
        if !program.is_absolute() || !program.is_file() || !seen.insert(program.clone()) {
            continue;
        }
        // Do not invoke Store aliases or Python Install Manager: inspection must
        // never open the Store or trigger automatic runtime installation.
        if program.components().any(|part| part.as_os_str().to_string_lossy().eq_ignore_ascii_case("WindowsApps")) {
            continue;
        }
        let mut command = Command::new(&program);
        if launcher { command.arg("-3"); }
        // Probe the version before loading bootstrap, which needs Python 3.10+.
        // -S also prevents site customizations during this discovery probe.
        let output = command.args(["-I", "-S", "-B", "-c",
            "import json, sys; sys.exit(3) if sys.version_info < (3, 10) else print(json.dumps(sys.executable))"])
            .current_dir(&layout.resources).env_clear().envs(layout.environment())
            .env_remove("PYLAUNCHER_ALLOW_INSTALL").env_remove("PYLAUNCHER_ALWAYS_INSTALL")
            .env("PYTHON_MANAGER_AUTOMATIC_INSTALL", "false")
            .creation_flags(CREATE_NO_WINDOW.0).output();
        let Ok(output) = output else { continue };
        if !output.status.success() || output.stdout.len() > 32768 { continue; }
        if let Ok(path) = serde_json::from_slice::<PathBuf>(&output.stdout) {
            if path.is_absolute() && path.is_file() { return Some(path); }
        }
    }
    None
}

pub fn winget(layout: &RuntimeLayout) -> Result<PathBuf, String> {
    let mut candidates = vec![layout.local_data.join("Microsoft/WindowsApps/winget.exe")];
    candidates.extend(path_executables("winget.exe"));
    candidates.into_iter().find(|path| path.is_absolute() && path.is_file()).ok_or_else(||
        "Python is missing and Windows Package Manager (winget) is unavailable. Install or update Microsoft's App Installer, then click Prepare Jarvis again; alternatively install Python 3.10+ for your user and click Check again. Jarvis will not use a fallback download URL.".into())
}

pub fn preflight(layout: &RuntimeLayout) -> Result<Preflight, String> {
    let root = &layout.resources;
    let script = root.join("scripts/jarvis_bootstrap.py");
    if !script.is_file() {
        return Err("The Jarvis bootstrap resource is missing.".into());
    }
    let Some(python) = find_python(layout) else {
        return Ok(Preflight {
            ready: false, python_executable: PathBuf::new(), runtime_active: false,
            missing: vec![MissingPrerequisite {
                code: "python".into(),
                message: "Compatible Python 3.10+ was not found. Click Prepare Jarvis to install Python 3.12 for your Windows user with Windows Package Manager. Remaining prerequisites will be checked after Python is available.".into(),
            }],
        });
    };
    let output = Command::new(&python)
        .arg("-I").arg("-B").arg(&script).arg("--preflight-json")
        .current_dir(root).env_clear().envs(layout.environment())
        .creation_flags(CREATE_NO_WINDOW.0).output()
        .map_err(|e| format!("Could not inspect prerequisites with the detected Python: {e}"))?;
    if !output.status.success() {
        return Err(format!("Python was found, but prerequisite inspection failed: {}",
            String::from_utf8_lossy(&output.stderr).trim()));
    }
    if output.stdout.len() > 65536 {
        return Err("The preflight response exceeded the desktop size limit.".into());
    }
    let mut report: Preflight = serde_json::from_slice(&output.stdout)
        .map_err(|_| "The bootstrap returned invalid preflight data.".to_string())?;
    // Use only the interpreter verified by discovery for subsequent processes.
    report.python_executable = python;
    Ok(report)
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
