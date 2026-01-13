#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Live Video Detection Pipeline
Élő videó stream objektum detektálás trigger alapján

Használat:
- Indítás után megnyílik a kamera/videó ablak
- Nyomj SPACE-t hogy készíts snapshot-ot és detektálj
- Nyomj 'q'-t a kilépéshez
"""

import os
import sys
import cv2
import time
import json
from pathlib import Path
from datetime import datetime
from PIL import Image
import numpy as np

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


class LiveVideoDetectionPipeline:
    """
    Élő videó stream objektum detektálás pipeline
    """
    
    def __init__(
        self,
        model_path: str = "IDEA-Research/Rex-Omni",
        backend: str = "transformers",
        categories: list = None,
        output_dir: str = "live_detections",
        camera_id: int = 0,
        video_path: str = None,
        stream_url: str = None
    ):
        """
        Pipeline inicializálása
        
        Args:
            model_path: Rex-Omni modell elérési útja
            backend: "transformers" vagy "vllm"
            categories: Detektálandó kategóriák listája
            output_dir: Kimeneti könyvtár snapshot-okhoz
            camera_id: Kamera ID (0 = default webcam)
            video_path: Videó fájl elérési útja (None esetén kamera)
            stream_url: HTTP stream URL (pl. http://laptop:5000/video)
        """
        self.model_path = model_path
        self.backend = backend
        self.categories = categories or COMMON_ASSEMBLY_OBJECTS
        self.output_dir = output_dir
        self.camera_id = camera_id
        self.video_path = video_path
        self.stream_url = stream_url
        
        # Output könyvtár
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Model betöltése
        self.model = None
        self._load_model()
        
        # Video capture
        self.cap = None
        
        # Statisztikák
        self.snapshot_count = 0
        self.last_detection_result = None
    
    def _load_model(self):
        """Model betöltése"""
        print("\n" + "="*70)
        print("LIVE VIDEO DETECTION PIPELINE")
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
    
    def _init_video_capture(self):
        """Videó capture inicializálása"""
        if self.stream_url:
            print(f"🌐 HTTP stream megnyitása: {self.stream_url}")
            self.cap = cv2.VideoCapture(self.stream_url)
        elif self.video_path:
            print(f"📹 Videó megnyitása: {self.video_path}")
            self.cap = cv2.VideoCapture(self.video_path)
        else:
            print(f"📷 Kamera megnyitása: {self.camera_id}")
            self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            raise RuntimeError("❌ Nem sikerült megnyitni a videó forrást!")
        
        # Kamera beállítások (opcionális, csak lokális kamerához)
        if not self.video_path and not self.stream_url:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print("✓ Videó forrás sikeresen megnyitva!\n")
    
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
        """
        Snapshot mentése vizualizációval és JSON-nel
        
        Args:
            frame: Eredeti képkocka
            detection_result: Detektálási eredmények
        """
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
    
    def _draw_overlay(self, frame: np.ndarray) -> np.ndarray:
        """
        Overlay információk rajzolása a képre
        
        Args:
            frame: Eredeti képkocka
        
        Returns:
            Képkocka overlay-vel
        """
        overlay = frame.copy()
        h, w = frame.shape[:2]
        
        # Háttér panel
        cv2.rectangle(overlay, (10, 10), (w - 10, 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Szövegek
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, "LIVE VIDEO DETECTION", (20, 40),
                    font, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"Snapshots: {self.snapshot_count}", (20, 70),
                    font, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, "[SPACE] Detect  [Q] Quit", (20, 100),
                    font, 0.6, (255, 255, 0), 1)
        
        # Utolsó detektálás eredménye
        if self.last_detection_result and self.last_detection_result['success']:
            result_text = (f"Last: {self.last_detection_result['total_count']} objects, "
                          f"{len(self.last_detection_result['found_objects'])} types")
            cv2.putText(frame, result_text, (w - 500, 40),
                        font, 0.6, (0, 255, 255), 1)
        
        return frame
    
    def run(self):
        """
        Pipeline futtatása
        """
        self._init_video_capture()
        
        print("="*70)
        print("VEZÉRLÉS:")
        print("  [SPACE]  - Snapshot készítése és detektálás")
        print("  [Q]      - Kilépés")
        print("="*70 + "\n")
        
        print("▶️  Videó stream indítása...\n")
        
        try:
            while True:
                ret, frame = self.cap.read()
                
                if not ret:
                    if self.video_path:
                        # Videó vége - újraindítás
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    else:
                        print("❌ Nem sikerült képkockát olvasni")
                        break
                
                # Overlay rajzolása
                display_frame = self._draw_overlay(frame.copy())
                
                # Megjelenítés
                cv2.imshow('Live Video Detection', display_frame)
                
                # Billentyű kezelés
                key = cv2.waitKey(1) & 0xFF
                
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
            # Cleanup
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            
            print("\n" + "="*70)
            print(f"✅ KÉSZ! Összesen {self.snapshot_count} snapshot készült")
            print(f"📁 Eredmények: {self.output_dir}/")
            print("="*70 + "\n")


def main():
    """Fő futtatási függvény"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Live Video Detection Pipeline'
    )
    parser.add_argument(
        '--video',
        type=str,
        default=None,
        help='Videó fájl elérési útja (alapértelmezett: webcam)'
    )
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Kamera ID (alapértelmezett: 0)'
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
        '--stream',
        type=str,
        default=None,
        help='HTTP stream URL (pl. http://192.168.1.100:5000/video)'
    )
    
    args = parser.parse_args()
    
    # Pipeline indítása
    pipeline = LiveVideoDetectionPipeline(
        model_path=args.model,
        backend="transformers",
        categories=COMMON_ASSEMBLY_OBJECTS,
        output_dir=args.output,
        camera_id=args.camera,
        video_path=args.video,
        stream_url=args.stream
    )
    
    pipeline.run()


if __name__ == "__main__":
    main()
