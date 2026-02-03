#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Headless Remote Camera Detection
SSH/headless szerver környezethez - nincs GUI preview

Használat:
    python headless_camera_detection.py --camera http://10.8.0.3:5001
    
Majd nyomj ENTER-t snapshot készítéséhez, vagy 'q' + ENTER a kilépéshez
"""

import os
import sys
import time
import json
import requests
import numpy as np
from pathlib import Path
from datetime import datetime
from PIL import Image
from io import BytesIO
import cv2
import threading

# Add directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Try to import from local repos
try:
    comfyui_src = os.path.join(current_dir, 'ComfyUI-RexOmni_repo', 'src')
    sys.path.insert(0, comfyui_src)
    from rex_omni.wrapper import RexOmniWrapper
    from rex_omni.utils import RexOmniVisualize
except ImportError:
    rex_omni_path = os.path.join(current_dir, 'Rex-Omni')
    sys.path.insert(0, rex_omni_path)
    from rex_omni.wrapper import RexOmniWrapper
    from rex_omni.utils import RexOmniVisualize

from factory_assembly_categories import COMMON_ASSEMBLY_OBJECTS


class HTTPFrameGrabber:
    """HTTP alapú frame grabber a camera server-hez"""
    
    def __init__(self, base_url: str, timeout: int = 10):
        """
        Args:
            base_url: Camera server base URL (pl. http://10.8.0.3:5001)
            timeout: Request timeout másodpercben
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def get_frame(self) -> np.ndarray:
        """
        Egyetlen frame letöltése
        
        Returns:
            numpy array (BGR format, mint az OpenCV)
        """
        try:
            # Snapshot endpoint hívása
            response = self.session.get(
                f"{self.base_url}/snapshot",
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # JPEG dekódolás
            img_array = np.frombuffer(response.content, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            return frame
            
        except Exception as e:
            raise RuntimeError(f"Frame letöltési hiba: {e}")
    
    def is_available(self) -> bool:
        """Ellenőrzi hogy elérhető-e a server"""
        try:
            response = self.session.get(
                f"{self.base_url}/",
                timeout=self.timeout
            )
            return response.status_code == 200
        except:
            return False


class HeadlessCameraDetection:
    """
    Headless camera detection pipeline SSH/szerver környezethez
    """
    
    def __init__(
        self,
        model_path: str = "IDEA-Research/Rex-Omni",
        backend: str = "transformers",
        categories: list = None,
        output_dir: str = "live_detections",
        camera_url: str = None
    ):
        """
        Pipeline inicializálása
        
        Args:
            model_path: Rex-Omni modell elérési útja
            backend: "transformers" vagy "vllm"
            categories: Detektálandó kategóriák listája
            output_dir: Kimeneti könyvtár snapshot-okhoz
            camera_url: Camera server URL (pl. http://10.8.0.3:5001)
        """
        self.model_path = model_path
        self.backend = backend
        self.categories = categories or COMMON_ASSEMBLY_OBJECTS
        self.output_dir = output_dir
        self.camera_url = camera_url
        
        # Output könyvtár
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Model betöltése
        self.model = None
        self._load_model()
        
        # Frame grabber
        self.frame_grabber = None
        self._init_frame_grabber()
        
        # Statisztikák
        self.snapshot_count = 0
        self.running = True
    
    def _load_model(self):
        """Model betöltése"""
        print("\n" + "="*70)
        print("HEADLESS REMOTE CAMERA DETECTION")
        print("="*70 + "\n")
        
        print(f"⏳ Model betöltése: {self.model_path}")
        print(f"   Backend: {self.backend}")
        print(f"   Kategóriák: {len(self.categories)} db\n")
        
        try:
            self.model = RexOmniWrapper(
                model_path=self.model_path,
                backend=self.backend,
                max_tokens=512,
                temperature=0.0,
                attn_implementation="sdpa",
                device_map="auto",
            )
            print("✓ Model sikeresen betöltve!\n")
        except Exception as e:
            print(f"❌ Model betöltési hiba: {e}\n")
            raise
    
    def _init_frame_grabber(self):
        """Frame grabber inicializálása"""
        print(f"🌐 Remote camera csatlakozás: {self.camera_url}")
        
        self.frame_grabber = HTTPFrameGrabber(self.camera_url)
        
        if not self.frame_grabber.is_available():
            raise RuntimeError(
                f"❌ A camera server nem elérhető: {self.camera_url}\n"
                f"   Ellenőrizd hogy fut-e a camera_server.py!"
            )
        
        print("✓ Camera server elérhető!\n")
        
        # Test frame - több próbálkozással (Macbook kamera néha lassú)
        print("📸 Kamera teszt...")
        test_success = False
        for attempt in range(5):
            try:
                test_frame = self.frame_grabber.get_frame()
                if test_frame is not None:
                    h, w = test_frame.shape[:2]
                    print(f"✓ Kamera OK - {w}x{h}\n")
                    test_success = True
                    break
            except Exception as e:
                if attempt < 4:
                    print(f"   Próba {attempt + 1}/5 - várakozás...")
                    import time
                    time.sleep(0.5)
                else:
                    print(f"⚠️  Kamera teszt sikertelen 5 próba után")
                    print(f"   Hiba: {e}")
                    print(f"   A detekció folytatódik, de lehet hogy lassabb lesz.\n")
        
        if not test_success:
            print("⚠️  WARNING: Kamera lehet instabil, de folytatom...\n")
    
    def detect_on_frame(self, frame: np.ndarray) -> dict:
        """
        Detektálás egy képkockán
        
        Args:
            frame: OpenCV képkocka (BGR formátum)
        
        Returns:
            dict: Detektálási eredmények
        """
        # BGR -> RGB konverzió és PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        
        # Detektálás
        start_time = time.time()
        try:
            results = self.model.inference(
                images=pil_image,
                task="detection",
                categories=self.categories
            )
            result = results[0]
            
            # Feldolgozás
            detection_time = time.time() - start_time
            
            if not result['success']:
                return {
                    'success': False,
                    'error': result.get('error', 'Ismeretlen hiba'),
                    'timestamp': datetime.now().isoformat()
                }
            
            # Az extracted_predictions tartalmazza a kategorizált eredményeket
            detected_objects = result['extracted_predictions']
            found_objects = {name: dets for name, dets in detected_objects.items() if dets}
            total_count = sum(len(dets) for dets in found_objects.values())
            
            # Flat detections lista a kompatibilitásért
            detections = []
            for label, dets in found_objects.items():
                for det in dets:
                    detections.append({
                        'label': label,
                        'type': det['type'],
                        'coords': det['coords']
                    })
            
            return {
                'success': True,
                'detections': detections,
                'found_objects': found_objects,
                'total_count': total_count,
                'detection_time': detection_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def save_snapshot(self, frame: np.ndarray, detection_result: dict):
        """Snapshot mentése vizualizációval és JSON-nel"""
        self.snapshot_count += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"snapshot_{self.snapshot_count:04d}_{timestamp}"
        
        # Eredeti kép mentése
        original_path = os.path.join(self.output_dir, f"{base_name}_original.jpg")
        cv2.imwrite(original_path, frame)
        
        if detection_result['success']:
            # Vizualizált kép mentése
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # RexOmniVisualize kategória dict-et vár, nem listát!
            viz_image = RexOmniVisualize(
                image=pil_image,
                predictions=detection_result['found_objects'],  # Ez már dict kategóriákkal!
                font_size=15,
                draw_width=3,
                show_labels=True
            )
            
            viz_path = os.path.join(self.output_dir, f"{base_name}_detected.jpg")
            viz_image.save(viz_path)
            
            # JSON mentése
            json_path = os.path.join(self.output_dir, f"{base_name}_result.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'snapshot_number': self.snapshot_count,
                    'timestamp': detection_result['timestamp'],
                    'total_objects': detection_result['total_count'],
                    'detection_time': detection_result['detection_time'],
                    'found_objects': {
                        k: len(v) for k, v in detection_result['found_objects'].items()
                    },
                    'detections': detection_result['detections']
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Snapshot #{self.snapshot_count} mentve:")
            print(f"   📁 {base_name}")
            print(f"   🎯 {detection_result['total_count']} objektum, "
                  f"{len(detection_result['found_objects'])} típus")
            print(f"   ⏱️  Detektálási idő: {detection_result['detection_time']:.2f}s")
            
            # Részletes eredmények
            if detection_result['found_objects']:
                print(f"\n   🎯 DETEKTÁLT OBJEKTUMOK:")
                for obj_name, detections in sorted(
                    detection_result['found_objects'].items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                ):
                    print(f"      • {obj_name}: {len(detections)} db")
        else:
            print(f"\n⚠️  Snapshot #{self.snapshot_count} - detektálási hiba: "
                  f"{detection_result.get('error')}")
    
    def capture_and_detect(self):
        """Egyetlen snapshot és detektálás"""
        print("\n📸 Snapshot készítése...")
        
        try:
            # Frame letöltése
            frame = self.frame_grabber.get_frame()
            if frame is None:
                print("❌ Nem sikerült frame-et letölteni")
                return
            
            print("✓ Frame letöltve")
            print("🔍 Detektálás folyamatban...")
            
            # Detektálás
            detection_result = self.detect_on_frame(frame)
            
            # Mentés
            self.save_snapshot(frame, detection_result)
            
        except Exception as e:
            import traceback
            print(f"❌ Hiba: {e}")
            print("FULL TRACEBACK:")
            traceback.print_exc()
    
    def run_interactive(self):
        """
        Interaktív headless mód - parancssorból vezérelve
        """
        print("="*70)
        print("VEZÉRLÉS (HEADLESS MÓD):")
        print("  [ENTER]  - Snapshot készítése és detektálás")
        print("  [q]      - Kilépés")
        print("="*70 + "\n")
        
        print("⌨️  Készen állok! Nyomj ENTER-t snapshot készítéséhez...\n")
        
        try:
            while self.running:
                # Várakozás input-ra
                user_input = input("> ").strip().lower()
                
                if user_input == 'q' or user_input == 'quit' or user_input == 'exit':
                    print("\n👋 Kilépés...")
                    self.running = False
                    break
                
                elif user_input == '' or user_input == 's' or user_input == 'snap':
                    # ENTER vagy 's' = snapshot
                    self.capture_and_detect()
                    print("\n⌨️  Nyomj ENTER-t újabb snapshot-hoz, vagy 'q' + ENTER a kilépéshez...\n")
                
                elif user_input == 'h' or user_input == 'help':
                    print("\nPARANCSOR:")
                    print("  ENTER / s    - Snapshot és detektálás")
                    print("  q / quit     - Kilépés")
                    print("  h / help     - Súgó")
                    print()
                
                else:
                    print("❓ Ismeretlen parancs. Nyomj ENTER-t snapshot-hoz vagy 'q'-t kilépéshez.")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Megszakítva (Ctrl+C)")
        
        finally:
            print("\n" + "="*70)
            print(f"✅ KÉSZ! Összesen {self.snapshot_count} snapshot készült")
            print(f"📁 Eredmények: {self.output_dir}/")
            print("="*70 + "\n")


def main():
    """Fő futtatási függvény"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Headless Remote Camera Detection (SSH környezethez)'
    )
    parser.add_argument(
        '--camera',
        type=str,
        required=True,
        help='Camera server URL (pl. http://10.8.0.3:5001)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='IDEA-Research/Rex-Omni',
        help='Model elérési útja'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='live_detections',
        help='Kimeneti könyvtár'
    )
    
    args = parser.parse_args()
    
    # Pipeline indítása
    pipeline = HeadlessCameraDetection(
        model_path=args.model,
        backend="transformers",
        categories=COMMON_ASSEMBLY_OBJECTS,
        output_dir=args.output,
        camera_url=args.camera
    )
    
    pipeline.run_interactive()


if __name__ == "__main__":
    main()
