import React from "react";
import WebSocketComponent from "./WebSocketComponent";

const Backend_test = () => {
  return (
    <div className="camera-container">
    <WebSocketComponent cameraId={0} label="default cam" />
    <WebSocketComponent cameraId={1} label="usb cam" />
    <WebSocketComponent cameraId={2} label="usb cam" />
  </div>
  );
};

export default Backend_test;