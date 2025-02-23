from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2
import threading
from collections import deque
import asyncio

app = FastAPI()

# Update with actual camera URLs or indices
camera_urls = {0: 0, 1: 1, 2: 2}  # Example: {0: "rtsp://camera1", 1: "rtsp://camera2"}
frame_queues = {cam_id: deque(maxlen=1) for cam_id in camera_urls}

class CameraThread(threading.Thread):
    def __init__(self, camera_id: int):
        super().__init__()
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(camera_urls[camera_id])
        self.cap.set(cv2.CAP_PROP_FPS, 30)  # Set desired FPS
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (640, 480))  # Reduce resolution
                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 65])  # Lower quality
                if len(frame_queues[self.camera_id]) == frame_queues[self.camera_id].maxlen:
                    frame_queues[self.camera_id].popleft()  # Drop oldest frame
                frame_queues[self.camera_id].append(buffer.tobytes())

    def stop(self):
        self.running = False
        self.cap.release()

# Start all camera threads
camera_threads = {cam_id: CameraThread(cam_id) for cam_id in camera_urls}
for cam_thread in camera_threads.values():
    cam_thread.start()

@app.websocket("/ws/webrtc/{camera_id}")
async def webrtc_endpoint(websocket: WebSocket, camera_id: int):
    if camera_id not in camera_urls:
        await websocket.close()
        return
    
    await websocket.accept()
    await websocket.send_json({"status": "connected", "camera_id": camera_id})
    
    try:
        while True:
            if frame_queues[camera_id]:
                frame_data = frame_queues[camera_id].pop()
                await websocket.send_bytes(frame_data)
            await asyncio.sleep(0.01)  # Small delay to avoid overwhelming the frontend
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for camera {camera_id}")
    except Exception as e:
        print(f"Error in WebSocket communication: {e}")
    finally:
        await websocket.close()

# Graceful shutdown
@app.on_event("shutdown")
def shutdown_event():
    for cam_thread in camera_threads.values():
        cam_thread.stop()
    print("Camera threads stopped")