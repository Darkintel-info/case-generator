# Case Generator v2.0

**Dark Web Hunting Toolkit | Dark Intel, Inc**  
Author: Todd G. Shipley, CFE, CFCE  
Web: www.darkintel.info  
Copyright 2026 Dark Intel. All rights reserved.

Original v1.0 developed by Chris Zachor and Todd G. Shipley.  
Rebuilt and extended for the Dark Web Hunting Toolkit by Todd G. Shipley.

\---

## Overview

Case Generator builds standardized investigation folder structures from
customizable templates, ensuring consistency and chain of custody compliance
across all investigations. It is part of the Dark Web Hunting Toolkit,
companion to *Dark Web Hunting* by Todd G. Shipley.

The tool creates a uniquely named case root folder derived from the case
reference and a UTC timestamp, then builds the complete subdirectory
structure defined by the selected template.

\---

## Installation

**Requirements:** Python 3.10 or higher

```bash
pip install -r requirements.txt
python case\_generator.py
```

\---

## Using Case Generator

1. Enter the **Examiner Name** -- the full name of the investigating examiner.
2. Enter the **Case Number/Name** -- this can be a case number, a descriptive
name, or both combined. Examples: `2025-001` or `2025-001 SilkRoad`.
3. Set the **Case Root** directory where the case folder will be created
(use the Browse button or type the path directly).
4. Select a **Template** from the dropdown and review the folder list preview.
5. Click **Build Directory Structure**.
6. After a successful build, click **Open Case Folder in Explorer** to go
directly to the new folder, or build another case without exiting.

The tool creates a folder named in the format:

```
CaseRef\_YYYYMMDD\_HHMMSS
```

For example, entering `2025-001 SilkRoad` creates:

```
2025-001\_SilkRoad\_20250321\_143022/
```

All subdirectories defined in the selected template are created inside
this root folder.

\---

## Managing Templates

Templates are plain text files stored in the `templates/` subfolder.
They can be managed directly in the GUI without editing files manually.

**To create a new template:** Click **New** next to the template dropdown,
or use the Templates menu.

**To edit a template:** Select it and click **Edit**, or use the Templates menu.

**To delete a template:** Select it and click **Delete**.

**To open the templates folder directly:** Use File > Open Templates Folder.

**Template format:**

* One folder path per line
* Paths must start and end with a forward slash: `/Evidence/`
* Subdirectories are listed after their parent: `/Evidence/Screenshots/`
* Lines beginning with `#` are comments and are ignored when building

**Example template:**

```
#My Investigation Template
/Evidence/
/Evidence/Screenshots/
/Evidence/Source\_Code/
/Reports/
/Reports/Analysis/
/Hashes/
/Forms/
/Forms/Chain\_of\_Custody/
```

\---

## Built-In Templates

|Template|Purpose|
|-|-|
|Dark Web Hunting|Dark web investigations following the book's workflow. 51 directories covering Tor, I2P, Freenet, cryptocurrency, OSINT, server reconnaissance, metadata, personas, reports, and forms.|
|Internet Investigations|General online investigations and OSINT including webpage collections, social networking, and IP research.|
|Forensic|Digital forensics examinations with support for XWays, IEF, Autopsy, FTK, and timeline analysis tools.|
|Data Recovery|Data recovery cases including imaging reports, carved files, and client data folders.|

\---

## Output Folder Structure

```
CaseRoot/
  CaseRef\_YYYYMMDD\_HHMMSS/
    \[All folders defined in the selected template]
```

\---

## Platform Support

Case Generator runs on Windows, macOS, and Linux. The Open Case Folder
button uses the native file manager on each platform (Explorer, Finder,
or the default file manager on Linux).

\---

## Acknowledgements

Case Generator v1.0 originally developed by Chris Zachor and Todd G. Shipley.  
Rebuilt and extended for the Dark Web Hunting Toolkit by Todd G. Shipley, CFE, CFCE.

\---

## License

Licensed for use by law enforcement, government agencies, legal professionals,
licensed investigators, cybersecurity practitioners, academic institutions,
students, and OSINT researchers. Users are responsible for ensuring their
use complies with all applicable laws and organizational policies.

See LICENSE.txt for full terms.

\---

*Part of the Dark Web Hunting Toolkit*  
*Companion to "Dark Web Hunting" by Todd G. Shipley, CFE, CFCE*  
*Dark Intel | www.darkintel.info*

\---

## Building a Windows Executable (.exe)

To create a single standalone `CaseGenerator.exe` that runs on any Windows
machine without requiring Python:

**Requirements:** Windows machine with Python 3.10+ installed.

**Step 1:** Open the `case\_generator` folder in File Explorer.

**Step 2:** Double-click `build\_windows.bat`.

The script will automatically install PyInstaller, build the executable,
and open the `dist` folder when complete.

**Output:** `dist\\CaseGenerator.exe`

This is a single self-contained file. Copy it to any Windows machine and
run it directly. No Python installation required on the target machine.

**Note:** The build must be run on a Windows machine. The resulting .exe
will only run on Windows. For macOS or Linux distribution, run PyInstaller
on those platforms separately.
<img width="943" height="1022" alt="Case_Generator_Dashboard" src="https://github.com/user-attachments/assets/30b24518-3e7d-4e1a-848b-479a052a3787" />

