# source/resink_backend.py
from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from typing import List, Optional

import pulsectl


@dataclass(frozen=True)
class SinkInfo:
    name: str
    description: str
    is_virtual: bool
    is_default: bool


def _run(cmd: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(cmd), capture_output=True, text=True)


def is_virtual_sink(sink: pulsectl.PulseSinkInfo) -> bool:
    """
    I treat the sink as virtual if it looks like a null sink or it lacks typical physical identifiers.
    """
    factory = (sink.proplist.get("factory.name", "") or "").lower()
    if "null-audio-sink" in factory:
        return True
    if "module-null-sink" in factory:
        return True

    mc = (sink.proplist.get("media.class", "") or "").lower()
    if mc == "audio/sink":
        physical_keys = ["alsa.card", "device.bus", "device.serial"]
        if not any(key in sink.proplist for key in physical_keys):
            return True
    return False


def suggest_resink_name() -> str:
    """
    I suggest the next free name in the sequence reSink, reSink-2, reSink-3, ...
    """
    base_name = "reSink"
    with pulsectl.Pulse("resink-manager") as pulse:
        sinks = pulse.sink_list()
        existing_names = {s.name for s in sinks}

    if base_name not in existing_names:
        return base_name

    i = 2
    while True:
        candidate = f"{base_name}-{i}"
        if candidate not in existing_names:
            return candidate
        i += 1


def get_sink_node_id_by_name(node_name: str) -> Optional[str]:
    """
    I resolve PipeWire node id by node.name using pw-cli list-objects output.
    """
    try:
        p = _run(["pw-cli", "list-objects"])
        if p.returncode != 0:
            return None

        lines = (p.stdout or "").splitlines()
        for i, line in enumerate(lines):
            if f'node.name = "{node_name}"' not in line:
                continue

            for prev in reversed(lines[:i]):
                s = prev.strip()
                if s.startswith("id"):
                    # Example: "id 56,"
                    parts = s.replace(",", " ").split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        return parts[1]
                    return None

    except FileNotFoundError:
        return None

    return None


def set_default_sink(node_name: str) -> None:
    """
    I set the default sink via wpctl set-default <node-id>.
    """
    sink_id = get_sink_node_id_by_name(node_name)
    if not sink_id:
        raise RuntimeError(f"Sink '{node_name}' not found (cannot set default).")

    try:
        p = _run(["wpctl", "set-default", sink_id])
    except FileNotFoundError as e:
        raise RuntimeError("wpctl not found in PATH.") from e

    if p.returncode != 0:
        msg = (p.stderr or p.stdout).strip()
        raise RuntimeError(f"Failed to set default sink: {msg}")


def create_virtual_sink(name: str, sample_rate: int) -> None:
    """
    I create a virtual sink via pw-cli create-node adapter {...}.
    """
    safe_name = name.replace('"', r"\"")
    props = (
        "{\n"
        "    factory.name=support.null-audio-sink\n"
        f'    node.name="{safe_name}"\n'
        "    media.class=Audio/Sink\n"
        "    object.linger=true\n"
        "    audio.position=[FL FR]\n"
        f"    audio.sample_rate={int(sample_rate)}\n"
        "}\n"
    )

    try:
        p = _run(["pw-cli", "create-node", "adapter", props])
    except FileNotFoundError as e:
        raise RuntimeError("pw-cli not found in PATH.") from e

    if p.returncode != 0:
        msg = (p.stderr or p.stdout).strip()
        raise RuntimeError(msg or "pw-cli create-node failed")


def wait_for_sink_to_appear(name: str, tries: int = 15, delay_s: float = 0.12) -> None:
    with pulsectl.Pulse("resink-manager") as pulse:
        for _ in range(max(1, tries)):
            sinks = pulse.sink_list()
            if any(s.name == name for s in sinks):
                return
            time.sleep(max(0.0, delay_s))
    raise RuntimeError(f"Sink '{name}' did not appear after creation.")


def destroy_sink_by_name(node_name: str) -> None:
    """
    I destroy a sink by node.name by resolving its node id and calling pw-cli destroy <id>.
    """
    sink_id = get_sink_node_id_by_name(node_name)
    if not sink_id:
        raise RuntimeError(f"Sink '{node_name}' not found (cannot destroy).")

    try:
        p = _run(["pw-cli", "destroy", sink_id])
    except FileNotFoundError as e:
        raise RuntimeError("pw-cli not found in PATH.") from e

    if p.returncode != 0:
        msg = (p.stderr or p.stdout).strip()
        raise RuntimeError(msg or f"Failed to destroy sink '{node_name}'.")


class ReSinkBackend:
    def __init__(self, pulse_client_name: str = "resink-gui") -> None:
        self._pulse_client_name = pulse_client_name

    def server_label(self) -> str:
        return "PipeWire (via pipewire-pulse)"

    def list_sinks(self) -> List[SinkInfo]:
        with pulsectl.Pulse(self._pulse_client_name) as pulse:
            server = pulse.server_info()
            default_name = (server.default_sink_name or "").strip()

            out: List[SinkInfo] = []
            for s in pulse.sink_list():
                v = is_virtual_sink(s)
                out.append(
                    SinkInfo(
                        name=s.name,
                        description=s.description or s.name,
                        is_virtual=v,
                        is_default=(s.name == default_name),
                    )
                )
            out.sort(key=lambda x: (not x.is_virtual, x.description.lower(), x.name.lower()))
            return out

    def can_spawn_patchbay(self) -> bool:
        return True

    def env_hint(self) -> str:
        return (os.environ.get("PIPEWIRE_REMOTE") or "").strip()
