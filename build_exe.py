"""Build script for creating Windows executable."""

import PyInstaller.__main__
import sys
import os
from pathlib import Path

# Project root
root = Path(__file__).parent

# Determine separator for data files (platform-specific)
separator = ';' if sys.platform == 'win32' else ':'

# Build configuration
args = [
    str(root / 'src' / 'cli' / 'main.py'),
    '--name=GameTelemetry',
    '--onefile',  # Single executable
    '--console',  # Console application
    
    # Add src to path
    f'--paths={root / "src"}',
    
    # Add data files
    f'--add-data=configs{separator}configs',
    f'--add-data=reference_images{separator}reference_images',
    
    # Hidden imports (for dynamic imports)
    '--hidden-import=pynput.keyboard',
    '--hidden-import=pynput.mouse',
    '--hidden-import=PIL',
    '--hidden-import=cv2',
    '--hidden-import=yaml',
    '--hidden-import=psutil',
    
    # Platform-specific hidden imports
    '--collect-submodules=pynput',
    
    # Optimize
    '--clean',
    '--noconfirm',
    
    # Output directory
    '--distpath=dist',
    '--workpath=build',
    '--specpath=.',
]

# Add platform-specific imports
if sys.platform == 'win32':
    args.extend([
        '--hidden-import=pynput.keyboard._win32',
        '--hidden-import=pynput.mouse._win32',
    ])
elif sys.platform == 'darwin':
    args.extend([
        '--hidden-import=pynput.keyboard._darwin',
        '--hidden-import=pynput.mouse._darwin',
    ])

PyInstaller.__main__.run(args)

print("\n" + "="*70)
print("✅ Build complete!")
print("="*70)
print(f"Executable: dist/GameTelemetry.exe")
print("\nUsage:")
print("  GameTelemetry.exe start --config configs/test_roi.yaml")
print("="*70)
