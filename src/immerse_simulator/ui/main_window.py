from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QListWidget, QMainWindow, QMessageBox, QSplitter, QStackedWidget, QVBoxLayout, QWidget, QHBoxLayout

from immerse_simulator.engine.runtime_engine import RuntimeEngine
from immerse_simulator.models.events import Event
from immerse_simulator.ui.pages.dashboard import DashboardPage
from immerse_simulator.ui.pages.event_log import EventLogPage
from immerse_simulator.ui.pages.node_simulator import NodeSimulatorPage
from immerse_simulator.ui.pages.operator_controls import OperatorControlsPage
from immerse_simulator.ui.pages.package_loader import PackageLoaderPage
from immerse_simulator.ui.pages.player_inputs import PlayerInputsPage
from immerse_simulator.ui.pages.room_view import RoomViewPage
from immerse_simulator.ui.pages.runtime_state import RuntimeStatePage
from immerse_simulator.ui.pages.settings import SettingsPage
from immerse_simulator.ui.pages.timeline_monitor import TimelineMonitorPage


class MainWindow(QMainWindow):
    PAGE_ORDER = [
        "Dashboard",
        "Room View",
        "Player Inputs",
        "Runtime State",
        "Node Simulator",
        "Operator Controls",
        "Event Log",
        "Timeline / Cue Monitor",
        "Package Loader",
        "Settings",
    ]

    def __init__(self, demo_package_path: Path) -> None:
        super().__init__()
        self.setWindowTitle("IMMERSE Escape Simulator")
        self.resize(1600, 950)
        self.demo_package_path = demo_package_path
        self.engine = RuntimeEngine()
        self.event_log: list[Event] = []
        self._refresh_in_progress = False
        self.engine.event_bus.event_emitted.connect(self._on_event)
        self.engine.package_loaded.connect(self.refresh_all)
        self.engine.state_changed.connect(self.refresh_all)
        self.engine.nodes_changed.connect(self.refresh_all)
        self.engine.timeline_changed.connect(self.refresh_all)

        root = QWidget()
        root.setObjectName("simulatorRoot")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        top_bar = QWidget()
        top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 12, 16, 12)
        title_stack = QVBoxLayout()
        self.title_label = QLabel("IMMERSE Escape Simulator")
        self.title_label.setObjectName("appTitle")
        self.subtitle_label = QLabel("Local digital twin for runtime, OCC, node, device, and puzzle simulation")
        self.subtitle_label.setObjectName("appSubtitle")
        title_stack.addWidget(self.title_label)
        title_stack.addWidget(self.subtitle_label)
        self.session_badge = QLabel("Session: Stopped")
        self.session_badge.setObjectName("sessionBadge")
        self.session_badge.setAlignment(Qt.AlignCenter)
        top_layout.addLayout(title_stack, 1)
        top_layout.addWidget(self.session_badge)
        root_layout.addWidget(top_bar)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)
        self.nav = QListWidget()
        self.nav.setObjectName("navList")
        self.nav.addItems(self.PAGE_ORDER)
        self.nav.currentRowChanged.connect(self._set_page_index)
        self.stack = QStackedWidget()
        self.pages = {
            "Dashboard": DashboardPage(self),
            "Room View": RoomViewPage(self),
            "Player Inputs": PlayerInputsPage(self),
            "Runtime State": RuntimeStatePage(self),
            "Node Simulator": NodeSimulatorPage(self),
            "Operator Controls": OperatorControlsPage(self),
            "Event Log": EventLogPage(self),
            "Timeline / Cue Monitor": TimelineMonitorPage(self),
            "Package Loader": PackageLoaderPage(self),
            "Settings": SettingsPage(self),
        }
        for name in self.PAGE_ORDER:
            container = QWidget()
            container.setObjectName("pageContainer")
            layout = QVBoxLayout(container)
            layout.setContentsMargins(14, 14, 14, 14)
            layout.addWidget(self.pages[name])
            self.stack.addWidget(container)
        splitter.addWidget(self.nav)
        splitter.addWidget(self.stack)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([260, 1280])
        root_layout.addWidget(splitter, 1)
        self.setCentralWidget(root)
        self.nav.setCurrentRow(0)
        self.load_package(str(self.demo_package_path))

    def load_package(self, path: str) -> None:
        try:
            self.engine.load_package(path)
        except Exception as exc:
            QMessageBox.critical(self, "Package Load Failed", f"Could not load package:\n{path}\n\n{exc}")

    def show_page(self, name: str) -> None:
        if name in self.PAGE_ORDER:
            index = self.PAGE_ORDER.index(name)
            self.stack.setCurrentIndex(index)
            self.nav.setCurrentRow(index)

    def _set_page_index(self, index: int) -> None:
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)

    def _on_event(self, event: Event) -> None:
        self.event_log.append(event)
        self.refresh_all()

    def refresh_all(self) -> None:
        if self._refresh_in_progress:
            return
        self._refresh_in_progress = True
        try:
            status = self.engine.session.status.title()
            package_name = self.engine.package.name if self.engine.package else "No Package"
            self.session_badge.setText(f"Session: {status}")
            self.subtitle_label.setText(
                f"{package_name} • Room: {self.engine.active_room} • Speed: {self.engine.session.speed:.1f}x"
            )
            for name, page in self.pages.items():
                try:
                    page.refresh()
                except Exception as exc:
                    self.event_log.append(Event(source="UI", event_type="error", severity="error", message=f"Refresh failed for {name}: {exc}"))
        finally:
            self._refresh_in_progress = False
