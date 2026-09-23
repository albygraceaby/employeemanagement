const http = require("http");

const jobs = [
  { id: 1, title: "Frontend Developer", company: "Tech Solutions", location: "Hyderabad", match: 92 },
  { id: 2, title: "React Developer", company: "Digital Labs", location: "Bengaluru", match: 88 },
  { id: 3, title: "Software Engineer", company: "InnovateX", location: "Chennai", match: 84 }
];

const server = http.createServer((req, res) => {
  const origin = req.headers.origin || "*";
  res.setHeader("Access-Control-Allow-Origin", origin);
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    return res.end();
  }

  res.setHeader("Content-Type", "application/json");

  if (req.url === "/api/jobs") {
    res.writeHead(200);
    return res.end(JSON.stringify({ jobs }));
  }

  const match = req.url.match(/^\/api\/simulate\/(400|401|403|404|429|500)$/);
  if (match) {
    const status = Number(match[1]);
    const messages = {
      400: "Invalid request",
      401: "Token expired",
      403: "Access denied",
      404: "Job list not found",
      429: "Rate limit exceeded",
      500: "Database unavailable"
    };
    res.writeHead(status);
    return res.end(JSON.stringify({ message: messages[status] }));
  }

  res.writeHead(404);
  res.end(JSON.stringify({ message: "Route not found" }));
});

server.listen(5000, () => {
  console.log("Backend running at http://localhost:5000");
});
