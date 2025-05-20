# === backend/main.py ===
# FastAPI + WebSocket server that sends dot updates to the frontend

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os
import uvicorn
import asyncio
import numpy as np

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_PATH = os.path.join(BASE_PATH, 'frontend')

app = FastAPI()

# Serve static frontend from the "frontend" folder
app.mount("/static", StaticFiles(directory=FRONTEND_PATH, html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []

# Serve index.html manually
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
            # Simulate a random matrix update (20x96 binary grid)
            matrix = np.random.choice([0, 1], size=(20, 96)).tolist()
            print("Sending matrix...")
            for client in clients:
                try:
                    await client.send_json(matrix)
                except Exception as e:
                    print("Error sending matrix...", e)
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        clients.remove(websocket)
        print("Client disconnected")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# === backend/main.py ===