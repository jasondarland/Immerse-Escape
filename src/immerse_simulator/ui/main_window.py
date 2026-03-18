from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QListWidget, QMainWindow, QSplitter, QStackedWidget, QWidget, QVBoxLayout

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
        self.engine.event_bus.event_emitted.connect(self._on_event)
        self.engine.package_loaded.connect(self.refresh_all)
        self.engine.state_changed.connect(self.refresh_all)
        self.engine.nodes_changed.connect(self.refresh_all)
        self.engine.timeline_changed.connect(self.refresh_all)

        splitter = QSplitter()
        nav = QListWidget()
        nav.addItems(self.PAGE_ORDER)
        nav.currentRowChanged.connect(self._set_page_index)
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
            layout = QVBoxLayout(container)
            layout.addWidget(self.pages[name])
            self.stack.addWidget(container)
        splitter.addWidget(nav)
        splitter.addWidget(self.stack)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)
        nav.setCurrentRow(0)
        self.load_package(str(self.demo_package_path))

    def load_package(self, path: str) -> None:
        self.engine.load_package(path)

    def show_page(self, name: str) -> None:
        self.stack.setCurrentIndex(self.PAGE_ORDER.index(name))

    def _set_page_index(self, index: int) -> None:
        self.stack.setCurrentIndex(index)

    def _on_event(self, event: Event) -> None:
        self.event_log.append(event)
        self.refresh_all()

    def refresh_all(self) -> None:
        for page in self.pages.values():
            page.refresh()
