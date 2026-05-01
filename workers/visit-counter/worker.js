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

    const current = parseInt(await env.COUNTER.get("visits") || "0");
    const updated = current + 1;
    await env.COUNTER.put("visits", String(updated));

    return new Response(JSON.stringify({ visits: updated }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  },
};
