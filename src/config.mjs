/**
 * Config persistence for goose-video. One JSON file at ~/.goose-video/config.json
 * holding the cal_ token + the backend / app-mcp URLs. Mirrors how goose-aeo
 * stashes its credentials.
 */
import { homedir } from "node:os";
import { join } from "node:path";
import { mkdir, readFile, writeFile, chmod, rm } from "node:fs/promises";

const CONFIG_DIR = join(homedir(), ".goose-video");
const CONFIG_PATH = join(CONFIG_DIR, "config.json");

export { CONFIG_PATH };

const DEFAULT_API_BASE = process.env.GOOSE_VIDEO_API_BASE || "http://localhost:5999";
const DEFAULT_MCP_URL = process.env.GOOSE_VIDEO_MCP_URL || "http://localhost:6200/mcp";
// The /cli/auth login page is served by the WEB app (frontend), not the backend
// API. In dev they're different ports (3999 vs 5999); in prod usually one origin.
const DEFAULT_WEB_URL = process.env.GOOSE_VIDEO_WEB_URL || "http://localhost:3999";

/** Read the saved config, or an empty object if there's none yet. */
export async function loadConfig() {
  try {
    const raw = await readFile(CONFIG_PATH, "utf8");
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

/** Merge-write config. Creates ~/.goose-video with 0700 and the file with 0600. */
export async function saveConfig(patch) {
  const current = await loadConfig();
  const next = { ...current, ...patch };
  await mkdir(CONFIG_DIR, { recursive: true, mode: 0o700 });
  await writeFile(CONFIG_PATH, JSON.stringify(next, null, 2));
  await chmod(CONFIG_PATH, 0o600).catch(() => {});
  return next;
}

/**
 * Resolve the effective settings: saved config, overlaid by CLI flags, with
 * sensible localhost defaults. Throws (with a friendly message) if no token.
 */
export async function resolveSettings(flags = {}) {
  const cfg = await loadConfig();
  const token = flags.token || cfg.token;
  if (!token) {
    throw new Error("Not logged in. Run `goose-video login` first.");
  }
  return {
    token,
    apiBase: stripSlash(flags.apiBase || cfg.apiBase || DEFAULT_API_BASE),
    mcpUrl: flags.mcpUrl || cfg.mcpUrl || DEFAULT_MCP_URL,
  };
}

export function defaults() {
  return { apiBase: DEFAULT_API_BASE, mcpUrl: DEFAULT_MCP_URL, webUrl: DEFAULT_WEB_URL };
}

/** Delete the saved config (logout). No-op if there's nothing saved. */
export async function clearConfig() {
  await rm(CONFIG_PATH, { force: true });
}

function stripSlash(u) {
  return typeof u === "string" ? u.replace(/\/+$/, "") : u;
}
