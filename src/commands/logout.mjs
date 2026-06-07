/**
 * `goose-video logout` — clear saved credentials (~/.goose-video/config.json).
 */
import { loadConfig, clearConfig } from "../config.mjs";

export async function logout() {
  const cfg = await loadConfig();
  if (!cfg.token) {
    console.log("Not logged in — nothing to clear.");
    return;
  }
  await clearConfig();
  console.log(`Logged out${cfg.email ? ` (${cfg.email})` : ""}.`);
}
