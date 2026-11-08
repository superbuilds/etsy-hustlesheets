const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const errs = [];
  const go = async (w, h, view) => { const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 2 }); p.on('pageerror', e => errs.push(e.message));
    await p.addInitScript(v => { window.__view = v; }, view); await p.goto('file://' + __dirname + '/index.html'); await p.waitForTimeout(1200); return p; };
  let p = await go(1600, 1000, 'Timeline'); await p.screenshot({ path: 'shots/timeline.png', fullPage: true });
  await p.getByRole('button', { name: 'Month', exact: true }).click(); await p.waitForTimeout(400); await p.screenshot({ path: 'shots/timeline-month.png', fullPage: true });
  await p.getByRole('button', { name: 'Week', exact: true }).click(); await p.waitForTimeout(300);
  await p.evaluate(() => window.__openEdit()); await p.waitForTimeout(400); await p.screenshot({ path: 'shots/edit.png' });
  p = await go(1600, 1000, 'Table'); await p.screenshot({ path: 'shots/table.png', fullPage: true });
  console.log('errors:', errs.length ? errs : 'none'); await b.close();
})();
