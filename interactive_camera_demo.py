#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rex-Omni Interactive Camera Detection
Interactive real-time detection with keyboard controls for changing categories
"""

import os
import sys
import cv2
import time
from PIL import Image
import numpy as np

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from rex_omni.wrapper import RexOmniWrapper
from rex_omni.utils import RexOmniVisualize


# Predefined category presets
CATEGORY_PRESETS = {
    '1': {
        'name': 'Emberek',
        'categories': ['person'],
        'description': 'Csak emberek detektálása'
    },
    '2': {
        'name': 'Járművek',
        'categories': ['car', 'truck', 'bus', 'motorcycle', 'bicycle'],
        'description': 'Járművek detektálása'
    },
    '3': {
        'name': 'Állatok',
        'categories': ['dog', 'cat', 'bird', 'horse', 'cow'],
        'description': 'Háziállatok és állatok'
    },
    '4': {
        'name': 'Elektronika',
        'categories': ['phone', 'laptop', 'tv', 'keyboard', 'mouse'],
        'description': 'Elektronikai eszközök'
    },
    '5': {
        'name': 'Bútorok',
        'categories': ['chair', 'couch', 'bed', 'table', 'desk'],
        'description': 'Bútorok és berendezési tárgyak'
    },
    '6': {
        'name': 'Konyha',
        'categories': ['bottle', 'cup', 'fork', 'knife', 'spoon', 'bowl'],
        'description': 'Konyhai eszközök'
    },
    '7': {
        'name': 'Minden (COCO)',
        'categories': [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 
            'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 
            'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
            'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ],
        'description': 'Összes COCO kategória'
    },
}


class InteractiveCameraDetector:
    def __init__(
        self, 
        model_path,
        backend="transformers",
        camera_source=0,
        fps_limit=5
    ):
        """
        Initialize Interactive Camera Detector
        """
        print("Initializing Rex-Omni model...")
        self.model = RexOmniWrapper(
            model_path=model_path,
            backend=backend,
            max_tokens=1024,
            temperature=0.0
        )
        
        self.camera_source = camera_source
        self.fps_limit = fps_limit
        self.current_preset = '1'  # Default to 'Emberek'
        self.categories = CATEGORY_PRESETS[self.current_preset]['categories']
        self.task = "detection"
        
        # Initialize visualizer
        self.visualizer = RexOmniVisualize()
        
        # Initialize camera
        print(f"Opening camera: {camera_source}")
        self.cap = cv2.VideoCapture(camera_source)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera: {camera_source}")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print("Initialization complete!")
        
    def cv2_to_pil(self, cv2_image):
        """Convert OpenCV image to PIL Image"""
        rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_image)
    
    def pil_to_cv2(self, pil_image):
        """Convert PIL Image to OpenCV image"""
        rgb_array = np.array(pil_image)
        return cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
    
    def draw_info_panel(self, frame, fps, num_detections, inference_time):
        """Draw information panel on frame"""
        h, w = frame.shape[:2]
        
        # Semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (w - 10, 180), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
        
        # FPS
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Detections
        cv2.putText(frame, f"Detections: {num_detections}", (20, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Inference time
        cv2.putText(frame, f"Time: {inference_time:.2f}s", (20, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Current preset
        preset_name = CATEGORY_PRESETS[self.current_preset]['name']
        cv2.putText(frame, f"Mode: {preset_name}", (20, 130), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Categories (truncated if too many)
        cat_text = ', '.join(self.categories[:5])
        if len(self.categories) > 5:
            cat_text += f" ... (+{len(self.categories) - 5})"
        cv2.putText(frame, f"Categories: {cat_text}", (20, 160), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame
    
    def draw_help_panel(self, frame):
        """Draw help panel"""
        h, w = frame.shape[:2]
        
        # Help panel on right side
        overlay = frame.copy()
        cv2.rectangle(overlay, (w - 350, 10), (w - 10, 300), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        help_texts = [
            "CONTROLS:",
            "1-7: Change category preset",
            "T: Change task type",
            "Q: Quit",
            "S: Save frame",
            "P: Pause/Resume",
            "H: Toggle help",
        ]
        
        for i, text in enumerate(help_texts):
            y = 40 + i * 35
            cv2.putText(frame, text, (w - 340, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        return frame
    
    def process_frame(self, frame):
        """Process a single frame"""
        pil_image = self.cv2_to_pil(frame)
        
        inference_params = {
            "images": pil_image,
            "task": self.task,
            "categories": self.categories
        }
        
        start_time = time.time()
        result = self.model.inference(**inference_params)
        inference_time = time.time() - start_time
        
        if result and len(result) > 0:
            result_dict = result[0] if isinstance(result, list) else result
            
            vis_image = self.visualizer.visualize(
                image=pil_image,
                task=self.task,
                predictions=result_dict.get('extracted_predictions', {}),
                image_size=pil_image.size
            )
            
            vis_frame = self.pil_to_cv2(vis_image)
            
            num_detections = sum(
                len(v) if isinstance(v, list) else 0 
                for v in result_dict.get('extracted_predictions', {}).values()
            )
            
            return vis_frame, num_detections, inference_time
        
        return frame, 0, inference_time
    
    def print_presets(self):
        """Print available presets"""
        print("\n" + "="*70)
        print("CATEGORY PRESETS:")
        print("="*70)
        for key, preset in CATEGORY_PRESETS.items():
            print(f"{key}. {preset['name']}: {preset['description']}")
            print(f"   Categories: {', '.join(preset['categories'][:5])}", end="")
            if len(preset['categories']) > 5:
                print(f" ... (+{len(preset['categories']) - 5})")
            else:
                print()
        print("="*70 + "\n")
    
    def change_preset(self, key):
        """Change category preset"""
        if key in CATEGORY_PRESETS:
            self.current_preset = key
            self.categories = CATEGORY_PRESETS[key]['categories']
            preset_name = CATEGORY_PRESETS[key]['name']
            print(f"\n✓ Preset changed to: {preset_name}")
            print(f"  Categories: {', '.join(self.categories[:5])}", end="")
            if len(self.categories) > 5:
                print(f" ... (+{len(self.categories) - 5})")
            else:
                print()
    
    def run(self):
        """Run interactive detection loop"""
        print("\n" + "="*70)
        print("INTERACTIVE CAMERA OBJECT DETECTION")
        print("="*70)
        self.print_presets()
        print("Controls:")
        print("  - Press '1-7' to change category preset")
        print("  - Press 'q' to quit")
        print("  - Press 's' to save current frame")
        print("  - Press 'p' to pause/resume")
        print("  - Press 'h' to toggle help panel")
        print("="*70 + "\n")
        
        frame_count = 0
        fps = 0
        fps_update_time = time.time()
        frame_time = 1.0 / self.fps_limit
        last_process_time = 0
        paused = False
        show_help = True
        num_detections = 0
        inference_time = 0
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame")
                    break
                
                current_time = time.time()
                display_frame = frame.copy()
                
                # Process frame if not paused
                if not paused and (current_time - last_process_time) >= frame_time:
                    try:
                        processed_frame, num_detections, inference_time = self.process_frame(frame)
                        display_frame = processed_frame
                        last_process_time = current_time
                    except Exception as e:
                        print(f"Error: {e}")
                
                # Draw info panel
                display_frame = self.draw_info_panel(display_frame, fps, num_detections, inference_time)
                
                # Draw help panel if enabled
                if show_help:
                    display_frame = self.draw_help_panel(display_frame)
                
                # Update FPS
                frame_count += 1
                if current_time - fps_update_time >= 1.0:
                    fps = frame_count / (current_time - fps_update_time)
                    frame_count = 0
                    fps_update_time = current_time
                
                # Show frame
                cv2.imshow('Rex-Omni Interactive Detection', display_frame)
                
                # Handle keyboard
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"detection_{timestamp}.jpg"
                    cv2.imwrite(filename, display_frame)
                    print(f"✓ Saved: {filename}")
                elif key == ord('p'):
                    paused = not paused
                    print(f"{'PAUSED' if paused else 'RESUMED'}")
                elif key == ord('h'):
                    show_help = not show_help
                elif chr(key) in CATEGORY_PRESETS:
                    self.change_preset(chr(key))
                    
        except KeyboardInterrupt:
            print("\nInterrupted")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        self.cap.release()
        cv2.destroyAllWindows()
        print("Done!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Rex-Omni Interactive Camera Detection")
    parser.add_argument("--model_path", type=str, default="models/Rex-Omni")
    parser.add_argument("--backend", type=str, default="transformers", choices=["transformers", "vllm"])
    parser.add_argument("--camera", type=str, default="0")
    parser.add_argument("--fps", type=int, default=5)
    
    args = parser.parse_args()
    
    try:
        camera_source = int(args.camera)
    except ValueError:
        camera_source = args.camera
    
    detector = InteractiveCameraDetector(
        model_path=args.model_path,
        backend=args.backend,
        camera_source=camera_source,
        fps_limit=args.fps
    )
    
    detector.run()


if __name__ == "__main__":
    main()
