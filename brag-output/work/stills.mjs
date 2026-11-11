// Contact sheet of stills, captured in time order. Usage: node stills.mjs t1 t2 ...
import { launch } from './cdp.mjs';
import { writeFileSync } from 'node:fs';
const ts = process.argv.slice(2).map(Number);
const b = await launch({ width: 1080, height: 1920, port: 9334 });
await b.goto('http://127.0.0.1:8765/brag-output/work/comp.html', 4000);
console.log(await b.evaluate('prepare()'));
for (const t of ts) {
  await b.evaluate(`render(${t})`);
  await b.sleep(350);
  writeFileSync(`shots/t${t.toFixed(3)}.png`, await b.shot({ clip: { x: 0, y: 0, width: 1080, height: 1920, scale: 0.34 } }));
}
await b.close();
