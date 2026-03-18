from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget


class PackageLoaderPage(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        layout = QVBoxLayout(self)
        controls = QHBoxLayout()
        self.path_label = QLabel(str(window.demo_package_path))
        browse = QPushButton("Browse Package")
        browse.clicked.connect(self._browse)
        load_demo = QPushButton("Load Demo Package")
        load_demo.clicked.connect(lambda: self.window.load_package(str(self.window.demo_package_path)))
        controls.addWidget(self.path_label)
        controls.addWidget(browse)
        controls.addWidget(load_demo)
        self.summary = QTextEdit()
        self.summary.setReadOnly(True)
        layout.addLayout(controls)
        layout.addWidget(self.summary)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Package", str(Path.home()), "Packages (*.immersepack *.zip)")
        if path:
            self.path_label.setText(path)
            self.window.load_package(path)

    def refresh(self) -> None:
        package = self.window.engine.package
        if not package:
            self.summary.setText("No package loaded. Use the bundled demo package or select an external package/folder.")
            return
        warnings = "\n".join(f"[{msg.severity}] {msg.message}" for msg in package.validation_messages) or "No validation warnings."
        self.summary.setText(
            f"Package: {package.name}\nVersion: {package.version}\nRooms: {[room['name'] for room in package.rooms]}\n"
            f"Devices: {len(package.devices)}\nPuzzles: {len(package.puzzles)}\nTimeline cues: {len(package.timeline)}\n\nValidation:\n{warnings}"
        )
