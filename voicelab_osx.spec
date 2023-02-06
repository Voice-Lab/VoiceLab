# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None


a = Analysis(['voicelab.py'],
             pathex=['VoiceLab'],
             binaries=[],
             datas=collect_data_files('librosa'),
             hiddenimports=['cmath',
                            'sklearn.utils._weight_vector',
                            'sklearn.neighbors._partition_nodes',
                            'sklearn.metrics._pairwise_distances_reduction._datasets_pair',
                            'sklearn.metrics._pairwise_distances_reduction._middle_term_computer'
                           ],
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
          [],
          exclude_binaries=True,
          name='VoiceLab',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , 
          icon='favicon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='VoiceLab')
app = BUNDLE(coll,
             name='VoiceLab.app',
             icon='Voicelab/favicon.ico',
             bundle_identifier=None)
