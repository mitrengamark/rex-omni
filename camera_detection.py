#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rex-Omni Camera Object Detection
Real-time object detection using webcam or IP camera
"""

import os
import sys
import cv2
import time
import argparse
from PIL import Image
import numpy as np

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from rex_omni.wrapper import RexOmniWrapper
from rex_omni.tasks import TaskType
from rex_omni.utils import RexOmniVisualize


class CameraObjectDetector:
    def __init__(
        self, 
        model_path,
        backend="transformers",
        max_tokens=1024,
        temperature=0.0,
        camera_source=0,
        fps_limit=5,
        categories=None,
        task="detection",
        keypoint_type="person",
        confidence_threshold=0.3
    ):
        """
        Initialize Camera Object Detector
        
        Args:
            model_path: Path to Rex-Omni model
            backend: 'transformers' or 'vllm'
            max_tokens: Maximum tokens for generation
            temperature: Temperature for sampling
            camera_source: Camera index (0 for default webcam) or IP camera URL
            fps_limit: Maximum FPS for processing (to reduce CPU/GPU load)
            categories: List of categories to detect (e.g., ['person', 'car', 'dog'])
            task: Task type ('detection', 'pointing', 'keypoint', 'ocr_box', etc.)
            keypoint_type: Type for keypoint detection ('person', 'animal', 'hand')
            confidence_threshold: Confidence threshold for filtering results
        """
        print("Initializing Rex-Omni model...")
        self.model = RexOmniWrapper(
            model_path=model_path,
            backend=backend,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        self.camera_source = camera_source
        self.fps_limit = fps_limit
        self.categories = categories or ["person", "car", "dog", "cat"]
        self.task = task
        self.keypoint_type = keypoint_type
        self.confidence_threshold = confidence_threshold
        
        # Initialize visualizer
        self.visualizer = RexOmniVisualize()
        
        # Initialize camera
        print(f"Opening camera: {camera_source}")
        self.cap = cv2.VideoCapture(camera_source)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera: {camera_source}")
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("Initialization complete!")
        
    def cv2_to_pil(self, cv2_image):
        """Convert OpenCV image (BGR) to PIL Image (RGB)"""
        rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_image)
    
    def pil_to_cv2(self, pil_image):
        """Convert PIL Image (RGB) to OpenCV image (BGR)"""
        rgb_array = np.array(pil_image)
        return cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
    
    def draw_fps(self, frame, fps):
        """Draw FPS on frame"""
        cv2.putText(
            frame, 
            f"FPS: {fps:.1f}", 
            (10, 30), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            (0, 255, 0), 
            2
        )
        return frame
    
    def draw_info(self, frame, num_detections, inference_time):
        """Draw detection info on frame"""
        info_text = f"Detections: {num_detections} | Time: {inference_time:.2f}s"
        cv2.putText(
            frame, 
            info_text, 
            (10, 70), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.7, 
            (0, 255, 255), 
            2
        )
        return frame
    
    def process_frame(self, frame):
        """Process a single frame with Rex-Omni"""
        # Convert to PIL Image
        pil_image = self.cv2_to_pil(frame)
        
        # Prepare inference parameters
        inference_params = {
            "images": pil_image,
            "task": self.task,
        }
        
        # Add task-specific parameters
        if self.task == "keypoint":
            inference_params["keypoint_type"] = self.keypoint_type
            inference_params["categories"] = [self.keypoint_type]
        else:
            inference_params["categories"] = self.categories
        
        # Run inference
        start_time = time.time()
        result = self.model.inference(**inference_params)
        inference_time = time.time() - start_time
        
        # Process result
        if result and len(result) > 0:
            result_dict = result[0] if isinstance(result, list) else result
            
            # Create visualization
            vis_image = self.visualizer.visualize(
                image=pil_image,
                task=self.task,
                predictions=result_dict.get('extracted_predictions', {}),
                image_size=pil_image.size
            )
            
            # Convert back to OpenCV
            vis_frame = self.pil_to_cv2(vis_image)
            
            # Count detections
            num_detections = sum(
                len(v) if isinstance(v, list) else 0 
                for v in result_dict.get('extracted_predictions', {}).values()
            )
            
            return vis_frame, num_detections, inference_time
        
        return frame, 0, inference_time
    
    def run(self):
        """Run real-time detection loop"""
        print("\n" + "="*60)
        print("Camera Object Detection Running!")
        print("="*60)
        print(f"Task: {self.task}")
        print(f"Categories: {', '.join(self.categories)}")
        print(f"FPS Limit: {self.fps_limit}")
        print(f"Controls:")
        print("  - Press 'q' to quit")
        print("  - Press 's' to save current frame")
        print("  - Press 'p' to pause/resume")
        print("="*60 + "\n")
        
        frame_count = 0
        fps = 0
        fps_update_time = time.time()
        frame_time = 1.0 / self.fps_limit
        last_process_time = 0
        paused = False
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame from camera")
                    break
                
                current_time = time.time()
                
                # Display frame and FPS
                display_frame = frame.copy()
                display_frame = self.draw_fps(display_frame, fps)
                
                # Process frame if not paused and enough time has passed
                if not paused and (current_time - last_process_time) >= frame_time:
                    try:
                        processed_frame, num_detections, inference_time = self.process_frame(frame)
                        display_frame = processed_frame
                        display_frame = self.draw_fps(display_frame, fps)
                        display_frame = self.draw_info(display_frame, num_detections, inference_time)
                        last_process_time = current_time
                    except Exception as e:
                        print(f"Error processing frame: {e}")
                        display_frame = self.draw_fps(display_frame, fps)
                
                # Update FPS
                frame_count += 1
                if current_time - fps_update_time >= 1.0:
                    fps = frame_count / (current_time - fps_update_time)
                    frame_count = 0
                    fps_update_time = current_time
                
                # Show frame
                cv2.imshow('Rex-Omni Camera Detection', display_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("Quitting...")
                    break
                elif key == ord('s'):
                    # Save frame
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"detection_{timestamp}.jpg"
                    cv2.imwrite(filename, display_frame)
                    print(f"Saved: {filename}")
                elif key == ord('p'):
                    # Pause/resume
                    paused = not paused
                    status = "PAUSED" if paused else "RESUMED"
                    print(f"{status}")
                    
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        self.cap.release()
        cv2.destroyAllWindows()
        print("Done!")


def main():
    parser = argparse.ArgumentParser(
        description="Rex-Omni Real-time Camera Object Detection"
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default="models/Rex-Omni",
        help="Path to Rex-Omni model directory"
    )
    parser.add_argument(
        "--backend",
        type=str,
        default="transformers",
        choices=["transformers", "vllm"],
        help="Backend to use (transformers or vllm)"
    )
    parser.add_argument(
        "--camera",
        type=str,
        default="0",
        help="Camera source (0 for default webcam, or IP camera URL)"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=5,
        help="Maximum FPS for processing (default: 5, lower = less CPU/GPU load)"
    )
    parser.add_argument(
        "--categories",
        type=str,
        nargs="+",
        default=["person", "car", "dog", "cat", "phone", "laptop"],
        help="Categories to detect (space-separated list)"
    )
    parser.add_argument(
        "--task",
        type=str,
        default="detection",
        choices=["detection", "pointing", "keypoint", "ocr_box", "ocr_polygon"],
        help="Task type"
    )
    parser.add_argument(
        "--keypoint_type",
        type=str,
        default="person",
        choices=["person", "animal", "hand"],
        help="Keypoint type (for keypoint task)"
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=1024,
        help="Maximum tokens for generation"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Temperature for sampling"
    )
    
    args = parser.parse_args()
    
    # Convert camera argument
    try:
        camera_source = int(args.camera)
    except ValueError:
        camera_source = args.camera  # Assume it's a URL
    
    # Create detector
    detector = CameraObjectDetector(
        model_path=args.model_path,
        backend=args.backend,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        camera_source=camera_source,
        fps_limit=args.fps,
        categories=args.categories,
        task=args.task,
        keypoint_type=args.keypoint_type
    )
    
    # Run detection
    detector.run()


if __name__ == "__main__":
    main()
