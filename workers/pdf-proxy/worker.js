export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const key = url.pathname.slice(1); // strip leading /

    const ALLOWED_PREFIXES = ["slokas/", "articles/", "announcements/"];
    if (!key || !ALLOWED_PREFIXES.some(p => key.startsWith(p))) {
      return new Response("Not found", { status: 404 });
    }

    // onlyIf: a browser re-checking its copy (If-None-Match) gets the object without a body when unchanged
    const object = await env.PRAPATTI_FILES.get(key, { onlyIf: request.headers });

    if (!object) {
      return new Response("Not found", { status: 404 });
    }

    const contentType = key.endsWith('.mp3') ? 'audio/mpeg'
      : key.endsWith('.wav') ? 'audio/wav'
      : 'application/pdf';

    // Files can be replaced under the same name, so browsers keep a copy for an hour
    // and then re-check it by ETag (a cheap 304 when nothing changed)
    const headers = {
      "Content-Type": contentType,
      "Cache-Control": "public, max-age=3600",
      "ETag": object.httpEtag,
    };
    if (!("body" in object)) {
      return new Response(null, { status: 304, headers });
    }
    return new Response(object.body, { headers });
  },
};
