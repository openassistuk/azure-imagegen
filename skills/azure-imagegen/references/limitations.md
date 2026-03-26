# Limitations

This v1 skill is intentionally narrow.

## Included

- Azure OpenAI v1 only
- Image generation and image edits through the Image API
- API-key auth
- Entra ID auth through `DefaultAzureCredential`
- JSONL batch generation
- Prompt augmentation helpers

## Excluded

- Classic Azure OpenAI `api-version` endpoint patterns
- Responses API runtime support
- Direct non-Azure OpenAI endpoint support
- Auto-install into live Codex skill folders
- Icons, branding assets, CI, or packaging automation

## Practical implications

- The CLI expects an Azure deployment name, not a raw model id.
- The deployment should target a compatible image model such as `gpt-image-1.5`.
- If a team needs classic endpoint support or a Responses API runtime, add that as a later versioned extension instead of bolting it onto this v1 skill.
