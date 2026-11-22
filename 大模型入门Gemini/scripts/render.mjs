import { spawn } from 'node:child_process';
import fs from 'node:fs';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(ROOT, 'images');

function findChrome() {
  const candidates = [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  ];
  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }
  throw new Error('Could not find Chrome or Edge executable.');
}

function getFreePort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.listen(0, '127.0.0.1', () => {
      const { port } = srv.address();
      srv.close(() => resolve(port));
    });
    srv.on('error', reject);
  });
}

async function waitForWsUrl(port, timeoutMs = 15000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/list`);
      if (res.ok) {
        const list = await res.json();
        const page = list.find((t) => t.type === 'page' && t.webSocketDebuggerUrl);
        if (page) return page.webSocketDebuggerUrl;
      }
    } catch {
      // retry
    }
    await new Promise((r) => setTimeout(r, 150));
  }
  throw new Error('Timed out waiting for headless Chrome DevTools endpoint.');
}

class CDPClient {
  constructor(ws) {
    this.ws = ws;
    this.nextId = 1;
    this.pending = new Map();
    ws.addEventListener('message', (evt) => {
      const msg = JSON.parse(evt.data.toString());
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(msg.error.message || JSON.stringify(msg.error)));
        else resolve(msg.result);
      }
    });
  }
  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = this.nextId++;
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
  close() {
    this.ws.close();
  }
}

async function connectCDP(wsUrl) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    ws.addEventListener('open', () => resolve(new CDPClient(ws)));
    ws.addEventListener('error', (err) => reject(err));
  });
}

async function loadFigureModules(filterArgs) {
  const figDir = path.join(__dirname, 'figures');
  if (!fs.existsSync(figDir)) return [];
  const files = fs.readdirSync(figDir).filter((f) => f.endsWith('.mjs')).sort();
  const all = [];
  for (const f of files) {
    const mod = await import(`file://${path.join(figDir, f).replace(/\\/g, '/')}`);
    const list = mod.figures || mod.default || [];
    for (const fig of list) {
      if (filterArgs.length === 0 || filterArgs.some((a) => fig.filename.includes(a))) {
        all.push(fig);
      }
    }
  }
  return all;
}

async function main() {
  const filterArgs = process.argv.slice(2);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const figures = await loadFigureModules(filterArgs);
  if (figures.length === 0) {
    console.log('No figures matched.');
    return;
  }

  const chromePath = findChrome();
  const port = await getFreePort();
  const userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'llm-fig-chrome-'));

  const chrome = spawn(
    chromePath,
    [
      '--headless=new',
      '--disable-gpu',
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--hide-scrollbars',
      `--remote-debugging-port=${port}`,
      `--user-data-dir=${userDataDir}`,
      'about:blank',
    ],
    { stdio: 'ignore' }
  );

  let client;
  try {
    const wsUrl = await waitForWsUrl(port);
    client = await connectCDP(wsUrl);
    await client.send('Page.enable');
    const { frameTree } = await client.send('Page.getFrameTree');
    const frameId = frameTree.frame.id;

    for (const fig of figures) {
      const { filename, width, height, render } = fig;
      const html = render();
      await client.send('Emulation.setDeviceMetricsOverride', {
        width,
        height,
        deviceScaleFactor: 2,
        mobile: false,
      });
      await client.send('Page.setDocumentContent', { frameId, html });
      await client.send('Runtime.evaluate', {
        expression: `new Promise(r => document.fonts.ready.then(() => requestAnimationFrame(() => requestAnimationFrame(() => r(true)))))`,
        awaitPromise: true,
      });
      const { data } = await client.send('Page.captureScreenshot', {
        format: 'png',
        clip: { x: 0, y: 0, width, height, scale: 1 },
      });
      const outPath = path.join(OUT_DIR, filename);
      fs.writeFileSync(outPath, Buffer.from(data, 'base64'));
      console.log(`Rendered ${filename} (${width * 2}x${height * 2})`);
    }
  } finally {
    if (client) client.close();
    chrome.kill();
    await new Promise((r) => setTimeout(r, 300));
    try {
      fs.rmSync(userDataDir, { recursive: true, force: true });
    } catch {
      // ignore Windows lock cleanup delay
    }
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
