const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2 });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => m.type() === 'error' && errs.push(m.text()));
  await p.goto('file://' + __dirname + '/index.html'); await p.waitForTimeout(1200);
  await p.screenshot({ path: 'shots/kanban.png', fullPage: true });
  for (const t of ['Calendar', 'Table', 'Insights']) { await p.getByRole('button', { name: t, exact: true }).click(); await p.waitForTimeout(500); await p.screenshot({ path: `shots/${t.toLowerCase()}.png`, fullPage: true }); }
  await p.getByRole('button', { name: 'Kanban', exact: true }).click(); await p.waitForTimeout(300);
  await p.getByRole('button', { name: 'New Content' }).click(); await p.waitForTimeout(300);
  await p.fill('input[placeholder^="e.g. 2027"]', 'Launch Week Recap: 5 Lessons Learned');
  await p.fill('input[placeholder^="e.g. Marketing Directors"]', 'Founders & marketing leads');
  await p.fill('input[placeholder^="e.g. Sarah"]', 'Sarah Chen');
  await p.screenshot({ path: 'shots/add.png' });
  // drag demo: start dragging a card mid-way
  await p.getByRole('button', { name: 'Cancel' }).click(); await p.waitForTimeout(200);
  const card = p.getByText('2027 Budget Allocation Benchmark Framework').first(); const bx = await card.boundingBox();
  await p.mouse.move(bx.x + 40, bx.y + 10); await p.mouse.down(); await p.mouse.move(bx.x + 120, bx.y + 40, { steps: 5 }); await p.mouse.move(bx.x + 300, bx.y + 60, { steps: 10 });
  await p.waitForTimeout(300); await p.screenshot({ path: 'shots/drag.png' }); await p.mouse.up();
  const ph = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  await ph.goto('file://' + __dirname + '/index.html'); await ph.waitForTimeout(1000); await ph.screenshot({ path: 'shots/phone.png' });
  console.log('errors:', errs.length ? errs.slice(0, 5) : 'none'); await b.close();
})();
