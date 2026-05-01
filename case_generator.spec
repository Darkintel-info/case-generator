# =============================================================================
# Case Generator v2.0 - PyInstaller Spec File
# Run: pyinstaller case_generator.spec
# Or just double-click build_windows.bat
# =============================================================================

block_cipher = None

a = Analysis(
    ['case_generator.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Bundle the default templates as read-only seed data.
        # At runtime these are extracted to sys._MEIPASS/templates/
        # and copied to the user's writable AppData folder on first run.
        ('templates', 'templates'),
        # Bundle the assets folder (icon etc.)
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
        'unittest',
        'email',
        'html',
        'http',
        'urllib',
        'xml',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CaseGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    # Single file - everything bundled into one .exe
    onefile=True,
    # No console window - GUI application only
    console=False,
    # Windows version info (shows in Properties > Details)
    version='version_info.txt',
    # Icon file for the executable
    icon='assets\\darkintel.ico',
)
