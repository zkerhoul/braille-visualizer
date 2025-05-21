# === backend/main.py ===
import os
import uvicorn
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from serial_read import SerialHandler

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_PATH = os.path.join(BASE_PATH, 'frontend')

# serial connection
ser = SerialHandler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting up...")
    yield
    print("App shutting down...")
    ser.close()

app = FastAPI(lifespan=lifespan)

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
            try:
                event = ser.events.get_nowait()
            except Exception:
                await asyncio.sleep(0.01)
                continue

            for client in clients:
                try:
                    await client.send_json(event)
                except Exception as e:
                    print("Error sending event to sketch: ", e)

    except WebSocketDisconnect:
        print("Client disconnected")
        if websocket in clients:
            clients.remove(websocket)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)