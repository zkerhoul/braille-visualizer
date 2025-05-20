// === frontend/sketch.js ===
console.log("sketch loaded");
let rows = 20;
let cols = 96;
let cellW, cellH;
let dotMatrix = [];

let socket = new WebSocket(WS_HOST);

function setup() {
  createCanvas(1600, 350);
  cellW = width / cols;
  cellH = height / rows;

  // Initialize empty matrix
  for (let i = 0; i < rows; i++) {
    dotMatrix[i] = Array(cols).fill(0);
  }

  // Connect to WebSocket server from config.js
  socket.onmessage = (event) => {
    console.log("Matrix raw event:", event.data);
    let data = JSON.parse(event.data);
    console.log("Parsed matrix:", data);
    dotMatrix = data;
  };

  socket.onopen = () => console.log("Connected to WebSocket");
  socket.onclose = () => console.log("Disconnected from WebSocket");
  socket.onerror = (err) => console.error("WebSocket error:", err);
}

function draw() {
  background(20);

  noStroke();
  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      let x = j * cellW;
      let y = i * cellH;
      fill(dotMatrix[i][j] ? "white" : "#444");
      ellipse(x + cellW / 2, y + cellH / 2, cellW * 0.7, cellH * 0.7);
    }
  }
}