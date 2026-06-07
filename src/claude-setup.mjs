/**
 * Wire the user's own Claude Code to run Gooseworks ads:
 *   1. install the `ads-remix` skill into ~/.claude/skills/ads-remix/SKILL.md
 *   2. register the `gooseworks` MCP server (so Claude can call the ad tools)
 *
 * This is the heart of the "install + paste a prompt into Claude" flow — once
 * set up, the user just opens Claude Code and pastes the instruction the
 * landing/app page gives them. `login` and `update` call these.
 */
import { homedir } from "node:os";
import { join } from "node:path";
import { mkdir, writeFile } from "node:fs/promises";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { renderMasterSkill } from "./prompt.mjs";

const run = promisify(execFile);

const SKILL_NAME = "ads-remix";
const SKILL_DIR = join(homedir(), ".claude", "skills", SKILL_NAME);
const SKILL_PATH = join(SKILL_DIR, "SKILL.md");

// Claude Code skill frontmatter. `description` is what Claude matches on to
// auto-load the skill when the user pastes a remix / brand-research instruction.
const FRONTMATTER = `---
name: ${SKILL_NAME}
description: Remix a Gooseworks static ad template into a branded ad, or research a brand. Use when the user pastes a goose-video instruction or asks to "remix this ad", references a static ad template id, or asks to "research my brand". Runs brand research, creates the brand + project in Gooseworks, and generates the final image through the Gooseworks media proxies (billed to ad credits).
---

`;

/** Install (or refresh) the ads-remix skill into the user's Claude Code. */
export async function installClaudeSkill({ update = false } = {}) {
  const body = await renderMasterSkill({ update });
  await mkdir(SKILL_DIR, { recursive: true });
  await writeFile(SKILL_PATH, FRONTMATTER + body);
  return SKILL_PATH;
}

/** The `claude mcp add` command we run / suggest, as a printable string. */
export function mcpAddCommand({ mcpUrl, token }) {
  return (
    `claude mcp add gooseworks ${mcpUrl} --scope user --transport http ` +
    `--header "Authorization: Bearer ${token}"`
  );
}

/**
 * Register the `gooseworks` MCP server in the user's Claude Code (user scope),
 * idempotently. Best-effort: returns { ok, method?, error? } and never throws —
 * if the `claude` CLI is missing or the flags differ across versions, the caller
 * prints the manual command from mcpAddCommand().
 */
export async function registerMcpServer({ mcpUrl, token }) {
  try {
    // Refresh cleanly: drop any stale entry first (ignore "not found").
    await run("claude", ["mcp", "remove", "gooseworks", "--scope", "user"]).catch(() => {});
    await run("claude", [
      "mcp",
      "add",
      "gooseworks",
      mcpUrl,
      "--scope",
      "user",
      "--transport",
      "http",
      "--header",
      `Authorization: Bearer ${token}`,
    ]);
    return { ok: true, method: "claude-cli" };
  } catch (err) {
    return { ok: false, error: err?.message || String(err) };
  }
}

/**
 * Run the full Claude Code setup after a token is saved: install the skill and
 * register the MCP server, printing what happened (and manual fallbacks).
 */
export async function setupClaudeCode(settings) {
  let skillPath = null;
  try {
    skillPath = await installClaudeSkill();
    console.log(`  ✓ skill installed:  ${skillPath}`);
  } catch (err) {
    console.warn(`  ⚠ couldn't install the ads-remix skill: ${err?.message || err}`);
  }

  const reg = await registerMcpServer({ mcpUrl: settings.mcpUrl, token: settings.token });
  if (reg.ok) {
    console.log("  ✓ gooseworks MCP server registered in Claude Code (user scope)");
  } else {
    console.log("  ⚠ couldn't auto-register the MCP server. Run this once:");
    console.log(`      ${mcpAddCommand({ mcpUrl: settings.mcpUrl, token: settings.token })}`);
  }
  return { skillPath, mcpRegistered: reg.ok };
}
