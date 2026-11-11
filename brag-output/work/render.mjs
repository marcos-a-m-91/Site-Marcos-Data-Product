import { launch } from './cdp.mjs';
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';
const FPS = 30, N = 600;
const b = await launch({ width: 1080, height: 1920, port: 9335 });
await b.goto('http://127.0.0.1:8765/brag-output/work/comp.html', 4000);
await b.evaluate('prepare()');
const ff = spawn('ffmpeg', ['-y','-v','error','-f','image2pipe','-framerate',String(FPS),'-c:v','png','-i','-','-c:v','libx264','-crf','12','-preset','medium','-pix_fmt','yuv420p','video.mp4'], { stdio: ['pipe','inherit','inherit'] });
for (let i = 0; i < N; i++) {
  await b.evaluate(`render(${i / FPS})`);
  if (i >= 360 && i < 412) await b.sleep(40); // typing: let the page's own filter paint
  const png = await b.shot();
  if (i === 84) writeFileSync('poster.png', png);
  if (i === 399) writeFileSync('shots/check.png', png);
  if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 100 === 0) console.log(i);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await b.close();
