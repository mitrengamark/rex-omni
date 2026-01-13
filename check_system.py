#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rex-Omni System Check
Ellenőrzi, hogy minden szükséges komponens telepítve van-e
"""

import sys
import os
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(text)
    print("="*60)

def check_python_version():
    """Check Python version"""
    print_header("Python verzió ellenőrzése")
    version = sys.version_info
    print(f"Python verzió: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✓ Python verzió megfelelő (3.8+)")
        return True
    else:
        print("✗ Python verzió túl régi! Szükséges: 3.8+")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name} telepítve")
        return True
    except ImportError:
        print(f"✗ {package_name} NINCS telepítve - telepítsd: pip install {package_name}")
        return False

def check_packages():
    """Check required packages"""
    print_header("Python csomagok ellenőrzése")
    
    packages = [
        ("torch", "torch"),
        ("torchvision", "torchvision"),
        ("PIL", "PIL"),
        ("numpy", "numpy"),
        ("opencv-python", "cv2"),
        ("transformers", "transformers"),
        ("huggingface-hub", "huggingface_hub"),
    ]
    
    results = []
    for package_name, import_name in packages:
        results.append(check_package(package_name, import_name))
    
    return all(results)

def check_model():
    """Check if Rex-Omni model exists"""
    print_header("Rex-Omni modell ellenőrzése")
    
    model_paths = [
        "models/Rex-Omni",
        "../models/Rex-Omni",
        "../../models/Rex-Omni"
    ]
    
    for model_path in model_paths:
        model_dir = Path(model_path)
        if model_dir.exists():
            # Check for essential files
            config_file = model_dir / "config.json"
            if config_file.exists():
                print(f"✓ Modell megtalálva: {model_dir.absolute()}")
                
                # List model files
                model_files = list(model_dir.glob("*"))
                print(f"  Fájlok száma: {len(model_files)}")
                
                # Check for model weights
                safetensors_files = list(model_dir.glob("*.safetensors"))
                bin_files = list(model_dir.glob("*.bin"))
                
                if safetensors_files or bin_files:
                    print(f"  Súly fájlok: {len(safetensors_files + bin_files)}")
                    return True
                else:
                    print("  ⚠ Figyelem: Súly fájlok nem találhatók")
                    return False
    
    print("✗ Modell NINCS telepítve")
    print("\nTelepítési utasítás:")
    print("  huggingface-cli download IDEA-Research/Rex-Omni --local-dir models/Rex-Omni")
    return False

def check_camera():
    """Check if camera is accessible"""
    print_header("Kamera ellenőrzése")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                print("✓ Kamera működik")
                print(f"  Felbontás: {frame.shape[1]}x{frame.shape[0]}")
                return True
            else:
                print("✗ Kamera megnyílt, de nem tud képet olvasni")
                return False
        else:
            print("✗ Nem lehet megnyitni a kamerát")
            print("  Próbáld meg manuálisan:")
            print("    - Ellenőrizd, hogy más alkalmazás használja-e")
            print("    - Próbálj más kamera indexet (1, 2, ...)")
            return False
    except Exception as e:
        print(f"✗ Hiba a kamera ellenőrzése során: {e}")
        return False

def check_gpu():
    """Check GPU availability"""
    print_header("GPU ellenőrzése")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            print("✓ CUDA GPU elérhető")
            print(f"  GPU név: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA verzió: {torch.version.cuda}")
            print(f"  GPU számok: {torch.cuda.device_count()}")
            return True
        else:
            print("⚠ GPU nem elérhető, CPU módban fog működni")
            print("  Ez lassabb lehet, de működni fog")
            return True  # Not critical
    except Exception as e:
        print(f"⚠ Nem lehet ellenőrizni a GPU-t: {e}")
        return True  # Not critical

def check_scripts():
    """Check if camera scripts exist"""
    print_header("Szkriptek ellenőrzése")
    
    scripts = [
        "simple_camera_demo.py",
        "camera_detection.py",
        "interactive_camera_demo.py",
    ]
    
    results = []
    for script in scripts:
        if Path(script).exists():
            print(f"✓ {script}")
            results.append(True)
        else:
            print(f"✗ {script} NINCS MEG")
            results.append(False)
    
    return all(results)

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║          Rex-Omni Kamerás Object Detection                   ║
║                 Rendszer Ellenőrző                           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    results = {
        "Python verzió": check_python_version(),
        "Python csomagok": check_packages(),
        "Rex-Omni modell": check_model(),
        "Kamera": check_camera(),
        "GPU": check_gpu(),
        "Szkriptek": check_scripts(),
    }
    
    print_header("ÖSSZESÍTÉS")
    
    for name, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {name}: {'OK' if result else 'PROBLÉMA'}")
    
    all_critical_ok = all([
        results["Python verzió"],
        results["Python csomagok"],
        results["Rex-Omni modell"],
        results["Szkriptek"]
    ])
    
    print("\n" + "="*60)
    if all_critical_ok:
        print("🎉 MINDEN RENDBEN! Készen állsz a használatra!")
        print("\nKövetkező lépés:")
        print("  python interactive_camera_demo.py")
    else:
        print("⚠ Van néhány probléma, amit meg kell oldani!")
        print("\nTelepítési útmutató:")
        print("  1. pip install -r requirements.txt")
        print("  2. pip install opencv-python")
        print("  3. huggingface-cli download IDEA-Research/Rex-Omni --local-dir models/Rex-Omni")
        print("\nRészletek: README_CAMERA.md")
    print("="*60)
    
    return 0 if all_critical_ok else 1

if __name__ == "__main__":
    sys.exit(main())
