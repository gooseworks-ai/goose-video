/**
 * `goose-video update` — re-pull the ads skill repos to latest (like
 * `gooseworks update`) AND refresh the `ads-remix` skill installed into the
 * user's Claude Code so it points at the freshly-pulled recipes.
 */
import { ensureSkillsPulled, SKILLS_DIR } from "../skills-repo.mjs";
import { installClaudeSkill } from "../claude-setup.mjs";

export async function update() {
  console.log("Updating skills…");
  const status = await ensureSkillsPulled({ update: true });
  for (const [repo, state] of Object.entries(status)) {
    console.log(`  · ${repo}: ${state}`);
  }
  console.log(`Skills at ${SKILLS_DIR}`);

  try {
    const skillPath = await installClaudeSkill({ update: true });
    console.log(`Refreshed Claude Code skill: ${skillPath}`);
  } catch (err) {
    console.warn(`Couldn't refresh the Claude Code skill: ${err?.message || err}`);
  }
}
