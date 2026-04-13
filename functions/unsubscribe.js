export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const email = url.searchParams.get("email");
  const token = url.searchParams.get("token");

  if (!email || !token) {
    return htmlPage("missing email or token.");
  }

  const normalised = email.toLowerCase().trim();
  const expected = await makeToken(normalised, env.WORKER_SECRET);

  if (token !== expected) {
    return htmlPage("invalid unsubscribe link.");
  }

  await env.SUBSCRIBERS.delete(normalised);

  return htmlPage("you've been unsubscribed. we'll miss you.");
}

async function makeToken(email, secret) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(email));
  return [...new Uint8Array(sig)].map(b => b.toString(16).padStart(2, "0")).join("").slice(0, 32);
}

function htmlPage(message) {
  return new Response(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>macrosushi</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400&display=swap" rel="stylesheet">
</head>
<body style="margin:0;padding:0;background:#fff;font-family:'DM Sans',sans-serif;">
  <div style="max-width:440px;margin:0 auto;padding:3rem 1.5rem;text-align:center;">
    <div style="font-size:22px;font-weight:300;color:#bbb;letter-spacing:0.02em;margin-bottom:4px;">
      macro<span style="color:#c9684a;">sushi</span>
    </div>
    <div style="font-size:15px;color:#1a1a1a;line-height:1.75;font-weight:300;margin-top:3rem;">
      ${message}
    </div>
  </div>
</body>
</html>`, {
    status: 200,
    headers: { "Content-Type": "text/html" }
  });
}
