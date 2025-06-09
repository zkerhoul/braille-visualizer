// === frontend/sketch.js ===

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

let VIRTUAL_WIDTH  = 1600;
let VIRTUAL_HEIGHT = 350;
let VIRTUAL_PADDING = 50;

let cellWidth, cellHeight;

let scaleFactor;
let offsetX, offsetY;

fingers = {};

let socket = new WebSocket(WS_HOST);

function setup() {
  createCanvas(windowWidth, windowHeight);
  calculateScaling();

  // WebSocket handlers
  socket.onmessage = handleMessage;
  socket.onopen    = () => console.log("Connected to WebSocket");
  socket.onclose   = () => console.log("Disconnected from WebSocket");
  socket.onerror   = (err) => console.error("WebSocket error:", err);
}

function handleMessage(event) {
  const msg = JSON.parse(event.data);
  if (msg.type === "matrix") {
    // Received a new 20×96 array → update and mark bgLayer dirty
    dotMatrix = msg.mat;
    bgNeedsRedraw = true;
  } else if (msg.type === "touch") {
    let fid = msg.id;
    if (msg.action === "down") {
      // Finger went down → add to fingers map
      let cx = map(msg.x, 0, 1600, VIRTUAL_PADDING/2, VIRTUAL_WIDTH - VIRTUAL_PADDING/2);
      let cy = map(msg.y, 0, 350,  VIRTUAL_PADDING/2, VIRTUAL_HEIGHT - VIRTUAL_PADDING/2);
      let c  = GESTURE_COLORS[msg.gesture] || DEFAULT_COLOR;
      fingers[fid] = { x: cx, y: cy, color: c };
    } else if (msg.action === "move") {
      // Finger moved → update its x,y, color (if needed)
      if (fingers[fid]) {
        let cx = map(msg.x, 0, 1600, VIRTUAL_PADDING/2, VIRTUAL_WIDTH - VIRTUAL_PADDING/2);
        let cy = map(msg.y, 0, 350,  VIRTUAL_PADDING/2, VIRTUAL_HEIGHT - VIRTUAL_PADDING/2);
        let c  = GESTURE_COLORS[msg.gesture] || DEFAULT_COLOR;
        fingers[fid].x     = cx;
  }
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
  calculateScaling();
}

function calculateScaling() {
  let scaleX = width  / VIRTUAL_WIDTH;
  let scaleY = height / VIRTUAL_HEIGHT;
  scaleFactor = min(scaleX, scaleY);

  // center it on screen if canvas is larger than virtual space
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