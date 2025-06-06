// === frontend/sketch.js ===

let ROWS    = 20;
let COLS    = 96;
let PADDING = 50;

let cellWidth, cellHeight;
let dotMatrix      = [];    // 20×96 array, updated on "matrix" messages
let doubleTaps     = [];    // (unchanged from before)
let fingers        = {};    // map: fingerID → { x, y, color }

let bgLayer;               // offscreen buffer for the dot‐matrix
let bgNeedsRedraw = true;  // set true whenever dotMatrix changes

let DEFAULT_COLOR;
let GESTURE_COLORS;

let socket = new WebSocket(WS_HOST);

function setup() {
  createCanvas(1600 + PADDING, 350 + PADDING);
  cellWidth  = (width  - PADDING) / COLS;
  cellHeight = (height - PADDING) / ROWS;

  // Create an offscreen buffer for the static 20×96 grid
  bgLayer = createGraphics(width, height);
  bgLayer.noStroke();

  // Initialize dotMatrix as all zeros
  for (let i = 0; i < ROWS; i++) {
    dotMatrix[i] = Array(COLS).fill(0);
  }

  // Gesture‐based colors (modify as needed)
  DEFAULT_COLOR = color(255, 255, 255, 200);
  GESTURE_COLORS = {
    scrubbing:   color(255,   0,   0, 200),
    regression:  color(255,   0, 255, 200)
  };

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
  }
  else if (msg.type === "touch") {
    let fid = msg.id;
    if (msg.action === "down") {
      // Finger went down → add to fingers map
      let cx = map(msg.x, 0, 1600, PADDING/2, width - PADDING/2);
      let cy = map(msg.y, 0, 350,  PADDING/2, height - PADDING/2);
      let c  = GESTURE_COLORS[msg.gesture] || DEFAULT_COLOR;
      fingers[fid] = { x: cx, y: cy, color: c };
    }
    else if (msg.action === "move") {
      // Finger moved → update its x,y, color (if needed)
      if (fingers[fid]) {
        let cx = map(msg.x, 0, 1600, PADDING/2, width - PADDING/2);
        let cy = map(msg.y, 0, 350,  PADDING/2, height - PADDING/2);
        let c  = GESTURE_COLORS[msg.gesture] || DEFAULT_COLOR;
        fingers[fid].x     = cx;
        fingers[fid].y     = cy;
        fingers[fid].color = c;
      }
    }
    else if (msg.action === "up") {
      // Finger lifted → remove from map
      delete fingers[fid];
    }
  }
  else if (msg.type === "double tap") {
    // (Unchanged double‐tap logic)
    let row_idx = msg.row * 5;
    let col_idx = msg.column * 3;
    for (let dy = 0; dy < 4; dy++) {
      for (let dx = 0; dx < 2; dx++) {
        doubleTaps.push({
          x_idx: col_idx + dx,
          y_idx: row_idx + dy,
          life:  300
        });
      }
    }
  }
}

function draw() {
  // 1) If the dotMatrix changed, re‐draw it into bgLayer
  if (bgNeedsRedraw) {
    bgLayer.background(0);
    for (let i = 0; i < ROWS; i++) {
      for (let j = 0; j < COLS; j++) {
        let x = j * cellWidth + PADDING/2;
        let y = i * cellHeight + PADDING/2;
        bgLayer.fill(dotMatrix[i][j] ? 255 : 68);
        if (j % 3 !== 2 && i % 5 !== 4) {
          bgLayer.ellipse(
            x + cellWidth/2,
            y + cellHeight/2,
            cellWidth * 0.56,
            cellHeight * 0.56
          );
        }
      }
    }
    bgNeedsRedraw = false;
  }

  // 2) Blit that cached background (erasing any old circles)
  image(bgLayer, 0, 0);

  // 3) Draw double‐tap highlights (this part is as before)
  noStroke();
  for (let i = doubleTaps.length - 1; i >= 0; i--) {
    let dt = doubleTaps[i];
    let x = dt.x_idx * cellWidth + PADDING/2;
    let y = dt.y_idx * cellHeight + PADDING/2;
    let alpha = map(dt.life, 0, 300, 0, 200);
    fill(0, 210, 255, alpha);
    ellipse(
      x + cellWidth/2,
      y + cellHeight/2,
      cellWidth * 0.56,
      cellHeight * 0.56
    );
    dt.life -= 3;
    if (dt.life <= 0) {
      doubleTaps.splice(i, 1);
    }
  }

  // 4) Finally, draw circles for any "down" fingers that remain in the map
  noStroke();
  for (let fid in fingers) {
    let f = fingers[fid];
    fill(f.color);
    ellipse(
      f.x + cellWidth/2,
      f.y + cellHeight/2,
      40,
      40
    );
  }
}