# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Recolectar todos los submódulos de streamlit
streamlit_hidden_imports = collect_submodules('streamlit')
# Recolectar todos los datos de streamlit
streamlit_datas = collect_data_files('streamlit')

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data', 'data'),
        ('frontend', 'frontend'),
        ('config', 'config'),
        ('visualization', 'visualization'),
        ('ml_analysis', 'ml_analysis'),
        ('utils', 'utils'),
        ('scenarios', 'scenarios'),
        ('automation', 'automation'),
        ('opinion', 'opinion'),
        ('*.html', '.'),
        ('*.jpg', '.'),
        ('*.txt', '.'),
    ] + streamlit_datas,  # Añadir datos de streamlit
    hiddenimports=[
        'streamlit',
        'openai',
        'PyPDF2',
        'pdfkit',
        'scikit-learn',
        'plotly',
        'pandas',
        'sqlite3',
        'sklearn.utils._typedefs',
        'sklearn.neighbors._partition_nodes',
        'numpy',
        'json',
        'dotenv',
        'importlib_metadata',
        'pkg_resources.py2_warn',
        'pkg_resources.markers',
        'packaging.version',
        'packaging.specifiers',
        'packaging.requirements',
    ] + streamlit_hidden_imports,  # Añadir imports de streamlit
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FinanceGPT2',
    debug=True,  # Habilitamos el debug para ver más información
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FinanceGPT2'
)