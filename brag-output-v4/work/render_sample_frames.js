const puppeteer = require("puppeteer-core");
const fs = require("fs");
const path = require("path");

const EDGE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const SAMPLES_DIR = path.join(__dirname, "sample_frames");
fs.mkdirSync(SAMPLES_DIR, { recursive: true });

const testFrames = [0, 80, 180, 300, 500, 720, 900, 1020];

(async () => {
  try {
    console.log("Launching Edge to render sample frames...");
    const browser = await puppeteer.launch({
      executablePath: EDGE_PATH,
      headless: true,
      args: ["--no-sandbox", "--disable-gpu", "--font-render-hinting=none"]
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    const htmlPath = "file:///" + path.resolve(__dirname, "composition.html").replace(/\\/g, "/");
    await page.goto(htmlPath, { waitUntil: "networkidle0" });

    // Set headless mode
    await page.evaluate(() => {
      window.IS_HEADLESS = true;
      if (typeof animId !== 'undefined' && animId) cancelAnimationFrame(animId);
    });

    for (const f of testFrames) {
      await page.evaluate((idx) => window.renderFrame(idx, 1080), f);
      const dataUrl = await page.evaluate(() => document.getElementById("canvas").toDataURL("image/jpeg", 0.95));
      const base64Data = dataUrl.replace(/^data:image\/jpeg;base64,/, "");
      const outPath = path.join(SAMPLES_DIR, `sample_frame_${String(f).padStart(4, "0")}.jpg`);
      fs.writeFileSync(outPath, base64Data, "base64");
      console.log(`Rendered sample frame ${f} -> ${outPath}`);
    }

    await browser.close();
    console.log("Sample rendering complete!");
  } catch (err) {
    console.error("Sample rendering error:", err);
    process.exit(1);
  }
})();
