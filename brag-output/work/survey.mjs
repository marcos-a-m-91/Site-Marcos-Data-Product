import { launch } from './cdp.mjs';
import { writeFileSync } from 'node:fs';
const b = await launch({ width: 430, height: 860, scale: 1, mobile: true });
for (const p of ['index','projetos','blog','biblioteca','sobre']) {
  await b.goto(`http://127.0.0.1:8765/${p}.html`, 3000);
  const h = await b.evaluate(`document.documentElement.scrollHeight`);
  // walk down so reveal-on-scroll content lands
  for (let y = 0; y < h; y += 500) { await b.evaluate(`window.scrollTo(0,${y})`); await b.sleep(120); }
  await b.evaluate(`window.scrollTo(0,0)`); await b.sleep(300);
  const png = await b.shot({ captureBeyondViewport: true, clip: { x: 0, y: 0, width: 430, height: Math.min(h, 5200), scale: 0.5 } });
  writeFileSync(`shots/${p}.png`, png); console.log(p, h);
}
await b.close();
