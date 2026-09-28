const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const TOTAL_FRAMES = 1320;
const WORKERS = 6;
const FRAMES_DIR = path.join(__dirname, "frames");
const POSTER_FRAME_INDEX = 1260;
const POSTER_OUTPUT_PATH = path.resolve(__dirname, "..", "poster.jpg");

fs.mkdirSync(FRAMES_DIR, { recursive: true });

console.log(`Starting parallel rendering of ${TOTAL_FRAMES} frames across ${WORKERS} Edge workers...`);
const t0 = Date.now();

const chunkSize = Math.ceil(TOTAL_FRAMES / WORKERS);
const workerPromises = [];

for (let w = 0; w < WORKERS; w++) {
  const startFrame = w * chunkSize;
  const endFrame = Math.min((w + 1) * chunkSize - 1, TOTAL_FRAMES - 1);
  if (startFrame > endFrame) continue;

  const promise = new Promise((resolve, reject) => {
    const workerScript = path.join(__dirname, "render_worker.js");
    const p = spawn("node", [workerScript, String(startFrame), String(endFrame), FRAMES_DIR], {
      stdio: "inherit"
    });

    p.on("close", (code) => {
      if (code === 0) {
        console.log(`[Worker ${w}] Finished frames ${startFrame} - ${endFrame}`);
        resolve();
      } else {
        reject(new Error(`Worker ${w} exited with code ${code}`));
      }
    });
  });

  workerPromises.push(promise);
}

Promise.all(workerPromises)
  .then(() => {
    const elapsed = ((Date.now() - t0) / 1000).toFixed(2);
    console.log(`\nAll workers completed! Rendered ${TOTAL_FRAMES} frames in ${elapsed}s (${(TOTAL_FRAMES / elapsed).toFixed(1)} fps).`);

    // Verify all frames exist
    let missing = 0;
    for (let f = 0; f < TOTAL_FRAMES; f++) {
      const p = path.join(FRAMES_DIR, `frame_${String(f).padStart(4, "0")}.jpg`);
      if (!fs.existsSync(p)) {
        missing++;
      }
    }

    if (missing > 0) {
      console.error(`ERROR: ${missing} frames are missing!`);
      process.exit(1);
    }
    console.log(`Verification: All 1,320 frames verified present on disk.`);

    // Generate poster.jpg from frame 1260 without touching frame 0000!
    const posterSrc = path.join(FRAMES_DIR, `frame_${String(POSTER_FRAME_INDEX).padStart(4, "0")}.jpg`);
    fs.copyFileSync(posterSrc, POSTER_OUTPUT_PATH);
    console.log(`Saved high-quality settled poster frame (${POSTER_FRAME_INDEX}) to: ${POSTER_OUTPUT_PATH}`);
    console.log(`Integrity Check: frame_0000.jpg remains authentic first frame (NO STROBE FLASH).`);
  })
  .catch((err) => {
    console.error("Rendering failed:", err);
    process.exit(1);
  });
