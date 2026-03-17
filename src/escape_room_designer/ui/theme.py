"""Dark professional UI theme."""


def build_stylesheet() -> str:
    return """
    QWidget {
        background: #161a20;
        color: #d9e0ee;
        font-size: 10pt;
    }
    QMainWindow, QDockWidget {
        background: #13171d;
    }
    QFrame#Panel {
        background: #1d232d;
        border: 1px solid #2d3644;
        border-radius: 8px;
    }
    QListWidget {
        background: #11161d;
        border-right: 1px solid #2b3442;
        outline: none;
    }
    QListWidget::item {
        padding: 10px;
        margin: 2px 4px;
        border-radius: 6px;
    }
    QListWidget::item:selected {
        background: #2a3950;
        color: #e8f1ff;
    }
    QPushButton {
        background: #2a3d58;
        border: 1px solid #3e5578;
        border-radius: 6px;
        padding: 6px 10px;
    }
    QPushButton:hover { background: #345073; }
    QToolBar {
        spacing: 6px;
        border: none;
        background: #1b212a;
        padding: 4px;
    }
    QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTreeWidget, QTableWidget {
        background: #0f141b;
        border: 1px solid #2c3643;
        border-radius: 6px;
        padding: 4px;
    }
    QGraphicsView {
        background: #0d1218;
        border: 1px solid #283241;
    }
    QTabWidget::pane {
        border: 1px solid #2a3442;
    }
    QHeaderView::section {
        background: #222b36;
        color: #d9e0ee;
        border: none;
        padding: 4px;
    }
    """
