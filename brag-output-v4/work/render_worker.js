const puppeteer = require("puppeteer-core");
const fs = require("fs");
const path = require("path");

const [,, startFrameStr, endFrameStr, framesDir] = process.argv;
const startFrame = parseInt(startFrameStr, 10);
const endFrame = parseInt(endFrameStr, 10);
const totalFrames = 1320;

(async () => {
  try {
    const browser = await puppeteer.launch({
      executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
      headless: true,
      args: ["--no-sandbox", "--disable-gpu", "--font-render-hinting=none"]
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    const htmlPath = "file:///" + path.resolve(__dirname, "composition.html").replace(/\\/g, "/");
    await page.goto(htmlPath, { waitUntil: "networkidle0" });

    // Set headless mode to prevent RAF loop interference
    await page.evaluate(() => {
      window.IS_HEADLESS = true;
      if (typeof animId !== 'undefined' && animId) cancelAnimationFrame(animId);
    });

    for (let f = startFrame; f <= endFrame; f++) {
      await page.evaluate((idx, total) => window.renderFrame(idx, total), f, totalFrames);
      const dataUrl = await page.evaluate(() => document.getElementById("canvas").toDataURL("image/jpeg", 0.98));
      const base64Data = dataUrl.replace(/^data:image\/jpeg;base64,/, "");
      const frameFileName = `frame_${String(f).padStart(4, "0")}.jpg`;
      const framePath = path.join(framesDir, frameFileName);
      fs.writeFileSync(framePath, base64Data, "base64");
    }

    await browser.close();
    process.exit(0);
  } catch (err) {
    console.error(`Worker error [${startFrame}-${endFrame}]:`, err);
    process.exit(1);
  }
})();
