use std::{io::{ErrorKind, Read}, net::{SocketAddr, TcpStream}, os::windows::process::CommandExt, path::PathBuf, process::Command, thread, time::{Duration, Instant}};
use reqwest::blocking::Client;
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

pub fn repository_root() -> Result<PathBuf, String> {
    // Repository-run foundation: no user-supplied executable or URL, registry,
    // private configuration, or alternate bootstrap. Preflight uses only fixed
    // Python launcher names; preparation uses the interpreter path they report.
    let executable = std::env::current_exe().map_err(|e| e.to_string())?;
    for ancestor in executable.ancestors().skip(1) {
        if ancestor.join("apps/desktop/launcher_adapter.py").is_file()
            && ancestor.join("scripts/jarvis_launcher.py").is_file()
            && ancestor.join("services/jarvis-core/src/jarvis_core/app.py").is_file()
        {
            return Ok(ancestor.to_path_buf());
        }
    }
    Err("Run the desktop executable from its build directory inside the Jarvis repository.".into())
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

pub fn preflight(root: &std::path::Path) -> Result<Preflight, String> {
    let script = root.join("scripts/jarvis_bootstrap.py");
    if !script.is_file() {
        return Err("The repository bootstrap script is missing.".into());
    }
    let mut last_error = String::from("Python 3.10 or newer could not be launched.");
    for (program, launcher_args) in [("python.exe", &[][..]), ("py.exe", &["-3"][..])] {
        let output = Command::new(program)
            .args(launcher_args)
            .arg("-I").arg("-B").arg(&script).arg("--preflight-json")
            .current_dir(root).creation_flags(CREATE_NO_WINDOW.0)
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
pub fn connect() -> Result<Option<OwnedLauncher>, String> {
    let client = client()?;
    if matches!(health(&client)?, HealthState::Ready) { return Ok(None); }
    let owned = OwnedLauncher::spawn(&repository_root()?)?;
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
