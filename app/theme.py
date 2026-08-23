from nicegui import ui


def apply_app_theme() -> None:
    ui.add_head_html(
        """
        <script>
          window.casaTheme = {
            apply() {
              const saved = localStorage.getItem('casa-theme') || 'light';
              const isDark = saved === 'dark';
              if (window.Quasar) Quasar.Dark.set(isDark);
              document.documentElement.dataset.theme = saved;
            },
            toggle() {
              const current = localStorage.getItem('casa-theme') || 'light';
              localStorage.setItem('casa-theme', current === 'dark' ? 'light' : 'dark');
              window.casaTheme.apply();
            }
          };
          window.casaTheme.apply();
        </script>
        <style>
          :root {
            --casa-bg: #f6f7f9;
            --casa-surface: #ffffff;
            --casa-surface-soft: #eef2f5;
            --casa-border: #d9e0e7;
            --casa-text: #1d2733;
            --casa-muted: #667085;
            --casa-accent: #1976d2;
            --casa-accent-soft: #e8f2ff;
          }

          html[data-theme="dark"] {
            --casa-bg: #0f141b;
            --casa-surface: #1b222b;
            --casa-surface-soft: #26303b;
            --casa-border: #465260;
            --casa-text: #f3f6fa;
            --casa-muted: #c2cad6;
            --casa-accent: #7cc4ff;
            --casa-accent-soft: #19364d;
          }

          body {
            background: var(--casa-bg);
            color: var(--casa-text);
          }

          .casa-header {
            background: color-mix(in srgb, var(--casa-surface) 92%, transparent);
            color: var(--casa-text);
            border-bottom: 1px solid var(--casa-border);
            backdrop-filter: blur(14px);
          }

          .casa-nav {
            background: var(--casa-surface-soft);
            border: 1px solid var(--casa-border);
            border-radius: 8px;
            padding: 3px;
          }

          .casa-nav .q-btn {
            border-radius: 6px;
            min-height: 34px;
            color: var(--casa-muted);
          }

          .casa-nav .is-active {
            background: var(--casa-surface);
            color: var(--casa-accent);
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.14);
          }

          .casa-card {
            background: var(--casa-surface);
            color: var(--casa-text);
            border: 1px solid var(--casa-border);
            border-radius: 8px;
            box-shadow: none;
          }

          .casa-muted {
            color: var(--casa-muted);
          }

          .casa-page-title {
            color: var(--casa-text);
            letter-spacing: 0;
          }

          .casa-filter {
            background: var(--casa-surface);
            color: var(--casa-text);
            border: 1px solid var(--casa-border);
            border-radius: 8px;
            padding: 10px 12px;
          }

          html[data-theme="dark"] .q-page,
          html[data-theme="dark"] .q-layout,
          html[data-theme="dark"] .q-drawer,
          html[data-theme="dark"] .q-menu,
          html[data-theme="dark"] .q-dialog__inner > div {
            background: var(--casa-bg);
            color: var(--casa-text);
          }

          html[data-theme="dark"] .q-card,
          html[data-theme="dark"] .q-menu,
          html[data-theme="dark"] .q-list,
          html[data-theme="dark"] .q-item {
            background: var(--casa-surface);
            color: var(--casa-text);
          }

          html[data-theme="dark"] .q-item.q-manual-focusable--focused,
          html[data-theme="dark"] .q-item--active,
          html[data-theme="dark"] .q-item:hover {
            background: var(--casa-surface-soft);
            color: var(--casa-text);
          }

          html[data-theme="dark"] .q-field,
          html[data-theme="dark"] .q-field__native,
          html[data-theme="dark"] .q-field__input,
          html[data-theme="dark"] .q-field__label,
          html[data-theme="dark"] .q-field__prefix,
          html[data-theme="dark"] .q-field__suffix,
          html[data-theme="dark"] .q-field__append,
          html[data-theme="dark"] .q-field__prepend {
            color: var(--casa-text);
          }

          html[data-theme="dark"] .q-field__label {
            color: var(--casa-muted);
          }

          html[data-theme="dark"] .q-field--focused .q-field__label,
          html[data-theme="dark"] .q-field--highlighted .q-field__label {
            color: var(--casa-accent);
          }

          html[data-theme="dark"] .q-field__control::before {
            border-color: var(--casa-border);
          }

          html[data-theme="dark"] .q-field__control::after {
            background: var(--casa-accent);
          }

          html[data-theme="dark"] .q-field__marginal,
          html[data-theme="dark"] .q-select__dropdown-icon {
            color: var(--casa-muted);
            opacity: 1;
          }

          html[data-theme="dark"] .q-btn--flat,
          html[data-theme="dark"] .q-btn--outline {
            color: var(--casa-accent);
          }

          html[data-theme="dark"] .q-btn--flat.text-grey-7,
          html[data-theme="dark"] .text-grey-7 {
            color: var(--casa-muted) !important;
          }

          html[data-theme="dark"] .text-blue-600,
          html[data-theme="dark"] .text-blue-700 {
            color: var(--casa-accent) !important;
          }

          html[data-theme="dark"] .border-b {
            border-color: var(--casa-border);
          }
        </style>
        """
    )


def page_container():
    return ui.column().classes("w-full max-w-4xl mx-auto p-4 gap-4")


def card_classes(extra: str = "") -> str:
    return f"casa-card {extra}".strip()
