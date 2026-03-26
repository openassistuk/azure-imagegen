# Azure ImageGen Skill

This repository contains a distributable Codex skill at [skills/azure-imagegen](./skills/azure-imagegen) for Azure OpenAI image generation and editing. It is intentionally separate from any live skill installation under `~/.codex/skills` or `.agents/skills`.

## What it includes

- a publishable skill folder with `SKILL.md`
- `agents/openai.yaml` UI metadata
- an Azure-aware CLI at `skills/azure-imagegen/scripts/image_gen.py`
- reference docs for CLI usage, auth, prompting, sample prompts, and current limitations

## Scope

- Azure OpenAI v1 only
- Image API only in v1
- full workflow coverage for `generate`, `edit`, and `generate-batch`
- API key or Entra ID auth

## Prerequisites

Required Python packages:

```bash
python -m pip install openai pillow
```

If you prefer `uv`:

```bash
uv pip install openai pillow
```

Optional for live Entra-authenticated runs:

```bash
python -m pip install azure-identity
```

Or with `uv`:

```bash
uv pip install azure-identity
```

Default env vars:

```text
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_DEPLOYMENT
AZURE_OPENAI_API_KEY
```

## Quick start

From the repo root:

```powershell
$IMAGE_GEN = ".\skills\azure-imagegen\scripts\image_gen.py"
python $IMAGE_GEN generate `
  --endpoint "https://example.openai.azure.com" `
  --deployment "gpt-image-prod" `
  --prompt "Minimal ceramic mug on a clean studio background" `
  --dry-run
```

That performs a zero-network smoke test. For a real call, replace the example endpoint and deployment with your Azure values or set the default env vars first.

API-key live call:

```powershell
python $IMAGE_GEN generate `
  --prompt "A cozy alpine cabin at dawn" `
  --out ".\output\imagegen\cabin.png"
```

Entra-authenticated live call:

```powershell
python $IMAGE_GEN generate `
  --auth-mode entra `
  --prompt "A cozy alpine cabin at dawn"
```

If you want ephemeral dependency installs instead, the same live commands also work with `uv run --with openai --with pillow` and `uv run --with openai --with pillow --with azure-identity`.

## Install into a live Codex environment later

Copy `skills/azure-imagegen` into one of the locations your Codex setup uses for skills, such as:

- `~/.codex/skills/azure-imagegen`
- `.agents/skills/azure-imagegen` in a target repo

This repo does not install the skill automatically.

## Layout

```text
skills/
  azure-imagegen/
    SKILL.md
    agents/openai.yaml
    scripts/image_gen.py
    references/
```

## Current limitations

See [skills/azure-imagegen/references/limitations.md](./skills/azure-imagegen/references/limitations.md).
