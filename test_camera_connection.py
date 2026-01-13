#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Camera Stream Connection Tester
Teszteli hogy elérhető-e a camera server
"""

import requests
import sys
import time

def test_connection(url, timeout=5):
    """
    Teszteli a kapcsolatot a camera server-rel
    
    Args:
        url: Stream URL (pl. http://192.168.1.100:5000/video)
        timeout: Timeout másodpercben
    """
    print("\n" + "="*70)
    print("CAMERA STREAM CONNECTION TEST")
    print("="*70 + "\n")
    
    # Parse URL
    if not url.startswith('http'):
        url = f'http://{url}'
    
    base_url = url.replace('/video', '')
    
    print(f"🎯 Target URL: {url}")
    print(f"📡 Base URL: {base_url}\n")
    
    # 1. Ping/elérhetőség teszt
    print("1️⃣  Teszt: Alap elérhetőség...")
    try:
        response = requests.get(base_url, timeout=timeout)
        print(f"   ✓ Válasz kód: {response.status_code}")
        print(f"   ✓ Szerver elérhető!\n")
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout ({timeout}s) - A szerver nem válaszol időben")
        print(f"   → Ellenőrizd hogy fut-e a camera_server.py\n")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection Error: {e}")
        print(f"   → Lehetséges okok:")
        print(f"      • A camera_server.py nem fut")
        print(f"      • Rossz IP cím")
        print(f"      • Tűzfal blokkolja a portot")
        print(f"      • Nem ugyanazon a hálózaton vagytok\n")
        return False
    except Exception as e:
        print(f"   ❌ Hiba: {e}\n")
        return False
    
    # 2. Stream endpoint teszt
    print("2️⃣  Teszt: Stream endpoint...")
    try:
        response = requests.get(url, timeout=timeout, stream=True)
        print(f"   ✓ Válasz kód: {response.status_code}")
        print(f"   ✓ Content-Type: {response.headers.get('Content-Type')}")
        
        # Próbáljunk olvasni egy kicsit
        chunk = next(response.iter_content(chunk_size=1024), None)
        if chunk:
            print(f"   ✓ Stream adatok érkeznek! ({len(chunk)} bytes)\n")
        else:
            print(f"   ⚠️  Stream üres vagy nem elérhető\n")
            
    except Exception as e:
        print(f"   ❌ Stream hiba: {e}\n")
        return False
    
    # 3. Sikeres
    print("="*70)
    print("✅ ÖSSZES TESZT SIKERES!")
    print("="*70)
    print("\nA camera stream elérhető és működik.")
    print(f"Használhatod: python live_video_detection.py --stream {url}\n")
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test camera stream connection'
    )
    parser.add_argument(
        'url',
        type=str,
        help='Stream URL (pl. http://192.168.1.100:5000/video)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=5,
        help='Timeout másodpercben (alapértelmezett: 5)'
    )
    
    args = parser.parse_args()
    
    success = test_connection(args.url, args.timeout)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
