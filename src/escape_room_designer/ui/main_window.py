"""Main window composition for IMMERSE Designer – Escape Room Edition."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QDockWidget,
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from escape_room_designer.models.project_model import EscapeProject
from escape_room_designer.services.export_service import ImmersePackExporter
from escape_room_designer.services.project_service import ProjectService
from escape_room_designer.services.validation_service import RuntimePackValidator
from escape_room_designer.ui.pages.dashboard_page import DashboardPage
from escape_room_designer.ui.pages.devices_page import DevicesPage
from escape_room_designer.ui.pages.layout_page import LayoutPage
from escape_room_designer.ui.pages.logic_page import LogicPage
from escape_room_designer.ui.pages.operator_page import OperatorPage
from escape_room_designer.ui.pages.projects_page import ProjectsPage
from escape_room_designer.ui.pages.puzzle_flow_page import PuzzleFlowPage
from escape_room_designer.ui.pages.reports_page import ReportsPage
from escape_room_designer.ui.pages.settings_page import SettingsPage
from escape_room_designer.ui.pages.simulator_page import SimulatorPage
from escape_room_designer.ui.pages.timeline_page import TimelinePage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMMERSE Designer – Escape Room Edition")
        self.resize(1800, 1000)
        self.service = ProjectService()
        self.pack_exporter = ImmersePackExporter()
        self.validator = RuntimePackValidator()
        self.current_project = EscapeProject(project_id="project-001", name="Untitled IMMERSE Project")
        self.current_project_dir: Path | None = None
        self.clipboard_payload = None
        self._updating_inspector = False

        self.nav = QListWidget(); self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.projects_page = ProjectsPage(self.service.root_dir)
        self.layout_page = LayoutPage()
        self.devices_page = DevicesPage()
        self.puzzle_page = PuzzleFlowPage()
        self.logic_page = LogicPage()
        self.timeline_page = TimelinePage()
        self.operator_page = OperatorPage()
        self.simulator_page = SimulatorPage()
        self.reports_page = ReportsPage()
        self.settings_page = SettingsPage()

        self.pages = {
            "Dashboard": self.dashboard_page,
            "Projects": self.projects_page,
            "Layout": self.layout_page,
            "Devices": self.devices_page,
            "Puzzle Flow": self.puzzle_page,
            "Logic": self.logic_page,
            "Timeline": self.timeline_page,
            "Operator": self.operator_page,
            "Simulator": self.simulator_page,
            "Reports": self.reports_page,
            "Settings": self.settings_page,
        }
        for n,p in self.pages.items(): self.nav.addItem(n); self.stack.addWidget(p)
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)

        root = QWidget(); rl = QHBoxLayout(root); rl.setContentsMargins(0,0,0,0); rl.addWidget(self.nav,0); rl.addWidget(self.stack,1); self.setCentralWidget(root)
        self._build_docks(); self._build_menu(); self._setup_shortcuts()

        self.dashboard_page.on_open_page = self.open_page
        self.dashboard_page.new_btn.clicked.connect(self.new_project)
        self.dashboard_page.open_btn.clicked.connect(self.open_project)
        self.projects_page.on_open_project_file = self._open_project_file
        self.devices_page.set_inspector_callback(self.update_inspector)
        self.layout_page.set_inspector_callback(self.update_inspector)

        self._load_demo_project()
        self.autosave_timer = QTimer(self); self.autosave_timer.timeout.connect(self._autosave); self.autosave_timer.start(120000)

    def open_page(self, name: str):
        for i in range(self.nav.count()):
            if self.nav.item(i).text() == name:
                self.nav.setCurrentRow(i)
                break

    def _build_docks(self):
        d = QDockWidget("Inspector", self); self.inspector = QTableWidget(0,2); self.inspector.setHorizontalHeaderLabels(["Property","Value"]); self.inspector.itemChanged.connect(self._inspector_item_changed); d.setWidget(self.inspector); self.addDockWidget(Qt.RightDockWidgetArea, d)
        d2 = QDockWidget("System Log", self); self.log_console = QPlainTextEdit(); self.log_console.setReadOnly(True); d2.setWidget(self.log_console); self.addDockWidget(Qt.BottomDockWidgetArea, d2)

    def _build_menu(self):
        m = self.menuBar().addMenu("File")
        m.addAction("New Project", self.new_project)
        m.addAction("Open Project", self.open_project)
        m.addAction("Save Project", self.save_project)
        m.addAction("Save Project As", self.save_project_as)
        m.addAction("Export IMMERSEPACK", self.export_project)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence.StandardKey.Copy, self, activated=self.copy_selection)
        QShortcut(QKeySequence.StandardKey.Paste, self, activated=self.paste_selection)
        QShortcut(QKeySequence.StandardKey.Delete, self, activated=self.delete_selection)
        QShortcut(QKeySequence.StandardKey.Cut, self, activated=self.cut_selection)
        QShortcut(QKeySequence("Ctrl+D"), self, activated=self.duplicate_selection)
        QShortcut(QKeySequence.ZoomIn, self, activated=self.zoom_in)
        QShortcut(QKeySequence.ZoomOut, self, activated=self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, activated=self.zoom_reset)

    def update_inspector(self, payload: dict[str, str]):
        self._updating_inspector = True
        self.inspector.setRowCount(0)
        for k,v in payload.items():
            r=self.inspector.rowCount(); self.inspector.insertRow(r); self.inspector.setItem(r,0,QTableWidgetItem(k)); self.inspector.setItem(r,1,QTableWidgetItem(str(v)))
        self._updating_inspector = False


    def _inspector_item_changed(self, item):
        if self._updating_inspector or item.column() != 1:
            return
        key_item = self.inspector.item(item.row(), 0)
        if not key_item:
            return
        key = key_item.text()
        page = self.stack.currentWidget()
        if hasattr(page, "update_selected_property"):
            page.update_selected_property(key, item.text())

    def _editable_page(self):
        p=self.stack.currentWidget(); return p if hasattr(p,'copy_selection') else None
    def copy_selection(self):
        p=self._editable_page();
        if p: self.clipboard_payload=p.copy_selection(); self.log("Copied selection.")
    def paste_selection(self):
        p=self._editable_page();
        if p and self.clipboard_payload: p.paste_selection(self.clipboard_payload); self.log("Pasted selection.")
    def delete_selection(self):
        p=self._editable_page();
        if p: p.delete_selection(); self.log("Deleted selection.")
    def cut_selection(self): self.copy_selection(); self.delete_selection()
    def duplicate_selection(self): self.copy_selection(); self.paste_selection()
    def zoom_in(self):
        p=self.stack.currentWidget();
        if hasattr(p,'zoom_in'): p.zoom_in()
    def zoom_out(self):
        p=self.stack.currentWidget();
        if hasattr(p,'zoom_out'): p.zoom_out()
    def zoom_reset(self):
        p=self.stack.currentWidget();
        if hasattr(p,'zoom_reset'): p.zoom_reset()

    def _load_demo_project(self):
        demo = Path(__file__).resolve().parents[1] / "demo_data" / "demo_project.json"
        if demo.exists():
            self.current_project = self.service.load_project(demo)
            self._apply_project_to_ui()
            self.log("Loaded bundled demo project.")

    def _apply_project_to_ui(self):
        p=self.current_project
        self.layout_page.import_rooms(p.layouts)
        self.devices_page.import_devices(p.devices)
        self.puzzle_page.scene.import_graph(p.puzzle_nodes, p.puzzle_edges)
        self.logic_page.scene.import_graph(p.logic_nodes, p.logic_edges)
        self.timeline_page.import_timeline(p.timeline)
        self.operator_page.bind_project(p)
        self.simulator_page.bind_project(p)
        self.reports_page.bind_project(p)
        self.settings_page.bind_project(p)
        validation = self.validator.validate(p)
        self.dashboard_page.bind_project(p, [f"{i.level}: {i.message}" for i in validation.issues])

    def _pull_ui_to_project(self):
        p=self.current_project
        p.layouts=self.layout_page.export_rooms()
        p.devices=self.devices_page.export_devices()
        p.puzzle_nodes,p.puzzle_edges=self.puzzle_page.scene.export_graph()
        p.logic_nodes,p.logic_edges=self.logic_page.scene.export_graph()
        p.timeline=self.timeline_page.export_timeline()
        p.updated_at = datetime.utcnow().isoformat()

    def log(self,msg:str):
        self.current_project.activity_log.append(msg)
        self.log_console.appendPlainText(msg)

    def new_project(self):
        self.current_project = EscapeProject(project_id="project-new", name="New IMMERSE Attraction")
        self.current_project_dir=None
        self._apply_project_to_ui(); self.log("Created new project.")

    def _open_project_file(self, project_file: Path):
        self.current_project = self.service.load_project(project_file)
        self.current_project_dir = project_file if project_file.is_dir() else project_file.parent
        self._apply_project_to_ui(); self.log(f"Opened project: {project_file}")

    def open_project(self):
        fn,_=QFileDialog.getOpenFileName(self,"Open Project","","Project Files (*.json *.immersepack *.zip);;Project JSON (*.json);;IMMERSEPACK (*.immersepack *.zip)")
        if fn: self._open_project_file(Path(fn))

    def save_project(self):
        self._pull_ui_to_project()
        if not self.current_project_dir:
            self.save_project_as(); return
        pf=self.service.save_project(self.current_project,self.current_project_dir); self.log(f"Saved project to {pf}"); self.projects_page.refresh(); self._apply_project_to_ui()

    def save_project_as(self):
        folder=QFileDialog.getExistingDirectory(self,"Save Project As")
        if folder:
            self.current_project_dir=Path(folder)
            self.save_project()

    def export_project(self):
        self._pull_ui_to_project()
        validation=self.validator.validate(self.current_project)
        for i in validation.issues: self.log(f"[{i.level.upper()}] {i.code}: {i.message}")
        if not validation.passed:
            QMessageBox.warning(self,"Validation Failed","Cannot export: fix validation errors in log.")
            return
        export_root = self.current_project_dir or Path.cwd()
        if export_root.is_file():
            export_root = export_root.parent
        default=str(export_root / self.pack_exporter.DEFAULT_ARCHIVE_NAME)
        fn,_=QFileDialog.getSaveFileName(self,"Export IMMERSEPACK",default,"IMMERSEPACK (*.immersepack);;ZIP Files (*.zip)")
        if not fn: return
        out=Path(fn)
        if out.suffix.lower() not in {'.immersepack', '.zip'}:
            out=out.with_suffix('.immersepack')
        out=out.with_name(f"IMMERSEPACK{out.suffix.lower()}")
        created=self.pack_exporter.export(self.current_project,out,validation)
        self.current_project.recent_exports.append({"file": str(created), "time": datetime.utcnow().isoformat(), "status": "success"})
        self.log(f"Exported IMMERSEPACK: {created}")
        self._apply_project_to_ui()
        QMessageBox.information(self,"Export Complete",f"Created {created}")

    def _autosave(self):
        if not self.current_project_dir: return
        self._pull_ui_to_project(); f=self.service.autosave(self.current_project,self.current_project_dir); self.log(f"Autosaved snapshot: {f.name}")
