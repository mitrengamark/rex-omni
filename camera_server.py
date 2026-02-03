#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Camera Streaming Server
HTTP alapú kamera stream a laptopról

Használat a LAPTOPON:
    python camera_server.py
    
Majd a SZERVEREN:
    python live_video_detection.py --stream http://LAPTOP_IP:5001/video
"""

from flask import Flask, Response
import cv2
import argparse

app = Flask(__name__)

# Globális camera objektum
camera = None
camera_id = 0


def get_camera():
    """Kamera singleton"""
    global camera
    if camera is None:
        try:
            camera = cv2.VideoCapture(camera_id)
            
            # Macbook kamera beállítások
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            camera.set(cv2.CAP_PROP_FPS, 30)
            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimális buffer
            
            # Ellenőrizzük hogy működik-e
            success, test_frame = camera.read()
            if not success or test_frame is None:
                print("⚠️  Kamera inicializálás: első read sikertelen, újrapróbálás...")
                camera.release()
                camera = cv2.VideoCapture(camera_id)
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                camera.set(cv2.CAP_PROP_FPS, 30)
                camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception as e:
            print(f"❌ Kamera inicializálás hiba: {e}")
            raise
    
    return camera


def generate_frames():
    """Generálja a JPEG frame-eket"""
    cam = get_camera()
    
    while True:
        success, frame = cam.read()
        if not success:
            break
        
        # JPEG kódolás
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        
        # Multipart response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/video')
def video_feed():
    """Video streaming route"""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/snapshot')
def snapshot():
    """Single frame snapshot - jobb VPN/instabil kapcsolatokhoz"""
    cam = get_camera()
    
    # Buffer flush - olvassunk pár frame-et hogy friss legyen
    # Macbook kameránál a buffer-ben gyakran lejárt frame van
    for _ in range(3):
        cam.read()
    
    # Most jöjjön a tényleges snapshot
    max_retries = 5
    for attempt in range(max_retries):
        success, frame = cam.read()
        
        if success and frame is not None:
            # JPEG kódolás
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if ret and buffer is not None:
                return Response(
                    buffer.tobytes(),
                    mimetype='image/jpeg'
                )
        
        # Ha sikertelen, várj egy kicsit és próbálj újra
        if attempt < max_retries - 1:
            import time
            time.sleep(0.05)
    
    # Ha mind az 5 próba sikertelen
    print(f"⚠️  Snapshot sikertelen {max_retries} próba után")
    return "Camera not ready", 503


@app.route('/test')
def test():
    """Test endpoint"""
    return """
    <html>
        <head><title>Camera Stream</title></head>
        <body>
            <h1>Camera Stream Test</h1>
            <img src="/video" width="100%">
            <p>Ha látod a kamerát, akkor működik!</p>
            <p>A szerveren használd: --stream http://LAPTOP_IP:5001/video</p>
        </body>
    </html>
    """


@app.route('/')
def index():
    """Info page"""
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    return f"""
    <html>
        <head><title>Camera Server</title></head>
        <body>
            <h1>📷 Camera Streaming Server</h1>
            <p><strong>Status:</strong> Running ✓</p>
            <p><strong>Camera ID:</strong> {camera_id}</p>
            <p><strong>Server IP:</strong> {local_ip}</p>
            <p><strong>Stream URL:</strong> http://{local_ip}:5001/video</p>
            <hr>
            <h2>Használat:</h2>
            <ol>
                <li>Teszteld a stream-et: <a href="/test">/test</a></li>
                <li>A szerveren futtasd:
                    <pre>python live_video_detection.py --stream http://{local_ip}:5001/video</pre>
                </li>
            </ol>
        </body>
    </html>
    """


def main():
    parser = argparse.ArgumentParser(
        description='Camera Streaming Server for Remote Detection'
    )
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Kamera ID (alapértelmezett: 0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5001,
        help='Port szám (alapértelmezett: 5001)'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host cím (alapértelmezett: 0.0.0.0)'
    )
    
    args = parser.parse_args()
    
    global camera_id
    camera_id = args.camera
    
    print("\n" + "="*70)
    print("📷 CAMERA STREAMING SERVER")
    print("="*70 + "\n")
    print(f"🎥 Kamera ID: {args.camera}")
    print(f"🌐 Host: {args.host}:{args.port}")
    print(f"\n✓ Server indítása...\n")
    print("="*70)
    print("Nyisd meg a böngészőben: http://localhost:5001")
    print("vagy http://LAPTOP_IP:5001 másik gépről")
    print("="*70 + "\n")
    
    app.run(
        host=args.host,
        port=args.port,
        debug=False,
        threaded=True
    )


if __name__ == '__main__':
    main()
