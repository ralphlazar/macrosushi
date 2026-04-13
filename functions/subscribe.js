export async function onRequestGet(context) {
  const { request, env } = context;

  const auth = request.headers.get("Authorization");
  if (auth !== `Bearer ${env.WORKER_SECRET}`) {
    return Response.json({ error: "unauthorized" }, { status: 401 });
  }

  const list = [];
  let cursor = null;

  do {
    const result = await env.SUBSCRIBERS.list({ cursor });
    for (const key of result.keys) {
      const value = await env.SUBSCRIBERS.get(key.name);
      if (value) {
        list.push(JSON.parse(value));
      }
    }
    cursor = result.list_complete ? null : result.cursor;
  } while (cursor);

  return Response.json({ subscribers: list });
}
