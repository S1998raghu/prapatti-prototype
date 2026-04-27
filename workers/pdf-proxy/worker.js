export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const key = url.pathname.slice(1); // strip leading /

    const ALLOWED_PREFIXES = ["slokas/", "articles/", "announcements/"];
    if (!key || !ALLOWED_PREFIXES.some(p => key.startsWith(p))) {
      return new Response("Not found", { status: 404 });
    }

    const object = await env.PRAPATTI_FILES.get(key);

    if (!object) {
      return new Response("Not found", { status: 404 });
    }

    const contentType = key.endsWith('.mp3') ? 'audio/mpeg'
      : key.endsWith('.wav') ? 'audio/wav'
      : 'application/pdf';

    return new Response(object.body, {
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "public, max-age=31536000, immutable",
      },
    });
  },
};
