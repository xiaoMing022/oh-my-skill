# Inputs

Collect every source in the user message before designing. One prototype
from the union of sources, not one prototype per link.

## Classify

| Source | Detect | Intake |
| --- | --- | --- |
| Feishu / Lark doc or wiki | `feishu.cn`, `feishu.com`, `larksuite.com`, `larkoffice.com`, `doubao.com` + `/docx/` or `/wiki/`, or a doc token | Feishu gate in `SKILL.md`, then `lark-doc` |
| Feishu sheet | `/sheets/` | `lark-sheets` only for sample data / field lists |
| Feishu Base / bitable | `/base/`, `/bitable/` | `lark-base` only for sample data / field lists |
| Public webpage | other `http(s)` URL | `web_fetch` or Playwright |
| Image / screenshot | attached image, local png/jpg/webp, or doc media | Read as an image |
| Local file | `.md`, `.txt`, `.pdf`, `.docx` | Read with the matching file skill |
| Pasted requirements | the rest of the message | Use as-is |

If several kinds arrive together, Feishu/PDF/markdown supply IA and copy;
screenshots supply layout, density, and color; webpages supply live product
language. Resolve conflicts in this order: **explicit user instruction >
screenshot of the current product > written PRD > inferred**.

## Feishu / Lark

Do not fetch until the Feishu gate in `SKILL.md` has passed.

Then read `lark-doc` (and `lark-shared` if auth is involved). Typical read:

```bash
# short doc
lark-cli docs +fetch --doc "<url-or-token>" --doc-format markdown --detail simple

# long doc: outline, then the product chapters
lark-cli docs +fetch --doc "<url-or-token>" --scope outline --max-depth 3
lark-cli docs +fetch --doc "<url-or-token>" --scope keyword \
  --keyword "需求|原型|功能|流程|页面|用户" --doc-format markdown
```

Pull brand screenshots from the doc when `<img>` tags matter. Use
`docs +media-preview` / `+media-download` as `lark-doc` describes.

If fetch fails with missing scopes or no access, follow `lark-shared`.
Never guess the PRD.

## Webpage

- Try `web_fetch` first for public docs and marketing pages.
- Use Playwright (or agent-browser) when the page is app-like, behind a
  client render, or the fetch is empty.
- If the page needs login you do not have, stop and ask for a screenshot
  or pasted copy. Do not attempt to bypass auth.
- Capture: IA, nav labels, primary actions, tone, color, type. Do not
  scrape the whole site.

## Image

Read the image with the file/image reader (vision). Extract:

- Platform (desktop app, web, iOS, Android)
- Chrome (top bar, sidebar, tabs, bottom nav)
- Palette (background, surface, text, primary, danger)
- Density and radius
- Key screens if it is a collage

If the image is a hand sketch, treat it as IA + layout, not as a color
source unless colors are clearly marked.

## Pasted or file text

Normalize into: who it is for, what they can do, screens, objects/fields,
non-goals. Ignore process meta ("this doc is a draft") unless it changes
scope.

## Thin sources

If the user only says "做一个后台", do not stall. Assume a small tool
(list + detail + create) and state those assumptions in the final message.
Ask a question only when two product types are equally likely (e.g. C 端
商城 vs 内部审批) and the screens would not overlap.
