#!/bin/bash
# Rex-Omni Telepítési Script
# Ez a script segít feltelepíteni a Rex-Omni-t kamerás használatra

set -e

echo "=========================================="
echo "Rex-Omni Camera Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Ellenőrzés: Python verzió..."
python3 --version || { echo "Hiba: Python3 nincs telepítve!"; exit 1; }

# Create virtual environment (optional)
read -p "Szeretnél virtual environment-et létrehozni? (y/n): " create_venv
if [ "$create_venv" = "y" ] || [ "$create_venv" = "Y" ]; then
    echo "Virtual environment létrehozása..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment aktiválva"
fi

# Install dependencies
echo ""
echo "Függőségek telepítése..."
pip install --upgrade pip
pip install -r requirements.txt
pip install opencv-python

echo "✓ Függőségek telepítve"

# Download model
echo ""
echo "=========================================="
echo "Modell letöltése"
echo "=========================================="
echo ""
echo "A Rex-Omni modell kb. 6 GB méretű."
read -p "Szeretnéd most letölteni a modellt? (y/n): " download_model

if [ "$download_model" = "y" ] || [ "$download_model" = "Y" ]; then
    echo "Hugging Face CLI telepítése..."
    pip install huggingface_hub
    
    echo "Modell letöltése..."
    huggingface-cli download IDEA-Research/Rex-Omni --local-dir models/Rex-Omni
    
    echo "✓ Modell letöltve: models/Rex-Omni"
else
    echo ""
    echo "A modellt később is letöltheted a következő paranccsal:"
    echo "  huggingface-cli download IDEA-Research/Rex-Omni --local-dir models/Rex-Omni"
fi

# Test installation
echo ""
echo "=========================================="
echo "Telepítés kész!"
echo "=========================================="
echo ""
echo "Következő lépések:"
echo ""
echo "1. Ha még nem töltötted le, töltsd le a modellt:"
echo "   huggingface-cli download IDEA-Research/Rex-Omni --local-dir models/Rex-Omni"
echo ""
echo "2. Próbáld ki az egyszerű demót:"
echo "   python simple_camera_demo.py"
echo ""
echo "3. Vagy indítsd el a real-time detektálást:"
echo "   python camera_detection.py"
echo ""
echo "4. Vagy használd az interaktív módot:"
echo "   python interactive_camera_demo.py"
echo ""
echo "További információ: README_CAMERA.md"
echo ""
