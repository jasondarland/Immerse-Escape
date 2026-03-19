from __future__ import annotations

from immerse_simulator.engine.media_simulator import MediaSimulator
from immerse_simulator.engine.node_simulator import NodeSimulatorManager
from immerse_simulator.models.events import Event


class OutputDispatcher:
    def __init__(self, media: MediaSimulator, nodes: NodeSimulatorManager, event_callback) -> None:
        self.media = media
        self.nodes = nodes
        self.event_callback = event_callback
        self.active_outputs: list[str] = []

    def dispatch(self, target: str, action: str, payload: dict[str, object] | None = None) -> None:
        payload = payload or {}
        description = f"{target}:{action}"
        if description not in self.active_outputs:
            self.active_outputs.append(description)
        if target == "audio":
            if action == "play":
                self.media.play_audio(str(payload.get("asset_id", "audio.asset")))
            elif action == "stop":
                self.media.stop_audio()
        elif target == "video":
            if action == "play":
                self.media.play_video(str(payload.get("asset_id", "video.asset")))
            elif action == "stop":
                self.media.stop_video()
        self.event_callback(Event(source="OutputDispatcher", event_type="output", message=f"Dispatched {description}", payload=payload))
