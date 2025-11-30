"""Build script for creating Windows executable."""

import PyInstaller.__main__
import sys
from pathlib import Path

# Project root
root = Path(__file__).parent

# Build configuration
PyInstaller.__main__.run([
    str(root / 'src' / 'cli' / 'main.py'),
    '--name=GameTelemetry',
    '--onefile',  # Single executable
    '--console',  # Console application
    '--icon=NONE',  # Add icon file path if you have one
    
    # Add data files
    '--add-data=configs:configs',
    '--add-data=reference_images:reference_images',
    
    # Hidden imports (for dynamic imports)
    '--hidden-import=pynput.keyboard._win32',
    '--hidden-import=pynput.mouse._win32',
    '--hidden-import=PIL._tkinter_finder',
    
    # Optimize
    '--clean',
    '--noconfirm',
    
    # Output directory
    '--distpath=dist',
    '--workpath=build',
    '--specpath=.',
])

print("\n" + "="*70)
print("✅ Build complete!")
print("="*70)
print(f"Executable: dist/GameTelemetry.exe")
print("\nUsage:")
print("  GameTelemetry.exe start --config configs/test_roi.yaml")
print("="*70)
