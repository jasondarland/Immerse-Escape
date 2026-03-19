from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QFormLayout, QGridLayout, QGroupBox, QLineEdit, QPushButton, QWidget


class PlayerInputsPage(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        layout = QGridLayout(self)

        keypad_box = QGroupBox("Keypad")
        keypad_layout = QFormLayout(keypad_box)
        self.keypad_input = QLineEdit()
        send_keypad = QPushButton("Send Code")
        send_keypad.clicked.connect(lambda: self.window.engine.handle_input("keypad", self.keypad_input.text(), room="Lab A"))
        keypad_layout.addRow("Code", self.keypad_input)
        keypad_layout.addRow(send_keypad)

        rfid_box = QGroupBox("RFID")
        rfid_layout = QFormLayout(rfid_box)
        self.rfid_tags = QComboBox()
        self.rfid_tags.addItems(["RFID-ALPHA", "RFID-BETA", "INVALID-TAG"])
        rfid_send = QPushButton("Simulate Scan")
        rfid_send.clicked.connect(lambda: self.window.engine.handle_input("rfid", self.rfid_tags.currentText(), room="Lab B"))
        rfid_layout.addRow("Tag", self.rfid_tags)
        rfid_layout.addRow(rfid_send)

        sequence_box = QGroupBox("Sequence Buttons")
        seq_layout = QFormLayout(sequence_box)
        self.sequence = QLineEdit("RGBY")
        seq_send = QPushButton("Submit Sequence")
        seq_send.clicked.connect(lambda: self.window.engine.handle_input("sequence", self.sequence.text(), room="Lab B"))
        seq_layout.addRow("Pattern", self.sequence)
        seq_layout.addRow(seq_send)

        sensor_box = QGroupBox("Generic Inputs")
        sensor_layout = QFormLayout(sensor_box)
        self.generic_action = QComboBox()
        self.generic_action.addItems(["button", "switch", "door", "pressure_plate", "pir", "clue", "sensor"])
        self.generic_value = QLineEdit("triggered")
        generic_send = QPushButton("Dispatch Input")
        generic_send.clicked.connect(lambda: self.window.engine.handle_input(self.generic_action.currentText(), self.generic_value.text(), room=self.window.engine.active_room))
        sensor_layout.addRow("Type", self.generic_action)
        sensor_layout.addRow("Value", self.generic_value)
        sensor_layout.addRow(generic_send)

        layout.addWidget(keypad_box, 0, 0)
        layout.addWidget(rfid_box, 0, 1)
        layout.addWidget(sequence_box, 1, 0)
        layout.addWidget(sensor_box, 1, 1)

    def refresh(self) -> None:
        return
