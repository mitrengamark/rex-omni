#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTTP Frame Grabber for Remote Camera
HTTP kérésekkel tölti le a képkockákat a kamerából

Ez jobban működik instabil kapcsolatoknál (VPN, WiFi)
"""

import os
import sys
import cv2
import time
import json
import requests
import numpy as np
from pathlib import Path
from datetime import datetime
from PIL import Image
from io import BytesIO

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
    
    def __init__(self, base_url: str, timeout: int = 5):
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


class RemoteCameraDetectionPipeline:
    """
    Remote camera detection pipeline HTTP frame grabber-rel
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
        self.last_detection_result = None
    
    def _load_model(self):
        """Model betöltése"""
        print("\n" + "="*70)
        print("REMOTE CAMERA DETECTION PIPELINE")
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
        
        # Test frame
        try:
            test_frame = self.frame_grabber.get_frame()
            if test_frame is None:
                raise RuntimeError("Üres frame")
            h, w = test_frame.shape[:2]
            print(f"✓ Test frame OK - {w}x{h}\n")
        except Exception as e:
            raise RuntimeError(f"❌ Frame teszt hiba: {e}")
    
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
            
            # Objektumok csoportosítása
            found_objects = {}
            for det in result.get('detections', []):
                label = det.get('label', 'unknown')
                if label not in found_objects:
                    found_objects[label] = []
                found_objects[label].append(det)
            
            total_count = len(result.get('detections', []))
            
            return {
                'success': True,
                'detections': result.get('detections', []),
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
            
            viz_image = RexOmniVisualize(
                image=pil_image,
                predictions=detection_result['detections'],
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
        else:
            print(f"\n⚠️  Snapshot #{self.snapshot_count} - detektálási hiba: "
                  f"{detection_result.get('error')}")
    
    def run_interactive(self, fps: int = 5):
        """
        Interaktív mód - live preview + SPACE trigger
        
        Args:
            fps: Frame rate (alacsonyabb = kevesebb sáv, ajánlott: 3-5)
        """
        print("="*70)
        print("VEZÉRLÉS:")
        print("  [SPACE]  - Snapshot készítése és detektálás")
        print("  [Q]      - Kilépés")
        print("="*70 + "\n")
        
        print(f"▶️  Live preview indítása ({fps} FPS)...\n")
        
        frame_delay = int(1000 / fps)  # ms
        
        try:
            while True:
                # Frame letöltése
                try:
                    frame = self.frame_grabber.get_frame()
                    if frame is None:
                        print("⚠️  Üres frame, retry...")
                        time.sleep(0.5)
                        continue
                except Exception as e:
                    print(f"⚠️  Frame hiba: {e}, retry...")
                    time.sleep(1)
                    continue
                
                # Preview overlay
                display_frame = frame.copy()
                h, w = frame.shape[:2]
                
                # Info text
                cv2.rectangle(display_frame, (10, 10), (w - 10, 80), (0, 0, 0), -1)
                cv2.putText(display_frame, "REMOTE CAMERA DETECTION", (20, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_frame, f"Snapshots: {self.snapshot_count} | [SPACE] Detect [Q] Quit",
                           (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Megjelenítés
                cv2.imshow('Remote Camera Detection', display_frame)
                
                # Billentyű kezelés
                key = cv2.waitKey(frame_delay) & 0xFF
                
                if key == ord('q') or key == 27:  # 'q' vagy ESC
                    print("\n👋 Kilépés...")
                    break
                
                elif key == ord(' '):  # SPACE
                    print("\n📸 Snapshot készítése és detektálás...")
                    
                    # Detektálás
                    detection_result = self.detect_on_frame(frame)
                    self.last_detection_result = detection_result
                    
                    # Mentés
                    self.save_snapshot(frame, detection_result)
                    
                    # Eredmény megjelenítése
                    if detection_result['success']:
                        print("\n🎯 DETEKTÁLT OBJEKTUMOK:")
                        for obj_name, detections in sorted(
                            detection_result['found_objects'].items(),
                            key=lambda x: len(x[1]),
                            reverse=True
                        ):
                            print(f"   • {obj_name}: {len(detections)} db")
                        print()
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Megszakítva (Ctrl+C)")
        
        finally:
            cv2.destroyAllWindows()
            
            print("\n" + "="*70)
            print(f"✅ KÉSZ! Összesen {self.snapshot_count} snapshot készült")
            print(f"📁 Eredmények: {self.output_dir}/")
            print("="*70 + "\n")


def main():
    """Fő futtatási függvény"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Remote Camera Detection Pipeline (HTTP Frame Grabber)'
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
    parser.add_argument(
        '--fps',
        type=int,
        default=5,
        help='Preview FPS (ajánlott: 3-5 VPN-hez)'
    )
    
    args = parser.parse_args()
    
    # Pipeline indítása
    pipeline = RemoteCameraDetectionPipeline(
        model_path=args.model,
        backend="transformers",
        categories=COMMON_ASSEMBLY_OBJECTS,
        output_dir=args.output,
        camera_url=args.camera
    )
    
    pipeline.run_interactive(fps=args.fps)


if __name__ == "__main__":
    main()
