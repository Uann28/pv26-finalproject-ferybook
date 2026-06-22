from PySide6.QtCore import QObject, Signal, QSettings, Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCharFormat, QColor


def style_calendar(date_edit):
    cal = date_edit.calendarWidget()
    if not cal:
        return
    cal.setStyleSheet(
        "QCalendarWidget QWidget { background-color: #FFFFFF; color: #000000; }"
        "QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #37474F; }"
        "QCalendarWidget QToolButton { color: #FFFFFF; background-color: transparent;"
        " font-size: 13px; font-weight: bold; }"
        "QCalendarWidget QSpinBox { color: #FFFFFF; background-color: #37474F; }"
        "QCalendarWidget QAbstractItemView:enabled {"
        " background-color: #FFFFFF; color: #000000;"
        " selection-background-color: #CFE0FF; selection-color: #000000; }"
        "QCalendarWidget QAbstractItemView:disabled { color: #B0B0B0; }"
    )
    fmt = QTextCharFormat()
    fmt.setForeground(QColor("#000000"))
    fmt.setBackground(QColor("#FFFFFF"))
    for day in (Qt.Monday, Qt.Tuesday, Qt.Wednesday, Qt.Thursday,
                Qt.Friday, Qt.Saturday, Qt.Sunday):
        cal.setWeekdayTextFormat(day, fmt)

DARK_STYLESHEET = """
* { font-family: 'Segoe UI', 'Arial', sans-serif; }

QMainWindow, QDialog { background-color: #1E1E2E; }
QWidget { background-color: #1E1E2E; color: #CDD6F4; font-size: 13px; }

/* ── Sidebar container ── */
#sidebar {
    background-color: #1E1E2E;
    border-right: 1px solid #313244;
    min-width: 200px; max-width: 200px;
}

/* ── Logo area ── */
#logo_area {
    background-color: transparent;
}
#logo_label {
    color: #CDD6F4;
    font-size: 14px;
    font-weight: bold;
    background: transparent;
}
#subtitle_label {
    color: #585B70;
    font-size: 9px;
    background: transparent;
}

/* ── User card ── */
#user_info_frame {
    background-color: transparent;
    border: none;
}
#avatar_label {
    background-color: #45475A;
    color: #CBA6F7;
    border-radius: 20px;
    font-size: 13px;
    font-weight: bold;
    qproperty-alignment: AlignCenter;
}
#user_name_label { color: #6C7086; font-size: 10px; font-weight: normal; background: transparent; }
#role_badge_admin {
    background-color: #1E3A5F;
    color: #89B4FA;
    border-radius: 6px;
    padding: 1px 7px;
    font-size: 9px;
    font-weight: bold;
}
#role_badge_petugas {
    background-color: #1A3020;
    color: #A6E3A1;
    border-radius: 6px;
    padding: 1px 7px;
    font-size: 9px;
    font-weight: bold;
}

/* ── Section label ── */
#section_label {
    color: #45475A;
    font-size: 9px;
    font-weight: bold;
    padding: 8px 18px 3px 18px;
    letter-spacing: 1.5px;
}

/* ── Nav buttons ── */
#nav_button {
    background-color: transparent;
    color: #A6ADC8;
    border: none;
    font-size: 13px;
    margin: 0px 6px;
    padding: 0px;
}
#nav_button:hover { background-color: #2A2A3E; color: #CDD6F4; }

#nav_button_active {
    background-color: transparent;
    color: #CBA6F7;
    border: none;
    font-size: 13px;
    font-weight: bold;
    margin: 0px 6px;
    padding: 0px;
}

#nav_text        { color: #A6ADC8; background: transparent; font-size: 13px; }
#nav_text_active { color: #CBA6F7; background: transparent; font-size: 13px; font-weight: bold; }

/* ── Bottom section ── */
#bottom_section_frame {
    background-color: #181825;
    border-top: 1px solid #313244;
}
#theme_toggle_btn {
    background-color: #313244;
    color: #CBA6F7;
    border: 1px solid #45475A;
    border-radius: 8px;
    font-size: 12px;
    font-weight: bold;
    padding: 0px;
}
#theme_toggle_btn:hover { background-color: #45475A; color: #CDD6F4; border-color: #89B4FA; }
#logout_button {
    background-color: transparent;
    color: #F38BA8;
    border: none;
    border-radius: 0px;
    text-align: left;
    font-size: 13px;
    padding: 0px 18px;
}
#logout_button:hover { background-color: rgba(243,139,168,0.10); color: #FAB387; }

/* ── Content area ── */
#content_area  { background-color: #1E1E2E; }
#page_title    { color: #CDD6F4; font-size: 22px; font-weight: bold; }
#page_subtitle { color: #A6ADC8; font-size: 12px; }

/* ── Cards ── */
#stat_card {
    background-color: #2A2A3E;
    border-radius: 12px;
    border: 1px solid #45475A;
    padding: 20px;
    min-width: 160px;
}
#stat_card_value { color: #89B4FA; font-size: 28px; font-weight: bold; }
#stat_card_label { color: #A6ADC8; font-size: 12px; }
#stat_card_icon  { font-size: 24px; }

/* ── Buttons ── */
QPushButton {
    background-color: #313244; color: #CDD6F4;
    border: 1px solid #45475A; border-radius: 6px;
    padding: 8px 16px; font-size: 13px;
}
QPushButton:hover   { background-color: #45475A; border-color: #89B4FA; }
QPushButton:pressed { background-color: #585B70; }
#btn_primary { background-color: #1E3A5F; color: #89B4FA; border: 1px solid #89B4FA; border-radius: 6px; padding: 9px 20px; font-weight: bold; }
#btn_primary:hover { background-color: #74C7EC; color: #1E1E2E; }
#btn_success { background-color: #1A3020; color: #A6E3A1; border: 1px solid #A6E3A1; border-radius: 6px; padding: 9px 20px; font-weight: bold; }
#btn_success:hover { background-color: #94E2D5; color: #1E1E2E; }
#btn_danger  { background-color: #3A1020; color: #F38BA8; border: 1px solid #F38BA8; border-radius: 6px; padding: 9px 20px; font-weight: bold; }
#btn_danger:hover  { background-color: #EBA0AC; color: #1E1E2E; }
#btn_warning { background-color: #3A2800; color: #F9E2AF; border: 1px solid #F9E2AF; border-radius: 6px; padding: 9px 20px; font-weight: bold; }
#btn_warning:hover { background-color: #FAB387; color: #1E1E2E; }

/* ── Tables ── */
QTableWidget {
    background-color: #2A2A3E; border: 1px solid #45475A;
    border-radius: 8px; gridline-color: #313244;
    color: #CDD6F4; font-size: 12px;
    selection-background-color: #45475A;
    alternate-background-color: #252535;
}
QTableWidget::item { padding: 8px; border-bottom: 1px solid #313244; }
QTableWidget::item:selected { background-color: #45475A; color: #CBA6F7; }
QHeaderView::section {
    background-color: #313244; color: #89B4FA;
    padding: 10px 8px; border: none;
    border-bottom: 2px solid #45475A;
    font-weight: bold; font-size: 12px;
}
QHeaderView { background-color: #313244; }

/* ── Inputs ── */
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
QDateEdit, QTimeEdit, QComboBox {
    background-color: #313244; border: 1px solid #45475A;
    border-radius: 6px; padding: 8px 12px;
    color: #CDD6F4; font-size: 13px;
    selection-background-color: #45475A;
}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QDateEdit:focus, QTimeEdit:focus,
QComboBox:focus { border: 1px solid #89B4FA; background-color: #2A2A3E; }
/* combo & date: panah segitiga; time & spinbox pakai panah bawaan Qt */
QComboBox::drop-down { width: 22px; border-left: 1px solid #45475A; }
QComboBox::down-arrow, QDateEdit::down-arrow {
    image: none; width: 0; height: 0;
    border-left: 5px solid transparent; border-right: 5px solid transparent;
    border-top: 7px solid #CDD6F4;
}
QComboBox QAbstractItemView { background-color: #313244; border: 1px solid #89B4FA; color: #CDD6F4; selection-background-color: #45475A; }
QDateEdit::drop-down { width: 22px; border-left: 1px solid #45475A; }
QTimeEdit::drop-down { width: 22px; border-left: 1px solid #45475A; }
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 18px; }

/* ── Labels ── */
QLabel { color: #CDD6F4; background: transparent; }
#form_label { color: #A6ADC8; font-size: 12px; font-weight: bold; }
#section_header { color: #CBA6F7; font-size: 15px; font-weight: bold; padding: 8px 0 4px 0; border-bottom: 1px solid #45475A; }

/* ── Group Box ── */
QGroupBox { border: 1px solid #45475A; border-radius: 8px; margin-top: 12px; padding-top: 12px; color: #A6ADC8; font-weight: bold; font-size: 12px; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #CBA6F7; }

/* ── Scrollbars ── */
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical   { background: #1E1E2E; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #45475A; border-radius: 4px; min-height: 20px; }
QScrollBar:horizontal { background: #1E1E2E; height: 8px; border-radius: 4px; }
QScrollBar::handle:horizontal { background: #45475A; border-radius: 4px; }

/* ── Tab ── */
QTabWidget::pane { border: 1px solid #45475A; border-radius: 8px; background: #2A2A3E; }
QTabBar::tab { background: #313244; color: #A6ADC8; padding: 8px 20px; border-radius: 4px 4px 0 0; margin-right: 2px; }
QTabBar::tab:selected { background: #45475A; color: #CBA6F7; font-weight: bold; }

/* ── Dialogs ── */
QDialog { background-color: #1E1E2E; }
QMessageBox { background-color: #1E1E2E; }
QMessageBox QLabel { color: #CDD6F4; }
QMessageBox QPushButton { min-width: 80px; }

/* ── Status bar ── */
QStatusBar { background-color: #181825; color: #585B70; border-top: 1px solid #313244; font-size: 11px; }

/* ── Misc frames ── */
#divider     { background-color: #313244; max-height: 1px; min-height: 1px; }
#action_cell { background: transparent; }
#action_cell QPushButton { padding: 2px 10px; }
#status_cell { background: transparent; }

/* ── Badges ── */
#badge_success { background-color: #1A3020; color: #A6E3A1; border: 1px solid #A6E3A1; border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold; }
#badge_warning { background-color: #3A2800; color: #F9E2AF; border: 1px solid #F9E2AF; border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold; }
#badge_danger  { background-color: #3A1020; color: #F38BA8; border: 1px solid #F38BA8; border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold; }
#badge_info    { background-color: #1E3A5F; color: #89B4FA; border: 1px solid #89B4FA; border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold; }

/* ── Date Chip ── */
#date_chip        { background-color: #313244; color: #A6ADC8; border: 1px solid #45475A; border-radius: 14px; padding: 4px 14px; font-size: 11px; }
#date_chip:hover  { background-color: #45475A; color: #CDD6F4; }
#date_chip_active { background-color: #89B4FA; color: #1E1E2E; border: 1px solid #89B4FA; border-radius: 14px; padding: 4px 14px; font-size: 11px; font-weight: bold; }

/* Calendar: tampilan dasar diatur lewat style_calendar() di kode */

/* ── Login ── */
#login_card    { background-color: #2A2A3E; border: 1px solid #45475A; border-radius: 16px; padding: 40px; }
#login_title   { color: #CBA6F7; font-size: 28px; font-weight: bold; background: transparent; }
#login_subtitle { color: #A6ADC8; font-size: 13px; background: transparent; }
#login_error       { color: #F38BA8; font-size: 12px; background: transparent; }
#login_hint        { color: #585B70; font-size: 11px; background: transparent; }
#info_row          { background-color: #181825; border-radius: 6px; }
"""


LIGHT_STYLESHEET = """
* { font-family: 'Segoe UI', 'Arial', sans-serif; }

QMainWindow, QDialog { background-color: #F0F2F5; }
QWidget { background-color: #F0F2F5; color: #1A1A2E; font-size: 13px; }

/* ── Sidebar container ── */
#sidebar {
    background-color: #1A237E;
    border-right: none;
    min-width: 200px; max-width: 200px;
}

/* ── Logo area ── */
#logo_area {
    background-color: transparent;
}
#logo_label {
    color: #FFFFFF;
    font-size: 14px;
    font-weight: bold;
    background: transparent;
}
#subtitle_label {
    color: #9FA8DA;
    font-size: 9px;
    background: transparent;
}

/* ── User card ── */
#user_info_frame {
    background-color: transparent;
    border: none;
}
#avatar_label {
    background-color: rgba(255,255,255,0.20);
    color: #FFFFFF;
    border-radius: 20px;
    font-size: 13px;
    font-weight: bold;
    qproperty-alignment: AlignCenter;
}
#user_name_label { color: #9FA8DA; font-size: 10px; font-weight: normal; background: transparent; }
#role_badge_admin {
    background-color: rgba(255,255,255,0.18);
    color: #E8EAF6;
    border-radius: 6px;
    padding: 1px 7px;
    font-size: 9px;
    font-weight: bold;
}
#role_badge_petugas {
    background-color: rgba(76,175,80,0.28);
    color: #C8E6C9;
    border-radius: 6px;
    padding: 1px 7px;
    font-size: 9px;
    font-weight: bold;
}

/* ── Section label ── */
#section_label {
    color: #7986CB;
    font-size: 9px;
    font-weight: bold;
    padding: 8px 18px 3px 18px;
    letter-spacing: 1.5px;
}

/* ── Nav buttons ── */
#nav_button {
    background-color: transparent;
    color: #C5CAE9;
    border: none;
    font-size: 13px;
    margin: 0px 6px;
    padding: 0px;
}
#nav_button:hover { background-color: rgba(255,255,255,0.10); color: #FFFFFF; }

#nav_button_active {
    background-color: transparent;
    color: #FFFFFF;
    border: none;
    font-size: 13px;
    font-weight: bold;
    margin: 0px 6px;
    padding: 0px;
}

#nav_text        { color: #C5CAE9; background: transparent; font-size: 13px; }
#nav_text_active { color: #FFFFFF;  background: transparent; font-size: 13px; font-weight: bold; }

/* ── Bottom section ── */
#bottom_section_frame {
    background-color: #151B6E;
    border-top: 1px solid rgba(255,255,255,0.10);
}
#theme_toggle_btn {
    background-color: rgba(255,255,255,0.12);
    color: #FFFFFF;
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 8px;
    font-size: 12px;
    font-weight: bold;
    padding: 0px;
}
#theme_toggle_btn:hover { background-color: rgba(255,255,255,0.22); border-color: rgba(255,255,255,0.50); }
#logout_button {
    background-color: transparent;
    color: #EF9A9A;
    border: none;
    border-radius: 0px;
    text-align: left;
    font-size: 13px;
    padding: 0px 18px;
}
#logout_button:hover { background-color: rgba(244,67,54,0.18); color: #FFCDD2; }

/* ── Content area ── */
#content_area  { background-color: #F0F2F5; }
#page_title    { color: #1A237E; font-size: 22px; font-weight: bold; }
#page_subtitle { color: #546E7A; font-size: 12px; }

/* ── Cards ── */
#stat_card { background-color: #FFFFFF; border-radius: 12px; border: 1px solid #CFD8DC; padding: 20px; min-width: 160px; }
#stat_card_value { color: #1A237E; font-size: 28px; font-weight: bold; }
#stat_card_label { color: #546E7A; font-size: 12px; }
#stat_card_icon  { font-size: 24px; }

/* ── Buttons ── */
QPushButton { background-color: #FFFFFF; color: #37474F; border: 1px solid #B0BEC5; border-radius: 6px; padding: 8px 16px; font-size: 13px; }
QPushButton:hover   { background-color: #ECEFF1; border-color: #1A237E; color: #1A237E; }
QPushButton:pressed { background-color: #CFD8DC; }
#btn_primary { background-color: #1A237E; color: #FFFFFF; border: 1px solid #1A237E; border-radius: 6px; padding: 9px 20px; font-weight: bold; }
#btn_primary:hover { background-color: #283593; }
#btn_success { background-color: #2E7D32; color: #FFFFFF; border: 1px solid #2E7D32; border-radius: 6px; padding: 9px 20px; font-weight: bold; }
#btn_success:hover { background-color: #1B5E20; }
#btn_danger  { background-color: #C62828; color: #FFFFFF; border: 1px solid #C62828; border-radius: 6px; padding: 9px 20px; font-weight: bold; }
#btn_danger:hover  { background-color: #B71C1C; }
#btn_warning { background-color: #E65100; color: #FFFFFF; border: 1px solid #E65100; border-radius: 6px; padding: 9px 20px; font-weight: bold; }
#btn_warning:hover { background-color: #BF360C; }

/* ── Tables ── */
QTableWidget { background-color: #FFFFFF; border: 1px solid #CFD8DC; border-radius: 8px; gridline-color: #ECEFF1; color: #1A1A2E; font-size: 12px; selection-background-color: #C5CAE9; alternate-background-color: #F5F5F5; }
QTableWidget::item { padding: 8px; border-bottom: 1px solid #ECEFF1; color: #1A1A2E; }
QTableWidget::item:selected { background-color: #C5CAE9; color: #1A237E; }
QHeaderView::section { background-color: #E8EAF6; color: #1A237E; padding: 10px 8px; border: none; border-bottom: 2px solid #3949AB; font-weight: bold; font-size: 12px; }
QHeaderView { background-color: #E8EAF6; }

/* ── Inputs ── */
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QComboBox {
    background-color: #FFFFFF; border: 1px solid #B0BEC5; border-radius: 6px;
    padding: 8px 12px; color: #1A1A2E; font-size: 13px; selection-background-color: #C5CAE9;
}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QDateEdit:focus, QTimeEdit:focus, QComboBox:focus { border: 1px solid #3949AB; }
/* combo & date: panah segitiga; time & spinbox pakai panah bawaan Qt */
QComboBox::drop-down { width: 22px; border-left: 1px solid #B0BEC5; }
QComboBox::down-arrow, QDateEdit::down-arrow {
    image: none; width: 0; height: 0;
    border-left: 5px solid transparent; border-right: 5px solid transparent;
    border-top: 7px solid #37474F;
}
QComboBox QAbstractItemView { background-color: #FFFFFF; border: 1px solid #3949AB; color: #1A1A2E; selection-background-color: #C5CAE9; }
QDateEdit::drop-down { width: 22px; border-left: 1px solid #B0BEC5; }
QTimeEdit::drop-down { width: 22px; border-left: 1px solid #B0BEC5; }
QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 18px; }

/* ── Labels ── */
QLabel { color: #1A1A2E; background: transparent; }
#form_label { color: #546E7A; font-size: 12px; font-weight: bold; }
#section_header { color: #1A237E; font-size: 15px; font-weight: bold; padding: 8px 0 4px 0; border-bottom: 2px solid #3949AB; }

/* ── Group Box ── */
QGroupBox { border: 1px solid #CFD8DC; border-radius: 8px; margin-top: 12px; padding-top: 12px; color: #546E7A; font-weight: bold; font-size: 12px; background-color: #FFFFFF; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #1A237E; }

/* ── Scrollbars ── */
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical   { background: #ECEFF1; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #B0BEC5; border-radius: 4px; min-height: 20px; }
QScrollBar:horizontal { background: #ECEFF1; height: 8px; border-radius: 4px; }
QScrollBar::handle:horizontal { background: #B0BEC5; border-radius: 4px; }

/* ── Tab ── */
QTabWidget::pane { border: 1px solid #CFD8DC; border-radius: 8px; background: #FFFFFF; }
QTabBar::tab { background: #ECEFF1; color: #546E7A; padding: 8px 20px; border-radius: 4px 4px 0 0; margin-right: 2px; }
QTabBar::tab:selected { background: #C5CAE9; color: #1A237E; font-weight: bold; }

/* ── Dialogs ── */
QDialog { background-color: #F0F2F5; }
QMessageBox { background-color: #F0F2F5; }
QMessageBox QLabel { color: #1A1A2E; }
QMessageBox QPushButton { min-width: 80px; }

/* ── Status bar ── */
QStatusBar { background-color: #E8EAF6; color: #546E7A; border-top: 1px solid #C5CAE9; font-size: 11px; }

/* ── Misc ── */
#divider     { background-color: rgba(255,255,255,0.12); max-height: 1px; min-height: 1px; }
#action_cell { background: transparent; }
#action_cell QPushButton { padding: 2px 10px; }
#status_cell { background: transparent; }

/* ── Badges ── */
#badge_success { background-color: #E8F5E9; color: #2E7D32; border: 1px solid #4CAF50; border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold; }
#badge_warning { background-color: #FFF3E0; color: #E65100; border: 1px solid #FF9800; border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold; }
#badge_danger  { background-color: #FFEBEE; color: #C62828; border: 1px solid #F44336; border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold; }
#badge_info    { background-color: #E8EAF6; color: #1A237E; border: 1px solid #3949AB; border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold; }

/* ── Date Chip ── */
#date_chip        { background-color: #ECEFF1; color: #546E7A; border: 1px solid #CFD8DC; border-radius: 14px; padding: 4px 14px; font-size: 11px; }
#date_chip:hover  { background-color: #CFD8DC; color: #263238; }
#date_chip_active { background-color: #3949AB; color: #FFFFFF; border: 1px solid #3949AB; border-radius: 14px; padding: 4px 14px; font-size: 11px; font-weight: bold; }

/* Calendar: tampilan dasar diatur lewat style_calendar() di kode */

/* ── Login ── */
#login_card    { background-color: #FFFFFF; border: 1px solid #CFD8DC; border-radius: 16px; padding: 40px; }
#login_title   { color: #1A237E; font-size: 28px; font-weight: bold; background: transparent; }
#login_subtitle { color: #546E7A; font-size: 13px; background: transparent; }
#login_error       { color: #C62828; font-size: 12px; background: transparent; }
#login_hint        { color: #90A4AE; font-size: 11px; background: transparent; }
#info_row          { background-color: #F4F6FB; border: 1px solid #E0E4EC; border-radius: 6px; }
"""


class ThemeManager(QObject):
    """ ThemeManager """

    theme_changed = Signal(str)
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._settings = QSettings("FerryBook", "Theme")
        self._current  = self._settings.value("theme", "dark")
        self._initialized = True

    @classmethod
    def instance(cls):
        return cls()

    def get_current_theme(self) -> str:
        return self._current

    def get_stylesheet(self, theme: str) -> str:
        return LIGHT_STYLESHEET if theme == "light" else DARK_STYLESHEET

    def apply_theme(self, app: QApplication = None):
        app = app or QApplication.instance()
        if app:
            app.setStyleSheet(self.get_stylesheet(self._current))

    def toggle_theme(self):
        self._current = "light" if self._current == "dark" else "dark"
        self._settings.setValue("theme", self._current)
        self.apply_theme()
        self.theme_changed.emit(self._current)
