fn main() {
    let attributes = tauri_build::Attributes::new().app_manifest(
        tauri_build::AppManifest::new().commands(&["inspect_startup", "preparation_status", "prepare_jarvis", "start_jarvis"]),
    );
    tauri_build::try_build(attributes).expect("Could not prepare Jarvis desktop resources");
}
