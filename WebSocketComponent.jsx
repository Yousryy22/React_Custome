import { useEffect, useRef } from "react";

const WebSocketComponent = ({ cameraId }) => {
  const videoRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    if (cameraId === undefined || cameraId === null) {
      console.error("Camera ID is undefined or invalid!");
      return;
    }

    const wsUrl = `ws://localhost:8000/ws/webrtc/${cameraId}`;
    console.log("Connecting to:", wsUrl);
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log(`WebSocket connected to camera ${cameraId}`);
    };

    wsRef.current.onmessage = async (event) => {
      try {
        const data = await event.data.arrayBuffer();
        const blob = new Blob([data], { type: "image/jpeg" });

        // Validate the Blob
        if (blob.size > 0) {
          createImageBitmap(blob)
            .then((bitmap) => {
              const ctx = videoRef.current.getContext("2d");
              ctx.drawImage(bitmap, 0, 0, videoRef.current.width, videoRef.current.height);
            })
            .catch((error) => {
              console.error("Error decoding image:", error);
            });
        } else {
          console.error("Received empty or invalid image data.");
        }
      } catch (error) {
        console.error("Error processing WebSocket message:", error);
      }
    };

    wsRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    wsRef.current.onclose = () => {
      console.log("WebSocket connection closed.");
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [cameraId]);

  return <canvas ref={videoRef} width="640" height="480" />;
};

export default WebSocketComponent;