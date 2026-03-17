"""Main window composition for Escape Room Designer."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QStackedWidget,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from escape_room_designer.models.project_model import EscapeProject
from escape_room_designer.services.project_service import ProjectService
from escape_room_designer.ui.pages.base_pages import PlaceholderPage
from escape_room_designer.ui.pages.layout_page import LayoutPage
from escape_room_designer.ui.pages.logic_page import LogicPage
from escape_room_designer.ui.pages.puzzle_flow_page import PuzzleFlowPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Escape Room Designer")
        self.resize(1600, 950)

        self.service = ProjectService()
        self.current_project = EscapeProject(name="Untitled Escape Project")
        self.current_project_dir: Path | None = None
        self.clipboard_payload = None

        self.nav = QListWidget()
        self.stack = QStackedWidget()
        self.layout_page = LayoutPage()
        self.puzzle_page = PuzzleFlowPage()
        self.logic_page = LogicPage()

        self.pages = {
            "Dashboard": PlaceholderPage("Dashboard", "Mission status, project KPIs, and readiness snapshots."),
            "Projects": self._build_projects_page(),
            "Layout": self.layout_page,
            "Puzzle Flow": self.puzzle_page,
            "Logic": self.logic_page,
            "Timeline": PlaceholderPage("Timeline", "Cue tracks for lighting, audio, video, effects, and automation."),
            "Patch": PlaceholderPage("Patch / I-O", "Device patch matrix and channel mapping for all endpoints."),
            "Media": PlaceholderPage("Media", "Ingest, preview, and assign media assets to cues and triggers."),
            "Lighting/Effects": PlaceholderPage("Lighting & Effects", "Create looks and atmospheric triggers by room or zone."),
            "Game Flow": PlaceholderPage("Game Flow", "End-to-end guest journey and puzzle dependency overview."),
            "Operator": PlaceholderPage("Operator", "Live game-master controls with alerting and event log."),
            "Simulator": PlaceholderPage("Simulator", "Virtual hardware testing with synthetic input events."),
            "Reports": PlaceholderPage("Reports", "Generate equipment sheets, manuals, and checklists."),
            "Settings": PlaceholderPage("Settings", "System preferences, integrations, and defaults."),
        }

        for name, page in self.pages.items():
            self.nav.addItem(name)
            self.stack.addWidget(page)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.nav, 0)
        root_layout.addWidget(self.stack, 1)
        self.setCentralWidget(root)

        self._build_docks()
        self._build_menu()
        self._setup_shortcuts()
        self._load_demo_project()

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self._autosave)
        self.autosave_timer.start(120000)

    def _build_projects_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("<h2>Projects</h2>")
        subtitle = QLabel("Create, open, duplicate, save, and export project packages.")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        return page

    def _build_docks(self) -> None:
        inspector_dock = QDockWidget("Inspector", self)
        inspector = QTableWidget(0, 2)
        inspector.setHorizontalHeaderLabels(["Property", "Value"])
        inspector_dock.setWidget(inspector)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, inspector_dock)

        self.log_dock = QDockWidget("System Log", self)
        self.log_console = QPlainTextEdit()
        self.log_console.setReadOnly(True)
        self.log_dock.setWidget(self.log_console)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_dock)

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction("New Project", self.new_project)
        file_menu.addAction("Open Project", self.open_project)
        file_menu.addAction("Save Project", self.save_project)
        file_menu.addAction("Save Project As", self.save_project_as)
        file_menu.addAction("Export Project", self.export_project)

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence.StandardKey.Copy, self, activated=self.copy_selection)
        QShortcut(QKeySequence.StandardKey.Paste, self, activated=self.paste_selection)
        QShortcut(QKeySequence.StandardKey.Delete, self, activated=self.delete_selection)
        QShortcut(QKeySequence.StandardKey.Cut, self, activated=self.cut_selection)
        QShortcut(QKeySequence("Ctrl+D"), self, activated=self.duplicate_selection)
        QShortcut(QKeySequence.ZoomIn, self, activated=self.zoom_in)
        QShortcut(QKeySequence.ZoomOut, self, activated=self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, activated=self.zoom_reset)

    def _editable_page(self):
        page = self.stack.currentWidget()
        return page if hasattr(page, "copy_selection") else None

    def copy_selection(self) -> None:
        page = self._editable_page()
        if not page:
            return
        self.clipboard_payload = page.copy_selection()
        self.log("Copied selection.")

    def paste_selection(self) -> None:
        page = self._editable_page()
        if not page or not self.clipboard_payload:
            return
        page.paste_selection(self.clipboard_payload)
        self.log("Pasted selection.")

    def delete_selection(self) -> None:
        page = self._editable_page()
        if not page:
            return
        page.delete_selection()
        self.log("Deleted selection.")

    def cut_selection(self) -> None:
        self.copy_selection()
        self.delete_selection()

    def duplicate_selection(self) -> None:
        self.copy_selection()
        self.paste_selection()


    def zoom_in(self) -> None:
        page = self.stack.currentWidget()
        if hasattr(page, "zoom_in"):
            page.zoom_in()

    def zoom_out(self) -> None:
        page = self.stack.currentWidget()
        if hasattr(page, "zoom_out"):
            page.zoom_out()

    def zoom_reset(self) -> None:
        page = self.stack.currentWidget()
        if hasattr(page, "zoom_reset"):
            page.zoom_reset()

    def _load_demo_project(self) -> None:
        demo_file = Path(__file__).resolve().parents[1] / "demo_data" / "demo_project.json"
        if demo_file.exists():
            self.current_project = self.service.load_project(demo_file)
            self._apply_project_to_ui()
            self.log("Loaded bundled demo project.")

    def _apply_project_to_ui(self) -> None:
        self.layout_page.import_rooms(self.current_project.layouts)
        self.puzzle_page.scene.import_graph(self.current_project.puzzle_nodes, self.current_project.puzzle_edges)
        self.logic_page.scene.import_graph(self.current_project.logic_nodes, self.current_project.logic_edges)

    def _pull_ui_to_project(self) -> None:
        self.current_project.layouts = self.layout_page.export_rooms()
        p_nodes, p_edges = self.puzzle_page.scene.export_graph()
        l_nodes, l_edges = self.logic_page.scene.export_graph()
        self.current_project.puzzle_nodes = p_nodes
        self.current_project.puzzle_edges = p_edges
        self.current_project.logic_nodes = l_nodes
        self.current_project.logic_edges = l_edges

    def log(self, message: str) -> None:
        self.log_console.appendPlainText(message)

    def new_project(self) -> None:
        self.current_project = EscapeProject(name="New Escape Experience")
        self.current_project_dir = None
        self._apply_project_to_ui()
        self.log("Created new project.")

    def open_project(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "Project JSON (*.json)")
        if not filename:
            return
        self.current_project = self.service.load_project(Path(filename))
        self.current_project_dir = Path(filename).parent
        self._apply_project_to_ui()
        self.log(f"Opened project: {filename}")

    def save_project(self) -> None:
        self._pull_ui_to_project()
        if not self.current_project_dir:
            self.save_project_as()
            return
        project_file = self.service.save_project(self.current_project, self.current_project_dir)
        self.log(f"Saved project to {project_file}")

    def save_project_as(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Save Project As")
        if not folder:
            return
        self.current_project_dir = Path(folder)
        self.save_project()

    def export_project(self) -> None:
        if not self.current_project_dir:
            QMessageBox.information(self, "Export", "Save the project before export.")
            return
        self.log(f"Export package ready: {self.current_project_dir}")

    def _autosave(self) -> None:
        if not self.current_project_dir:
            return
        self._pull_ui_to_project()
        autosave_file = self.service.autosave(self.current_project, self.current_project_dir)
        self.log(f"Autosaved snapshot: {autosave_file.name}")
