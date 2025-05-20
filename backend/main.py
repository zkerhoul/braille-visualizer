# === backend/main.py ===
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os
import uvicorn
import asyncio

from serial_read import SerialHandler

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_PATH = os.path.join(BASE_PATH, 'frontend')

app = FastAPI()

# serve static frontend from the frontend folder
app.mount("/static", StaticFiles(directory=FRONTEND_PATH, html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []

# serial connection
ser = SerialHandler()

# serve index manually
@app.get("/")
async def get_index():
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    print("Client connected")

    try:
        while True:
            with ser.lock:
                matrix = ser.matrix
            if matrix is not None:
                print("Sending matrix...")
                for client in clients:
                    try:
                        await client.send_json(matrix)
                    except Exception as e:
                        print("Error sending matrix: ", e)
            await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        clients.remove(websocket)
        print("Client disconnected")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)