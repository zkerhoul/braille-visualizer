// === frontend/sketch.js ===
let rows = 20;
let cols = 96;
let cellW, cellH;
let dotMatrix = [];
let fingers = {};

// connect to WebSocket server from config.js
let socket = new WebSocket(WS_HOST);

function setup() {
  createCanvas(1600, 350);
  cellW = width / cols;
  cellH = height / rows;

  // Initialize empty matrix
  for (let i = 0; i < rows; i++) {
    dotMatrix[i] = Array(cols).fill(0);
  }

  socket.onmessage = handleMessage;
  socket.onopen = () => console.log("Connected to WebSocket");
  socket.onclose = () => console.log("Disconnected from WebSocket");
  socket.onerror = (err) => console.error("WebSocket error:", err);
}

function handleMessage(event) {
  const msg = JSON.parse(event.data);

  if (msg.type == "matrix") {
    dotMatrix = msg.mat;
  } else if (msg.type == "touch") {
    let finger = fingers[msg.id] || {
      down: false,
      x: null,
      y: null,
      color: color(random(255), random(255), random(255)),
    };
    if (msg.action == "down") {
      finger.down = true;
      finger.x = msg.x;
      finger.y = msg.y;
    } else if (msg.action == "up") {
      finger.down = false;
      finger.x = null;
      finger.y = null;
    } else if (msg.action == "move") {
      if (finger.down == true) {
        stroke(finger.color);
        strokeWeight(2);
        line(finger.x, finger.y, msg.x, msg.y, msg.color);
      }
      finger.x = msg.x;
      finger.y = msg.y;
    }
    fingers[msg.id] = finger;
  }
}

function draw() {
  background(20);
  noStroke();
  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      let x = j * cellW;
      let y = i * cellH;
      fill(dotMatrix[i][j] ? "white" : "#444");
      // only draw the circles that appear on the device
      if (j % 3 != 2 && i % 5 != 4) {
        ellipse(x + cellW / 2, y + cellH / 2, cellW * 0.7, cellH * 0.7);
      }
    }
  }
}
