# source/ui_help_content.py
from __future__ import annotations

from rehelp import wrap_help_html


def help_html(app_name: str) -> str:
    return wrap_help_html(
        f"{app_name} — Help / About",
        """
        <p class="muted">
          reSink manages PipeWire/Pulse sinks with a focus on virtual (null) sinks.
          I can create and destroy virtual sinks, set a sink as the default output, and
          launch a patchbay tool (qpwgraph/Helvum/Patchance/custom).
        </p>

        <h2>What reSink is</h2>
        <ul>
          <li><b>Virtual sink manager</b>: create and tear down null sinks.</li>
          <li><b>Default sink helper</b>: set the system default output sink.</li>
          <li><b>Patchbay launcher</b>: open your chosen graph UI from one place.</li>
        </ul>

        <h2>How selection works</h2>
        <ul>
          <li>Only <b>virtual sinks</b> can be selected for destructive operations.</li>
          <li><b>Destroy selected</b> removes the selected virtual sinks.</li>
          <li><b>Make default</b> requires exactly one selection.</li>
        </ul>

        <h2>Patchbay</h2>
        <ul>
          <li>Configure a patchbay app in <b>Patchbay settings</b>.</li>
          <li>reSink can launch qpwgraph/Helvum/Patchance or a custom executable.</li>
        </ul>

        <h2>Troubleshooting</h2>
        <ul>
          <li><b>Can’t create/destroy</b>: ensure <code>pw-cli</code> exists in PATH.</li>
          <li><b>Can’t set default</b>: ensure <code>wpctl</code> exists in PATH.</li>
          <li><b>No sinks shown</b>: ensure <code>pipewire-pulse</code> is running.</li>
        </ul>

        <h2>Support</h2>
        <p class="muted">
          Use the buttons below to open the repository, releases, or file a bug report.
          Include “Copy diagnostics” output when reporting issues.
        </p>
        """,
    )
