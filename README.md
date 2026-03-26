# Azure ImageGen Skill

This repository contains a distributable Codex skill at [skills/azure-imagegen](./skills/azure-imagegen) for Azure OpenAI image generation and editing.
The installable unit is the [`skills/azure-imagegen`](./skills/azure-imagegen) folder, not the repo root.

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

## Install the skill

1. Clone this repository:

```bash
git clone https://github.com/openassistuk/azure-imagegen.git
cd azure-imagegen
```

2. Copy `skills/azure-imagegen` into one of your Codex skill locations:

- global install: `~/.codex/skills/azure-imagegen`
- project-local install: `.agents/skills/azure-imagegen` inside the repo where you want Codex to use it

3. Install the Python dependencies in the environment that will run the bundled CLI:

```bash
python -m pip install openai pillow
```

Optional for live Entra-authenticated runs:

```bash
python -m pip install azure-identity
```

This repo does not install the skill automatically. Copy the skill folder into place yourself.

## Install examples

PowerShell global install:

```powershell
git clone https://github.com/openassistuk/azure-imagegen.git
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
Copy-Item -Recurse .\azure-imagegen\skills\azure-imagegen "$HOME\.codex\skills\azure-imagegen"
```

Bash global install:

```bash
git clone https://github.com/openassistuk/azure-imagegen.git
mkdir -p ~/.codex/skills
cp -R azure-imagegen/skills/azure-imagegen ~/.codex/skills/azure-imagegen
```

## CLI prerequisites

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

## Quick start from this repo

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

If you install the skill into Codex, the same bundled CLI lives at `skills/azure-imagegen/scripts/image_gen.py` inside the installed skill folder.

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
