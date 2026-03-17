DARK_QSS = """
QMainWindow, QWidget { background: #11151b; color: #e6edf3; font-size: 13px; }
QGroupBox {
    border: 1px solid #2a3440; border-radius: 8px; margin-top: 8px; padding-top: 8px;
    background: #171d26;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #9fb4ca; }
QPushButton {
    background: #223248; border: 1px solid #3a4d66; border-radius: 8px;
    padding: 10px 14px; min-height: 32px; font-weight: 600;
}
QPushButton:hover { background: #2a3f5a; }
QPushButton:pressed { background: #1e2d40; }
QPushButton#danger { background: #7a2222; border-color: #a43232; }
QPushButton#danger:hover { background: #913030; }
QPushButton#success { background: #1f6a43; border-color: #2e8a59; }
QListWidget, QTextEdit, QLineEdit, QComboBox, QTableWidget {
    background: #111821; border: 1px solid #2d3a49; border-radius: 6px; padding: 6px;
}
QHeaderView::section { background: #1d2632; color: #cdd9e5; border: 0; padding: 6px; }
QTabWidget::pane { border: 1px solid #2a3440; }
QTabBar::tab { background: #1a2330; padding: 12px 18px; margin-right: 2px; }
QTabBar::tab:selected { background: #2b3d55; }
QLabel#status_ready { color: #7bd88f; font-weight: 700; }
QLabel#status_active { color: #59c2ff; font-weight: 700; }
QLabel#status_paused { color: #ffcd57; font-weight: 700; }
QLabel#status_fault, QLabel#status_reset_needed { color: #ff7070; font-weight: 700; }
"""
