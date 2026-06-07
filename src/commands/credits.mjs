/**
 * `goose-video credits` — show the agent's credit balance.
 * Hits the same `/v1/credits` endpoint the gooseworks CLI uses (Bearer cal_).
 */
import { resolveSettings, loadConfig } from "../config.mjs";

export async function credits(flags) {
  const settings = await resolveSettings(flags);
  const cfg = await loadConfig();
  const res = await fetch(`${settings.apiBase}/v1/credits`, {
    headers: { Authorization: `Bearer ${settings.token}` },
  });
  if (!res.ok) {
    throw new Error(`/v1/credits → HTTP ${res.status} ${res.statusText}`);
  }
  const body = await res.json();
  const d = body?.data || {};
  console.log(`Credits (agent ${d.agent_id || cfg.agentId || "?"}):`);
  console.log(`  available:    ${d.available_credits ?? "?"}`);
  console.log(`  subscription: ${d.subscription_credits ?? "?"}`);
  console.log(`  purchased:    ${d.purchased_credits ?? "?"}`);
}
