export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const key = url.pathname.slice(1); // strip leading /

    if (!key || !key.startsWith("slokas/")) {
      return new Response("Not found", { status: 404 });
    }

    const object = await env.PRAPATTI_FILES.get(key);

    if (!object) {
      return new Response("Not found", { status: 404 });
    }

    return new Response(object.body, {
      headers: {
        "Content-Type": "application/pdf",
        "Cache-Control": "public, max-age=31536000, immutable",
      },
    });
  },
};
