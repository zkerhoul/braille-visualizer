// === frontend/sketch.js ===
// const TOUCH_WIDTH = 1600;
// const TOUCH_HEIGHT = 350;
// const PADDING = 50;
//
// const ROWS = 21;
// const COLS = 96;
//
// let cellWidth, cellHeight;
//
// let socket = new WebSocket(WS_HOST);
//
// function setup() {
//   createCanvas(800, 400);
//   background(0);
//   noStroke();
//
//   // WebSocket handlers
//   socket.onmessage = handleMessage;
//   socket.onopen    = () => console.log("Connected to WebSocket");
//   socket.onclose   = () => console.log("Disconnected from WebSocket");
//   socket.onerror   = (err) => console.error("WebSocket error:", err);
// }
//
// function handleMessage(event) {
//   const msg = JSON.parse(event.data);
//
//   if (msg.type === "matrix") {
//     // Received a new 20×96 array → update and mark bgLayer dirty
//     dotMatrix = msg.mat;
//     bgNeedsRedraw = true;
//   }
//   else if (msg.type === "touch") {
//     let fid = msg.id;
//     if (msg.action === "down") {
//       // Finger went down → add to fingers map
//       let cx = map(msg.x, 0, 1600, PADDING/2, width - PADDING/2);
//       let cy = map(msg.y, 0, 350,  PADDING/2, height - PADDING/2);
//       let c  = GESTURE_COLORS[msg.gesture] || DEFAULT_COLOR;
//       fingers[fid] = { x: cx, y: cy, color: c };
//     }
//     else if (msg.action === "move") {
//       // Finger moved → update its x,y, color (if needed)
//       if (fingers[fid]) {
//         let cx = map(msg.x, 0, 1600, PADDING/2, width - PADDING/2);
//         let cy = map(msg.y, 0, 350,  PADDING/2, height - PADDING/2);
//         let c  = GESTURE_COLORS[msg.gesture] || DEFAULT_COLOR;
//         fingers[fid].x     = cx;
//         fingers[fid].y     = cy;
//         fingers[fid].color = c;
//       }
//     }
//     else if (msg.action === "up") {
//       // Finger lifted → remove from map
//       delete fingers[fid];
//     }
//   }
// }
//
// function draw() {
//   background(0);
//
//   let tx = map(mouseX, 0, width, 0, TOUCH_WIDTH);
//   let ty = map(mouseY, 0, height, 0, TOUCH_HEIGHT);
//
//   let mapped = touchToCanvas(tx, ty);
//
//   // Draw mapped circle
//   fill(0, 255, 255);
//   ellipse(mapped.x, mapped.y, 20);
//
// }
//
// function touchToCanvas(x, y) {
//   // map from touchscreen space -> canvas space
//   let cx = map(x, 0, TOUCH_WIDTH, PADDING, width - PADDING);
//   let cy = map(y, 0, TOUCH_HEIGHT, PADDING, height - PADDING);
//   return { x: cx, y: cy };
// }

let VIRTUAL_WIDTH  = 1600;
let VIRTUAL_HEIGHT = 350;
let VIRTUAL_PADDING = 50;

let scaleFactor;
let offsetX, offsetY;

let socket = new WebSocket(WS_HOST);

function setup() {
  createCanvas(windowWidth, windowHeight);
  calculateScaling();

  // WebSocket handlers
  // socket.onmessage = handleMessage;
  // socket.onopen    = () => console.log("Connected to WebSocket");
  // socket.onclose   = () => console.log("Disconnected from WebSocket");
  // socket.onerror   = (err) => console.error("WebSocket error:", err);
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
  calculateScaling();
}

function calculateScaling() {
  let scaleX = width  / VIRTUAL_WIDTH;
  let scaleY = height / VIRTUAL_HEIGHT;
  scaleFactor = min(scaleX, scaleY);

  // Center it on screen if canvas is larger than virtual space
  offsetX = (width  - VIRTUAL_WIDTH  * scaleFactor) / 2;
  offsetY = (height - VIRTUAL_HEIGHT * scaleFactor) / 2;
}

function draw() {
  background(30);

  // 1. Apply transform
  push();
  // translate(offsetX, offsetY);
  scale(scaleFactor);

  // 2. Draw in virtual space (0–1600 × 0–350)
  drawGrid();

  // You could draw touches at (x, y) here directly

  pop();
}

function drawGrid() {
  stroke(100);
  noFill();

  const rows = 21;
  const cols = 96;

  let gridWidth  = VIRTUAL_WIDTH  - 2 * VIRTUAL_PADDING;
  let gridHeight = VIRTUAL_HEIGHT - 2 * VIRTUAL_PADDING;

  let cellW = gridWidth / cols;
  let cellH = gridHeight / rows;

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      let x = VIRTUAL_PADDING + c * cellW;
      let y = VIRTUAL_PADDING + r * cellH;
      rect(x, y, cellW, cellH);
    }
  }
}