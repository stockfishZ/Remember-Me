const puppeteer = require("puppeteer-core");

(async () => {
  try {
    const browser = await puppeteer.launch({
      executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
      headless: true,
      args: ["--no-sandbox", "--disable-gpu"]
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    await page.setContent("<h1 style='color:red;'>Hello Edge Headless</h1>");
    await page.screenshot({ path: "test.png" });
    await browser.close();
    console.log("EDGE_HEADLESS_OK");
  } catch (err) {
    console.error("EDGE_ERROR:", err);
  }
})();
