const puppeteer = require("puppeteer-core");
const fs = require("fs");
const path = require("path");

(async () => {
  const sampleDir = path.join(__dirname, "sample_frames");
  fs.mkdirSync(sampleDir, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    headless: true,
    args: ["--no-sandbox", "--disable-gpu", "--font-render-hinting=none"]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  const htmlPath = "file:///" + path.resolve(__dirname, "composition.html").replace(/\\/g, "/");
  await page.goto(htmlPath, { waitUntil: "networkidle0" });

  const testFrames = [
    { frame: 120, name: "beat1_avalanche_120.jpg" },
    { frame: 320, name: "beat2_spiral_320.jpg" },
    { frame: 540, name: "beat3_levitation_540.jpg" },
    { frame: 640, name: "beat3_activated_640.jpg" },
    { frame: 780, name: "beat4_metric1_reachable_780.jpg" },
    { frame: 900, name: "beat4_metric2_diskreads_900.jpg" },
    { frame: 1040, name: "beat4_metric3_costsaved_1040.jpg" },
    { frame: 1260, name: "beat5_outro_settled_1260.jpg" }
  ];

  for (const item of testFrames) {
    await page.evaluate((idx) => window.renderFrame(idx, 1320), item.frame);
    const dataUrl = await page.evaluate(() => document.getElementById("canvas").toDataURL("image/jpeg", 0.95));
    const base64Data = dataUrl.replace(/^data:image\/jpeg;base64,/, "");
    const outPath = path.join(sampleDir, item.name);
    fs.writeFileSync(outPath, base64Data, "base64");
    console.log(`Saved ${item.name} (${item.frame})`);
  }

  await browser.close();
  console.log("All sample frames generated successfully!");
})();
