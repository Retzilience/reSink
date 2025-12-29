# reSink

reSink is a small PySide6 GUI for managing PipeWire/PulseAudio sinks with a bias toward **virtual (null) sinks**. It can create/destroy virtual sinks, set the system default output sink, and launch a patchbay graph UI (qpwgraph/Helvum/Patchance/custom, plus aSyphon via config handoff).

![reSink UI](https://github.com/Retzilience/reSink/raw/main/assets/ui.png)

## Features

- Create PipeWire null sinks (virtual sinks)
- Destroy selected virtual sinks (only virtual sinks are eligible)
- Set a sink as the system default output (via `wpctl`)
- List sinks via PulseAudio compatibility (`pipewire-pulse`) using `pulsectl`
- Launch a patchbay tool from one place:
  - qpwgraph / Helvum / Patchance
  - custom executable
  - aSyphon
- Help/About dialog with diagnostics and update checking (driven by `version.upd` in this repo)

## License

CC BY-NC-SA 4.0 (Attribution required; noncommercial only; derivatives must use the same license).
