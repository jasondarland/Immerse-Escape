DARK_THEME = """
QWidget { background-color: #161a20; color: #e6e8eb; font-family: 'Segoe UI'; font-size: 12px; }
QMainWindow, QTabWidget::pane, QFrame { background-color: #161a20; }
QGroupBox { border: 1px solid #2a313b; margin-top: 12px; padding-top: 12px; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; }
QPushButton { background-color: #232a33; border: 1px solid #36404d; padding: 8px 12px; border-radius: 4px; }
QPushButton:hover { background-color: #2d3642; }
QPushButton[accent='true'] { background-color: #0f6d4a; border-color: #169867; }
QPushButton[danger='true'] { background-color: #7d1d1d; border-color: #b02a2a; }
QTableWidget, QTreeWidget, QListWidget, QTextEdit, QLineEdit, QComboBox { background-color: #1b2128; border: 1px solid #303846; }
QHeaderView::section { background-color: #20262f; padding: 6px; border: 0; }
QLabel[role='title'] { font-size: 22px; font-weight: 700; }
QLabel[role='cardTitle'] { font-size: 11px; color: #95a0ad; text-transform: uppercase; }
QLabel[status='running'] { color: #46d17c; font-weight: 700; }
QLabel[status='paused'] { color: #58a6ff; font-weight: 700; }
QLabel[status='warning'] { color: #ffbf47; font-weight: 700; }
QLabel[status='fault'] { color: #ff6b6b; font-weight: 700; }
QLabel[status='idle'] { color: #99a2ad; font-weight: 700; }
"""
