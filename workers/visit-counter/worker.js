export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const allowed = ["https://prapatti.com", "https://www.prapatti.com", "https://dev.prapatti.com"];
    const corsOrigin = allowed.includes(origin) ? origin : allowed[0];

    const corsHeaders = {
      "Access-Control-Allow-Origin": corsOrigin,
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);
    const current = parseInt(await env.COUNTER.get("visits") || "0");

    // Read-only: just return the current count
    if (url.pathname === "/count") {
      return new Response(JSON.stringify({ visits: current }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Increment: deduplicate by IP per UTC day using KV with 25h TTL
    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    const day = new Date().toISOString().slice(0, 10); // "2026-05-02"
    const seenKey = `seen:${day}:${ip}`;
    const alreadySeen = await env.COUNTER.get(seenKey);

    if (alreadySeen) {
      return new Response(JSON.stringify({ visits: current }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Mark this IP as seen for today (expires after 25h to cover timezone edge cases)
    await env.COUNTER.put(seenKey, "1", { expirationTtl: 90000 });
    const updated = current + 1;
    await env.COUNTER.put("visits", String(updated));

    return new Response(JSON.stringify({ visits: updated }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  },
};
