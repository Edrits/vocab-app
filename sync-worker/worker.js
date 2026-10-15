// Cloudflare Worker: PIN-keyed progress sync for 网语 · Netizen Vocab.
// Everything is keyed by a hash of the PIN sent in the X-Pin header.
//   GET    /        → return the stored progress blob (or null)
//   PUT    /        → store the posted progress blob
//   GET    /inbox   → list the "words I saw" inbox
//   POST   /inbox   → add {text, note} to the inbox
//   DELETE /inbox?ids=a,b → remove inbox items (the daily fetch clears what it imported)
// Requires a KV namespace bound as `SYNC`.

const ALLOWED_ORIGINS = [
  'https://edrits.github.io',
  'http://localhost:4173',
];

function corsHeaders(origin) {
  return {
    'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0],
    'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Pin',
  };
}

async function pinKey(pin) {
  const data = new TextEncoder().encode('netizen-vocab:' + pin);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return [...new Uint8Array(hash)].map(b => b.toString(16).padStart(2, '0')).join('');
}

const INBOX_MAX = 100;

async function inbox(request, env, key, headers) {
  const json = (v, status = 200) => new Response(JSON.stringify(v), { status, headers });
  const items = JSON.parse((await env.SYNC.get(key)) || '[]');

  if (request.method === 'GET') return json(items);

  if (request.method === 'POST') {
    let body;
    try { body = JSON.parse(await request.text()); } catch { return json({ error: 'invalid JSON' }, 400); }
    const text = String(body.text || '').trim();
    const note = String(body.note || '').trim();
    if (!text || text.length > 40) return json({ error: 'text must be 1-40 characters' }, 400);
    if (note.length > 300) return json({ error: 'note must be under 300 characters' }, 400);
    if (items.length >= INBOX_MAX) return json({ error: 'inbox full' }, 409);
    const id = String(body.id || '').slice(0, 40) || crypto.randomUUID();
    if (!items.some(i => i.id === id)) items.push({ id, text, note, at: new Date().toISOString() });
    await env.SYNC.put(key, JSON.stringify(items));
    return json(items);
  }

  if (request.method === 'DELETE') {
    const ids = new Set((new URL(request.url).searchParams.get('ids') || '').split(',').filter(Boolean));
    const kept = items.filter(i => !ids.has(i.id));
    await env.SYNC.put(key, JSON.stringify(kept));
    return json(kept);
  }

  return json({ error: 'method not allowed' }, 405);
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const headers = { ...corsHeaders(origin), 'Content-Type': 'application/json' };
    if (request.method === 'OPTIONS') return new Response(null, { headers: corsHeaders(origin) });

    const pin = request.headers.get('X-Pin') || '';
    if (pin.length < 4 || pin.length > 64) {
      return new Response(JSON.stringify({ error: 'PIN must be 4-64 characters' }), { status: 400, headers });
    }
    const hash = await pinKey(pin);
    const key = 'p:' + hash;

    if (new URL(request.url).pathname === '/inbox') return inbox(request, env, 'i:' + hash, headers);

    if (request.method === 'GET') {
      const stored = await env.SYNC.get(key);
      return new Response(stored || 'null', { headers });
    }

    if (request.method === 'PUT') {
      const body = await request.text();
      if (body.length > 5000000) { // KV allows 25MB; progress grows ~125 bytes per word studied
        return new Response(JSON.stringify({ error: 'blob too large' }), { status: 413, headers });
      }
      try { JSON.parse(body); } catch {
        return new Response(JSON.stringify({ error: 'invalid JSON' }), { status: 400, headers });
      }
      await env.SYNC.put(key, body);
      return new Response(JSON.stringify({ ok: true }), { headers });
    }

    return new Response(JSON.stringify({ error: 'method not allowed' }), { status: 405, headers });
  },
};
