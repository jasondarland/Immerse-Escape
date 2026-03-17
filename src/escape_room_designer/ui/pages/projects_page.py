"""Project manager page."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ProjectsPage(QWidget):
    def __init__(self, root_projects_dir: Path):
        super().__init__()
        self.root_projects_dir = root_projects_dir
        self.root_projects_dir.mkdir(parents=True, exist_ok=True)
        self.on_open_project_file = None

        root = QHBoxLayout(self)
        left = QVBoxLayout(); right = QVBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("Search projects...")
        self.search.textChanged.connect(self.refresh)
        self.list = QListWidget(); self.list.itemSelectionChanged.connect(self.load_selected_metadata)

        btns = QHBoxLayout()
        self.new_btn = QPushButton("Create")
        self.dup_btn = QPushButton("Duplicate")
        self.rename_btn = QPushButton("Rename")
        self.delete_btn = QPushButton("Delete")
        self.open_btn = QPushButton("Open")
        for b in [self.new_btn, self.dup_btn, self.rename_btn, self.delete_btn, self.open_btn]: btns.addWidget(b)
        self.new_btn.clicked.connect(self.create_project)
        self.dup_btn.clicked.connect(self.duplicate_project)
        self.rename_btn.clicked.connect(self.rename_project)
        self.delete_btn.clicked.connect(self.delete_project)
        self.open_btn.clicked.connect(self.open_selected)

        left.addWidget(self.search); left.addWidget(self.list,1); left.addLayout(btns)

        self.meta_name = QLineEdit(); self.meta_author = QLineEdit(); self.meta_version = QLineEdit(); self.meta_desc = QTextEdit()
        form = QFormLayout(); form.addRow("Name", self.meta_name); form.addRow("Author", self.meta_author); form.addRow("Version", self.meta_version); form.addRow("Description", self.meta_desc)
        save_meta = QPushButton("Save Metadata"); save_meta.clicked.connect(self.save_metadata)
        right.addLayout(form); right.addWidget(save_meta); right.addStretch()
        root.addLayout(left,2); root.addLayout(right,1)
        self.refresh()

    def refresh(self):
        q = self.search.text().lower().strip()
        self.list.clear()
        for p in sorted(self.root_projects_dir.iterdir()):
            if not p.is_dir() or not (p / "project.json").exists():
                continue
            if q and q not in p.name.lower():
                continue
            self.list.addItem(p.name)

    def _selected_dir(self) -> Path | None:
        it = self.list.currentItem()
        if not it:
            return None
        return self.root_projects_dir / it.text()

    def create_project(self):
        base = self.root_projects_dir / "New_Project"
        i = 1
        p = base
        while p.exists():
            i += 1
            p = self.root_projects_dir / f"New_Project_{i}"
        p.mkdir(parents=True)
        (p / "project.json").write_text(json.dumps({"project_id": p.name, "name": p.name, "version": "0.1.0"}, indent=2), encoding="utf-8")
        self.refresh()

    def duplicate_project(self):
        src = self._selected_dir()
        if not src:
            return
        dst = src.parent / f"{src.name}_copy"
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        self.refresh()

    def rename_project(self):
        src = self._selected_dir()
        if not src:
            return
        dst = src.parent / f"{src.name}_renamed"
        src.rename(dst)
        self.refresh()

    def delete_project(self):
        src = self._selected_dir()
        if src and src.exists():
            shutil.rmtree(src)
            self.refresh()

    def open_selected(self):
        src = self._selected_dir()
        if src and self.on_open_project_file:
            self.on_open_project_file(src / "project.json")

    def load_selected_metadata(self):
        src = self._selected_dir()
        if not src:
            return
        data = json.loads((src / "project.json").read_text(encoding="utf-8"))
        self.meta_name.setText(data.get("name", ""))
        self.meta_author.setText(data.get("author", ""))
        self.meta_version.setText(data.get("version", ""))
        self.meta_desc.setPlainText(data.get("description", ""))

    def save_metadata(self):
        src = self._selected_dir()
        if not src:
            return
        data = json.loads((src / "project.json").read_text(encoding="utf-8"))
        data.update({"name": self.meta_name.text(), "author": self.meta_author.text(), "version": self.meta_version.text(), "description": self.meta_desc.toPlainText()})
        (src / "project.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
