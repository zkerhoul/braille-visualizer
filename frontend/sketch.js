// === frontend/sketch.js ===
let rows = 20;
let cols = 96;
let padding = 50;
let cellWidth, cellHeight;

let dotMatrix = [];
let doubleTaps = [];
let fingers = {};

// connect to WebSocket server from config.js
let socket = new WebSocket(WS_HOST);

function setup() {
  createCanvas(1600 + padding, 350 + padding);

  cellWidth = (width - padding) / cols;
  cellHeight = (height - padding) / rows;

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
  }

  else if (msg.type == "touch") {
    let finger = fingers[msg.id] || {
      down: false,
      x: null,
      y: null,
      color: color(255, 255, 255, 200)
    };
    if (msg.action == "down") {
      finger.down = true;
      finger.x = map(msg.x, 0, 1600, (padding / 2), width - (padding / 2));
      finger.y = map(msg.y, 0, 350, (padding / 2), height - (padding / 2));
    } else if (msg.action == "up") {
      finger.down = false;
      finger.x = null;
      finger.y = null;
      finger.color = getGestureColor(null)
    } else if (msg.action == "move") {
      if (finger.down == true) {
        finger.color = getGestureColor(msg.gesture);
        stroke(finger.color);
        strokeWeight(40);
        x_new = map(msg.x, 0, 1600, (padding / 2), width - (padding / 2));
        y_new = map(msg.y, 0, 350, (padding / 2), height - (padding / 2));
        line(finger.x, finger.y, x_new, y_new);
      }
      finger.x = map(msg.x, 0, 1600, (padding / 2), width - (padding / 2));
      finger.y = map(msg.y, 0, 350, (padding / 2), height - (padding / 2));
    }
    fingers[msg.id] = finger;
  }

  else if (msg.type == "double tap") {
    row_idx = msg.row * 5
    y_idxs = [row_idx, row_idx + 1, row_idx + 2, row_idx + 3]

    col_idx = msg.column * 3
    x_idxs = [col_idx, col_idx + 1]

    for (let x of x_idxs) {
      for (let y of y_idxs) {
        doubleTaps.push({'x_idx': x, 'y_idx': y, 'life': 300})
      }
    }
  }
}

function getGestureColor(gesture) {
  if (gesture === "scrubbing") {
    return color(255, 0, 0, 200);
  }

  else if (gesture === "regression") {
    return color(255, 0, 255, 200)
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
      let x = j * cellWidth + (padding / 2);
      let y = i * cellHeight + (padding / 2);
      fill(dotMatrix[i][j] ? "white" : "#444");
      // only draw the circles that appear on the device
      if (j % 3 != 2 && i % 5 != 4) {
        ellipse(x + cellWidth / 2, y + cellHeight / 2, cellWidth * 0.56, cellHeight * 0.56);
      }
    }
  }

  for (let i = doubleTaps.length - 1; i >= 0; i--) {
    let dt = doubleTaps[i];
    let x = dt.x_idx * cellWidth + (padding / 2);
    let y = dt.y_idx * cellHeight + (padding / 2);
    let alpha = map(dt.life, 0, 300, 0, 200);
    fill(0, 210, 255, alpha);
    ellipse(x + cellWidth / 2, y + cellHeight / 2, cellWidth * 0.56, cellHeight * 0.56);

    dt.life = dt.life - 3;
    if (dt.life === 0) {
      doubleTaps.splice(i, 1);
    }
    else {
      doubleTaps[i] = dt;
    }

  }
}
