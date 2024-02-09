var ALLOW_LIST = ["data.csv"];

var hasValidHeader = (request, env) => {
  return request.headers.get("X-Custom-Auth-Key") === env.AUTH_KEY_SECRET;
};

function authorizeRequest(request, env, key) {
  switch (request.method) {
    case "PUT":
    case "DELETE":
      return hasValidHeader(request, env);
    case "GET":
      return ALLOW_LIST.includes(key) || key.endsWith(".csv");
    default:
      return false;
  }
}

var src_default = {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      const key = url.pathname.slice(1);

      if (!authorizeRequest(request, env, key)) {
        return new Response("Forbidden", { status: 403 });
      }

      switch (request.method) {
        case "PUT":
          await env.logsBucket.put(key, request.body);
          return new Response(`Put ${key} successfully!`);

        case "GET":
          const object = await env.logsBucket.get(key);
          if (object === null) {
            return new Response("Object Not Found", { status: 404 });
          }
          const headers = new Headers();
          object.writeHttpMetadata(headers);
          headers.set("etag", object.httpEtag);
          if (key.endsWith(".csv")) {
            headers.set("Content-Type", "text/csv");ßß
          }
          return new Response(object.body, { headers });

        case "DELETE":
          await env.logsBucket.delete(key);
          return new Response("Deleted!");

        default:
          return new Response("Method Not Allowed", {
            status: 405,
            headers: { Allow: "PUT, GET, DELETE" }
          });
      }
    } catch (error) {
      console.log(`Error handling request: ${error.message}`);
      return new Response(`Internal Server Error: ${error.message}`, { status: 500 });
    }
  }
};

export { src_default as default };
//# sourceMappingURL=index.js.map
