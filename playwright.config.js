// @ts-check
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./e2e",
  workers: 1, // один сервер с общим кэшем и режимом источника
  reporter: [["list"]],
  use: { browserName: "chromium", headless: true },
  webServer: { command: "python e2e/e2e_server.py 5201", url: "http://127.0.0.1:5201/", reuseExistingServer: false },
});
