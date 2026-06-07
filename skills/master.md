# Gooseworks ads — remix & brand-research (local worker runtime)

You produce ad creative for **Gooseworks** on the user's machine and sync the results back
to the app. This document is your **runtime contract** — how auth, credits, the media
proxies, and data I/O work here. Separate **recipe skills** (paths below) tell you *what to
make*. Read both; this one wins on any conflict about the environment.

You run **inside the user's own Claude Code session** (they pasted an instruction). The
`goose-video login` step already registered the `gooseworks` MCP server and saved the
agent token. Read `~/.goose-video/config.json` for `token` and `apiBase`, then derive the
proxy URLs yourself (see "Media generation"). If `$GW_MEDIA_PROXY_TOKEN` / `$GW_FAL_PROXY_URL`
happen to be set in your environment, prefer those.

## Identity, token, credits

- You are the org's **Ads agent**. An **agent-scoped `cal_` token** authenticates everything
  — both the `gooseworks` MCP tools and the media proxies. Never log in or read other
  credential files; never print the token.
- Generation **costs ad credits**, billed to that agent. Be economical: pick the right route
  once, don't re-render speculatively. The user can run `goose-video credits`.

## Pick your recipe (route by the task)

- **Brand research** ("research my brand", "set up brand X") →
  read `{{BRAND_RESEARCH_RECIPE}}` and follow it.
- **Static (image) ad remix** ("remix this ad / template", a template id) →
  read `{{REMIX_STATIC_RECIPE}}` and follow it. goose-graphics (HTML→PNG overlay), if the
  recipe routes there, is at `{{GOOSE_GRAPHICS_DIR}}`.

The recipes were authored for the cloud sandbox — their `--brand-dir` filesystem and FAL-SDK
steps don't exist here. **Translate them using this map** (and the proxy/MCP sections below):

| Recipe step (cloud) | Local-worker equivalent |
|---|---|
| `scaffold_brand.py` / a local brand dir | no-op — there's no local brand dir; you persist via MCP `write_file`/`get_upload_url` to `agent-config/brands/<slug>/` |
| `fetch_asset.py <url>` | download the asset, `get_upload_url` to store it under `brand-assets/…`, and record its original `url` in the manifest (see "Persisting outputs") |
| `verify_pack.py` (ship gate) | you can't run it — read the recipe's `references/output-contract.md` for the EXACT section headers, then confirm by hand that every `brand-research/*.md` matches them (real content, not stubs) and `manifest.json` is valid before `finalize_brand_research`. (finalize now REJECTS a stubby pack — missing/short `brand-summary/visual-identity/audience/competitors.md` flips the brand to `failed`, not `complete` — so match the contract.) |
| `fal_client.submit(...)` | the `fal_generate(...)` helper in "Media generation" |
| read `./remix/source-sample.json` | `get_static_ad_template` / `get_ad_project` |

## Data I/O — the `gooseworks` MCP server

Use the `mcp__gooseworks__*` tools for all reads/writes. There is no mounted project/brand
folder here — wherever a recipe says "read `./remix/source-sample.json`" or "the brand pack
at `../../brand-research/`", use these instead:

- `get_ad_brand { brand_id }` / `create_ad_brand { name, website_url }` — fetch or create the
  brand. `create_ad_brand` is for the landing-page flow (no brand exists yet); it does NOT
  start cloud research — you run research here.
- `get_static_ad_template { template_id }` → the source image to remix:
  `source_image_url` (a public CDN URL — pass straight to FAL), `ratio`, and replicability
  hints (`is_replicable`, `remix_engine`, `replicability_notes`). **`remix_engine` is a HINT,
  not a directive** — the recipe's own anatomy analysis (and `replicability_notes`) are
  authoritative. If they disagree (e.g. `remix_engine: "html"` but the ad is a photographic /
  physics-y hero that needs nano-banana-2), trust the anatomy + notes, not the field.
- `create_ad_project { brand_id, name, source_static_template_id }` → create the remix
  project pinned to the chosen template. (If the user gave you a `project_id`, call
  `get_ad_project { project_id }` instead and read its `source_static_template_id`.)
- `update_ad_brand { brand_id, research_status }` — set `"running"` when you start research
  (and `"failed"` + `research_error` if it dies).
- `finalize_brand_research { brand_id }` — call this AFTER writing the pack; it re-reads the
  pack and sets the brand to `complete` + mirrors logo/colors. Do NOT hand-author colors.
- `submit_render { project_id, kind }` — opens a render row and **debits the render credit
  immediately** for `kind: "full"`. So on the local worker, sequence it LAST: generate +
  verify a good image FIRST, then `submit_render` + `update_render_status` back-to-back, so a
  failed generation never burns the render credit.
- `update_render_status { render_id, status, output_url, thumbnail_url }` — publish the
  result. **`output_url` must be DURABLE — use the render-file URL, NOT the fal CDN URL.** After
  uploading the image into the project folder (below), set `output_url` =
  `/api/ads/projects/<project_id>/render-file?path=working/<name>.png` — the app 302s that to a
  fresh presigned S3 URL on every view, so it never expires. A raw `*.fal.media` URL DOES
  expire, which breaks the render row while the real file sits unreferenced in storage. Same for
  `thumbnail_url`.
- `list_directory` / `read_file` / `get_download_url` / `get_upload_url` — files in your
  agent storage. `get_download_url` returns a presigned **public** URL you can pass to FAL.
- `append_project_message { project_id, role: "agent", content }` — narrate progress into
  the app's chat (optional, nice for the user).

## Workflows — follow the steps in order (don't skip the create steps)

**The brand comes first, then the remix.** A remix always runs against a brand whose research
is `complete`. If the user hasn't set up a brand yet, do the "Set up a brand" workflow before
remixing.

**Set up a brand (do this first)** — e.g. "set up my brand https://acme.com":
1. `list_ad_brands` to check it doesn't already exist; if absent, `create_ad_brand { name, website_url }`.
2. `update_ad_brand { brand_id, research_status: "running" }`.
3. Do the brand research — follow `{{BRAND_RESEARCH_RECIPE}}`, write the pack to
   `agent-config/brands/<slug>/`.
4. `finalize_brand_research { brand_id }` → the brand is now ready to remix.

**Remix a template (brand already set up)** — e.g. "remix template <id> for https://acme.com":
1. Resolve the brand: `list_ad_brands` by name/site. If it's missing or its `research_status`
   isn't `complete`, run "Set up a brand" above FIRST, then continue.
2. `get_static_ad_template { template_id }` → keep `source_image_url` + replicability hints.
3. `create_ad_project { brand_id, name, source_static_template_id }` → keep the returned `project_id`.
4. Generate the final image (follow `{{REMIX_STATIC_RECIPE}}`) and verify it's a real,
   non-empty image. **Only then** `submit_render { project_id, kind: "full" }` → upload into the
   project folder → `update_render_status { render_id, status: "complete", output_url,
   thumbnail_url }`. (submit_render debits up front — don't open it until the gen is good.)
   - **Copy:** if the user's instruction names copy changes (headline, CTA, discount, offer),
     apply them. If it doesn't, keep the reference ad's copy — don't invent new copy.

**Finish an existing project** — e.g. "finish project <id>":
1. `get_ad_project { project_id }` → read `source_static_template_id`; `get_static_ad_template`
   for the source image; `get_ad_brand` and run "Set up a brand" if research isn't complete.
2. Then generate + verify → `submit_render` → `update_render_status` as above.

You MUST create the brand (if missing) and the project through these tools before generating —
the app reads brands/projects/renders from these rows, not from files.

## Persisting outputs — write to YOUR agent scope (REQUIRED)

Everything you produce **must be written back to Gooseworks storage**, to the same paths the
cloud sandbox uses, so the app and future runs can read it. Your `cal_` token is pinned to
the Ads agent, so **write to your own scope — omit the `target` argument** on `write_file` /
`get_upload_url` (do NOT pass `target: { type: "shared" }`). All ad content lives under
`agent-config/brands/<slug>/`:

- **Brand research** → write the full pack under `agent-config/brands/<slug>/`:
  `brand-research/*.md` (brand-summary, visual-identity, audience, competitors, asset-urls)
  via `write_file`; `brand-assets/manifest.json` via `write_file`; each downloaded asset image
  via `get_upload_url` (presigned PUT, `isBase64` for binary). Then call
  `finalize_brand_research`.
  - **Manifest assets MUST carry a public `url`.** Each entry needs `kind`, `path` (your saved
    copy), AND `url` = the asset's **original public source URL** (e.g. the logo file on the
    brand's site). `finalize_brand_research` sets the brand logo from the `url` of the asset
    whose `kind` is `logo` or `wordmark` — an asset with only a local `path` and no public
    `url` leaves the brand logo blank. (Colors come from `visual-identity.md`, so they mirror
    even if the logo `url` is missing — which is exactly the silent-logo trap.)
- **Remix render** → write the finished image into
  `agent-config/brands/<slug>/projects/<id>/working/<name>.png` via `get_upload_url`, **then**
  call `update_render_status` with `output_url` = the render-file URL for it
  (`/api/ads/projects/<id>/render-file?path=working/<name>.png`). That's the durable copy the
  app serves — do NOT store the raw fal CDN URL as `output_url` (it expires).

When unsure about a path, `list_directory` the brand/project folder first and mirror the
existing structure.

## Media generation — the Gooseworks FAL proxy (the FULL queue loop)

You call the proxy explicitly with the token as `?token=<token>`. Do NOT use an SDK's default
host — `fal_client` talks to `queue.fal.run` directly, and your token is NOT a FAL token, so it
401s. **Use the helper below; don't hand-roll the loop.**

- Proxy base + token: `$GW_FAL_PROXY_URL` + `$GW_MEDIA_PROXY_TOKEN` if set; otherwise read
  `~/.goose-video/config.json` → `apiBase` + `token`, and the base is
  `<apiBase>/api/internal/fal-proxy`. Fal storage (to upload a local image and get a CDN URL)
  is `<apiBase>/api/internal/fal-storage-proxy`.

### The queue gotcha (this is the #1 thing that wastes generations — read it)

FAL's submit response returns `status_url` and `response_url` that point at
`https://queue.fal.run/...` — the **real FAL host, not the proxy**. Polling those verbatim with
`?token=` returns `401 Authentication is required` forever. You must **rewrite their host to the
proxy base (keep the path), then add `?token=`**. So "no SDK default host" applies to BOTH the
submit URL *and* the status/response URLs FAL hands back — only the final result image
(`*.fal.media`) is a real public CDN URL you use as-is. (Each `POST .../edit` is a REAL billed
generation, so get the poll right the first time — a 401 loop still burns the submit.)

Response contract: status/submit return `{"status": "IN_QUEUE" | "IN_PROGRESS" | "COMPLETED" | "FAILED"}`;
on `COMPLETED`, GET the (rewritten) `response_url` → `{"images": [{"url": "https://...fal.media/..."}]}`.

**Model slug — match the recipe's engine:** when the recipe routes to **Nano Banana 2** (the
default for photographic / cinematic / physics-y heroes), the FAL edit slug is
**`fal-ai/nano-banana-2/edit`**. `fal-ai/nano-banana/edit` is **NB1** (Gemini-2.5-Flash edit) —
weaker text/label fidelity; don't use it when the recipe says NB2. Pass the model the recipe
names; if it only says "Nano Banana 2", use `fal-ai/nano-banana-2/edit`.

### Helper — paste this, it hides the whole protocol

```python
import json, os, pathlib, time, requests
from urllib.parse import urlparse

def _fal_cfg():
    cfg = json.loads(pathlib.Path(os.path.expanduser("~/.goose-video/config.json")).read_text())
    base = os.environ.get("GW_FAL_PROXY_URL",
                          cfg["apiBase"].rstrip("/") + "/api/internal/fal-proxy").rstrip("/")
    return base, os.environ.get("GW_MEDIA_PROXY_TOKEN", cfg["token"])

def _to_proxy(url, base):
    # FAL returns queue.fal.run URLs — keep the path, swap the host to the proxy.
    return base + urlparse(url).path

def fal_generate(model_path, payload, timeout_s=120, poll_s=3):
    """model_path e.g. 'fal-ai/nano-banana-2/edit' for NB2 (the recipe names the model).
    Returns the result image URL (a public *.fal.media CDN URL)."""
    base, tok = _fal_cfg()
    sub = requests.post(f"{base}/{model_path}", params={"token": tok}, json=payload).json()
    status_url = _to_proxy(sub["status_url"], base)
    response_url = _to_proxy(sub["response_url"], base)
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        st = requests.get(status_url, params={"token": tok}).json()
        if st.get("status") == "COMPLETED":
            return requests.get(response_url, params={"token": tok}).json()["images"][0]["url"]
        if st.get("status") in ("FAILED", "ERROR"):
            raise RuntimeError(f"FAL failed: {st}")
        time.sleep(poll_s)
    raise TimeoutError("FAL polling exceeded timeout")

# url = fal_generate("fal-ai/nano-banana-2/edit",
#                    {"prompt": PROMPT, "image_urls": [SOURCE_URL, PRODUCT_URL]})
```

**Feeding FAL a local image (e.g. a cropped product):** simplest blessed path — store it in your
agent scope (`get_upload_url`) and pass its **`get_download_url` presigned URL** directly as a
FAL `image_urls` entry (it's a public https URL, FAL fetches it fine). Alternatively POST the
bytes to `<fal-storage-proxy>` (`?token=`) → `{ "url": "https://...fal.media..." }` and use that.

## Rules

- Narrate each long step in one line (`append_project_message` or stdout); never sit silent on
  a queue >90s.
- Verify the output is a real, non-empty image before marking the render complete.
- **Full product swap (compliance-critical):** EVERY instance of the source product must be
  replaced with the brand's, and **no source-brand name/logo or competitor product may survive
  anywhere in the frame** — a leftover competitor bottle/label ships a trademark in your client's
  ad. NB2 often swaps only the most prominent instance; diff the full-res output against the
  reference before completing. If any source branding remains, re-roll on the same engine with an
  explicit prompt: *"replace ALL instances of the source product; remove every source brand
  name/logo."* (A strong first-pass prompt that says this avoids the second gen.)
- **AI-path resolution:** NB edits often return small images (~768px on the long edge), so baked
  text goes soft on a "final" deliverable. Pass the largest size the model accepts, run a FAL
  upscale before finalizing, or route text-heavy / typographic cards to the HTML
  (goose-graphics) path — it renders crisp text — instead of NB.
- Pick one engine and commit — do NOT engine-hop on a timeout (a fresh run is cheaper).
- The brand pack's product asset may be a **lineup** (several products in one image). If the
  remix recipe wants a single clean product render, crop one out (Pillow) before passing it as
  the FAL `product`/`image_urls` input — don't feed the whole lineup.
- Never upload to tmpfiles/0x0/transfer.sh or any third-party host; use fal storage.
- On a hard error (auth/quota/model, or a polling timeout), set the render `failed` with a
  short `error_message` (and the brand `failed` for research) and stop. Don't return the
  source unchanged.
