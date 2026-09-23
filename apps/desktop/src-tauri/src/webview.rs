use std::{io::Read, sync::mpsc, time::Duration};
use tauri::{webview::NewWindowResponse, AppHandle, Manager, WebviewUrl, WebviewWindow, WebviewWindowBuilder};
use webview2_com::{Microsoft::Web::WebView2::Win32::*, PermissionRequestedEventHandler, WebResourceRequestedEventHandler};
use windows::{core::{w, HSTRING, Interface, PWSTR}, Win32::{System::Com::CoTaskMemFree, UI::Shell::SHCreateMemStream}};
use crate::runtime;

// Set on every remote document response before the browser parses any content.
// Inline scripts/styles are required by the existing server-rendered assistant.
const CSP: &str = "default-src 'none'; script-src http://127.0.0.1:8000 'unsafe-inline'; style-src http://127.0.0.1:8000 'unsafe-inline'; connect-src http://127.0.0.1:8000; img-src http://127.0.0.1:8000 data:; font-src http://127.0.0.1:8000; media-src http://127.0.0.1:8000; form-action http://127.0.0.1:8000; base-uri 'none'; object-src 'none'; frame-src 'none'; worker-src 'none'";
const BROWSER_ARGS: &str = "--no-proxy-server --disable-background-networking --disable-component-update --disable-domain-reliability --disable-sync --no-pings --disable-features=msWebOOUI,msPdfOOUI,msSmartScreenProtection";

pub fn shell_url(url: &tauri::Url) -> bool {
    url.scheme() == "http" && url.host_str() == Some("tauri.localhost")
        && url.port().is_none() && url.username().is_empty() && url.password().is_none()
        && matches!(url.path(), "/" | "/index.html")
}

pub fn startup(app: &AppHandle) -> tauri::Result<WebviewWindow> {
    WebviewWindowBuilder::new(app, "startup", WebviewUrl::App("index.html".into()))
        .title("Jarvis PC Local").inner_size(800.0, 520.0).min_inner_size(520.0, 360.0)
        .incognito(true).devtools(false).general_autofill_enabled(false)
        .additional_browser_args(BROWSER_ARGS)
        .on_navigation(shell_url).on_new_window(|_, _| NewWindowResponse::Deny)
        .on_download(|_, _| false).build()
}

fn document(client: &reqwest::blocking::Client, url: &tauri::Url) -> Result<Vec<u8>, String> {
    if !runtime::allowed_url(url) { return Err("Navigation outside Jarvis was blocked.".into()); }
    if !matches!(runtime::health(client)?, runtime::HealthState::Ready) {
        return Err("Jarvis is no longer ready. Close the desktop and retry.".into());
    }
    let response = client.get(url.clone()).send().map_err(|e| e.to_string())?;
    if response.status() != reqwest::StatusCode::OK {
        return Err("Jarvis did not return the requested page. Redirects are disabled.".into());
    }
    if !response.headers().get(reqwest::header::CONTENT_TYPE).and_then(|v| v.to_str().ok())
        .is_some_and(|v| v.split(';').next() == Some("text/html")) {
        return Err("Jarvis returned an unexpected page type.".into());
    }
    let mut body = Vec::new();
    response.take(8 * 1024 * 1024 + 1).read_to_end(&mut body).map_err(|e| e.to_string())?;
    if body.len() > 8 * 1024 * 1024 { return Err("The Jarvis page exceeded the desktop size limit.".into()); }
    Ok(body)
}

pub fn assistant(app: &AppHandle) -> Result<(), String> {
    // Fetch before creating the remote view so a failed first page uses Retry.
    let client = runtime::client()?;
    let initial = document(&client, &runtime::ASSISTANT.parse().unwrap())?;
    let window = WebviewWindowBuilder::new(app, "assistant", WebviewUrl::App("blank.html".into()))
        .title("Jarvis PC Local").inner_size(1280.0, 860.0).min_inner_size(800.0, 600.0)
        .visible(false).incognito(true).devtools(false).general_autofill_enabled(false)
        .additional_browser_args(BROWSER_ARGS)
        .on_navigation(|url| runtime::allowed_url(url)
            || (url.as_str() == "http://tauri.localhost/blank.html"))
        .on_new_window(|_, _| NewWindowResponse::Deny)
        .on_download(|_, _| false)
        .build().map_err(|e| e.to_string())?;
    let result = (|| {
        let (sender, receiver) = mpsc::sync_channel(1);
        window.with_webview(move |platform| {
            let result = unsafe { install_guard(platform, client, initial) }.map_err(|e| e.to_string());
            let _ = sender.send(result);
        }).map_err(|e| e.to_string())?;
        receiver.recv_timeout(Duration::from_secs(10))
            .map_err(|_| "The local-only WebView guard could not be initialized.".to_string())??;
        window.navigate(runtime::ASSISTANT.parse().unwrap()).map_err(|e| e.to_string())?;
        window.show().map_err(|e| e.to_string())?;
        window.set_focus().map_err(|e| e.to_string())?;
        if let Some(startup) = app.get_webview_window("startup") {
            startup.hide().map_err(|e| e.to_string())?;
        }
        Ok(())
    })();
    if result.is_err() { let _ = window.destroy(); }
    result
}

unsafe fn install_guard(
    platform: tauri::webview::PlatformWebview,
    client: reqwest::blocking::Client,
    initial: Vec<u8>,
) -> windows::core::Result<()> {
    let view = platform.controller().CoreWebView2()?;
    let environment = platform.environment();
    let settings = view.Settings()?;
    settings.SetAreDefaultContextMenusEnabled(false)?;
    settings.SetAreDevToolsEnabled(false)?;
    settings.SetIsStatusBarEnabled(false)?;
    settings.cast::<ICoreWebView2Settings3>()?.SetAreBrowserAcceleratorKeysEnabled(false)?;
    let settings4 = settings.cast::<ICoreWebView2Settings4>()?;
    settings4.SetIsPasswordAutosaveEnabled(false)?;
    settings4.SetIsGeneralAutofillEnabled(false)?;
    let mut token = 0;
    view.add_PermissionRequested(&PermissionRequestedEventHandler::create(Box::new(|_, args| {
        if let Some(args) = args { args.SetState(COREWEBVIEW2_PERMISSION_STATE_DENY)?; }
        Ok(())
    })), &mut token)?;
    // Require the filter covering document, frame and worker request sources.
    // If WebView2 is too old, initialization fails before remote navigation.
    view.cast::<ICoreWebView2_22>()?.AddWebResourceRequestedFilterWithRequestSourceKinds(
        w!("*"), COREWEBVIEW2_WEB_RESOURCE_CONTEXT_ALL, COREWEBVIEW2_WEB_RESOURCE_REQUEST_SOURCE_KINDS_ALL,
    )?;
    let mut initial = Some(initial);
    view.add_WebResourceRequested(&WebResourceRequestedEventHandler::create(Box::new(move |_, args| {
        let Some(args) = args else { return Ok(()) };
        // Begin denied, including if subsequent COM parsing fails.
        let blocked = environment.CreateWebResourceResponse(None, 403, w!("Blocked"), w!("Content-Type: text/plain\r\nCache-Control: no-store"))?;
        args.SetResponse(&blocked)?;
        let request = args.Request()?;
        let mut raw = PWSTR::null();
        request.Uri(&mut raw)?;
        let uri = raw.to_string();
        CoTaskMemFree(Some(raw.0.cast()));
        let Ok(uri) = uri else { return Ok(()) };
        let Ok(url) = tauri::Url::parse(&uri) else { return Ok(()) };
        if !runtime::allowed_url(&url) { return Ok(()) }
        let mut context = COREWEBVIEW2_WEB_RESOURCE_CONTEXT::default();
        args.ResourceContext(&mut context)?;
        if context == COREWEBVIEW2_WEB_RESOURCE_CONTEXT_DOCUMENT {
            let content = if url.as_str() == runtime::ASSISTANT && initial.is_some() {
                Ok(initial.take().unwrap())
            } else { document(&client, &url) };
            let (status, body) = match content {
                Ok(body) => (200, body),
                Err(_) => (503, b"<!doctype html><title>Jarvis unavailable</title><p>Jarvis is unavailable or navigation was blocked. Close the desktop and reopen it to retry.</p>".to_vec()),
            };
            let stream = SHCreateMemStream(Some(&body)).ok_or_else(windows::core::Error::from_win32)?;
            let headers = HSTRING::from(format!("Content-Type: text/html; charset=utf-8\r\nCache-Control: no-store\r\nContent-Security-Policy: {CSP}\r\nPermissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()\r\nReferrer-Policy: no-referrer"));
            let response = environment.CreateWebResourceResponse(&stream, status, w!("Jarvis"), &headers)?;
            args.SetResponse(&response)?;
        } else {
            // Only this exact loopback origin can issue ordinary API/assets
            // requests. Redirect targets re-enter this same filter.
            args.SetResponse(None::<&ICoreWebView2WebResourceResponse>)?;
        }
        Ok(())
    })), &mut token)?;
    Ok(())
}
