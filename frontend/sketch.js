// === frontend/sketch.js ===
let rows = 20;
let cols = 96;
let cellWidth, cellHeight;

let dotMatrix = [];
let fingers = {};

// connect to WebSocket server from config.js
let socket = new WebSocket(WS_HOST);

function setup() {
  createCanvas(1600, 350);

  cellWidth = width / cols;
  cellHeight = height / rows;

  // initialize empty matrix
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
      color: color(255, 255, 255, 200),
    };
    if (msg.action == "down") {
      finger.down = true;
      finger.x = msg.x;
      finger.y = msg.y;
    } else if (msg.action == "up") {
      finger.down = false;
      finger.x = null;
      finger.y = null;
      finger.color = getGestureColor(null)
    } else if (msg.action == "move") {
      if (finger.down == true) {
        finger.color = getGestureColor(msg.gesture)
        stroke(finger.color);
        strokeWeight(40);
        line(finger.x, finger.y, msg.x, msg.y);
      }
      finger.x = msg.x;
      finger.y = msg.y;
    }
    fingers[msg.id] = finger;
  }
}

function getGestureColor(gesture) {
  if (gesture === "scrubbing") {
    return color(255, 0, 0, 200);
  }
  else {
    return color(255, 255, 255, 200);
  }
}

function draw() {
  noStroke();
  fill(0, 0, 0, 20);
  rect(0, 0, width, height);

  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      let x = j * cellWidth;
      let y = i * cellHeight;
      fill(dotMatrix[i][j] ? "white" : "#444");
      // only draw the circles that appear on the device
      if (j % 3 != 2 && i % 5 != 4) {
        ellipse(x + cellWidth / 2, y + cellHeight / 2, cellWidth * 0.56, cellHeight * 0.56);
      }
    }
  }
}
