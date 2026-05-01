#!/usr/bin/env python3
import json
import os
import time
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = ROOT / ".env"
OUT_DIR = ROOT / "scripts/ep01/videos"
META_PATH = OUT_DIR / "ep01_sh01_seedance2_from_9x16_nine_grid.metadata.json"
VIDEO_PATH = OUT_DIR / "ep01_sh01_seedance2_from_9x16_nine_grid.mp4"
LAST_FRAME_PATH = OUT_DIR / "ep01_sh01_seedance2_from_9x16_nine_grid_last_frame.png"
LOG_PREFIX = "[ep01_sh01_seedance]"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


def write_meta(meta: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    META_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def download(url: str, path: Path) -> None:
    with requests.get(url, stream=True, timeout=300) as response:
        response.raise_for_status()
        with path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)


def main() -> int:
    load_env(ENV_PATH)
    api_key = os.environ["ARK_API_KEY"]
    base = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com").rstrip("/")
    model = os.getenv("ARK_VIDEO_MODEL_STANDARD", "doubao-seedance-2-0-260128")
    reference_image_url = (
        "https://static1203.yingsaidata.com/"
        "comic-create/scripts/ep01/images/ep01_sh01_nine_grid_storyboard_9x16_gpt-image-2.png"
    )
    prompt = (
        "图片1是一张9:16竖版3x3九宫格连续分镜参考图，请把九个格子理解为同一段视频从左到右、从上到下推进的连续关键帧，"
        "不要保留九宫格边框、分格、拼贴布局或任何文字编号。生成单段9:16竖版电影写实视频："
        "镜头从混沌虚空大远景缓慢推进，冷暗星河中破碎星辰漂浮，巨大帝尸从黑暗深处逐渐显现并横亘虚空，"
        "金色大道法则锁链从上方垂落并震动，金色光流沿锁链闪烁，星尘被震开；"
        "远处黑暗灾厄翻涌成黑潮，黑潮边缘吞噬星光并朝帝尸封锁区域逼近；"
        "最后形成巨大帝尸、金色法则锁链和灾厄黑潮对峙的压迫定格。"
        "保持参考图中的冷暗宇宙、黑金高对比光影、远古神话压迫感和帝尸/锁链/黑潮核心位置关系，"
        "镜头运动为缓慢推进，时间和空间连续，不要出现人物、字幕、LOGO、水印。"
        "无人物对白；如生成声音，仅保留低沉宇宙轰鸣、法则锁链震动声和低频神话压迫音乐，不要人声旁白。"
    )
    payload = {
        "model": model,
        "content": [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "role": "reference_image",
                "image_url": {"url": reference_image_url},
            },
        ],
        "duration": 6,
        "resolution": "720p",
        "ratio": "9:16",
        "generate_audio": True,
        "watermark": False,
        "return_last_frame": True,
        "execution_expires_after": 3600,
    }
    meta = {
        "provider": "Volcengine Ark",
        "model": model,
        "status": "preparing",
        "source_image_path": "scripts/ep01/images/ep01_sh01_九宫格分镜_gpt-image-2.png",
        "source_image_url": reference_image_url,
        "local_video_path": str(VIDEO_PATH.relative_to(ROOT)),
        "local_last_frame_path": str(LAST_FRAME_PATH.relative_to(ROOT)),
        "prompt": prompt,
        "payload": payload,
        "status_history": [],
    }

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    create_url = f"{base}/api/v3/contents/generations/tasks"
    existing_meta = {}
    if META_PATH.exists():
        try:
            existing_meta = json.loads(META_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing_meta = {}

    task_id = existing_meta.get("task_id")
    if task_id and not VIDEO_PATH.exists():
        meta.update(existing_meta)
        meta["status"] = existing_meta.get("status") or "resuming"
        write_meta(meta)
        print(f"{LOG_PREFIX} resuming task_id={task_id}", flush=True)
    else:
        write_meta(meta)
        response = requests.post(create_url, headers=headers, json=payload, timeout=120)
        meta["create_status_code"] = response.status_code
        if response.status_code >= 400:
            meta["status"] = "submit_failed"
            meta["create_response_text"] = response.text
            write_meta(meta)
            response.raise_for_status()

        create_data = response.json()
        task_id = (
            create_data.get("id")
            or create_data.get("task_id")
            or (create_data.get("data") or {}).get("id")
            or (create_data.get("data") or {}).get("task_id")
        )
        if not task_id:
            meta["status"] = "submit_failed"
            meta["create_response"] = create_data
            write_meta(meta)
            raise RuntimeError("Cannot find Seedance task id in create response")

        meta["task_id"] = task_id
        meta["status"] = "submitted"
        meta["create_response"] = create_data
        write_meta(meta)
        print(f"{LOG_PREFIX} task_id={task_id}", flush=True)

    query_url = f"{create_url}/{task_id}"
    deadline = time.time() + 3600
    while time.time() < deadline:
        query_response = requests.get(query_url, headers={"Authorization": f"Bearer {api_key}"}, timeout=120)
        meta["last_query_status_code"] = query_response.status_code
        if query_response.status_code >= 400:
            meta["status"] = "query_failed"
            meta["last_query_response_text"] = query_response.text
            write_meta(meta)
            query_response.raise_for_status()

        data = query_response.json()
        status = data.get("status") or (data.get("data") or {}).get("status")
        meta["status"] = status
        meta["status_history"].append({"time": int(time.time()), "status": status})
        write_meta(meta)
        print(f"{LOG_PREFIX} status={status}", flush=True)

        if status == "succeeded":
            content = data.get("content") or (data.get("data") or {}).get("content") or {}
            video_url = content.get("video_url")
            last_frame_url = content.get("last_frame_url")
            if not video_url:
                raise RuntimeError("Succeeded Seedance task missing video_url")
            meta["video_url"] = video_url
            meta["last_frame_url"] = last_frame_url
            meta["final_response"] = data
            write_meta(meta)
            download(video_url, VIDEO_PATH)
            if last_frame_url:
                download(last_frame_url, LAST_FRAME_PATH)
            meta["status"] = "downloaded"
            meta["video_bytes"] = VIDEO_PATH.stat().st_size
            if LAST_FRAME_PATH.exists():
                meta["last_frame_bytes"] = LAST_FRAME_PATH.stat().st_size
            write_meta(meta)
            return 0

        if status in {"failed", "expired", "cancelled"}:
            meta["final_response"] = data
            write_meta(meta)
            return 1

        time.sleep(15)

    meta["status"] = "timeout"
    write_meta(meta)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
