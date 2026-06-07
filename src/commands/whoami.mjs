/**
 * `goose-video whoami` — verify the saved cal_ token reaches app-mcp by listing
 * the caller's ad brands. Doubles as a connectivity check for mcpUrl.
 */
import { resolveSettings } from "../config.mjs";
import { withMcp, callTool } from "../mcp-client.mjs";

export async function whoami(flags) {
  const settings = await resolveSettings(flags);
  console.log(`app-mcp: ${settings.mcpUrl}`);
  const brands = await withMcp(settings, (client) => callTool(client, "list_ad_brands", {}));
  // app-mcp list tools return { items, total, hasMore }.
  const list = Array.isArray(brands) ? brands : brands?.items || brands?.data || [];
  if (!Array.isArray(list) || list.length === 0) {
    console.log("Token OK. No ad brands yet — create one in the app first.");
    return;
  }
  console.log(`Token OK. ${list.length} brand(s):`);
  for (const b of list) {
    console.log(`  · ${b.slug || b.id}  ${b.name ? `— ${b.name}` : ""}`);
  }
}
