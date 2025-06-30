import express from 'express';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'templates')));

const py = spawn('python3', ['-u', path.join(__dirname, 'jarvis.py')], {
  env: { ...process.env, PYTHONUNBUFFERED: '1' }
});

let buffer = '', nextId = 0;
const pending = new Map();

py.stdout.on('data', chunk => {
  buffer += chunk.toString();
  let idx;
  while ((idx = buffer.indexOf('\n')) !== -1) {
    const line = buffer.slice(0, idx).trim();
    buffer = buffer.slice(idx + 1);
    try {
      const { id, reply } = JSON.parse(line);
      const handler = pending.get(id);
      if (handler) {
        handler.resolve(reply);
        pending.delete(id);
      }
    } catch (e) {
      console.error('Invalid JSON:', line);
    }
  }
});

app.post('/chat', (req, res) => {
  const msg = req.body.message;
  if (!msg) return res.status(400).json({ error: 'Missing message' });

  const id = `${Date.now()}_${nextId++}`;
  const payload = JSON.stringify({ id, message: msg }) + '\n';

  let resolve, reject;
  const promise = new Promise((r, j) => { resolve = r; reject = j; });
  pending.set(id, { resolve, reject });

  py.stdin.write(payload);

  setTimeout(() => {
    if (pending.has(id)) {
      reject('timeout');
      pending.delete(id);
    }
  }, 5000);

  promise
    .then(reply => res.json({ reply }))
    .catch(err => res.status(500).json({ error: err }));
});
app.use('/images', express.static(path.join(__dirname, 'images')));
app.use(express.static(path.join(__dirname, 'templates')));
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'login.html')));
app.get('/gui.html', (req, res) => res.sendFile(path.join(__dirname, 'templates','gui.html')));

app.listen(3000, () => console.log('✅ Running on http://localhost:3000'));
