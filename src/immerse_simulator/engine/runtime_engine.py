from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal

from immerse_simulator.engine.event_bus import EventBus
from immerse_simulator.engine.logic_engine import LogicEngine
from immerse_simulator.engine.media_simulator import MediaSimulator
from immerse_simulator.engine.node_simulator import NodeSimulatorManager
from immerse_simulator.engine.output_dispatcher import OutputDispatcher
from immerse_simulator.engine.occ_controller import OCCController
from immerse_simulator.engine.package_loader import PackageLoader
from immerse_simulator.engine.session_manager import SessionManager
from immerse_simulator.engine.state_manager import StateManager
from immerse_simulator.models.events import Event
from immerse_simulator.models.package import ShowPackage


class RuntimeEngine(QObject):
    package_loaded = Signal()
    state_changed = Signal()
    nodes_changed = Signal()
    timeline_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.event_bus = EventBus()
        self.loader = PackageLoader()
        self.state_manager = StateManager()
        self.session = SessionManager()
        self.media = MediaSimulator()
        self.nodes = NodeSimulatorManager()
        self.logic = LogicEngine()
        self.dispatcher = OutputDispatcher(self.media, self.nodes, self.event_bus.emit_event)
        self.occ = OCCController(self.event_bus.emit_event)
        self.package: ShowPackage | None = None
        self.active_room = "Lab A"
        self.current_room_mode = "standby"
        self.active_alerts: list[str] = []
        self.room_backgrounds: dict[str, str] = {}
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def load_package(self, source: str) -> None:
        self.package = self.loader.load(source)
        self.logic.bind_package(self.package)
        self.state_manager = StateManager()
        self.state_manager.bulk_load(self.package.states)
        self.nodes.load_devices(self.package.devices)
        self.active_room = self.package.rooms[0]["name"] if self.package.rooms else "Global"
        self.room_backgrounds = {room.get("name", "Unnamed Room"): room.get("background_image", "") for room in self.package.rooms}
        self.event_bus.emit_event(Event(source="PackageLoader", event_type="package", message=f"Loaded package {self.package.name}"))
        self.package_loaded.emit()
        self.state_changed.emit()
        self.nodes_changed.emit()
        self.timeline_changed.emit()


    def set_room_background(self, room: str, image_path: str | None) -> None:
        if not room:
            return
        self.room_backgrounds[room] = image_path or ""
        action = image_path if image_path else "cleared"
        self.event_bus.emit_event(Event(source="RoomView", event_type="background", message=f"Background for {room}: {action}", room=room))
        self.state_changed.emit()

    def get_room_background(self, room: str) -> str:
        return self.room_backgrounds.get(room, "")

    def start_session(self) -> None:
        self.session.start()
        self.current_room_mode = "live"
        self.dispatcher.dispatch("audio", "play", {"asset_id": "intro_audio"})
        self.dispatcher.dispatch("video", "play", {"asset_id": "briefing_video"})
        self.event_bus.emit_event(Event(source="Runtime", event_type="session", message="Session started"))
        self.state_changed.emit()

    def pause_session(self) -> None:
        self.session.pause()
        self.event_bus.emit_event(Event(source="Runtime", event_type="session", message="Session paused", severity="warning"))
        self.state_changed.emit()

    def stop_session(self) -> None:
        self.session.stop()
        self.dispatcher.dispatch("audio", "stop")
        self.dispatcher.dispatch("video", "stop")
        self.event_bus.emit_event(Event(source="Runtime", event_type="session", message="Session stopped"))
        self.state_changed.emit()

    def reset_room(self) -> None:
        if not self.package:
            return
        for puzzle in self.package.puzzles:
            puzzle.solved = False
        for device in self.package.devices:
            device.state = device.metadata.get("default_state", "idle")
        self.state_manager.bulk_load(self.package.states)
        self.event_bus.emit_event(Event(source="Runtime", event_type="reset", message="Room reset"))
        self.state_changed.emit()
        self.nodes_changed.emit()

    def handle_input(self, action: str, value: str, room: str = "Global") -> None:
        self.event_bus.emit_event(Event(source="PlayerInput", event_type="input", message=f"{action} => {value}", room=room))
        for result in self.logic.evaluate_input(action, value):
            self._apply_logic_result(result)
        self.state_changed.emit()
        self.nodes_changed.emit()
        self.timeline_changed.emit()

    def trigger_operator_action(self, action: str) -> None:
        self.occ.trigger(action, self.active_room)
        if action == "Emergency Unlock All" and self.package:
            for device in self.package.devices:
                if device.kind == "lock":
                    device.state = "unlocked"
        elif action == "Trigger Finale":
            self.handle_input("sequence", "RGBY", room="Lab B")
        self.state_changed.emit()
        self.nodes_changed.emit()

    def _apply_logic_result(self, result: dict[str, object]) -> None:
        if not self.package:
            return
        result_type = result.get("type")
        if result_type == "puzzle_solved":
            puzzle_id = result["puzzle_id"]
            for puzzle in self.package.puzzles:
                if puzzle.puzzle_id == puzzle_id:
                    puzzle.solved = True
                    self.event_bus.emit_event(Event(source="LogicEngine", event_type="logic", message=f"Puzzle solved: {puzzle.name}", room=puzzle.room))
        elif result_type == "device_state":
            for device in self.package.devices:
                if device.device_id == result["device_id"]:
                    device.state = str(result["state"])
                    self.event_bus.emit_event(Event(source="LogicEngine", event_type="device", message=f"{device.name} => {device.state}", room=device.room))
        elif result_type == "state":
            self.state_manager.set_state(str(result["key"]), result["value"])
        elif result_type == "play_audio":
            self.dispatcher.dispatch("audio", "play", {"asset_id": result["asset_id"]})
        elif result_type == "play_video":
            self.dispatcher.dispatch("video", "play", {"asset_id": result["asset_id"]})
        elif result_type == "effect":
            for device in self.package.devices:
                if device.device_id == result["device_id"]:
                    device.state = str(result["state"])
                    self.dispatcher.active_outputs.append(f"fx:{device.device_id}:{device.state}")

    def _tick(self) -> None:
        self.session.tick(1.0)
        self.media.tick(1.0)
        self.nodes.heartbeat_tick()
        self.state_changed.emit()
        self.nodes_changed.emit()
        self.timeline_changed.emit()
