# APIMart GPT-Image-2 API Notes

## Base URL

`https://api.apimart.ai`

Endpoint paths:

- `POST /v1/images/generations`
- `GET /v1/tasks/{task_id}`

## Generation Response

APIMart returns a submitted task rather than the final image:

```json
{
  "code": 200,
  "data": [
    {
      "status": "submitted",
      "task_id": "task_01K..."
    }
  ]
}
```

## Task Status Response

Completed image task:

```json
{
  "code": 200,
  "data": {
    "id": "task_01K...",
    "status": "completed",
    "progress": 100,
    "result": {
      "images": [
        {
          "url": [
            "https://upload.apimart.ai/f/image/example.png"
          ],
          "expires_at": 1776835126
        }
      ]
    },
    "actual_time": 52
  }
}
```

Read image URL from:

```text
data.result.images[0].url[0]
```

Terminal statuses:

- `completed`
- `failed`
- `cancelled`

Non-terminal statuses may include:

- `submitted`
- `pending`
- `processing`
- `in_progress`

## Sizes

APIMart documentation supports aspect-ratio values such as `16:9`; existing OpenAI-compatible integrations may send pixel sizes such as `1024x1024`, `1536x1024`, or `1152x2048`. Test the deployed provider with the exact size format your application sends.

## Known Integration Pitfall

If existing code does:

```python
base_url = "https://api.apimart.ai/v1"
url = f"{base_url}/v1/images/generations"
```

the resulting URL is wrong:

```text
https://api.apimart.ai/v1/v1/images/generations
```

Normalize a trailing `/v1` from configured base URLs or store the base as `https://api.apimart.ai`.
