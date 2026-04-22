const ADMIN_PASSWORD = env.ADMIN_PASSWORD;
const ALLOWED_ORIGINS = ["https://beta.prapatti.com", "https://prapatti.com", "http://localhost:1313"];

function corsOrigin(request) {
  const origin = request.headers.get("Origin") || "";
  return ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
}

function json(data, status = 200, request = null) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": request ? corsOrigin(request) : ALLOWED_ORIGINS[0],
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}

function unauthorized() {
  return json({ error: "Unauthorized" }, 401, request);
}

function isAdmin(request) {
  const auth = request.headers.get("Authorization") || "";
  return auth === `Bearer ${ADMIN_PASSWORD}`;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": corsOrigin(request),
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
      });
    }

    // POST /submit — public form submission
    if (request.method === "POST" && path === "/submit") {
      let body;
      try { body = await request.json(); } catch { return json({ error: "Invalid JSON" }, 400, request); }

      const { author, email, location, message, honeypot } = body;
      if (honeypot) return json({ ok: true }, 200, request); // spam trap
      if (!author?.trim() || !message?.trim()) return json({ error: "Name and message required" }, 400, request);

      const timestamp = new Date().toUTCString();
      await env.DB.prepare(
        "INSERT INTO entries (author, email, location, message, timestamp, approved) VALUES (?, ?, ?, ?, ?, 0)"
      ).bind(author.trim(), email?.trim() || "", location?.trim() || "", message.trim(), timestamp).run();

      return json({ ok: true }, 200, request);
    }

    // GET /entries — public approved entries
    if (request.method === "GET" && path === "/entries") {
      const page = parseInt(url.searchParams.get("page") || "1");
      const limit = 20;
      const offset = (page - 1) * limit;

      const { results } = await env.DB.prepare(
        "SELECT id, author, location, message, timestamp, reply FROM entries WHERE approved=1 ORDER BY id DESC LIMIT ? OFFSET ?"
      ).bind(limit, offset).all();

      const { results: countResult } = await env.DB.prepare(
        "SELECT COUNT(*) as total FROM entries WHERE approved=1"
      ).all();

      return json({ entries: results, total: countResult[0].total, page, limit }, 200, request);
    }

    // Admin routes — require password
    // GET /admin/entries — all pending + approved
    if (request.method === "GET" && path === "/admin/entries") {
      if (!isAdmin(request)) return unauthorized();
      const { results } = await env.DB.prepare(
        "SELECT * FROM entries ORDER BY approved ASC, id DESC"
      ).all();
      return json(results, 200, request);
    }

    // POST /admin/approve — approve an entry
    if (request.method === "POST" && path === "/admin/approve") {
      if (!isAdmin(request)) return unauthorized();
      const { id } = await request.json();
      await env.DB.prepare("UPDATE entries SET approved=1 WHERE id=?").bind(id).run();
      return json({ ok: true });
    }

    // POST /admin/reply — add a reply
    if (request.method === "POST" && path === "/admin/reply") {
      if (!isAdmin(request)) return unauthorized();
      const { id, reply } = await request.json();
      await env.DB.prepare("UPDATE entries SET reply=? WHERE id=?").bind(reply, id).run();
      return json({ ok: true });
    }

    // POST /admin/delete — delete an entry
    if (request.method === "POST" && path === "/admin/delete") {
      if (!isAdmin(request)) return unauthorized();
      const { id } = await request.json();
      await env.DB.prepare("DELETE FROM entries WHERE id=?").bind(id).run();
      return json({ ok: true });
    }

    return json({ error: "Not found" }, 404, request);
  },
};
