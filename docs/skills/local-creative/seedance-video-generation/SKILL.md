---
name: seedance-video-generation
description: Use when implementing or reviewing Seedance 2.0 video generation in a backend/frontend product, including Ark API wrappers, async task polling, private portrait asset library ingestion and Active review, asset:// references, OBS persistence, job state, and integration with render draft workflows.
---

# Seedance Video Generation

## Scope

Use this skill for engineering work that wires Seedance 2.0 into an application, not for pure prompt writing. It covers:

- Volcengine Ark Seedance video task create/query wrappers.
- private portrait asset library registration and review (`CreateAssetGroup`, `CreateAsset`, `GetAsset`, `Status=Active`).
- converting approved portrait assets to `asset://<asset_id>` references.
- async job/task design for long-running video generation.
- persisting generated video and last-frame assets before provider URLs expire.
- frontend `render draft -> edit -> generate video -> version history -> lock` flows.

For standalone prompt optimization, use `seedance` or `make-prompt-seedance2`. For story-to-series prompt packages, use `seedance-storyboard-generator`.

## Architecture Pattern

Keep the integration split into five boundaries:

1. **Config**
   - Ark API key and model names.
   - Asset library AK/SK signing settings.
   - storage/OBS settings.
   - polling timeout and retry settings.

2. **Provider clients**
   - `ArkVideoClient` or equivalent: Bearer-auth Seedance video create/query.
   - `VolcanoAssetClient` or equivalent: AK/SK HMAC-signed private portrait asset library calls.
   - The provider clients should classify auth, param, content-filter, rate-limit, timeout, and server errors into stable internal errors.

3. **Domain service**
   - Validate stage/preconditions.
   - Create a version row, snapshot prompt/references/params, and create an async job.
   - Never block HTTP while provider generation or asset review runs.

4. **Worker task**
   - Resolve references.
   - Submit Seedance task.
   - Poll provider task id.
   - Persist result video/last frame.
   - Update version/job state through transition helpers.

5. **Frontend**
   - Generate/load render draft.
   - Let user edit prompt, references, duration, resolution, model type.
   - Submit generation and poll job.
   - Display current video, version history, errors, and lock action.

## Required Environment

Use component env vars, not hard-coded credentials:

| Purpose | Variables |
| --- | --- |
| Ark video/chat/image APIs | `ARK_API_KEY`, `ARK_BASE_URL`, `ARK_VIDEO_MODEL_STANDARD`, `ARK_VIDEO_MODEL_FAST` |
| Provider mode | `AI_PROVIDER_MODE=real` for real calls, `mock` for tests/dev |
| Asset library | `VOLC_ACCESS_KEY_ID`, `VOLC_SECRET_ACCESS_KEY`, `ARK_PROJECT_NAME`, `VOLC_ASSET_HOST`, `VOLC_ASSET_REGION`, `VOLC_ASSET_SERVICE` |
| Output persistence | `OBS_AK`, `OBS_SK`, `OBS_ENDPOINT`, `OBS_BUCKET`, `OBS_PUBLIC_BASE_URL` |
| Polling | `ARK_VIDEO_EXECUTION_EXPIRES_AFTER`, `ASSET_WAIT_TIMEOUT_SEC`, `ASSET_WAIT_INTERVAL_SEC` |

Never print, commit, or persist user-provided keys.

## API Contracts

### Seedance Video Create

Auth: `Authorization: Bearer $ARK_API_KEY`

Endpoint:

```text
POST https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
```

Payload shape:

```json
{
  "model": "doubao-seedance-2-0-fast-260128",
  "content": [
    { "type": "text", "text": "图片1中的主角在雨夜宫门前回头，近景固定机位，面部稳定。" },
    {
      "type": "image_url",
      "role": "reference_image",
      "image_url": { "url": "asset://asset-xxxx" }
    }
  ],
  "duration": 5,
  "resolution": "720p",
  "ratio": "9:16",
  "generate_audio": false,
  "watermark": false,
  "return_last_frame": true,
  "execution_expires_after": 3600
}
```

### Seedance Video Query

```text
GET https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}
```

Treat statuses as:

| Status | Internal handling |
| --- | --- |
| `queued`, `running` | keep polling, update progress estimate |
| `succeeded` | persist `content.video_url` and optional `content.last_frame_url` immediately |
| `failed`, `expired`, `cancelled` | mark version/job failed with provider error |

### Asset Library

Asset library is a separate API surface from Seedance video generation:

- host: `ark.cn-beijing.volcengineapi.com`
- auth: Volcengine AK/SK HMAC-SHA256 signing
- actions: `CreateAssetGroup`, `CreateAsset`, `GetAsset`

Do not submit a portrait asset to Seedance as `asset://...` until `GetAsset` returns `Status == "Active"`.

## Private Portrait Asset Workflow

Use this when a generated or uploaded character portrait should be used as a stable Seedance reference.

1. Confirm the business object has a public URL for the image. If assets are stored as object keys, convert through the public asset URL builder first.
2. Check existing metadata. If `asset_id` exists and `asset_status == "Active"`, skip registration.
3. Create an asset group when missing:
   - `GroupType="AIGC"`
   - `ProjectName` must match the Ark project/API key context.
4. Create the asset:
   - `AssetType="Image"`
   - `URL=<public image url>`
   - save returned `asset_id` and mark local status `Pending`.
5. Poll `GetAsset` until:
   - `Active`: persist `asset_status=Active`, `asset_updated_at`.
   - `Failed`: fail the job and surface the provider error.
   - timeout: fail with retryable timeout.
6. Close the asset client after async use.

Recommended local metadata:

```json
{
  "asset_group_id": "ag-...",
  "asset_id": "asset-...",
  "asset_status": "Active",
  "asset_updated_at": "2026-04-30T..."
}
```

## Reference Resolution

When generating video:

1. Start from the user-confirmed references in the render draft.
2. If a reference is already an `asset://` URL, pass it through.
3. If reference kind is `character` or `scene`, look up the source object.
4. If the source object has `video_style_ref.asset_id` and `asset_status == "Active"`, send `asset://<asset_id>`.
5. Otherwise send the public image URL.

Keep natural-language prompt references semantic. Do not put raw `asset://asset-xxx` in the text as a subject. If the UI lets users write `@角色名`, append a reference-binding note such as:

```text
参考图绑定关系:
- @女主-全身 => character:01...
```

## Backend Flow

The HTTP endpoint should do only fast validation and dispatch:

```text
POST /projects/{project_id}/shots/{shot_id}/video
  -> validate stage, prompt, references, duration, resolution, model_type
  -> create ShotVideoRender(version_no, queued, prompt_snapshot, params_snapshot)
  -> advance project to rendering, mark shot generating
  -> create render_shot_video job
  -> dispatch worker
  -> return { job_id, sub_job_ids: [] }
```

The worker should:

```text
load video version + shot
resolve references
mark job running, mark version running
create provider task
save provider_task_id
poll provider status
on success:
  download video_url and last_frame_url
  upload to durable storage
  save object keys
  mark version succeeded
  set shot.current_video_render_id
  mark job succeeded
on failure:
  mark version failed
  mark job failed
```

State writes should go through transition helpers or equivalent central state-machine functions.

## Frontend Flow

The intended product flow is:

```text
fetchRenderDraft / generateRenderDraft
  -> user edits prompt and reference images
  -> choose duration/resolution/model
  -> generateVideoFromDraft
  -> poll render_shot_video job
  -> reload project + fetch video versions
  -> preview current video
  -> select version or lock final version
```

Validation should happen before submit:

- prompt is non-empty.
- at least one reference image exists.
- no other active video generation job for the same project if only one is supported.
- duration is 4-15 seconds.
- resolution is `480p` or `720p`.
- model type is `standard` or `fast`.

## Failure Handling

Map provider failures to stable user-facing categories:

| Category | Examples | Handling |
| --- | --- | --- |
| auth | 401/403 | configuration/credential error |
| param | 400 non-content-filter | developer payload bug |
| content filter | `InputImageSensitiveContentDetected`, `ContentFilter` | ask user to change prompt/reference |
| rate limit | 429 | retry after provider hint or backoff |
| timeout | http timeout or polling expiry | retryable |
| server | 5xx/transport | retryable |

For content-filtered input images, prefer a direct message such as: `参考图被平台判定含隐私或敏感信息，请更换参考图后重试`.

## Testing Checklist

Use deterministic tests with fake clients by default:

- create video version validates stage, params, and snapshots.
- worker submits correct payload to provider.
- succeeded provider response persists mp4 and last frame and sets current video version.
- failed/content-filter provider response marks both version and job failed.
- registered `Active` character reference is converted to `asset://...`.
- asset-library registration is idempotent when already Active.
- dispatch failures mark job failed rather than leaving queued rows.

Do not run real provider tests unless explicitly requested and real credentials are available.

## Project-Specific References

For this repo, read these files when implementing or reviewing:

- `references/project/comic-drama-code-map.md` for concrete local paths and contracts.
- `references/volcengine-api/创建视频生成任务 API.md` for create payload details.
- `references/volcengine-api/查询视频生成任务 API.md` for polling result shape.
- `references/volcengine-api/私域虚拟人像素材资产库使用指南.md` for asset review constraints.
- `scripts/CreateAssetGroup_Demo (1).py` and `scripts/CreateAsset&GetAsset_Demo (1).py` for AK/SK signing examples.

Prefer the live repo code over older docs if they conflict.
