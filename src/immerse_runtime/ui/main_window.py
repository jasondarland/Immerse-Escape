from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from immerse_runtime.models.entities import RuntimeStatus


class MainWindow(QMainWindow):
    def __init__(self, runtime_service) -> None:
        super().__init__()
        self.runtime = runtime_service
        self.runtime.updated.connect(self.refresh_all)
        self.setWindowTitle("IMMERSE Runtime – Escape Room Edition")
        self.resize(1680, 980)
        self._build_ui()
        self.refresh_all()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)

        header = QHBoxLayout()
        title = QLabel("IMMERSE Runtime – Escape Room Edition")
        title.setProperty("role", "title")
        self.package_label = QLabel("No package loaded")
        self.runtime_status = QLabel("IDLE")
        self.runtime_status.setProperty("status", "idle")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(QLabel("Package:"))
        header.addWidget(self.package_label)
        header.addSpacing(20)
        header.addWidget(QLabel("Status:"))
        header.addWidget(self.runtime_status)
        layout.addLayout(header)

        actions = QHBoxLayout()
        load_btn = QPushButton("Load Package")
        load_btn.clicked.connect(self.load_package)
        start_btn = QPushButton("Start Session")
        start_btn.setProperty("accent", True)
        start_btn.clicked.connect(lambda: self.runtime.start_session(self.room_selector.currentText(), self.preset_selector.currentText()))
        pause_btn = QPushButton("Pause")
        pause_btn.clicked.connect(self.runtime.pause_session)
        resume_btn = QPushButton("Resume")
        resume_btn.clicked.connect(self.runtime.resume_session)
        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(self.runtime.stop_session)
        reset_btn = QPushButton("Reset Room")
        reset_btn.clicked.connect(lambda: self.runtime.reset_room(False))
        full_reset_btn = QPushButton("Full Reset")
        full_reset_btn.clicked.connect(lambda: self.runtime.reset_room(True))
        unlock_btn = QPushButton("Emergency Unlock")
        unlock_btn.setProperty("danger", True)
        unlock_btn.clicked.connect(self.runtime.emergency_unlock)
        stop_outputs_btn = QPushButton("Stop All Outputs")
        stop_outputs_btn.clicked.connect(self.runtime.stop_all_outputs)
        ack_btn = QPushButton("Acknowledge Alert")
        ack_btn.clicked.connect(self.runtime.acknowledge_latest_alert)
        self.room_selector = QComboBox()
        self.room_selector.addItems(["Atrium", "Laboratory"])
        self.preset_selector = QComboBox()
        self.preset_selector.addItems(["Standard", "VIP", "Training"])
        for w in [load_btn, QLabel("Room"), self.room_selector, QLabel("Preset"), self.preset_selector, start_btn, pause_btn, resume_btn, stop_btn, reset_btn, full_reset_btn, unlock_btn, stop_outputs_btn, ack_btn]:
            actions.addWidget(w)
        layout.addLayout(actions)

        self.tabs = QTabWidget()
        self.dashboard_tab = self._build_dashboard_tab()
        self.session_tab = self._build_session_tab()
        self.device_tab = self._build_device_tab()
        self.logic_tab = self._build_logic_tab()
        self.event_tab = self._build_event_tab()
        self.output_tab = self._build_output_tab()
        self.alert_tab = self._build_alert_tab()
        self.settings_tab = self._build_settings_tab()
        for name, tab in [
            ("Runtime Dashboard", self.dashboard_tab),
            ("Session Control", self.session_tab),
            ("Device Monitor", self.device_tab),
            ("Logic / State Monitor", self.logic_tab),
            ("Event Log", self.event_tab),
            ("Outputs / Cue Monitor", self.output_tab),
            ("Alerts / Faults", self.alert_tab),
            ("Settings / Connections", self.settings_tab),
        ]:
            self.tabs.addTab(tab, name)
        layout.addWidget(self.tabs)
        self.setCentralWidget(root)

    def _metric_card(self, label: str):
        box = QGroupBox()
        layout = QVBoxLayout(box)
        title = QLabel(label)
        title.setProperty("role", "cardTitle")
        value = QLabel("--")
        value.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        layout.addWidget(value)
        return box, value

    def _build_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        grid = QGridLayout()
        labels = [
            "Runtime Status", "Session State", "Room Health", "Node Health", "Active Puzzles", "Solved Puzzles",
            "Active Outputs", "Active Media", "Active Alerts", "Uptime"
        ]
        self.dashboard_values = {}
        for idx, name in enumerate(labels):
            card, value = self._metric_card(name)
            self.dashboard_values[name] = value
            grid.addWidget(card, idx // 5, idx % 5)
        layout.addLayout(grid)
        quick = QGroupBox("Live Runtime Summary")
        ql = QVBoxLayout(quick)
        self.dashboard_summary = QPlainTextEdit()
        self.dashboard_summary.setReadOnly(True)
        ql.addWidget(self.dashboard_summary)
        layout.addWidget(quick)
        return tab

    def _build_session_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)
        self.session_table = QTableWidget(8, 2)
        self.session_table.setHorizontalHeaderLabels(["Field", "Value"])
        session_fields = ["Session ID", "Room", "Preset", "State", "Start Time", "Elapsed", "Puzzle Progress", "Operator Notes"]
        for row, field in enumerate(session_fields):
            self.session_table.setItem(row, 0, QTableWidgetItem(field))
        layout.addWidget(self.session_table, 0, 0, 1, 2)
        controls = QGroupBox("Manual Session Actions")
        cl = QVBoxLayout(controls)
        for label, trigger in [("Skip Puzzle", "keypad_correct"), ("Trigger Hint", "rfid_presented"), ("Trigger Finale", "finale_trigger")]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _=False, trig=trigger: self.runtime.manual_trigger(trig))
            cl.addWidget(btn)
        self.operator_notes = QPlainTextEdit()
        self.operator_notes.setPlaceholderText("Operator notes...")
        self.operator_notes.textChanged.connect(self._sync_notes)
        cl.addWidget(self.operator_notes)
        layout.addWidget(controls, 0, 2)
        return tab

    def _build_device_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        filters = QHBoxLayout()
        self.device_filter_room = QComboBox(); self.device_filter_room.addItems(["All", "Atrium", "Laboratory"])
        self.device_filter_type = QComboBox(); self.device_filter_type.addItems(["All", "keypad", "rfid", "mag_lock", "audio_cue", "video_cue", "light_cue", "relay"])
        self.device_filter_status = QComboBox(); self.device_filter_status.addItems(["All", "online", "offline", "degraded"])
        self.device_filter_node = QLineEdit(); self.device_filter_node.setPlaceholderText("Filter by node")
        for w in [QLabel("Room"), self.device_filter_room, QLabel("Type"), self.device_filter_type, QLabel("Status"), self.device_filter_status, QLabel("Node"), self.device_filter_node]:
            filters.addWidget(w)
        layout.addLayout(filters)
        self.device_table = QTableWidget(0, 8)
        self.device_table.setHorizontalHeaderLabels(["Name", "Type", "Room", "Node", "Status", "Last Update", "Current State", "Fault"])
        layout.addWidget(self.device_table)
        actions = QHBoxLayout()
        for label, trigger in [("Trigger Relay", "keypad_correct"), ("Unlock Door", "keypad_correct"), ("Play Cue", "rfid_presented"), ("Send Test Command", "finale_trigger")]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _=False, trig=trigger: self.runtime.manual_trigger(trig))
            actions.addWidget(btn)
        layout.addLayout(actions)
        return tab

    def _build_logic_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)
        self.logic_progress = QPlainTextEdit(); self.logic_progress.setReadOnly(True)
        self.logic_variables = QTableWidget(0, 2); self.logic_variables.setHorizontalHeaderLabels(["Variable", "Value"])
        self.logic_summary = QPlainTextEdit(); self.logic_summary.setReadOnly(True)
        layout.addWidget(QGroupBox(""), 0, 0)
        boxes = [("Progression / Sequences", self.logic_progress), ("State Variables", self.logic_variables), ("Read-only Logic Graph Summary", self.logic_summary)]
        for idx, (title, widget) in enumerate(boxes):
            group = QGroupBox(title)
            gl = QVBoxLayout(group)
            gl.addWidget(widget)
            layout.addWidget(group, 0 if idx < 2 else 1, idx if idx < 2 else 0, 1, 1 if idx < 2 else 2)
        return tab

    def _build_event_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        top = QHBoxLayout()
        self.event_search = QLineEdit(); self.event_search.setPlaceholderText("Search event log")
        export_btn = QPushButton("Export Log")
        export_btn.clicked.connect(self.export_log)
        clear_btn = QPushButton("Clear View")
        clear_btn.clicked.connect(lambda: self.event_table.setRowCount(0))
        top.addWidget(self.event_search); top.addWidget(export_btn); top.addWidget(clear_btn)
        layout.addLayout(top)
        self.event_table = QTableWidget(0, 6)
        self.event_table.setHorizontalHeaderLabels(["Timestamp", "Severity", "Room", "Source", "Type", "Message"])
        layout.addWidget(self.event_table)
        return tab

    def _build_output_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.output_table = QTableWidget(0, 5)
        self.output_table.setHorizontalHeaderLabels(["Target", "Room", "Start Time", "Expected Duration", "State"])
        layout.addWidget(self.output_table)
        return tab

    def _build_alert_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.alert_table = QTableWidget(0, 6)
        self.alert_table.setHorizontalHeaderLabels(["ID", "Severity", "Source", "Message", "Acknowledged", "Notes"])
        layout.addWidget(self.alert_table)
        return tab

    def _build_settings_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)
        self.settings_table = QTableWidget(0, 2)
        self.settings_table.setHorizontalHeaderLabels(["Setting", "Value"])
        layout.addWidget(self.settings_table, 0, 0)
        transport = QGroupBox("Connection Profiles")
        tl = QVBoxLayout(transport)
        tl.addWidget(QLabel("MQTT: mock://broker.local"))
        tl.addWidget(QLabel("TCP: 127.0.0.1:4100"))
        tl.addWidget(QLabel("WebSocket: ws://127.0.0.1:8765/runtime"))
        tl.addWidget(QLabel("REST: http://127.0.0.1:8080/api/runtime"))
        layout.addWidget(transport, 0, 1)
        return tab

    def _sync_notes(self):
        self.runtime.session_manager.current.notes = self.operator_notes.toPlainText()

    def load_package(self):
        default_path = str((Path(__file__).resolve().parents[3] / "demo_package"))
        path = QFileDialog.getExistingDirectory(self, "Select Runtime Package", default_path)
        if not path:
            path = default_path
        try:
            self.runtime.load_package(path)
        except Exception as exc:
            QMessageBox.critical(self, "Package Load Error", str(exc))

    def export_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Event Log", "runtime-log.txt", "Text Files (*.txt)")
        if path:
            self.runtime.event_logger.export(path)

    def refresh_all(self):
        pkg = self.runtime.current_package
        self.package_label.setText(pkg.name if pkg else "No package loaded")
        status = self.runtime.status.value if isinstance(self.runtime.status, RuntimeStatus) else str(self.runtime.status)
        self.runtime_status.setText(status.upper())
        self.runtime_status.setProperty("status", "fault" if status in ["fault", "emergency"] else ("paused" if status == "paused" else ("running" if status == "running" else ("warning" if status == "reset_needed" else "idle"))))
        self.runtime_status.style().unpolish(self.runtime_status); self.runtime_status.style().polish(self.runtime_status)

        session = self.runtime.session_manager.current
        active_alerts = len([a for a in self.runtime.alert_manager.alerts if a.active and not a.acknowledged])
        active_media = len([o for o in self.runtime.output_dispatcher.active_outputs if o.action.startswith("play")])
        node_ok = sum(1 for n in self.runtime.node_manager.nodes.values() if n.status == "online")
        node_total = len(self.runtime.node_manager.nodes)
        room_health = "Healthy" if active_alerts == 0 else "Attention Required"
        self.dashboard_values["Runtime Status"].setText(status.upper())
        self.dashboard_values["Session State"].setText(session.state.upper())
        self.dashboard_values["Room Health"].setText(room_health)
        self.dashboard_values["Node Health"].setText(f"{node_ok}/{node_total} online")
        self.dashboard_values["Active Puzzles"].setText(str(session.active_puzzles))
        self.dashboard_values["Solved Puzzles"].setText(str(session.solved_puzzles))
        self.dashboard_values["Active Outputs"].setText(str(len([o for o in self.runtime.output_dispatcher.active_outputs if o.state == 'active'])))
        self.dashboard_values["Active Media"].setText(str(active_media))
        self.dashboard_values["Active Alerts"].setText(str(active_alerts))
        self.dashboard_values["Uptime"].setText(f"{session.elapsed_seconds}s")
        self.dashboard_summary.setPlainText(
            f"Loaded Project: {pkg.project.get('title', 'None') if pkg else 'None'}\n"
            f"Current Room: {session.room}\n"
            f"Runtime Mode: Mock / Simulation\n"
            f"Connected Nodes: {node_total}\n"
            f"Devices Registered: {len(self.runtime.device_registry.devices)}\n"
            f"Latest Progression: {', '.join(self.runtime.state_manager.state.get('progression', [])[-5:]) or 'No progression yet'}"
        )

        session_values = [
            session.id, session.room, session.preset, session.state,
            session.started_at.isoformat(timespec='seconds') if session.started_at else '-',
            f"{session.elapsed_seconds}s", f"{session.solved_puzzles} solved / {session.active_puzzles} active", session.notes,
        ]
        for row, value in enumerate(session_values):
            self.session_table.setItem(row, 1, QTableWidgetItem(value))
        if self.operator_notes.toPlainText() != session.notes:
            self.operator_notes.setPlainText(session.notes)

        devices = list(self.runtime.device_registry.devices.values())
        room_filter = self.device_filter_room.currentText()
        type_filter = self.device_filter_type.currentText()
        status_filter = self.device_filter_status.currentText()
        node_filter = self.device_filter_node.text().strip().lower()
        filtered = [d for d in devices if (room_filter == 'All' or d.room == room_filter) and (type_filter == 'All' or d.type == type_filter) and (status_filter == 'All' or d.status == status_filter) and (not node_filter or node_filter in d.node.lower())]
        self.device_table.setRowCount(len(filtered))
        for row, device in enumerate(filtered):
            for col, value in enumerate([device.name, device.type, device.room, device.node, device.status, device.last_update.isoformat(timespec='seconds'), device.current_state, device.fault]):
                self.device_table.setItem(row, col, QTableWidgetItem(str(value)))

        progression = self.runtime.state_manager.state.get("progression", [])
        self.logic_progress.setPlainText("\n".join(progression) or "Awaiting runtime triggers...")
        variables = self.runtime.state_manager.state.get("variables", {})
        self.logic_variables.setRowCount(len(variables))
        for row, (key, value) in enumerate(variables.items()):
            self.logic_variables.setItem(row, 0, QTableWidgetItem(key))
            self.logic_variables.setItem(row, 1, QTableWidgetItem(str(value)))
        graph = self.runtime.logic_engine.logic_graph
        self.logic_summary.setPlainText(
            f"Rooms: {', '.join(graph.get('rooms', []))}\n"
            f"Puzzle Flow: {' -> '.join(graph.get('puzzle_flow', []))}\n"
            f"Conditions: {', '.join(graph.get('conditions', []))}\n"
            f"Timers: {', '.join(graph.get('timers', []))}\n"
            f"Fail-safe rules: {', '.join(graph.get('failsafe', []))}"
        )

        search = self.event_search.text().lower().strip()
        events = [e for e in self.runtime.event_logger.events if not search or search in e.message.lower() or search in e.source.lower()]
        self.event_table.setRowCount(len(events))
        for row, event in enumerate(reversed(events)):
            for col, value in enumerate([event.timestamp.isoformat(timespec='seconds'), event.severity.value, event.room, event.source, event.event_type, event.message]):
                self.event_table.setItem(row, col, QTableWidgetItem(str(value)))

        outputs = self.runtime.output_dispatcher.active_outputs
        self.output_table.setRowCount(len(outputs))
        for row, output in enumerate(reversed(outputs)):
            for col, value in enumerate([output.target, output.room, output.started_at.isoformat(timespec='seconds'), f"{output.expected_duration}s", output.state]):
                self.output_table.setItem(row, col, QTableWidgetItem(str(value)))

        alerts = self.runtime.alert_manager.alerts
        self.alert_table.setRowCount(len(alerts))
        for row, alert in enumerate(reversed(alerts)):
            for col, value in enumerate([alert.id, alert.severity.value, alert.source, alert.message, str(alert.acknowledged), alert.resolution_notes]):
                self.alert_table.setItem(row, col, QTableWidgetItem(str(value)))

        config = pkg.runtime_config if pkg else {}
        settings = {
            "Package Path": pkg.project.get('package_root', 'demo_package') if pkg else 'Not loaded',
            "Auto-load Last Package": config.get('auto_load_last_package', True),
            "Device Polling Interval": config.get('device_poll_interval_ms', 1000),
            "Watchdog Enabled": config.get('watchdog_enabled', True),
            "Reset Behavior": config.get('reset_behavior', 'safe'),
            "Logging Level": config.get('logging_level', 'info'),
            "Mock Mode": True,
        }
        self.settings_table.setRowCount(len(settings))
        for row, (key, value) in enumerate(settings.items()):
            self.settings_table.setItem(row, 0, QTableWidgetItem(str(key)))
            self.settings_table.setItem(row, 1, QTableWidgetItem(str(value)))
