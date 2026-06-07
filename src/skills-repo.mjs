/**
 * Pulls the canonical ads skills from git into ~/.goose-video/skills/ and
 * resolves a project format → recipe SKILL.md. Single source of truth: the same
 * `gooseworks-ai/gooseworks-ads-skills` repo the cloud sandbox sparse-clones, so
 * local and cloud run the same recipes.
 *
 *   ~/.goose-video/skills/
 *     gooseworks-ads-skills/   ← static remix, brand-research, atoms, molecules
 *     goose-skills/            ← goose-graphics (HTML→PNG overlay)
 *
 * The format → skill MAP lives in the repo (`formats.json` at its root) so adding
 * a format (animated, podcast, …) is a repo-only change. Until that file exists,
 * we fall back to the bundled DEFAULT_FORMAT_MAP below.
 */
import { homedir } from "node:os";
import { join } from "node:path";
import { mkdir, readFile, writeFile, access } from "node:fs/promises";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const run = promisify(execFile);

const SKILLS_DIR = join(homedir(), ".goose-video", "skills");

const REPOS = {
  ads: {
    dir: join(SKILLS_DIR, "gooseworks-ads-skills"),
    url: "https://github.com/gooseworks-ai/gooseworks-ads-skills.git",
    sparse: ["skills/"],
    sentinel: "skills/molecules/ad-format/remix-graphic-ad-from-reference/SKILL.md",
  },
  goose: {
    dir: join(SKILLS_DIR, "goose-skills"),
    url: "https://github.com/gooseworks-ai/goose-skills.git",
    sparse: ["skills/composites/goose-graphics/", "bin/", "package.json"],
    sentinel: "skills/composites/goose-graphics/SKILL.md",
  },
};

/** Format key → path (under the ads repo) of the recipe skill folder. */
const DEFAULT_FORMAT_MAP = {
  static: "skills/molecules/ad-format/remix-graphic-ad-from-reference",
  "brand-research": "skills/templates/brand-research",
};

const exists = (p) =>
  access(p).then(
    () => true,
    () => false,
  );

/** Sparse git clone, mirroring the sandbox's ensureAdsSkillsInstalled. */
async function pullRepo(repo, { update }) {
  if (!update && (await exists(join(repo.dir, repo.sentinel)))) {
    return "cached";
  }
  await mkdir(repo.dir, { recursive: true });
  const git = (args) => run("git", args, { cwd: repo.dir });
  if (!(await exists(join(repo.dir, ".git")))) {
    await git(["init", "-q"]);
    await git(["remote", "add", "origin", repo.url]).catch(() => {});
  }
  await git(["config", "core.sparseCheckout", "true"]);
  await writeFile(join(repo.dir, ".git/info/sparse-checkout"), repo.sparse.join("\n") + "\n");
  await git(["pull", "-q", "--depth", "1", "origin", "main"]);
  if (!(await exists(join(repo.dir, repo.sentinel)))) {
    throw new Error(`Skill repo pulled but sentinel missing: ${repo.sentinel}`);
  }
  return update ? "updated" : "cloned";
}

/**
 * Ensure both skill repos are present locally. `update: true` re-pulls latest.
 * Returns a per-repo status map for logging.
 */
export async function ensureSkillsPulled({ update = false } = {}) {
  const out = {};
  for (const [key, repo] of Object.entries(REPOS)) {
    out[key] = await pullRepo(repo, { update });
  }
  return out;
}

/** Load the repo's format map (formats.json), falling back to the bundled default. */
async function loadFormatMap() {
  try {
    const raw = await readFile(join(REPOS.ads.dir, "formats.json"), "utf8");
    return { ...DEFAULT_FORMAT_MAP, ...JSON.parse(raw) };
  } catch {
    return DEFAULT_FORMAT_MAP;
  }
}

/**
 * Resolve a format key (e.g. "static", "brand-research") to the absolute path of
 * its recipe SKILL.md (and its folder). Ensures skills are pulled first.
 */
export async function resolveSkill(formatKey, { update = false } = {}) {
  await ensureSkillsPulled({ update });
  const map = await loadFormatMap();
  const rel = map[formatKey];
  if (!rel) {
    const known = Object.keys(map).join(", ");
    throw new Error(`No skill mapped for format "${formatKey}". Known formats: ${known}.`);
  }
  const dir = join(REPOS.ads.dir, rel);
  const skillMd = join(dir, "SKILL.md");
  if (!(await exists(skillMd))) {
    throw new Error(`Recipe skill missing on disk: ${skillMd}. Try \`goose-video update\`.`);
  }
  return { dir, skillMd };
}

/** Absolute path to goose-graphics (HTML→PNG overlay), for recipes that use it. */
export function gooseGraphicsDir() {
  return join(REPOS.goose.dir, "skills/composites/goose-graphics");
}

export { SKILLS_DIR };
