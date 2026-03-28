# CLI reference (`scripts/image_gen.py`)

Keep `SKILL.md` overview-first. Put verbose command details here.

## What this CLI does

- `generate`: create a new image from a prompt
- `edit`: edit one or more existing images, optionally with a mask
- `generate-batch`: run many prompt jobs from a JSONL file

Real API calls require network access. `--dry-run` does not.

## Default configuration

- Deployment source: explicit `--deployment` or `AZURE_OPENAI_DEPLOYMENT`
- Size: `1024x1024`
- Quality: `high`
- Output format: `png`
- Auth mode: `api-key`
- Default env vars:
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_DEPLOYMENT`
  - `AZURE_OPENAI_API_KEY`

`AZURE_OPENAI_ENDPOINT` may be either:
- the Azure resource root, for example `https://example.openai.azure.com`
- the full v1 base URL, for example `https://example.openai.azure.com/openai/v1/`

## Config resolution

For endpoint and deployment values, resolve in this order:

1. direct CLI value (`--endpoint`, `--deployment`)
2. custom env-var-name flag (`--endpoint-env`, `--deployment-env`, `--api-key-env`)
3. default env var

If a custom env-var-name flag is set, treat that env var as the source of truth for that setting.

## Quick start

Set a stable path to the skill CLI from the repo root:

```powershell
$IMAGE_GEN = ".\skills\azure-imagegen\scripts\image_gen.py"
```

Install dependencies first with either:

```bash
python -m pip install openai pillow
```

Or:

```bash
uv pip install openai pillow
```

Dry-run a generation with default env vars:

```powershell
python $IMAGE_GEN generate --prompt "Minimal ceramic mug on a clean studio background" --dry-run
```

Dry-run with explicit endpoint and deployment:

```powershell
python $IMAGE_GEN generate `
  --endpoint "https://example.openai.azure.com" `
  --deployment "gpt-image-prod" `
  --prompt "Minimal ceramic mug on a clean studio background" `
  --dry-run
```

Live call with API-key auth:

```powershell
uv run --with openai --with pillow python $IMAGE_GEN generate `
  --prompt "A cozy alpine cabin at dawn" `
  --size 1024x1024 `
  --out ".\output\imagegen\cabin.png"
```

Live call with Entra auth:

```powershell
uv run --with openai --with pillow --with azure-identity python $IMAGE_GEN generate `
  --auth-mode entra `
  --prompt "A cozy alpine cabin at dawn"
```

If dependencies are already installed in the current Python environment, drop the `uv run ...` prefix and invoke `python $IMAGE_GEN ...` directly.

## Guardrails

- Use `python ...\scripts\image_gen.py` or an equivalent full path.
- Prefer `--dry-run` first when validating config, prompt structure, or output paths.
- Do not pass secrets on the command line.
- Do not add ad hoc wrapper scripts unless the user explicitly asks for one.

## Common recipes

Generate and also write a downscaled copy for web delivery:

```powershell
uv run --with openai --with pillow python $IMAGE_GEN generate `
  --prompt "A cozy alpine cabin at dawn" `
  --downscale-max-dim 1024 `
  --out ".\output\imagegen\cabin.png"
```

Generate with prompt augmentation fields:

```powershell
python $IMAGE_GEN generate `
  --prompt "A minimal hero image of a ceramic coffee mug" `
  --asset-type "landing page hero" `
  --use-case "stylized-concept" `
  --style "clean product photography" `
  --composition "centered product, generous negative space on the right" `
  --constraints "no logos, no text" `
  --dry-run
```

Generate with custom env-var names:

```powershell
python $IMAGE_GEN generate `
  --endpoint-env "AZURE_OPENNYC_ENDPOINT" `
  --deployment-env "AZURE_OPENNYC_DEPLOYMENT" `
  --api-key-env "AZURE_OPENNYC_API_KEY" `
  --prompt "Editorial product shot of a travel flask" `
  --dry-run
```

Generate many prompts concurrently:

```powershell
python $IMAGE_GEN generate-batch `
  --input ".\tmp\imagegen\prompts.jsonl" `
  --out-dir ".\output\imagegen\batch" `
  --concurrency 5 `
  --dry-run
```

Edit with a mask:

```powershell
python $IMAGE_GEN edit `
  --image ".\input.png" `
  --mask ".\mask.png" `
  --prompt "Replace only the background with a warm sunset gradient" `
  --dry-run
```

Edit with high fidelity:

```powershell
python $IMAGE_GEN edit `
  --image ".\portrait.png" `
  --prompt "Change only the shirt to a charcoal wool sweater" `
  --input-fidelity high `
  --quality high `
  --dry-run
```

## Batch JSONL shape

Each line can be:
- a raw string prompt
- a JSON object with `prompt`
- a JSON object with `prompt` plus per-job overrides

Supported per-job overrides:
- `n`
- `size`
- `quality`
- `background`
- `output_format`
- `output_compression`
- `moderation`
- any augmentation field such as `use_case`, `asset_type`, `composition`, or `constraints`

## Notes

- Supported sizes: `1024x1024`, `1536x1024`, `1024x1536`
- Transparent backgrounds require `--output-format png` or `webp`
- `generate-batch` requires `--out-dir`
- `--input-fidelity` is edit-only

## See also

- `references/azure-auth.md`
- `references/prompting.md`
- `references/sample-prompts.md`
- `references/limitations.md`
