# reSink

![Download the Latest Release Here](https://github.com/Retzilience/reSink/releases/latest)

reSink is a small PySide6 GUI for managing PipeWire/PulseAudio sinks with a bias toward **virtual (null) sinks**. It can create/destroy virtual sinks, set the system default output sink, and launch a patchbay graph UI (qpwgraph/Helvum/Patchance/custom, and aSyphon).

![reSink UI](https://github.com/Retzilience/reSink/raw/main/assets/ui.png)

## Features

- Create PipeWire null sinks (virtual sinks)
- Destroy selected virtual sinks (only virtual sinks are eligible)
- Set a sink as the system default output (via `wpctl`)
- List sinks via PulseAudio compatibility (`pipewire-pulse`) using `pulsectl`
- Launch a patchbay tool from one place:
  - qpwgraph / Helvum / Patchance
  - custom executable
  - ![aSyphon](https://github.com/Retzilience/aSyphon)
- Help/About dialog with diagnostics and update checking

## Runtime notes

reSink targets Linux systems running PipeWire (including `pipewire-pulse`). If your desktop audio is already working on PipeWire, you are almost certainly fine.

Two system tools are used for the actual “do the thing” operations:
- Creating/destroying virtual sinks uses `pw-cli`
- Setting the default output uses `wpctl`

If either tool is missing, reSink will still open and list sinks, but the related action will fail.

## License

CC BY-NC-SA 4.0 (Attribution required; noncommercial only; derivatives must use the same license).
