export async function onRequest(context) {
  const { request, env } = context;

  if (request.method !== "POST") {
    return new Response("method not allowed", { status: 405 });
  }

  try {
    const { email } = await request.json();

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return Response.json({ error: "valid email required" }, { status: 400 });
    }

    const normalised = email.toLowerCase().trim();

    const existing = await env.SUBSCRIBERS.get(normalised);
    if (existing) {
      return Response.json({ ok: true, message: "already subscribed" });
    }

    const token = await makeToken(normalised, env.WORKER_SECRET);

    await env.SUBSCRIBERS.put(normalised, JSON.stringify({
      email: normalised,
      subscribed: new Date().toISOString(),
      token
    }));

    return Response.json({ ok: true, message: "subscribed" });
  } catch (e) {
    return Response.json({ error: "something went wrong" }, { status: 500 });
  }
}

async function makeToken(email, secret) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(email));
  return [...new Uint8Array(sig)].map(b => b.toString(16).padStart(2, "0")).join("").slice(0, 32);
}
