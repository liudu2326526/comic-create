# Comic Drama Platform Code Map

This reference maps the `comic-drama-platform` implementation to the Seedance video generation skill.

## Config

- `backend/app/config.py`
  - Ark: `ark_api_key`, `ark_base_url`, `ark_video_model_standard`, `ark_video_model_fast`, `ark_video_execution_expires_after`
  - Asset library: `volc_access_key_id`, `volc_secret_access_key`, `ark_project_name`, `volc_asset_host`, `volc_asset_region`, `volc_asset_service`
  - OBS: `obs_ak`, `obs_sk`, `obs_endpoint`, `obs_bucket`, `obs_public_base_url`

## Provider Clients

- `backend/app/infra/volcano_client.py`
  - `RealVolcanoClient.video_generations_create`: builds `content` with one text item plus `reference_image` items and posts to `/contents/generations/tasks`.
  - `RealVolcanoClient.video_generations_get`: queries `/contents/generations/tasks/{task_id}`.
  - `image_generations` and `chat_completions` support earlier prompt/asset steps.

- `backend/app/infra/volcano_asset_client.py`
  - Implements AK/SK HMAC signing.
  - `create_asset_group`, `create_asset`, `get_asset`, `wait_asset_active`.
  - Must be closed with `aclose()` after async use.

- `backend/app/infra/volcano_errors.py`
  - Classifies provider HTTP and transport errors.
  - `humanize_volcano_error_message` maps privacy/content-filter image errors to a user-readable message.

## Asset Library Ingestion

- `backend/app/domain/services/character_service.py`
  - `register_asset_async`: creates `register_character_asset` job and dispatches it.
  - `_register_asset_steps`: idempotent group/create/wait flow.
  - Stores asset metadata in `Character.video_style_ref`.

- `backend/app/tasks/ai/register_character_asset.py`
  - Celery task `ai.register_character_asset`.
  - Progress total is 3: group/create/wait.
  - Calls `CharacterService._register_asset_steps`.

## Render Draft

- `backend/app/api/shots.py`
  - `POST /projects/{project_id}/shots/{shot_id}/render-draft` creates `gen_shot_draft` job.

- `backend/app/tasks/ai/gen_shot_draft.py`
  - First asks chat model to select reference images.
  - Then asks chat model to create a prompt using `docs/huoshan_api/SKILL.md`.
  - Saves `ShotDraft(prompt, references_snapshot, optimizer_snapshot)`.

- `backend/app/domain/services/reference_candidates.py`
  - Builds auto candidates from generated scene and character images.
  - Defaults to one scene and up to two characters.

## Video Generation

- `frontend/src/components/generation/GenerationPanel.vue`
  - `generateDraft`: submits render-draft job.
  - `generateVideo`: persists the edited draft and calls `store.generateVideoFromDraft`.
  - Users can edit prompt, references, duration, resolution, and model type.

- `frontend/src/store/workbench.ts`
  - `generateVideoFromDraft`: builds payload with `prompt`, `references`, optional `reference_mentions`, `resolution`, `model_type`, optional `duration`.
  - `extractReferenceMentions`: turns UI `@alias` mentions into binding metadata.

- `backend/app/api/shots.py`
  - `POST /projects/{project_id}/shots/{shot_id}/video`: creates video version + `render_shot_video` job and dispatches `video.render_shot_video`.
  - `GET /projects/{project_id}/shots/{shot_id}/videos`: lists video versions.
  - `POST /projects/{project_id}/shots/{shot_id}/videos/{video_id}/select`: switches current video version.
  - `POST /projects/{project_id}/shots/{shot_id}/lock`: locks current video version when present.

- `backend/app/domain/services/shot_video_service.py`
  - Validates allowed stages, prompt, references, duration, resolution, and model type.
  - Creates `ShotVideoRender` with `prompt_snapshot` and `params_snapshot`.
  - Advances project to `rendering` and marks the shot `generating`.

- `backend/app/tasks/video/render_shot_video.py`
  - Resolves references to public URLs or `asset://` when source character/scene has Active `video_style_ref`.
  - Calls `client.video_generations_create`.
  - Polls `client.video_generations_get`.
  - Persists video and last frame through `persist_generated_asset`.
  - Marks `ShotVideoRender`, `StoryboardShot`, and `Job` terminal states.

## Persistence

- `backend/app/infra/asset_store.py`
  - `persist_generated_asset`: downloads provider output URL to local tmp, uploads to OBS, returns object key, then cleans tmp file.
  - `build_asset_url`: converts object key to public OBS URL.

## State Model

- `backend/app/domain/models/shot_video_render.py`
  - `queued`, `running`, `succeeded`, `failed`.
  - Stores `video_url`, `last_frame_url`, `provider_task_id`, `provider_status`, errors.

- `backend/app/domain/models/storyboard.py`
  - `current_video_render_id` points to the selected successful video render.

- `backend/app/pipeline/transitions.py`
  - `mark_shot_video_running`, `mark_shot_video_succeeded`, `mark_shot_video_failed`, `select_shot_video_version`, `mark_shot_locked`.
  - `advance_to_ready_for_export_if_complete` moves the project when all shots are complete.

## Tests To Reuse

- `backend/tests/integration/test_render_shot_video_flow.py`
  - persistence of video and last frame.
  - content-filter humanized errors.
  - Active character asset conversion to `asset://`.

- `backend/tests/integration/test_shot_video_api.py`
  - API-level video job creation.

- `backend/tests/unit/test_shot_video_service.py`
  - service validation and version behavior.
