const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT_DIR = path.resolve(__dirname, '..');
const VENDOR_FILE = path.join(ROOT_DIR, 'assets', 'vendor', 'resource_3fa48481346f.js');
const OUTPUT_CSS = path.join(ROOT_DIR, 'assets', 'css', 'tailwind.css');

// Coleta todas as classes presentes nos arquivos .html, .js e templates .py
function collectClasses() {
  const classTokens = new Set();
  const fileExtensions = ['.html', '.js', '.py'];

  function scanDir(dir) {
    if (!fs.existsSync(dir)) return;
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === '.git' || entry.name === 'node_modules' || entry.name === 'references') continue;
        scanDir(fullPath);
      } else if (fileExtensions.includes(path.extname(entry.name).toLowerCase())) {
        const content = fs.readFileSync(fullPath, 'utf8');
        // Match class="..." ou class='...' ou className="..."
        const classMatches = content.matchAll(/(?:class|className)\s*=\s*["'`]([^"'`]+)["'`]/g);
        for (const m of classMatches) {
          const tokens = m[1].split(/\s+/).filter(Boolean);
          tokens.forEach(t => classTokens.add(t));
        }
        // Match tokens de classes utilitárias no CSS ou JS (ex: bg-[#...], text-[...], etc)
        const rawTokens = content.matchAll(/[a-zA-Z0-9_\-\/\[\]#%.:]+/g);
        for (const m of rawTokens) {
          if (m[0].length > 1 && m[0].length < 60) {
            classTokens.add(m[0]);
          }
        }
      }
    }
  }

  scanDir(ROOT_DIR);
  return Array.from(classTokens);
}

async function build() {
  const classes = collectClasses();
  console.log(`[Tailwind] ${classes.length} tokens de classe identificados`);

  let compiledCss = null;

  // Mock de ambiente DOM para a biblioteca standalone de Tailwind
  class MockElement {
    constructor(tag) {
      this.tagName = (tag || 'DIV').toUpperCase();
      this.children = [];
      this.attributes = {};
      this.classList = new Set();
      this.textContent = '';
      this.isConnected = true;
    }
    getAttribute(name) { return this.attributes[name] || null; }
    setAttribute(name, val) { this.attributes[name] = val; }
    append(child) { this.children.push(child); }
  }

  const documentElement = new MockElement('HTML');
  const head = new MockElement('HEAD');
  const body = new MockElement('BODY');

  // Adiciona elementos com classes
  const elementsWithClasses = classes.map(c => {
    const el = new MockElement('DIV');
    el.classList.add(c);
    return el;
  });

  const mockDocument = {
    documentElement,
    head,
    body,
    createElement(tag) {
      const el = new MockElement(tag);
      if (tag.toLowerCase() === 'style') {
        let _text = '';
        Object.defineProperty(el, 'textContent', {
          get() { return _text; },
          set(val) {
            _text = val;
            compiledCss = val;
          }
        });
      }
      return el;
    },
    querySelectorAll(selector) {
      if (selector === '[class]') {
        return elementsWithClasses;
      }
      if (selector.startsWith('style[')) {
        return [];
      }
      return [];
    }
  };

  class MockMutationObserver {
    constructor(callback) {
      this.callback = callback;
    }
    observe() {
      // Dispara imediatamente o callback
      setTimeout(() => {
        try {
          this.callback([]);
        } catch (e) {
          console.error(e);
        }
      }, 10);
    }
    disconnect() {}
  }

  const context = {
    window: {},
    self: {},
    document: mockDocument,
    MutationObserver: MockMutationObserver,
    setTimeout,
    clearTimeout,
    setInterval,
    clearInterval,
    console: {
      log: () => {},
      warn: () => {},
      error: console.error,
      info: () => {}
    },
    Promise,
    Set,
    Map,
    Array,
    Object,
    String,
    Number,
    Boolean,
    RegExp,
    Error,
    TypeError,
    Date,
    Math,
    JSON,
    Proxy,
    Reflect
  };
  context.window = context;
  context.self = context;

  const vendorCode = fs.readFileSync(VENDOR_FILE, 'utf8');
  vm.createContext(context);
  vm.runInContext(vendorCode, context);

  // Aguarda a compilação assíncrona
  let waited = 0;
  while (!compiledCss && waited < 4000) {
    await new Promise(r => setTimeout(r, 100));
    waited += 100;
  }

  if (compiledCss) {
    fs.writeFileSync(OUTPUT_CSS, compiledCss, 'utf8');
    const kb = (Buffer.byteLength(compiledCss, 'utf8') / 1024).toFixed(1);
    console.log(`[OK] assets/css/tailwind.css gerado com sucesso (${kb} KB)`);
  } else {
    console.error('[ERRO] Não foi possível compilar o CSS via Tailwind standalone');
    process.exit(1);
  }
}

build();

