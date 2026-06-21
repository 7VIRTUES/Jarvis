# Dashboard Accessibility And Keyboard Navigation

This dashboard polish adds client-side accessibility helpers without changing backend behavior.

## What It Adds

- A skip link to jump to Dashboard Home.
- Visible focus styling for links, buttons, inputs, selects, and textareas.
- Keyboard shortcuts:
  - `/` focuses dashboard section search.
  - `Escape` clears dashboard section search and filter.
  - `e` expands all sections when focus is not inside a typing control.
  - `c` collapses all sections when focus is not inside a typing control.
- Shortcut help text near Dashboard Home.

## Boundaries

- No backend endpoint is added.
- No existing dashboard section, safety note, or control is removed.
- No new action capability is added.
- Existing dashboard/LAN access behavior is unchanged.
