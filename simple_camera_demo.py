#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rex-Omni Simple Camera Detection Example
Single frame capture and detection
"""

import os
import sys
import cv2
from PIL import Image

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from rex_omni.wrapper import RexOmniWrapper
from rex_omni.utils import RexOmniVisualize


def capture_and_detect():
    """
    Simple example: capture one frame from webcam and run detection
    """
    
    # 1. Initialize model
    print("Loading Rex-Omni model...")
    model = RexOmniWrapper(
        model_path="models/Rex-Omni",  # Adjust path if needed
        backend="transformers",
        max_tokens=1024,
        temperature=0.0
    )
    print("Model loaded!")
    
    # 2. Open camera
    print("Opening camera...")
    cap = cv2.VideoCapture(0)  # 0 = default webcam
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    print("Camera opened! Press SPACE to capture, ESC to exit")
    
    # 3. Show preview and wait for capture
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break
        
        cv2.imshow('Camera Preview - Press SPACE to capture', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            print("Exiting without capture")
            cap.release()
            cv2.destroyAllWindows()
            return
        elif key == 32:  # SPACE
            print("Captured!")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    # 4. Convert OpenCV image to PIL
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_frame)
    
    # 5. Run object detection
    print("Running object detection...")
    categories = ["person", "car", "dog", "cat", "phone", "laptop", "cup", "bottle"]
    
    result = model.inference(
        images=pil_image,
        task="detection",
        categories=categories
    )
    
    # 6. Process results
    if result and len(result) > 0:
        result_dict = result[0]
        
        print("\n" + "="*60)
        print("DETECTION RESULTS")
        print("="*60)
        
        # Print raw output
        print("\nRaw output:")
        print(result_dict.get('raw_output', 'N/A'))
        
        # Print extracted predictions
        print("\nExtracted predictions:")
        predictions = result_dict.get('extracted_predictions', {})
        if predictions:
            for category, detections in predictions.items():
                print(f"\n{category}: {len(detections)} detected")
                for i, det in enumerate(detections, 1):
                    if isinstance(det, dict):
                        bbox = det.get('bbox', 'N/A')
                        score = det.get('score', 'N/A')
                        print(f"  {i}. bbox: {bbox}, score: {score}")
                    else:
                        print(f"  {i}. {det}")
        else:
            print("No objects detected")
        
        # Print statistics
        print(f"\nInference time: {result_dict.get('inference_time', 0):.2f}s")
        print(f"Tokens per second: {result_dict.get('tokens_per_second', 0):.1f}")
        
        # 7. Create visualization
        print("\nCreating visualization...")
        visualizer = RexOmniVisualize()
        vis_image = visualizer.visualize(
            image=pil_image,
            task="detection",
            predictions=predictions,
            image_size=pil_image.size
        )
        
        # Save results
        output_path = "detection_result.jpg"
        vis_image.save(output_path)
        print(f"Visualization saved to: {output_path}")
        
        # Display result
        import numpy as np
        vis_array = np.array(vis_image)
        vis_bgr = cv2.cvtColor(vis_array, cv2.COLOR_RGB2BGR)
        cv2.imshow('Detection Result - Press any key to close', vis_bgr)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        print("\nDone!")
    else:
        print("No results returned from model")


if __name__ == "__main__":
    capture_and_detect()
