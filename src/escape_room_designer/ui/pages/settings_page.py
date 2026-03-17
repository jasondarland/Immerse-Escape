"""Settings page."""
from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QFormLayout, QLineEdit, QPushButton, QSpinBox, QVBoxLayout, QWidget


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self._project = None
        root = QVBoxLayout(self)
        form = QFormLayout()
        self.theme = QComboBox(); self.theme.addItems(["dark", "light"])
        self.autosave = QSpinBox(); self.autosave.setMaximum(3600)
        self.project_path = QLineEdit(); self.export_path = QLineEdit()
        self.snap = QSpinBox(); self.snap.setMaximum(5000)
        self.scale = QLineEdit(); self.sim_delay = QSpinBox(); self.sim_delay.setMaximum(5000)
        self.verbosity = QComboBox(); self.verbosity.addItems(["debug", "info", "warning", "error"])
        self.strictness = QComboBox(); self.strictness.addItems(["low", "normal", "strict"])
        self.pack_ver = QLineEdit(); self.node_pattern = QLineEdit(); self.device_pattern = QLineEdit()
        form.addRow("Theme", self.theme); form.addRow("Autosave interval (s)", self.autosave)
        form.addRow("Default project path", self.project_path); form.addRow("Default export path", self.export_path)
        form.addRow("Timeline snap interval (ms)", self.snap); form.addRow("Default room scale", self.scale)
        form.addRow("Simulation delay (ms)", self.sim_delay); form.addRow("Log verbosity", self.verbosity)
        form.addRow("Validation strictness", self.strictness); form.addRow("Pack format version", self.pack_ver)
        form.addRow("Node naming pattern", self.node_pattern); form.addRow("Device naming pattern", self.device_pattern)
        save = QPushButton("Save Settings")
        save.clicked.connect(self.save)
        root.addLayout(form); root.addWidget(save); root.addStretch()

    def bind_project(self, project):
        self._project = project
        s = project.settings
        self.theme.setCurrentText(s.get("theme", "dark"))
        self.autosave.setValue(int(s.get("autosave_interval_s", 120)))
        self.project_path.setText(s.get("default_project_path", ""))
        self.export_path.setText(s.get("default_export_path", ""))
        self.snap.setValue(int(s.get("timeline_snap_ms", 100)))
        self.scale.setText(str(s.get("default_room_scale", 0.01)))
        self.sim_delay.setValue(int(s.get("simulation_delay_ms", 50)))
        self.verbosity.setCurrentText(s.get("log_verbosity", "info"))
        self.strictness.setCurrentText(s.get("validation_strictness", "normal"))
        self.pack_ver.setText(s.get("runtime_pack_format_version", "1.0.0"))
        self.node_pattern.setText(s.get("default_node_name_pattern", "node-{type}-{n}"))
        self.device_pattern.setText(s.get("default_device_name_pattern", "{type}-{n}"))

    def save(self):
        if not self._project:
            return
        self._project.settings.update({
            "theme": self.theme.currentText(),
            "autosave_interval_s": self.autosave.value(),
            "default_project_path": self.project_path.text(),
            "default_export_path": self.export_path.text(),
            "timeline_snap_ms": self.snap.value(),
            "default_room_scale": float(self.scale.text() or 0.01),
            "simulation_delay_ms": self.sim_delay.value(),
            "log_verbosity": self.verbosity.currentText(),
            "validation_strictness": self.strictness.currentText(),
            "runtime_pack_format_version": self.pack_ver.text(),
            "default_node_name_pattern": self.node_pattern.text(),
            "default_device_name_pattern": self.device_pattern.text(),
        })
