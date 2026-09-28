const puppeteer = require("puppeteer-core");
const fs = require("fs");

(async () => {
  const browser = await puppeteer.launch({
    executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    headless: true,
    args: ["--no-sandbox", "--disable-gpu", "--font-render-hinting=none"]
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  await page.setContent(`
    <style>body { margin:0; overflow:hidden; background:#000; }</style>
    <canvas id="c" width="1920" height="1080"></canvas>
    <script>
      const c = document.getElementById('c');
      const ctx = c.getContext('2d');
      window.renderFrame = function(idx) {
        ctx.fillStyle = '#070709';
        ctx.fillRect(0, 0, 1920, 1080);
        ctx.fillStyle = '#F97316';
        ctx.font = 'bold 80px sans-serif';
        ctx.fillText('Frame: ' + idx, 100, 200 + (idx * 10));
      };
    </script>
  `);

  console.log("Testing screenshot speed for 10 frames...");
  const t0 = Date.now();
  for (let i = 0; i < 10; i++) {
    await page.evaluate((idx) => window.renderFrame(idx), i);
    await page.screenshot({ path: `bench_${i}.png`, type: 'png' });
  }
  const dt1 = (Date.now() - t0) / 10;
  console.log(`page.screenshot took: ${dt1.toFixed(1)} ms/frame (${(1000/dt1).toFixed(1)} fps)`);

  const t1 = Date.now();
  for (let i = 0; i < 10; i++) {
    await page.evaluate((idx) => window.renderFrame(idx), i);
    const dataUrl = await page.evaluate(() => document.getElementById('c').toDataURL('image/jpeg', 0.95));
    const base64Data = dataUrl.replace(/^data:image\/jpeg;base64,/, "");
    fs.writeFileSync(`bench_c_${i}.jpg`, base64Data, 'base64');
  }
  const dt2 = (Date.now() - t1) / 10;
  console.log(`canvas.toDataURL(jpeg) took: ${dt2.toFixed(1)} ms/frame (${(1000/dt2).toFixed(1)} fps)`);

  await browser.close();
})();
