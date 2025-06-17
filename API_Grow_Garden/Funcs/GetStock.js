const https = require("https");

function createOptions(path) {
  return {
    method: "GET",
    hostname: "growagardenstock.com",
    path: path,
    headers: {
      accept: "*/*",
      "accept-language": "en-US,en;q=0.9",
      referer: "https://growagardenstock.com/api/stock",
      "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0",
    },
  };
}

function fetchStockData(path) {
  return new Promise((resolve, reject) => {
    const options = createOptions(path);
    const req = https.request(options, (res) => {
      let data = "";

      res.on("data", (chunk) => {
        data += chunk;
      });

      res.on("end", () => {
        try {
          const parsed = JSON.parse(data);
          resolve(parsed);
        } catch (e) {
          reject(new Error("Failed to parse JSON: " + e.message));
        }
      });
    });

    req.on("error", (e) => {
      reject(e);
    });

    req.end();
  });
}

function extractCounts(items) {
  return items.map(item => {
    const match = item.match(/\*\*x(\d+)\*\*/);
    const stock = match ? match[1] : "0";
    const name = item.replace(/\s*\*\*x\d+\*\*$/, "").trim();
    return { name, stock };
  });
}

function register(app) {
  app.get("/api/stock/GetStock", async (req, res) => {
    try {
      const [mainStock, specialStock] = await Promise.all([
        fetchStockData("/api/stock"),
        fetchStockData("/api/special-stock")
      ]);

      const formattedData = {
        Data: {
          updatedAt: mainStock.updatedAt || Date.now(),
          gear: extractCounts(mainStock.gear || []),
          seeds: extractCounts(mainStock.seeds || []),
          egg: extractCounts(mainStock.egg || []),
          honey: extractCounts(specialStock.honey || []),
          cosmetics: extractCounts(specialStock.cosmetics || []),
        },
      };

      res.json(formattedData);
    } catch (err) {
      res.status(500).json({ error: err.message || "Failed to fetch stock data" });
    }
  });
}

module.exports = { register };
