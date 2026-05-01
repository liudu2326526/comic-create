---
name: apimart-gpt-image-2
description: Integrate, debug, or test APIMart GPT-Image-2 image generation in backend services, workers, or scripts. Use when Codex needs to call APIMart's OpenAI-compatible /v1/images/generations endpoint, handle its asynchronous task_id response, poll /v1/tasks/{task_id}, support image-to-image references, configure APIMART_API_KEY or OPENAI_IMAGE_API_KEY, or diagnose GPT-Image-2 generation failures through APIMart.
---

# APIMart GPT-Image-2

## Core Difference

APIMart exposes an OpenAI-compatible Images endpoint, but `gpt-image-2` is asynchronous:

1. `POST /v1/images/generations` returns `{"data": [{"status": "submitted", "task_id": "..."}]}`.
2. Poll `GET /v1/tasks/{task_id}` until `data.status` is `completed` or `failed`.
3. Read the final image URL from `data.result.images[0].url[0]`.

Do not assume the generation response contains OpenAI-style `data[0].b64_json` or `data[0].url`.

## Configuration

Use these runtime variables. Never commit API keys.

```bash
export APIMART_API_KEY="sk-..."
export APIMART_BASE_URL="https://api.apimart.ai"
```

If integrating into an existing OpenAI-compatible image service, these aliases are also acceptable:

```bash
export OPENAI_IMAGE_API_KEY="$APIMART_API_KEY"
export OPENAI_IMAGE_BASE_URL="https://api.apimart.ai"
export OPENAI_IMAGE_MODEL="gpt-image-2"
```

If a caller provides `https://api.apimart.ai/v1`, normalize it to `https://api.apimart.ai` before appending `/v1/...`, or build endpoint URLs with a helper that avoids `/v1/v1`.

The bundled `scripts/test_generation.py` automatically loads a `.env` file from the current working directory when present. It does not print API keys.

## Request Shape

Text-to-image:

```json
{
  "model": "gpt-image-2",
  "prompt": "A clean blue geometric icon on white background, no text",
  "n": 1,
  "size": "1024x1024",
  "quality": "low",
  "output_format": "png"
}
```

Image-to-image uses the same endpoint. APIMart accepts reference images through documented image URL/base64 fields; prefer hosted URLs for backend workflows unless the existing code already uses multipart edits against another provider.

## Polling

Recommended behavior:

- Wait 3-5 seconds between polls.
- Use total timeout at least 180 seconds; high quality or large outputs can take longer.
- Treat `completed` as success and download/mirror the returned URL immediately.
- Treat `failed` and `cancelled` as terminal; surface `data.error.message` when present.
- Send a browser/curl-like `User-Agent` such as `curl/8.7.1`. APIMart's front layer may reject Python `urllib`'s default user agent with `HTTP 403` and `error code: 1010`.

Minimal Python flow:

```python
submit = await client.post(f"{base}/v1/images/generations", headers=headers, json=payload)
task_id = submit.json()["data"][0]["task_id"]

while True:
    status = await client.get(f"{base}/v1/tasks/{task_id}", headers=headers)
    data = status.json()["data"]
    if data["status"] == "completed":
        image_url = data["result"]["images"][0]["url"][0]
        break
    if data["status"] in {"failed", "cancelled"}:
        raise RuntimeError(data.get("error", {}).get("message") or data["status"])
    await asyncio.sleep(5)
```

## Integration Checklist

When wiring APIMart into a backend:

1. Keep API key and base URL in environment or secret config.
2. Normalize base URL and append `/v1/images/generations` and `/v1/tasks/{task_id}` explicitly.
3. Preserve existing direct OpenAI response parsing if other providers still return `b64_json` or `url`.
4. Add an async-response branch when `data[0].task_id` is present.
5. Store the provider `task_id` in task output metadata for debugging.
6. Download the result URL and mirror it to project storage/CDN if the app expects stable local/OBS URLs.
7. Add tests for both direct OpenAI-style responses and APIMart async responses.

## Testing Script

Use `scripts/test_generation.py` to verify credentials and polling outside the app. From a project directory containing `.env`, no explicit key export is needed:

```bash
python ~/.codex/skills/apimart-gpt-image-2/scripts/test_generation.py \
  --prompt "A clean blue geometric icon on white background, no text" \
  --size 1024x1024 \
  --quality low \
  --output /tmp/apimart-test.png
```

Or pass credentials explicitly:

```bash
APIMART_API_KEY="sk-..." APIMART_BASE_URL="https://api.apimart.ai/v1" \
python ~/.codex/skills/apimart-gpt-image-2/scripts/test_generation.py \
  --prompt "A clean blue geometric icon on white background, no text" \
  --size 1024x1024 \
  --quality low \
  --output /tmp/apimart-test.png
```

The script submits a task, polls until completion, prints the final URL, and downloads the image when `--output` is provided. It defaults to `User-Agent: curl/8.7.1`; override with `--user-agent` only if APIMart changes its gateway behavior.

## References

For endpoint details and response examples, read `references/api.md`.
