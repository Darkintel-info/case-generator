# =============================================================================
# Tool Name: Case Generator
# Version:   2.0
# Author:    Todd G. Shipley, CFE, CFCE
# Org:       Dark Intel | www.darkintel.info
# Copyright: 2025 Dark Intel. All rights reserved.
# License:   Proprietary - Dark Intel
#
# Part of the Dark Web Hunting Toolkit
# Companion to "Dark Web Hunting" by Todd G. Shipley
#
# Licensed for use by law enforcement, government agencies, legal professionals,
# licensed investigators, cybersecurity practitioners, academic institutions,
# students, and OSINT researchers. Users are responsible for ensuring their
# use complies with all applicable laws and organizational policies.
# =============================================================================

import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon, QLinearGradient, QPainter
from PyQt6.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QFileDialog,
    QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPlainTextEdit, QProgressBar, QPushButton,
    QScrollArea, QSizePolicy, QStatusBar, QTextEdit,
    QVBoxLayout, QWidget, QComboBox,
)

from core.config import (
    APP_NAME, APP_VERSION, APP_AUTHOR, APP_ORG, APP_URL,
    APP_COPYRIGHT, APP_DESCRIPTION, APP_LEGAL, APP_CREDITS,
    COLOR_DARK_BLUE, COLOR_MED_BLUE, COLOR_LIGHT_BLUE,
    COLOR_ACCENT, COLOR_WHITE, COLOR_LIGHT_GRAY,
    COLOR_MID_GRAY, COLOR_DARK_GRAY, COLOR_SUCCESS,
    COLOR_ERROR,
)
from core.template_manager import TemplateManager
from core.directory_builder import DirectoryBuilder


def _app_icon() -> QIcon:
    """
    Load the Dark Intel icon from the correct location whether running
    as a Python script or a compiled PyInstaller executable.
    """
    if getattr(sys, "frozen", False):
        # Running as exe - icon is in the _MEIPASS extraction folder
        icon_path = Path(sys._MEIPASS) / "assets" / "darkintel.ico"
    else:
        # Running as script - icon is next to the script
        icon_path = Path(__file__).parent / "assets" / "darkintel.ico"

    if icon_path.exists():
        return QIcon(str(icon_path))
    return QIcon()  # Fallback: no icon rather than crash


# ---------------------------------------------------------------------------
# Worker thread
# ---------------------------------------------------------------------------

class BuildWorker(QThread):
    """Runs directory creation on a background thread."""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str, list, list)
    error    = pyqtSignal(str)

    def __init__(self, root_path: Path, case_folder: str, dir_list: list):
        super().__init__()
        self.root_path   = root_path
        self.case_folder = case_folder
        self.dir_list    = dir_list

    def run(self):
        def on_progress(pct, msg):
            self.progress.emit(pct, msg)

        builder = DirectoryBuilder(progress_callback=on_progress)
        try:
            case_root, created, errors = builder.build(
                self.root_path, self.case_folder, self.dir_list
            )
            self.finished.emit(str(case_root), created, errors)
        except Exception as exc:
            self.error.emit(str(exc))


# ---------------------------------------------------------------------------
# Banner widget
# ---------------------------------------------------------------------------

class LogoBanner(QWidget):
    """Dark Intel branded header banner drawn programmatically."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event):
        with QPainter(self) as p:
            p.setRenderHint(QPainter.RenderHint.Antialiasing)

            grad = QLinearGradient(0, 0, self.width(), 0)
            grad.setColorAt(0, QColor(COLOR_DARK_BLUE))
            grad.setColorAt(1, QColor(COLOR_MED_BLUE))
            p.fillRect(self.rect(), grad)

            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(COLOR_ACCENT))
            sx, sy, sw, sh = 18, 15, 44, 60
            p.drawRoundedRect(sx, sy, sw, sh, 6, 6)
            p.setBrush(QColor(COLOR_DARK_BLUE))
            p.drawRoundedRect(sx + 5, sy + 5, sw - 10, sh - 12, 4, 4)

            p.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            p.setPen(QColor(COLOR_ACCENT))
            p.drawText(sx, sy + 5, sw, sh - 10,
                       Qt.AlignmentFlag.AlignCenter, "DI")

            p.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            p.setPen(QColor(COLOR_WHITE))
            p.drawText(74, 18, self.width() - 160, 32,
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                       "Dark Intel")

            p.setFont(QFont("Arial", 9))
            p.setPen(QColor(COLOR_LIGHT_BLUE))
            p.drawText(75, 48, self.width() - 160, 20,
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                       "Dark Web Hunting Toolkit  |  www.darkintel.info")

            p.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            p.setPen(QColor(COLOR_ACCENT))
            p.drawText(0, 10, self.width() - 14, 30,
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                       APP_NAME)

            p.setFont(QFont("Arial", 8))
            p.setPen(QColor(COLOR_LIGHT_BLUE))
            p.drawText(0, 38, self.width() - 14, 20,
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                       f"v{APP_VERSION}")


# ---------------------------------------------------------------------------
# Template editor dialog
# ---------------------------------------------------------------------------

class TemplateEditorDialog(QDialog):

    def __init__(self, manager: TemplateManager, template_name: str = "",
                 parent=None):
        super().__init__(parent)
        self.manager       = manager
        self.original_name = template_name
        self.setWindowTitle("Edit Template" if template_name else "New Template")
        self.setMinimumSize(580, 520)
        self._build_ui()
        if template_name:
            self._load(template_name)

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        lay.setContentsMargins(14, 14, 14, 14)

        row = QHBoxLayout()
        lbl = QLabel("Template Name:")
        lbl.setFixedWidth(130)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g.  Dark Web Hunting")
        row.addWidget(lbl)
        row.addWidget(self.name_edit)
        lay.addLayout(row)

        help_lbl = QLabel(
            "One folder path per line. Paths start and end with /. "
            "Subdirectories must list their parent first. "
            "Lines starting with # are comments."
        )
        help_lbl.setWordWrap(True)
        help_lbl.setStyleSheet(f"color:{COLOR_DARK_GRAY}; font-size:11px;")
        lay.addWidget(help_lbl)

        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Courier New", 10))
        self.editor.setPlaceholderText(
            "#Example template\n/Evidence/\n/Evidence/Screenshots/\n/Reports/\n"
        )
        lay.addWidget(self.editor)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _load(self, name: str):
        self.name_edit.setText(name)
        try:
            self.editor.setPlainText(self.manager.load_template_raw(name))
        except FileNotFoundError as exc:
            QMessageBox.warning(self, "Load Error", str(exc))

    def _save(self):
        name    = self.name_edit.text().strip()
        content = self.editor.toPlainText()

        if not name:
            QMessageBox.warning(self, "Validation", "Template name is required.")
            return
        if not content.strip():
            QMessageBox.warning(self, "Validation", "Template cannot be empty.")
            return

        if self.original_name and self.original_name != name:
            if self.manager.template_exists(name):
                r = QMessageBox.question(
                    self, "Overwrite?",
                    f"Template '{name}' already exists. Overwrite?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if r != QMessageBox.StandardButton.Yes:
                    return
            try:
                self.manager.delete_template(self.original_name)
            except FileNotFoundError:
                pass

        try:
            self.manager.save_template(name, content)
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Save Error", str(exc))

    def get_saved_name(self) -> str:
        return self.name_edit.text().strip()


# ---------------------------------------------------------------------------
# About dialog
# ---------------------------------------------------------------------------

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        self.setWindowIcon(_app_icon())
        self.setFixedSize(460, 400)
        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.addWidget(LogoBanner())
        info = QLabel(
            f"<b>{APP_NAME} v{APP_VERSION}</b><br><br>"
            f"{APP_DESCRIPTION}<br><br>"
            f"<b>Author:</b> {APP_AUTHOR}<br>"
            f"<b>Organization:</b> {APP_ORG}<br>"
            f"<b>Web:</b> {APP_URL}<br><br>"
            f"<b>Acknowledgements:</b><br>"
            f"{APP_CREDITS}<br><br>"
            f"<small>{APP_COPYRIGHT}</small><br><br>"
            f"<small>{APP_LEGAL}</small>"
        )
        info.setWordWrap(True)
        lay.addWidget(info)
        btn = QPushButton("Close")
        btn.clicked.connect(self.accept)
        lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------

def _section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-weight:bold; color:{COLOR_DARK_BLUE}; font-size:13px; border:none;"
    )
    return lbl


def _separator() -> QFrame:
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    sep.setStyleSheet(f"background-color:{COLOR_MID_GRAY}; max-height:1px;")
    return sep


def _field_row(label_text: str, widget: QWidget,
               extra: QWidget = None) -> QHBoxLayout:
    row = QHBoxLayout()
    lbl = QLabel(label_text)
    lbl.setFixedWidth(120)
    lbl.setStyleSheet("border:none;")
    row.addWidget(lbl)
    row.addWidget(widget)
    if extra:
        row.addWidget(extra)
    return row


def _card() -> tuple:
    frame = QFrame()
    frame.setStyleSheet(
        f"background-color:{COLOR_WHITE}; "
        f"border:1px solid {COLOR_MID_GRAY}; border-radius:5px;"
    )
    lay = QVBoxLayout(frame)
    lay.setSpacing(10)
    lay.setContentsMargins(14, 12, 14, 14)
    return frame, lay


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class CaseGeneratorWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.manager          = TemplateManager()
        self._worker          = None   # Kept as instance attr to prevent GC
        self._last_case_root  = ""

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}  |  Dark Intel")
        self.setWindowIcon(_app_icon())
        self.setMinimumWidth(640)
        # Minimum height: banner(90) + menu(30) + fields(~280) + template(~220)
        # + results(~110) + btn_panel(68) + statusbar(24) = 822 minimum
        self.setMinimumHeight(700)
        self.resize(760, 860)

        self._apply_styles()
        self._build_menu()
        self._build_ui()
        self._refresh_templates()

    # ---------------------------------------------------------------- styles

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow  {{ background:{COLOR_LIGHT_GRAY}; }}
            QWidget      {{ font-family:Arial,sans-serif; font-size:12px; }}
            QLabel       {{ color:{COLOR_DARK_GRAY}; }}

            QLineEdit {{
                border:1px solid {COLOR_MID_GRAY}; border-radius:3px;
                padding:5px 7px; background:{COLOR_WHITE}; color:{COLOR_DARK_GRAY};
                min-height:26px;
            }}
            QLineEdit:focus {{ border:2px solid {COLOR_MED_BLUE}; }}

            QComboBox {{
                border:1px solid {COLOR_MID_GRAY}; border-radius:3px;
                padding:5px 7px; background:{COLOR_WHITE}; color:{COLOR_DARK_GRAY};
                min-height:26px;
            }}
            QComboBox:focus {{ border:2px solid {COLOR_MED_BLUE}; }}

            QPushButton {{
                background:{COLOR_MED_BLUE}; color:{COLOR_WHITE};
                border:none; border-radius:4px;
                padding:6px 16px; font-weight:bold;
            }}
            QPushButton:hover    {{ background:{COLOR_DARK_BLUE}; }}
            QPushButton:disabled {{ background:{COLOR_MID_GRAY}; color:{COLOR_WHITE}; }}

            QPushButton#exitBtn       {{ background:{COLOR_DARK_GRAY}; }}
            QPushButton#exitBtn:hover {{ background:#222; }}

            QPushButton#secondaryBtn {{
                background:{COLOR_LIGHT_GRAY}; color:{COLOR_DARK_BLUE};
                border:1px solid {COLOR_MED_BLUE};
            }}
            QPushButton#secondaryBtn:hover {{ background:{COLOR_LIGHT_BLUE}; }}

            QPushButton#openBtn       {{ background:{COLOR_SUCCESS}; color:{COLOR_WHITE}; font-weight:bold; }}
            QPushButton#openBtn:hover {{ background:#1B5E20; }}

            QProgressBar {{
                border:1px solid {COLOR_MID_GRAY}; border-radius:3px;
                background:{COLOR_WHITE}; text-align:center; height:20px;
            }}
            QProgressBar::chunk {{ background:{COLOR_MED_BLUE}; border-radius:2px; }}

            QTextEdit, QPlainTextEdit {{
                border:1px solid {COLOR_MID_GRAY}; border-radius:3px;
                background:{COLOR_WHITE}; color:{COLOR_DARK_GRAY};
                font-family:"Courier New",monospace; font-size:11px;
            }}

            QMenuBar   {{ background:{COLOR_DARK_BLUE}; color:{COLOR_WHITE}; }}
            QMenuBar::item:selected {{ background:{COLOR_MED_BLUE}; }}
            QMenu      {{ background:{COLOR_WHITE}; border:1px solid {COLOR_MID_GRAY}; }}
            QMenu::item:selected {{ background:{COLOR_LIGHT_BLUE}; }}

            QStatusBar {{
                background:{COLOR_DARK_BLUE}; color:{COLOR_LIGHT_BLUE};
                font-size:11px;
            }}
            QScrollArea {{ border:none; background:{COLOR_LIGHT_GRAY}; }}
        """)

    # ----------------------------------------------------------------- menu

    def _build_menu(self):
        mb = self.menuBar()

        fm = mb.addMenu("File")
        fm.addAction("Open Templates Folder").triggered.connect(
            self._open_templates_folder)
        fm.addSeparator()
        fm.addAction("Exit").triggered.connect(self.close)

        tm = mb.addMenu("Templates")
        tm.addAction("New Template...").triggered.connect(self._new_template)
        tm.addAction("Edit Selected Template...").triggered.connect(
            self._edit_template)
        tm.addSeparator()
        tm.addAction("Delete Selected Template").triggered.connect(
            self._delete_template)

        hm = mb.addMenu("Help")
        hm.addAction(f"About {APP_NAME}...").triggered.connect(self._show_about)

    # ------------------------------------------------------------------- UI

    def _build_ui(self):
        # Outer shell: banner + scrollable body
        outer = QWidget()
        outer_lay = QVBoxLayout(outer)
        outer_lay.setSpacing(0)
        outer_lay.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(outer)

        outer_lay.addWidget(LogoBanner())

        # Scroll area so nothing is ever clipped at any window size
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # stretch=1 so scroll area yields space to the fixed button panel below
        outer_lay.addWidget(scroll, stretch=1)

        body = QWidget()
        body.setStyleSheet(f"background:{COLOR_LIGHT_GRAY};")
        scroll.setWidget(body)

        body_lay = QVBoxLayout(body)
        body_lay.setSpacing(14)
        body_lay.setContentsMargins(18, 16, 18, 20)

        # ---- Card 1: Investigation Details ----
        card1, c1 = _card()
        c1.addWidget(_section_label("Investigation Details"))
        c1.addWidget(_separator())

        self.examiner_edit  = QLineEdit()
        self.case_ref_edit  = QLineEdit()
        self.root_edit      = QLineEdit()

        self.examiner_edit.setPlaceholderText(
            "Full name of the examining investigator")
        self.case_ref_edit.setPlaceholderText(
            "Case number, case name, or both  e.g.  2025-001  or  2025-001 SilkRoad")
        self.root_edit.setPlaceholderText(
            "Base directory where the case folder will be created")

        browse_btn = QPushButton("Browse...")
        browse_btn.setObjectName("secondaryBtn")
        browse_btn.setFixedWidth(100)
        browse_btn.setFixedHeight(36)
        browse_btn.clicked.connect(self._browse_root)

        c1.addLayout(_field_row("Examiner Name:",    self.examiner_edit))
        c1.addLayout(_field_row("Case Number/Name:", self.case_ref_edit))
        c1.addLayout(_field_row("Case Root:",        self.root_edit, browse_btn))

        self.folder_preview = QLabel("")
        self.folder_preview.setStyleSheet(
            f"color:{COLOR_MED_BLUE}; font-size:11px; "
            f"border:none; font-style:italic; padding-left:4px;"
        )
        self.folder_preview.setWordWrap(True)
        c1.addWidget(self.folder_preview)

        body_lay.addWidget(card1)

        # ---- Card 2: Template ----
        card2, c2 = _card()
        c2.addWidget(_section_label("Template"))
        c2.addWidget(_separator())

        self.template_combo = QComboBox()
        self.template_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.template_combo.currentTextChanged.connect(
            self._on_template_changed)

        new_btn  = QPushButton("New");    new_btn.setObjectName("secondaryBtn")
        edit_btn = QPushButton("Edit");   edit_btn.setObjectName("secondaryBtn")
        del_btn  = QPushButton("Delete"); del_btn.setObjectName("secondaryBtn")
        new_btn.setFixedWidth(58);  new_btn.clicked.connect(self._new_template)
        edit_btn.setFixedWidth(58); edit_btn.clicked.connect(self._edit_template)
        del_btn.setFixedWidth(68);  del_btn.clicked.connect(self._delete_template)

        tmpl_row = QHBoxLayout()
        lbl_t = QLabel("Template:"); lbl_t.setFixedWidth(120)
        lbl_t.setStyleSheet("border:none;")
        tmpl_row.addWidget(lbl_t)
        tmpl_row.addWidget(self.template_combo)
        tmpl_row.addWidget(new_btn)
        tmpl_row.addWidget(edit_btn)
        tmpl_row.addWidget(del_btn)
        c2.addLayout(tmpl_row)

        self.tmpl_preview = QTextEdit()
        self.tmpl_preview.setReadOnly(True)
        self.tmpl_preview.setFixedHeight(130)
        self.tmpl_preview.setPlaceholderText(
            "Select a template to preview its folder structure.")
        c2.addWidget(self.tmpl_preview)

        body_lay.addWidget(card2)

        # ---- Build / Exit buttons - inside scroll body, directly below template ----
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.build_btn = QPushButton("Build Directory Structure")
        self.build_btn.setFixedHeight(44)
        self.build_btn.setStyleSheet(f"""
            QPushButton {{
                background:{COLOR_ACCENT}; color:{COLOR_DARK_BLUE};
                border:none; border-radius:5px;
                font-size:14px; font-weight:bold; padding:8px 24px;
            }}
            QPushButton:hover    {{ background:#D4B85A; }}
            QPushButton:disabled {{ background:{COLOR_MID_GRAY}; color:{COLOR_WHITE}; }}
        """)
        self.build_btn.clicked.connect(self._build)

        exit_btn = QPushButton("Exit")
        exit_btn.setObjectName("exitBtn")
        exit_btn.setFixedHeight(44)
        exit_btn.setFixedWidth(100)
        exit_btn.clicked.connect(self.close)

        btn_row.addWidget(self.build_btn)
        btn_row.addWidget(exit_btn)
        body_lay.addLayout(btn_row)

        # ---- Progress bar ----
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        body_lay.addWidget(self.progress_bar)

        # ---- Result log ----
        self.result_log = QTextEdit()
        self.result_log.setReadOnly(True)
        self.result_log.setFixedHeight(110)
        self.result_log.setPlaceholderText(
            "Build results will appear here after clicking "
            "'Build Directory Structure'.")
        body_lay.addWidget(self.result_log)

        # ---- Open folder button (hidden until a successful build) ----
        self.open_folder_btn = QPushButton("Open Case Folder in Explorer")
        self.open_folder_btn.setObjectName("openBtn")
        self.open_folder_btn.setFixedHeight(36)
        self.open_folder_btn.setVisible(False)
        self.open_folder_btn.clicked.connect(self._open_last_case_folder)
        body_lay.addWidget(self.open_folder_btn)

        body_lay.addStretch(1)

        # ---- Status bar ----
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(
            f"{APP_NAME} v{APP_VERSION}  |  {APP_ORG}  |  {APP_URL}")

        # Live folder preview
        self.case_ref_edit.textChanged.connect(self._update_preview)
        self.root_edit.textChanged.connect(self._update_preview)

    # ------------------------------------------------------- template ops

    def _refresh_templates(self, select_name: str = ""):
        self.template_combo.blockSignals(True)
        self.template_combo.clear()
        templates = self.manager.list_templates()
        if templates:
            self.template_combo.addItems(templates)
            if select_name and select_name in templates:
                self.template_combo.setCurrentText(select_name)
            self._on_template_changed(self.template_combo.currentText())
        else:
            self.tmpl_preview.setPlainText(
                "No templates found. Click 'New' to create one.")
        self.template_combo.blockSignals(False)

    def _on_template_changed(self, name: str):
        if not name:
            self.tmpl_preview.clear()
            return
        try:
            dirs = self.manager.load_template(name)
            self.tmpl_preview.setPlainText(
                "\n".join(dirs) if dirs else "(empty)")
        except FileNotFoundError:
            self.tmpl_preview.setPlainText("Template file not found.")

    def _new_template(self):
        dlg = TemplateEditorDialog(self.manager, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name = dlg.get_saved_name()
            self._refresh_templates(select_name=name)
            self.status_bar.showMessage(f"Template '{name}' created.")

    def _edit_template(self):
        name = self.template_combo.currentText()
        if not name:
            QMessageBox.information(self, "No Template",
                                    "Select a template to edit.")
            return
        dlg = TemplateEditorDialog(
            self.manager, template_name=name, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            saved = dlg.get_saved_name()
            self._refresh_templates(select_name=saved)
            self.status_bar.showMessage(f"Template '{saved}' saved.")

    def _delete_template(self):
        name = self.template_combo.currentText()
        if not name:
            QMessageBox.information(self, "No Template",
                                    "Select a template to delete.")
            return
        r = QMessageBox.question(
            self, "Delete Template",
            f"Delete template '{name}'? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if r == QMessageBox.StandardButton.Yes:
            try:
                self.manager.delete_template(name)
                self._refresh_templates()
                self.status_bar.showMessage(f"Template '{name}' deleted.")
            except Exception as exc:
                QMessageBox.critical(self, "Delete Error", str(exc))

    def _open_templates_folder(self):
        tmpl_dir = self.manager.get_templates_dir()
        # When running as a compiled exe, briefly tell the user where
        # templates are stored since it is not next to the executable
        if self.manager.is_user_data_dir():
            self.status_bar.showMessage(
                f"Templates folder: {tmpl_dir}")
        self._open_path(str(tmpl_dir))

    # ----------------------------------------------------- field helpers

    def _browse_root(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Case Root Directory", str(Path.home()))
        if folder:
            self.root_edit.setText(folder)

    def _update_preview(self):
        ref  = self.case_ref_edit.text().strip()
        root = self.root_edit.text().strip()
        if not ref:
            self.folder_preview.setText("")
            return
        try:
            folder = DirectoryBuilder().build_case_folder_name(ref, "", "")
            sep    = "\\" if sys.platform == "win32" else "/"
            prefix = f"{root}{sep}" if root else ""
            self.folder_preview.setText(f"Folder: {prefix}{folder}")
        except Exception:
            self.folder_preview.setText("")

    # --------------------------------------------------------------- build

    def _build(self):
        examiner  = self.examiner_edit.text().strip()
        case_ref  = self.case_ref_edit.text().strip()
        root_text = self.root_edit.text().strip()
        tmpl_name = self.template_combo.currentText()

        problems = []
        if not examiner:  problems.append("Examiner Name is required.")
        if not case_ref:  problems.append("Case Number/Name is required.")
        if not root_text: problems.append("Case Root directory is required.")
        if not tmpl_name: problems.append("Please select a template.")

        if problems:
            QMessageBox.warning(self, "Missing Information",
                                "\n".join(problems))
            return

        root_path = Path(root_text)
        if not root_path.exists():
            r = QMessageBox.question(
                self, "Directory Not Found",
                f"'{root_path}' does not exist.\nCreate it now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if r != QMessageBox.StandardButton.Yes:
                return
            try:
                root_path.mkdir(parents=True)
            except OSError as exc:
                QMessageBox.critical(self, "Error",
                                     f"Could not create directory:\n{exc}")
                return

        try:
            dir_list = self.manager.load_template(tmpl_name)
        except FileNotFoundError as exc:
            QMessageBox.critical(self, "Template Error", str(exc))
            return

        case_folder = DirectoryBuilder().build_case_folder_name(
            case_ref, "", examiner)

        r = QMessageBox.question(
            self, "Confirm Build",
            f"Create directory structure?\n\n"
            f"Root folder:  {root_path / case_folder}\n"
            f"Template:     {tmpl_name}\n"
            f"Folders:      {len(dir_list)}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if r != QMessageBox.StandardButton.Yes:
            return

        # Reset UI
        self.result_log.clear()
        self.result_log.setStyleSheet("")
        self.open_folder_btn.setVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.build_btn.setEnabled(False)
        self.status_bar.showMessage("Building directory structure...")

        # Create worker and keep a strong reference on self so GC never
        # collects it between .start() and the finished signal
        self._worker = BuildWorker(root_path, case_folder, dir_list)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_build_finished)
        self._worker.error.connect(self._on_build_error)
        self._worker.start()

    def _on_progress(self, percent: int, message: str):
        self.progress_bar.setValue(percent)
        if message:
            self.status_bar.showMessage(message)

    def _on_build_finished(self, case_root: str,
                            created: list, errors: list):
        self._last_case_root = case_root
        self.build_btn.setEnabled(True)

        lines = [
            f"Case folder : {case_root}",
            f"Directories : {len(created)} created",
        ]

        if errors:
            lines.append(f"\nErrors ({len(errors)}):")
            lines.extend(f"  {e}" for e in errors)
            self.result_log.setStyleSheet(
                f"color:{COLOR_ERROR}; background:{COLOR_WHITE};")
            self.status_bar.showMessage(
                f"Build finished with {len(errors)} error(s).")
        else:
            lines.append("\nAll directories created successfully.")
            self.result_log.setStyleSheet(
                f"color:{COLOR_SUCCESS}; background:{COLOR_WHITE};")
            self.status_bar.showMessage(
                f"Build complete. {len(created)} directories created.")
            # Reveal the open-folder button; investigator decides if they
            # want to open it or go straight to building another case
            self.open_folder_btn.setVisible(True)

        self.result_log.setPlainText("\n".join(lines))
        # Release worker reference
        self._worker = None

    def _on_build_error(self, message: str):
        self.build_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self._worker = None
        QMessageBox.critical(self, "Build Error", message)
        self.status_bar.showMessage("Build failed.")

    def _open_last_case_folder(self):
        if self._last_case_root:
            self._open_path(self._last_case_root)

    # ------------------------------------------------------------- helpers

    @staticmethod
    def _open_path(path: str):
        if sys.platform == "win32":
            subprocess.Popen(["explorer", path])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def _show_about(self):
        AboutDialog(self).exec()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORG)
    app.setOrganizationDomain(APP_URL)
    app.setWindowIcon(_app_icon())
    window = CaseGeneratorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
