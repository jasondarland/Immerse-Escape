from __future__ import annotations

from pathlib import Path
import random
import logging

from PySide6.QtCore import QObject, QTimer, Signal

from immerse_runtime.models.entities import RuntimeStatus, Severity
from immerse_runtime.services.alert_manager import AlertManager
from immerse_runtime.services.device_registry import DeviceRegistry
from immerse_runtime.services.event_bus import EventBus
from immerse_runtime.services.event_logger import EventLogger
from immerse_runtime.services.logic_engine import LogicEngine
from immerse_runtime.services.node_manager import NodeManager
from immerse_runtime.services.output_dispatcher import OutputDispatcher
from immerse_runtime.services.package_loader import PackageLoader
from immerse_runtime.services.session_manager import SessionManager
from immerse_runtime.services.state_manager import StateManager


class RuntimeService(QObject):
    updated = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger("immerse_runtime.runtime")
        self.status = RuntimeStatus.IDLE
        self.package_loader = PackageLoader()
        self.event_bus = EventBus()
        self.device_registry = DeviceRegistry()
        self.node_manager = NodeManager()
        self.state_manager = StateManager()
        self.event_logger = EventLogger()
        self.alert_manager = AlertManager()
        self.output_dispatcher = OutputDispatcher()
        self.session_manager = SessionManager()
        self.logic_engine = LogicEngine(
            self.state_manager,
            self.output_dispatcher,
            self.event_logger,
            self.alert_manager,
            self.device_registry,
        )
        self.current_package = None
        self._timer = QTimer()
        self._timer.timeout.connect(self.simulation_tick)
        self._timer.start(1000)

    def load_package(self, package_path: str | Path) -> None:
        self.logger.info("Loading runtime package from %s", package_path)
        self.current_package = self.package_loader.load(package_path)
        self.device_registry.load(self.current_package.devices)
        self.node_manager.load(self.current_package.project)
        self.state_manager.load(self.current_package.states)
        self.logic_engine.load(self.current_package.logic_graph)
        self.logger.info("Loaded package %s with %s devices and %s nodes", self.current_package.name, len(self.current_package.devices), len(self.current_package.project.get("nodes", [])))
        self.event_logger.log(Severity.INFO, "runtime", "package_loader", "package", f"Loaded package {self.current_package.name}")
        self.updated.emit()

    def start_session(self, room: str = "Atrium", preset: str = "Standard") -> None:
        self.logger.info("Starting session for room=%s preset=%s", room, preset)
        self.session_manager.start(room, preset)
        self.status = RuntimeStatus.RUNNING
        self.event_logger.log(Severity.INFO, room, "session", "session", "Session started")
        self.updated.emit()

    def pause_session(self) -> None:
        self.logger.info("Pausing session %s", self.session_manager.current.id)
        self.session_manager.pause()
        self.status = RuntimeStatus.PAUSED
        self.event_logger.log(Severity.WARNING, self.session_manager.current.room, "session", "session", "Session paused")
        self.updated.emit()

    def resume_session(self) -> None:
        self.logger.info("Resuming session %s", self.session_manager.current.id)
        self.session_manager.resume()
        self.status = RuntimeStatus.RUNNING
        self.event_logger.log(Severity.INFO, self.session_manager.current.room, "session", "session", "Session resumed")
        self.updated.emit()

    def stop_session(self) -> None:
        self.logger.info("Stopping session %s", self.session_manager.current.id)
        self.session_manager.stop()
        self.status = RuntimeStatus.STOPPED
        self.event_logger.log(Severity.WARNING, self.session_manager.current.room, "session", "session", "Session stopped")
        self.updated.emit()

    def reset_room(self, full: bool = False) -> None:
        self.logger.warning("Reset requested full=%s", full)
        self.state_manager.reset()
        self.session_manager.reset()
        self.logger.warning("Stop all outputs requested")
        self.output_dispatcher.stop_all()
        self.status = RuntimeStatus.RESET_NEEDED if not full else RuntimeStatus.IDLE
        self.event_logger.log(Severity.WARNING, self.session_manager.current.room, "runtime", "reset", "Full reset" if full else "Room reset")
        self.updated.emit()

    def emergency_unlock(self) -> None:
        self.logger.critical("Emergency unlock activated")
        self.status = RuntimeStatus.EMERGENCY
        for device in self.device_registry.devices.values():
            if "lock" in device.type:
                self.device_registry.update_state(device.id, "unlocked", "online")
        self.alert_manager.create(Severity.CRITICAL, "runtime", "Emergency unlock activated")
        self.event_logger.log(Severity.CRITICAL, "runtime", "runtime", "emergency", "Emergency unlock executed")
        self.updated.emit()

    def acknowledge_latest_alert(self) -> None:
        active = self.alert_manager.active()
        if active:
            self.alert_manager.acknowledge(active[-1].id, "Acknowledged by operator")
            self.updated.emit()

    def stop_all_outputs(self) -> None:
        self.logger.warning("Stop all outputs requested")
        self.output_dispatcher.stop_all()
        self.event_logger.log(Severity.WARNING, self.session_manager.current.room, "runtime", "outputs", "Stopped all outputs")
        self.updated.emit()

    def manual_trigger(self, trigger: str) -> None:
        room = self.session_manager.current.room if self.session_manager.current.room != "Unassigned" else "Atrium"
        self.logger.info("Manual trigger received: %s for room=%s", trigger, room)
        self.logic_engine.process_trigger(trigger, room)
        self.updated.emit()

    def simulation_tick(self) -> None:
        self.node_manager.heartbeat()
        session = self.session_manager.current
        if session.state == "running":
            session.elapsed_seconds += 1
            solved = sum(1 for value in self.state_manager.state.get("variables", {}).values() if value is True)
            session.solved_puzzles = solved
            session.active_puzzles = max(0, 5 - solved)
            if random.random() > 0.985:
                self.alert_manager.create(Severity.WARNING, "node-heartbeat", "Transient node latency detected")
        self.updated.emit()
