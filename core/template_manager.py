# =============================================================================
# Tool Name: Case Generator - Template Manager
# Version:   2.0
# Author:    Todd G. Shipley, CFE, CFCE
# Org:       Dark Intel, Inc | www.darkintel.info
# Copyright: 2026 Dark Intel, Inc. All rights reserved.
# License:   Proprietary - Dark Intel
#
# Part of the Dark Web Hunting Toolkit
# Companion to "Dark Web Hunting" by Todd G. Shipley
# =============================================================================

import shutil
import sys
from pathlib import Path
from typing import Optional


def _get_user_templates_dir() -> Path:
    """
    Return the writable user-level templates directory.

    When running as a PyInstaller .exe, we cannot write back into the
    executable itself. Instead we use the platform's standard location
    for user application data:

      Windows : %LOCALAPPDATA%\\DarkIntel\\CaseGenerator\\templates
      macOS   : ~/Library/Application Support/DarkIntel/CaseGenerator/templates
      Linux   : ~/.local/share/DarkIntel/CaseGenerator/templates

    On the very first run we seed this directory by copying the bundled
    default templates out of the executable so the user starts with a
    full set.
    """
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Local"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"

    user_dir = base / "DarkIntel" / "CaseGenerator" / "templates"
    user_dir.mkdir(parents=True, exist_ok=True)

    # Seed built-in templates on first run (only if directory is empty)
    if not any(user_dir.glob("*.txt")):
        _seed_default_templates(user_dir)

    return user_dir


def _get_bundled_templates_dir() -> Optional[Path]:
    """
    Return the path to the read-only bundled templates directory.

    When running as a PyInstaller onefile exe, sys._MEIPASS points to
    the temporary extraction directory. When running as a plain Python
    script, templates live next to the main script.
    """
    if getattr(sys, "frozen", False):
        # Running as compiled exe - templates extracted to _MEIPASS
        return Path(sys._MEIPASS) / "templates"
    else:
        # Running as script - templates next to this file's grandparent
        return Path(__file__).parent.parent / "templates"


def _seed_default_templates(dest: Path) -> None:
    """
    Copy all bundled default templates into the user's writable directory.
    Called once on first run when the user directory is empty.
    """
    bundled = _get_bundled_templates_dir()
    if bundled and bundled.exists():
        for src_file in bundled.glob("*.txt"):
            dest_file = dest / src_file.name
            if not dest_file.exists():
                shutil.copy2(src_file, dest_file)


class TemplateManager:
    """
    Manages loading, saving, listing, and deleting case folder templates.

    When running as a compiled Windows executable, templates are stored in
    the user's AppData folder so they remain editable. When running as a
    Python script, templates are stored in the templates/ subfolder next
    to the script as before.
    """

    def __init__(self, templates_dir: Optional[Path] = None):
        if templates_dir is not None:
            # Explicit override (used in tests)
            self.templates_dir = Path(templates_dir)
        elif getattr(sys, "frozen", False):
            # Running as PyInstaller exe - use writable user directory
            self.templates_dir = _get_user_templates_dir()
        else:
            # Running as script - use local templates/ folder
            self.templates_dir = Path(__file__).parent.parent / "templates"

        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def list_templates(self) -> list[str]:
        """Return sorted list of template display names (without extension)."""
        return [
            self._path_to_display_name(p)
            for p in sorted(self.templates_dir.glob("*.txt"))
        ]

    def load_template(self, display_name: str) -> list[str]:
        """
        Load a template by display name and return its directory paths
        as a list of strings (comments and blank lines removed).
        """
        path = self._display_name_to_path(display_name)
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {display_name}")

        return [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    def load_template_raw(self, display_name: str) -> str:
        """Load full raw template text including comments."""
        path = self._display_name_to_path(display_name)
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {display_name}")
        return path.read_text(encoding="utf-8")

    def save_template(self, display_name: str, content: str) -> Path:
        """Save template content to file. Creates or overwrites."""
        display_name = display_name.strip()
        if not display_name:
            raise ValueError("Template name cannot be empty.")
        path = self._display_name_to_path(display_name)
        path.write_text(content, encoding="utf-8")
        return path

    def delete_template(self, display_name: str) -> None:
        """Delete a template file."""
        path = self._display_name_to_path(display_name)
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {display_name}")
        path.unlink()

    def rename_template(self, old_name: str, new_name: str) -> None:
        """Rename a template."""
        old_path = self._display_name_to_path(old_name)
        new_path = self._display_name_to_path(new_name)
        if not old_path.exists():
            raise FileNotFoundError(f"Template not found: {old_name}")
        if new_path.exists():
            raise FileExistsError(
                f"A template named '{new_name}' already exists.")
        old_path.rename(new_path)

    def template_exists(self, display_name: str) -> bool:
        """Check whether a template with the given name exists."""
        return self._display_name_to_path(display_name).exists()

    def get_templates_dir(self) -> Path:
        """Return the templates directory path."""
        return self.templates_dir

    def is_user_data_dir(self) -> bool:
        """
        Returns True when templates are stored in the user's AppData folder
        (i.e. running as compiled exe). Used by the UI to show informational
        messages about template storage location.
        """
        return getattr(sys, "frozen", False)

    def _display_name_to_path(self, display_name: str) -> Path:
        """Convert display name to file path. Case-insensitive matching."""
        safe = display_name.strip().replace(" ", "_")
        exact = self.templates_dir / f"{safe}.txt"
        if exact.exists():
            return exact
        lower = self.templates_dir / f"{safe.lower()}.txt"
        if lower.exists():
            return lower
        return lower

    def _path_to_display_name(self, path: Path) -> str:
        """Convert file path to display name."""
        return path.stem.replace("_", " ").title()
