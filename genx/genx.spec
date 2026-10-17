# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
import os
import site
import sys
from pathlib import Path

spec_dir = Path(SPECPATH).resolve()


def collect_optional_libraries(search_dirs):
    """Collect existing OpenMP/MKL/CUDA files, without requiring Intel MKL."""
    binaries, datas = [], []
    seen = set()
    for directory in search_dirs:
        for pattern, destinations, is_data in (
            ('libiomp5md.dll', ('.',), False),
            ('mkl_*.dll', ('.',), False),
            ('nvvm64*.dll', ('DLLs', 'Library/bin'), False),
            ('cudart64*.dll', ('Library/bin',), False),
            ('libdevice*.bc', ('DLLs',), True),
        ):
            for path in sorted(directory.glob(pattern)):
                if not path.is_file():
                    continue
                for destination in destinations:
                    # The first match wins if multiple locations provide a DLL.
                    key = (path.name.lower(), destination)
                    if key in seen:
                        continue
                    seen.add(key)
                    (datas if is_data else binaries).append((str(path.resolve()), destination))
    return binaries, datas


# Conda DLLs need not be on PATH; pip wheels keep theirs beside the package.
# Prefer the active environment to unrelated installations on the system PATH.
search_dirs = []
for prefix in dict.fromkeys((sys.prefix, sys.base_prefix)):
    search_dirs.extend((Path(prefix) / 'Library/bin', Path(prefix) / 'DLLs', Path(prefix)))
for packages in site.getsitepackages():
    for relative in ('numpy.libs', 'scipy.libs', 'numpy/.libs', 'scipy/.libs'):
        search_dirs.append(Path(packages) / relative)
for key, value in sorted(os.environ.items()):
    if key == 'CUDA_PATH' or key.startswith('CUDA_PATH_V'):
        cuda = Path(value)
        search_dirs.extend((cuda / 'bin', cuda / 'nvvm/bin', cuda / 'nvvm/libdevice'))
search_dirs.extend(Path(value.strip('"')) for value in os.environ.get('PATH', '').split(os.pathsep) if value)
optional_binaries, optional_datas = collect_optional_libraries(search_dirs)

# Discover dynamically loaded models and plugins from the spec location.
genx_modules = [
    '.'.join(path.relative_to(spec_dir).with_suffix('').parts)
    for pattern in ('genx/plugins/*/*.py', 'genx/plugins/*/help_modules/*.py', 'genx/models/*.py')
    for path in sorted(spec_dir.glob(pattern))
    if path.name != '__init__.py'
]

a = Analysis([str(spec_dir / 'scripts/genx')],
             pathex=[str(spec_dir)],
             binaries=optional_binaries,
             datas=[(str(spec_dir / 'genx'), 'genx')] + optional_datas,
             hiddenimports=genx_modules + ['pymysql', 'numba', 'numba.cuda',
							'scipy._lib.array_api_compat.numpy.fft', 'scipy.special._special_ufuncs',
			                'vtk', 'vtkmodules', 'vtkmodules.all','vtkmodules.util.colors',
							'vtkmodules.util','vtkmodules.util.numpy_support',
                            'scipy.special.cython_special', 'xml.dom.minidom',
                            'docutils.parsers.null', 'genx.plugins.add_ons.LayerGraphics',
                            'genx.gui.plotpanel', 'genx.gui.plotpanel_wx'],
             hooksconfig={
                 "matplotlib": {
                     "backends": "WxAgg",
                     },},
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt5', ],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
splash = Splash(
        str(spec_dir / "windows_build/genx_splash.png"),
        binaries=a.binaries,
        datas=a.datas,
        text_pos=(42, 456),
        text_size=12,
        text_color="black",
        minify_script=True,
        always_on_top=True,
        text_default="Extracting GenX...",
    )
exe = EXE(pyz,
          a.scripts,
          splash,
          [],
          exclude_binaries=True,
          name='genx',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False , icon=str(spec_dir / 'windows_build/genx.ico'))
exe_console = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='genx_console',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True , icon=str(spec_dir / 'windows_build/genx.ico'))
coll = COLLECT(exe,
               exe_console,
               a.binaries,
               a.zipfiles,
               a.datas,
               splash.binaries,
               strip=False,
               upx=False,
               upx_exclude=[],
               name='genx')
