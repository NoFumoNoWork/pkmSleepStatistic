"""Application stylesheet and color tokens."""

APP_STYLESHEET = """
QWidget {
    font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    font-size: 10pt;
    color: #1a1a2e;
}

QMainWindow, QDialog {
    background-color: #f0f2f8;
}

QPushButton {
    background-color: #ffffff;
    border: 1px solid #c8d0e0;
    border-radius: 8px;
    padding: 8px 16px;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #eef3ff;
    border-color: #6b8cff;
}
QPushButton:pressed {
    background-color: #dce6ff;
}
QPushButton:disabled {
    color: #9aa3b5;
    background-color: #f5f6fa;
}

QPushButton#primaryButton,
QPushButton#createPokemonButton {
    background-color: #4f6ef7;
    color: #ffffff;
    border: none;
    font-weight: 600;
    min-width: 120px;
}
QPushButton#primaryButton:hover,
QPushButton#createPokemonButton:hover {
    background-color: #3d5ce6;
    color: #ffffff;
}
QPushButton#primaryButton:pressed,
QPushButton#createPokemonButton:pressed {
    background-color: #2f4ed4;
    color: #ffffff;
}

QPushButton#dangerButton {
    background-color: #fff0f0;
    color: #d32f2f;
    border: 1px solid #ffcdd2;
}
QPushButton#dangerButton:hover {
    background-color: #ffebee;
    border-color: #ef9a9a;
}

QPushButton#accentButton {
    background-color: #e8f0fe;
    color: #2b4acb;
    border: 1px solid #b8ccf9;
    font-weight: 600;
}

QLineEdit, QSpinBox, QDoubleSpinBox, QDateTimeEdit {
    background: white;
    border: 1px solid #c8d0e0;
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 24px;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateTimeEdit:focus {
    border-color: #4f6ef7;
}

QCheckBox {
    spacing: 8px;
}

QTableWidget {
    background: white;
    border: 1px solid #dde3ef;
    border-radius: 8px;
    gridline-color: #eef1f7;
}
QTableWidget::item {
    padding: 6px;
}
QHeaderView::section {
    background: #f5f7fc;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #dde3ef;
    font-weight: 600;
}

QTabWidget::pane {
    border: 1px solid #dde3ef;
    border-radius: 8px;
    background: white;
}
QTabBar::tab {
    background: #e8ecf4;
    border: 1px solid #dde3ef;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 18px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: white;
    font-weight: 600;
}

QScrollArea {
    border: none;
    background: transparent;
}

QLabel#hintLabel {
    color: #5c6370;
    font-size: 9pt;
}

QLabel#panelTitle {
    font-size: 12pt;
    font-weight: 600;
}

QToolButton#infoButton {
    border: 1px solid #c8d0e0;
    border-radius: 12px;
    background: #f5f7fc;
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
    font-weight: bold;
    color: #4f6ef7;
}
QToolButton#infoButton:hover {
    background: #e8f0fe;
}
"""

CARD_NORMAL_STYLE = """
PokemonCard {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffffff, stop:1 #f0f3fa);
    border: 1px solid #d0d8ea;
    border-radius: 14px;
}
"""

CARD_HOVER_STYLE = """
PokemonCard {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffffff, stop:1 #e8eeff);
    border: 1px solid #8aa8ff;
    border-radius: 14px;
}
"""

CARD_SELECTED_STYLE = """
PokemonCard {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #e8f0ff, stop:1 #d4e2ff);
    border: 2px solid #4f6ef7;
    border-radius: 14px;
}
"""

CARD_SKILL_GLOW = """
PokemonCard[skillType="true"] {
    border: 2px solid #7c5cff;
}
"""
