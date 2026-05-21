const path = require("path");
const { chromium } = require("playwright");

const root = __dirname;
const outDir = path.join(root, "out");
const html = `file://${path.join(root, "index.html")}`;

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  });
  const page = await browser.newPage({
    viewport: { width: 430, height: 900 },
    deviceScaleFactor: 2,
  });
  await page.goto(html, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts && document.fonts.ready);

  const slices = await page.$$("[data-shot]");
  for (const slice of slices) {
    const name = await slice.getAttribute("data-shot");
    await slice.screenshot({
      path: path.join(outDir, `${name}.png`),
      animations: "disabled",
    });
  }

  await page.screenshot({
    path: path.join(outDir, "captain-mobile-full-preview.png"),
    fullPage: true,
    animations: "disabled",
  });

  await browser.close();
})();
