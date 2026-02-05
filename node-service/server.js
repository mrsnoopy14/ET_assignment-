const express = require('express');

const fetchImpl =
  global.fetch ||
  ((...args) => import('node-fetch').then(({ default: fetch }) => fetch(...args)));

const app = express();
app.use(express.json({ limit: '1mb' }));

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '127.0.0.1';
const SOLVER_URL = process.env.SOLVER_URL || 'http://127.0.0.1:5000/thermal';

app.get('/', (_req, res) => {
  res.json({
    status: 'ok',
    solverUrl: SOLVER_URL,
    endpoints: ['POST /solve', 'GET /solve/default']
  });
});

// Calls the Python solver with default inputs (GET /thermal)
app.get('/solve/default', async (_req, res) => {
  try {
    const response = await fetchImpl(SOLVER_URL, { method: 'GET' });
    const text = await response.text();

    // Pass through status code + JSON if possible
    const contentType = response.headers.get('content-type') || '';
    if (!response.ok) {
      return res.status(502).json({ error: 'Solver API error', status: response.status, body: text });
    }

    if (contentType.includes('application/json')) {
      return res.json(JSON.parse(text));
    }
    return res.json({ raw: text });
  } catch (err) {
    return res.status(502).json({
      error: 'Failed to call solver API',
      solverUrl: SOLVER_URL,
      details: err && err.message ? err.message : String(err)
    });
  }
});

// Forwards JSON body to Python solver (POST /thermal)
app.post('/solve', async (req, res) => {
  try {
    const response = await fetchImpl(SOLVER_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body || {})
    });

    const text = await response.text();
    const contentType = response.headers.get('content-type') || '';

    if (!response.ok) {
      return res.status(502).json({ error: 'Solver API error', status: response.status, body: text });
    }

    if (contentType.includes('application/json')) {
      return res.json(JSON.parse(text));
    }
    return res.json({ raw: text });
  } catch (err) {
    return res.status(502).json({
      error: 'Failed to call solver API',
      solverUrl: SOLVER_URL,
      details: err && err.message ? err.message : String(err)
    });
  }
});

app.listen(PORT, HOST, () => {
  console.log(`Node service listening on http://${HOST}:${PORT}`);
  console.log(`Forwarding solver calls to: ${SOLVER_URL}`);
});
