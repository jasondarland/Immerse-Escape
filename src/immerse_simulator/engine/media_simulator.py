from __future__ import annotations


class MediaSimulator:
    def __init__(self) -> None:
        self.audio_state = {"asset_id": None, "status": "stopped", "elapsed": 0.0}
        self.video_state = {"asset_id": None, "status": "stopped", "elapsed": 0.0}

    def play_audio(self, asset_id: str) -> None:
        self.audio_state = {"asset_id": asset_id, "status": "playing", "elapsed": 0.0}

    def stop_audio(self) -> None:
        self.audio_state["status"] = "stopped"

    def play_video(self, asset_id: str) -> None:
        self.video_state = {"asset_id": asset_id, "status": "playing", "elapsed": 0.0}

    def stop_video(self) -> None:
        self.video_state["status"] = "stopped"

    def tick(self, seconds: float) -> None:
        for state in (self.audio_state, self.video_state):
            if state["status"] == "playing":
                state["elapsed"] += seconds
