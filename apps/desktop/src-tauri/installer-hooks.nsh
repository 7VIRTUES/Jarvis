; Keep Tauri's normal removal of installed files and application shortcuts.
; Its optional app-data cleanup recursively deletes local.jarvis.desktop,
; which owns Jarvis data, the prepared runtime, and Ollama models. Never allow
; that cleanup, even if selected in the standard uninstall confirmation page.
; This hook also runs for silent uninstall and uninstall during replacement.
!macro NSIS_HOOK_PREUNINSTALL
  StrCpy $DeleteAppDataCheckboxState 0
  DetailPrint "Preserving Jarvis user data, runtime, models, and user projects."
!macroend
