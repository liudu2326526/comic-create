---
name: "seedance-api-integration"
description: "Use when integrating Volcengine Ark Seedance 2.0 or Seedance 2.0 fast APIs, creating or querying video/image generation tasks, ingesting private virtual portrait assets, using asset:// references, polling tasks, or wiring 火山/方舟 API calls into code."
---

# Seedance API Integration

## Role
Act as a Volcengine Ark integration engineer for Seedance 2.0 series APIs. Focus on executable API workflows, payload shape, authentication, private virtual portrait asset library ingestion, `asset://` usage, task polling, and failure handling. For pure prompt optimization, use the separate `sd2-pe` skill.

## Load References
Read only the files needed for the current task:

- Video create API: `创建视频生成任务 API.md`
- Video task query API: `查询视频生成任务 API.md`
- Video task list/cancel/delete: `查询视频生成任务列表.md`, `取消或删除视频生成任务.md`
- Image generation: `图片生成 API.md`
- Chat: `对话(Chat) API.md`
- Private portrait asset library: `私域虚拟人像素材资产库使用指南.md`
- AK/SK signing demos: `人像库 demo/CreateAssetGroup_Demo (1).py`, `人像库 demo/CreateAsset&GetAsset_Demo (1).py`

## Authentication Split

| Capability | Endpoint | Auth |
|---|---|---|
| Seedance video generation | `https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks` | `Authorization: Bearer $ARK_API_KEY` |
| Video task query | `GET /api/v3/contents/generations/tasks/{id}` | `Authorization: Bearer $ARK_API_KEY` |
| Seedream image generation | `https://ark.cn-beijing.volces.com/api/v3/images/generations` | `Authorization: Bearer $ARK_API_KEY` |
| Asset library APIs | `https://ark.cn-beijing.volcengineapi.com/?Action=...&Version=2024-01-01` | Volcengine AK/SK HMAC-SHA256 signing |

Never print, hard-code, or invent credentials. Live calls that upload files, transmit private assets, or spend quota require explicit user confirmation at action time.

## Workflow: Ingest Virtual Portrait Assets

Use this for private virtual human / character assets that must be referenced by Seedance 2.0.

1. Verify the asset is appropriate for the private portrait library. The user must have rights to the asset; ordinary non-portrait references do not need ingestion.
2. Create or reuse an Asset Group with `CreateAssetGroup`.
3. Upload assets with `CreateAsset`: pass `GroupId`, `URL`, `AssetType` (`Image`, `Video`, `Audio`), and `ProjectName`.
4. Poll `GetAsset` until `Status == "Active"`.
5. Stop on `Status == "Failed"` and surface the error. Never pass a failed or processing asset to generation.

Constraints:

- Image formats: jpeg, png, webp, bmp, tiff, gif, heic/heif.
- Single image: aspect ratio `(0.4, 2.5)`, side length `(300, 6000)` px, under 30 MB.
- Recommended character group: full-body front image plus face close-up in the same Asset Group.
- `ProjectName` must match across Asset Group, Asset, GetAsset/ListAssets, and the project/API key used for inference.
- CreateAsset is asynchronous and has no upload-time SLA.

Prefer adapting the bundled AK/SK demos instead of rewriting signing:

```python
# CreateAssetGroup: Name, Description, GroupType="AIGC", ProjectName
# CreateAsset: GroupId, URL, AssetType, ProjectName
# GetAsset: Id until Result.Status == "Active"
```

## Workflow: Use Asset Library Materials

Use `asset://<asset_id>` only in media URL fields. In `content.text`, reference the material by sequence: `图片 1`, `视频 1`, `音频 1`. Do not write the Asset ID as the subject in natural language.

```json
{
  "model": "doubao-seedance-2-0-260128",
  "content": [
    {
      "type": "text",
      "text": "图片 1中的女主穿着图片 2中的服装，在雨夜宫门前回头，近景固定机位，冷蓝月光，电影感，面部稳定不变形。"
    },
    {
      "type": "image_url",
      "role": "reference_image",
      "image_url": { "url": "asset://asset-xxxxxxxx" }
    },
    {
      "type": "image_url",
      "role": "reference_image",
      "image_url": { "url": "asset://asset-yyyyyyyy" }
    }
  ],
  "generate_audio": true,
  "ratio": "9:16",
  "duration": 8,
  "resolution": "720p",
  "watermark": false,
  "return_last_frame": true
}
```

Submit:

```bash
curl -X POST 'https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d @payload.json
```

Poll:

```bash
curl 'https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/<TASK_ID>' \
  -H "Authorization: Bearer $ARK_API_KEY"
```

Handle statuses:

- In progress: `queued`, `running`
- Success: `succeeded`; persist `content.video_url` and `content.last_frame_url` quickly because output URLs expire after 24 hours
- Terminal failure: `failed`, `cancelled`, `expired`

## Seedance 2.0 Parameter Rules

- Model: prefer `doubao-seedance-2-0-260128` unless the user asks for fast model or an Endpoint ID.
- `duration`: integer `4..15`, or `-1`; do not use `frames` for Seedance 2.0 / 2.0 fast.
- `ratio`: `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `21:9`, or `adaptive`.
- `resolution`: `480p` or `720p`; `1080p` is not supported by Seedance 2.0 fast.
- `image_url.role`: `first_frame`, `last_frame`, or `reference_image`.
- `video_url.role`: `reference_video`.
- `audio_url.role`: `reference_audio`; do not submit audio alone. Include at least one image or video reference.
- First-frame / first-last-frame mode and multimodal reference mode are mutually constrained; check the create API doc before combining roles.

## Output Contract

For integration answers, include:

1. Required env vars and auth method.
2. Media mapping table: request order -> `图片 1` / `视频 1` / `音频 1` -> URL or `asset://`.
3. Final JSON payload or code snippet.
4. Polling logic and terminal status handling.
5. Asset-library caveats when using private portraits.

## Common Mistakes

- Putting `asset://asset-xxx` inside `content.text`.
- Calling video generation before `GetAsset` returns `Active`.
- Mixing `ProjectName` between asset APIs and inference.
- Using ordinary image/video URLs for restricted human-face material instead of the required authorized asset path.
- Forgetting that generation outputs expire after 24 hours.
- Sending large media as base64 when a public URL or asset ingestion is more appropriate.
