# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files


block_cipher = None


a = Analysis(['voicelab.py'],
             pathex=['VoiceLab'],
             binaries=[],
             datas=collect_data_files('librosa'),
             hiddenimports=['qdarkstyle',
                             'PyQt5.sip',
                             'sklearn.neighbors._partition_nodes',],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='voicelab',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='favicon.ico')
