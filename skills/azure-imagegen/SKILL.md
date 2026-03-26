---
name: azure-imagegen
description: "Generate, edit, and batch-create images with Azure OpenAI v1 Image API. Use when Codex needs Azure-first image generation or image editing workflows for deployed image models, including prompt-to-image, masked edits, background extraction, transparent backgrounds, product shots, UI mockups, or batch JSONL runs, with API key or Entra ID authentication via the bundled CLI (`scripts/image_gen.py`)."
---

# Azure ImageGen

Generate or edit images with Azure OpenAI v1 by using the bundled CLI `scripts/image_gen.py`. Use deployment names instead of raw model names, prefer dry-runs before live calls, and keep the skill Azure-specific.

## Runtime Scope

- Target Azure OpenAI v1 only.
- Use the Image API only in v1.
- Exclude classic Azure `api-version` endpoints.
- Exclude a Responses API runtime path in v1.

## Workflow

1. Decide `generate`, `edit`, or `generate-batch`.
2. Collect prompt(s), exact text, constraints, and any input image(s) or mask(s).
3. Resolve Azure configuration in this order:
   - direct CLI value (`--endpoint`, `--deployment`)
   - custom env-var-name flag (`--endpoint-env`, `--deployment-env`, `--api-key-env`)
   - default env var (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_KEY`)
4. Run the bundled CLI with `--dry-run` first unless configuration is already known-good.
5. Inspect outputs, then iterate with one targeted prompt or mask change at a time.

## Command Selection

- If the user provides one or more input images, or asks to retouch, inpaint, mask, localize text, replace a background, or "change only X", use `edit`.
- If the user needs many prompts or many assets in one run, use `generate-batch`.
- Otherwise use `generate`.

## Authentication

- Default to `--auth-mode api-key`.
- Use `--auth-mode entra` when the environment is configured for `DefaultAzureCredential`.
- Never ask the user to paste secrets into chat.
- If `--auth-mode api-key` is used, read the key from an environment variable, not a CLI secret flag.
- If `--auth-mode entra` is used, require `azure-identity` for live calls.

## Defaults And Rules

- Assume the deployment targets `gpt-image-1.5` unless the user says otherwise.
- Prefer the bundled CLI over ad hoc wrapper scripts.
- Keep prompt augmentation short and structural; do not invent new creative requirements.
- For edits, restate invariants every iteration.
- Use `quality=high` for text-heavy or detail-critical outputs.
- Use `input_fidelity=high` for identity-preserving or layout-sensitive edits.

## Prompt Augmentation

Reformat user prompts into a short production-style spec. Include only lines that are relevant.

```text
Use case: <taxonomy slug>
Asset type: <where the asset will be used>
Primary request: <user prompt>
Scene/background: <environment>
Subject: <main subject>
Style/medium: <photo/illustration/3D/etc>
Composition/framing: <wide/close/top-down; placement>
Lighting/mood: <lighting + mood>
Color palette: <palette notes>
Materials/textures: <surface details>
Text (verbatim): "<exact text>"
Constraints: <must keep/must avoid>
Avoid: <negative constraints>
```

## Use-Case Taxonomy

Generate:
- `photorealistic-natural`
- `product-mockup`
- `ui-mockup`
- `infographic-diagram`
- `logo-brand`
- `illustration-story`
- `stylized-concept`
- `historical-scene`

Edit:
- `text-localization`
- `identity-preserve`
- `precise-object-edit`
- `lighting-weather`
- `background-extraction`
- `style-transfer`
- `compositing`
- `sketch-to-render`

## Output Conventions

- Use `tmp/imagegen/` for temporary JSONL files or scratch assets.
- Write final outputs under `output/imagegen/` when working inside a repo.
- Keep filenames stable and descriptive by setting `--out` or `--out-dir`.

## Dependencies

Install dependencies with `python -m pip`, or use `uv` if it is already part of the environment.

```bash
python -m pip install openai pillow
```

Optional `uv` form:

```bash
uv pip install openai pillow
```

For live Entra-authenticated calls:

```bash
python -m pip install azure-identity
```

Optional `uv` form:

```bash
uv pip install azure-identity
```

## Reference Map

- `references/cli.md`: command catalog and CLI recipes
- `references/azure-auth.md`: API key and Entra auth setup
- `references/prompting.md`: prompting principles and iteration tips
- `references/sample-prompts.md`: copy/paste prompt recipes
- `references/limitations.md`: explicit v1 boundaries and non-goals
