DARK_THEME = """
QWidget {
    color: #E6EEF8;
    font-family: Segoe UI, Arial;
    background: transparent;
}
QMainWindow, QWidget#simulatorRoot {
    background: #0B1220;
}
QWidget#topBar {
    background: #0F1728;
    border: 1px solid #24324A;
    border-radius: 10px;
}
QWidget#pageContainer, QWidget#pageFrame, QFrame#metricCard, QListWidget#navList,
QTableWidget, QTextEdit, QPlainTextEdit, QLineEdit, QComboBox, QSpinBox,
QGraphicsView, QGroupBox {
    background: #101A2B;
    border: 1px solid #24324A;
    border-radius: 10px;
}
QFrame#metricCard {
    background: #0F1A2E;
}
QGroupBox {
    margin-top: 12px;
    padding: 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #AFC2D9;
}
QListWidget#navList {
    padding: 10px;
    font-size: 15px;
}
QListWidget#navList::item {
    min-height: 28px;
    padding: 10px 12px;
    margin: 4px 0;
    border-radius: 8px;
}
QListWidget#navList::item:selected {
    background: #163659;
    color: #E6EEF8;
    border: 1px solid #1E90FF;
}
QPushButton {
    background: #1E90FF;
    color: white;
    border: 1px solid #1C6FCC;
    border-radius: 8px;
    padding: 8px 12px;
    font-weight: 600;
}
QPushButton:hover {
    background: #3B9FFF;
}
QPushButton:pressed {
    background: #186FC9;
}
QHeaderView::section {
    background: #0F1728;
    color: #AFC2D9;
    padding: 6px;
    border: 1px solid #24324A;
}
QTableCornerButton::section {
    background: #0F1728;
    border: 1px solid #24324A;
}
QLabel#appTitle {
    font-size: 26px;
    font-weight: 700;
}
QLabel#appSubtitle, QLabel[role='secondary'] {
    color: #AFC2D9;
}
QLabel#sessionBadge {
    background: #163659;
    border: 1px solid #1E90FF;
    border-radius: 8px;
    padding: 6px 10px;
    font-weight: 700;
}
QLabel[role='success'] { color: #21C55D; }
QLabel[role='warning'] { color: #F59E0B; }
QLabel[role='error'] { color: #E63946; }
"""
