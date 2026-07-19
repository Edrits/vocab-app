// Cloudflare Worker: PIN-keyed progress sync for 网语 · Netizen Vocab.
// Two operations, keyed by a hash of the PIN sent in the X-Pin header:
//   GET  → return the stored progress blob (or null)
//   PUT  → store the posted progress blob
// Requires a KV namespace bound as `SYNC`.

const ALLOWED_ORIGINS = [
  'https://edrits.github.io',
  'http://localhost:4173',
];

function corsHeaders(origin) {
  return {
    'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0],
    'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Pin',
  };
}

async function pinKey(pin) {
  const data = new TextEncoder().encode('netizen-vocab:' + pin);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return 'p:' + [...new Uint8Array(hash)].map(b => b.toString(16).padStart(2, '0')).join('');
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
    const key = await pinKey(pin);

    if (request.method === 'GET') {
      const stored = await env.SYNC.get(key);
      return new Response(stored || 'null', { headers });
    }

    if (request.method === 'PUT') {
      const body = await request.text();
      if (body.length > 200000) {
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
