"""Main window composition for IMMERSE Designer – Escape Room Edition."""
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
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from escape_room_designer.models.project_model import EscapeProject
from escape_room_designer.services.export_service import ImmersePackExporter
from escape_room_designer.services.project_service import ProjectService
from escape_room_designer.ui.pages.base_pages import PlaceholderPage
from escape_room_designer.ui.pages.devices_page import DevicesPage
from escape_room_designer.ui.pages.layout_page import LayoutPage
from escape_room_designer.ui.pages.logic_page import LogicPage
from escape_room_designer.ui.pages.puzzle_flow_page import PuzzleFlowPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMMERSE Designer – Escape Room Edition")
        self.resize(1700, 980)

        self.service = ProjectService()
        self.pack_exporter = ImmersePackExporter()
        self.current_project = EscapeProject(name="Untitled IMMERSE Project")
        self.current_project_dir: Path | None = None
        self.clipboard_payload = None

        self.nav = QListWidget()
        self.stack = QStackedWidget()
        self.layout_page = LayoutPage()
        self.devices_page = DevicesPage()
        self.puzzle_page = PuzzleFlowPage()
        self.logic_page = LogicPage()

        self.pages = {
            "Dashboard": PlaceholderPage("Dashboard", "Production snapshot for the active IMMERSE attraction project."),
            "Projects": self._build_projects_page(),
            "Layout": self.layout_page,
            "Devices": self.devices_page,
            "Puzzle Flow": self.puzzle_page,
            "Logic": self.logic_page,
            "Timeline": PlaceholderPage("Timeline", "Timeline engine with tracks for cues and conditional playback."),
            "Operator": PlaceholderPage("Operator", "Operator control mappings to runtime endpoints."),
            "Simulator": PlaceholderPage("Simulator", "Virtual device/event simulator and execution trace console."),
            "Reports": PlaceholderPage("Reports", "Generate engineering documentation and deployment sheets."),
            "Settings": PlaceholderPage("Settings", "System defaults and runtime compatibility preferences."),
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
        self.devices_page.set_inspector_callback(self.update_inspector)
        self._load_demo_project()

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self._autosave)
        self.autosave_timer.start(120000)

    def _build_projects_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("<h2>IMMERSE Projects</h2>")
        subtitle = QLabel("Author, save, simulate, and export deployable IMMERSEPACK.ZIP packages.")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        return page

    def _build_docks(self) -> None:
        inspector_dock = QDockWidget("Inspector", self)
        self.inspector = QTableWidget(0, 2)
        self.inspector.setHorizontalHeaderLabels(["Property", "Value"])
        inspector_dock.setWidget(self.inspector)
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
        file_menu.addAction("Export IMMERSEPACK.ZIP", self.export_project)

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence.StandardKey.Copy, self, activated=self.copy_selection)
        QShortcut(QKeySequence.StandardKey.Paste, self, activated=self.paste_selection)
        QShortcut(QKeySequence.StandardKey.Delete, self, activated=self.delete_selection)
        QShortcut(QKeySequence.StandardKey.Cut, self, activated=self.cut_selection)
        QShortcut(QKeySequence("Ctrl+D"), self, activated=self.duplicate_selection)
        QShortcut(QKeySequence.ZoomIn, self, activated=self.zoom_in)
        QShortcut(QKeySequence.ZoomOut, self, activated=self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, activated=self.zoom_reset)

    def update_inspector(self, payload: dict[str, str]) -> None:
        self.inspector.setRowCount(0)
        for key, value in payload.items():
            row = self.inspector.rowCount()
            self.inspector.insertRow(row)
            self.inspector.setItem(row, 0, QTableWidgetItem(key))
            self.inspector.setItem(row, 1, QTableWidgetItem(str(value)))

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
        self.devices_page.import_devices(self.current_project.devices)
        self.puzzle_page.scene.import_graph(self.current_project.puzzle_nodes, self.current_project.puzzle_edges)
        self.logic_page.scene.import_graph(self.current_project.logic_nodes, self.current_project.logic_edges)

    def _pull_ui_to_project(self) -> None:
        self.current_project.layouts = self.layout_page.export_rooms()
        self.current_project.devices = self.devices_page.export_devices()
        p_nodes, p_edges = self.puzzle_page.scene.export_graph()
        l_nodes, l_edges = self.logic_page.scene.export_graph()
        self.current_project.puzzle_nodes = p_nodes
        self.current_project.puzzle_edges = p_edges
        self.current_project.logic_nodes = l_nodes
        self.current_project.logic_edges = l_edges

    def log(self, message: str) -> None:
        self.log_console.appendPlainText(message)

    def new_project(self) -> None:
        self.current_project = EscapeProject(name="New IMMERSE Attraction")
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
        self._pull_ui_to_project()
        default = str((self.current_project_dir or Path.cwd()) / "IMMERSEPACK.ZIP")
        filename, _ = QFileDialog.getSaveFileName(self, "Export IMMERSEPACK", default, "ZIP Files (*.zip)")
        if not filename:
            return
        output = Path(filename)
        if output.suffix.lower() != ".zip":
            output = output.with_suffix(".zip")
        if output.name.upper() != "IMMERSEPACK.ZIP":
            output = output.with_name("IMMERSEPACK.ZIP")
        created = self.pack_exporter.export(self.current_project, output)
        self.log(f"Exported IMMERSEPACK: {created}")
        QMessageBox.information(self, "Export Complete", f"Created {created}")

    def _autosave(self) -> None:
        if not self.current_project_dir:
            return
        self._pull_ui_to_project()
        autosave_file = self.service.autosave(self.current_project, self.current_project_dir)
        self.log(f"Autosaved snapshot: {autosave_file.name}")
