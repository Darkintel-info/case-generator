# =============================================================================
# Tool Name: Case Generator - Directory Builder
# Version:   2.0
# Author:    Todd G. Shipley, CFE, CFCE
# Org:       Dark Intel | www.darkintel.info
# Copyright: 2025 Dark Intel. All rights reserved.
# License:   Proprietary - Dark Intel
# =============================================================================

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional


class DirectoryBuilder:
    """
    Parses a template directory list and builds the folder structure
    under a case root directory. The case root folder name is derived
    from the case number, case name, and UTC timestamp.
    """

    def __init__(
        self,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        event_callback: Optional[Callable[[str, str], None]] = None,
    ):
        self.progress_callback = progress_callback or (lambda p, m: None)
        self.event_callback = event_callback or (lambda level, msg: None)

    def build_case_folder_name(
        self,
        case_number: str,
        case_name: str,
        examiner: str,
    ) -> str:
        """
        Build the root case folder name in the format:
        CaseNumber_CaseName_YYYYMMDD_HHMMSS
        """
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        safe_num = self._sanitize(case_number)
        safe_name = self._sanitize(case_name)

        parts = [p for p in [safe_num, safe_name, timestamp] if p]
        folder_name = "_".join(parts)

        # Enforce max length, preserving timestamp
        max_len = 120
        if len(folder_name) > max_len:
            ts_suffix = f"_{timestamp}"
            allowed = max_len - len(ts_suffix)
            prefix = "_".join([p for p in [safe_num, safe_name] if p])[:allowed]
            folder_name = f"{prefix}{ts_suffix}"

        return folder_name

    def build(
        self,
        root_path: Path,
        case_folder_name: str,
        directory_list: list[str],
    ) -> tuple[Path, list[str], list[str]]:
        """
        Create the case folder and all subdirectories defined in directory_list.

        Returns:
            (case_root_path, created_dirs, errors)
        """
        case_root = root_path / case_folder_name
        created = []
        errors = []

        total = len(directory_list) + 1  # +1 for root folder
        done = 0

        # Create root case folder
        try:
            case_root.mkdir(parents=True, exist_ok=False)
            created.append(str(case_root))
            self.event_callback("ACTION", f"Created root: {case_root}")
        except FileExistsError:
            errors.append(f"Case folder already exists: {case_root}")
            self.event_callback("ERROR", f"Folder exists: {case_root}")
            return case_root, created, errors
        except OSError as exc:
            errors.append(f"Could not create root folder: {exc}")
            self.event_callback("ERROR", f"Root creation failed: {exc}")
            return case_root, created, errors

        done += 1
        self.progress_callback(int(done / total * 100), f"Created root folder")

        # Create each subdirectory
        for raw_path in directory_list:
            # Strip leading/trailing slashes and whitespace
            clean = raw_path.strip().strip("/").strip("\\")
            if not clean:
                continue

            # On Windows convert forward slashes to Path separators
            sub = Path(*clean.replace("\\", "/").split("/"))
            target = case_root / sub

            try:
                target.mkdir(parents=True, exist_ok=True)
                created.append(str(target))
                self.event_callback("ACTION", f"Created: {sub}")
            except OSError as exc:
                errors.append(f"Could not create {sub}: {exc}")
                self.event_callback("ERROR", f"Failed {sub}: {exc}")

            done += 1
            self.progress_callback(
                int(done / total * 100),
                f"Creating: {sub}"
            )

        self.progress_callback(100, "Complete")
        return case_root, created, errors

    @staticmethod
    def _sanitize(text: str) -> str:
        """Remove characters not safe for folder names across platforms."""
        safe = re.sub(r"[^\w\-]", "_", text.strip())
        safe = re.sub(r"_+", "_", safe).strip("_")
        return safe
