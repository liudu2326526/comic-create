#!/usr/bin/env python3
import json
import os
import shutil
import time
import datetime
import hashlib
import hmac
from pathlib import Path
from urllib.parse import quote

import requests
from obs import ObsClient


ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = ROOT / ".env"
OUT_DIR = ROOT / "scripts/ep01/videos"
SOURCE_IMAGE_PATH = ROOT / "scripts/ep01/images/ep01_sh02_九宫格分镜_gpt-image-2.png"
META_PATH = OUT_DIR / "ep01_sh02_seedance2_from_9x16_nine_grid.metadata.json"
VIDEO_PATH = OUT_DIR / "ep01_sh02_seedance2_from_9x16_nine_grid.mp4"
LAST_FRAME_PATH = OUT_DIR / "ep01_sh02_seedance2_from_9x16_nine_grid_last_frame.png"
OBS_OBJECT_KEY = "comic-create/scripts/ep01/images/ep01_sh02_nine_grid_storyboard_9x16_gpt-image-2.png"
ASSET_RECORD_NAME = "ep01_sh02_nine_grid_storyboard_9x16_gpt-image-2"
ASSET_ORIGINAL_PATH = ROOT / "volcengine-private-assets/originals/ep01_sh02_nine_grid_storyboard_9x16_gpt-image-2.png"
ASSET_RECORD_PATH = ROOT / "volcengine-private-assets/records/ep01_sh02_nine_grid_storyboard_9x16_gpt-image-2.json"
ASSET_API_HOST = "ark.cn-beijing.volcengineapi.com"
ASSET_API_VERSION = "2024-01-01"
ASSET_API_REGION = "cn-beijing"
ASSET_API_SERVICE = "ark"
LOG_PREFIX = "[ep01_sh02_seedance]"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def write_meta(meta: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    META_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_asset_record(record: dict) -> None:
    ASSET_RECORD_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSET_RECORD_PATH.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def archive_asset_original() -> None:
    ASSET_ORIGINAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not ASSET_ORIGINAL_PATH.exists():
        shutil.copy2(SOURCE_IMAGE_PATH, ASSET_ORIGINAL_PATH)


def upload_reference_image() -> str:
    if not SOURCE_IMAGE_PATH.exists():
        raise FileNotFoundError(SOURCE_IMAGE_PATH)

    endpoint = os.environ["OBS_ENDPOINT"]
    bucket = os.environ["OBS_BUCKET"]
    public_base_url = os.environ["OBS_PUBLIC_BASE_URL"].rstrip("/")
    client = ObsClient(
        access_key_id=os.environ["OBS_AK"],
        secret_access_key=os.environ["OBS_SK"],
        server=endpoint,
    )
    response = client.putFile(
        bucket,
        OBS_OBJECT_KEY,
        str(SOURCE_IMAGE_PATH),
        headers={"Content-Type": "image/png"},
    )
    status = getattr(response, "status", None)
    if status is None or int(status) >= 300:
        error_code = getattr(response, "errorCode", None)
        error_message = getattr(response, "errorMessage", None)
        raise RuntimeError(f"OBS upload failed status={status} code={error_code} message={error_message}")

    url = f"{public_base_url}/{OBS_OBJECT_KEY}"
    head = requests.head(url, timeout=60)
    if head.status_code >= 400:
        raise RuntimeError(f"Uploaded reference image is not publicly readable: {head.status_code} {url}")
    return url


def norm_query(params: dict) -> str:
    query = ""
    for key in sorted(params.keys()):
        if isinstance(params[key], list):
            for value in params[key]:
                query += quote(key, safe="-_.~") + "=" + quote(str(value), safe="-_.~") + "&"
        else:
            query += quote(key, safe="-_.~") + "=" + quote(str(params[key]), safe="-_.~") + "&"
    return query[:-1].replace("+", "%20")


def hmac_sha256(key: bytes, content: str) -> bytes:
    return hmac.new(key, content.encode("utf-8"), hashlib.sha256).digest()


def hash_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def signed_asset_api(action: str, body: dict) -> dict:
    ak = os.environ["VOLC_ACCESS_KEY_ID"]
    sk = os.environ["VOLC_SECRET_ACCESS_KEY"]
    body_json = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    now = datetime.datetime.utcnow()
    x_date = now.strftime("%Y%m%dT%H%M%SZ")
    short_x_date = x_date[:8]
    query = {"Action": action, "Version": ASSET_API_VERSION}
    content_type = "application/json"
    body_hash = hash_sha256(body_json)
    signed_headers = "content-type;host;x-content-sha256;x-date"
    canonical_request = "\n".join(
        [
            "POST",
            "/",
            norm_query(query),
            "\n".join(
                [
                    f"content-type:{content_type}",
                    f"host:{ASSET_API_HOST}",
                    f"x-content-sha256:{body_hash}",
                    f"x-date:{x_date}",
                ]
            ),
            "",
            signed_headers,
            body_hash,
        ]
    )
    credential_scope = "/".join([short_x_date, ASSET_API_REGION, ASSET_API_SERVICE, "request"])
    string_to_sign = "\n".join(
        ["HMAC-SHA256", x_date, credential_scope, hash_sha256(canonical_request)]
    )
    k_date = hmac_sha256(sk.encode("utf-8"), short_x_date)
    k_region = hmac_sha256(k_date, ASSET_API_REGION)
    k_service = hmac_sha256(k_region, ASSET_API_SERVICE)
    k_signing = hmac_sha256(k_service, "request")
    signature = hmac_sha256(k_signing, string_to_sign).hex()
    headers = {
        "Host": ASSET_API_HOST,
        "X-Content-Sha256": body_hash,
        "X-Date": x_date,
        "Content-Type": content_type,
        "Authorization": (
            "HMAC-SHA256 Credential={}, SignedHeaders={}, Signature={}".format(
                f"{ak}/{credential_scope}",
                signed_headers,
                signature,
            )
        ),
    }
    response = requests.post(
        f"https://{ASSET_API_HOST}/",
        params=query,
        headers=headers,
        data=body_json.encode("utf-8"),
        timeout=120,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"{action} failed HTTP {response.status_code}: {response.text}")
    return response.json()


def nested(data: dict, *keys: str) -> str:
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return ""
        current = current.get(key)
        if current is None:
            return ""
    return str(current) if current is not None else ""


def get_asset(asset_id: str) -> dict:
    return signed_asset_api("GetAsset", {"Id": asset_id})


def extract_asset_status(response: dict) -> str:
    return nested(response, "Result", "Status") or nested(response, "Status")


def ensure_private_asset(reference_image_url: str) -> tuple[str, dict]:
    archive_asset_original()
    project_name = os.getenv("ARK_ASSET_PROJECT_NAME", "default")
    existing = {}
    if ASSET_RECORD_PATH.exists():
        try:
            existing = json.loads(ASSET_RECORD_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    existing_asset_id = existing.get("asset_id")
    if existing_asset_id:
        status_response = get_asset(existing_asset_id)
        status = extract_asset_status(status_response)
        if status == "Active":
            existing["status"] = status
            existing["asset_uri"] = f"asset://{existing_asset_id}"
            existing["last_checked_at"] = int(time.time())
            existing["last_get_asset_response"] = status_response
            write_asset_record(existing)
            return existing["asset_uri"], existing

    group_response = signed_asset_api(
        "CreateAssetGroup",
        {
            "Name": "comic-create-ep01-sh02-nine-grid",
            "Description": "ep01_sh02 九宫格分镜参考图，Seedance 2.0 视频生成私域素材",
            "GroupType": "AIGC",
            "ProjectName": project_name,
        },
    )
    group_id = nested(group_response, "Result", "Id") or nested(group_response, "Id")
    if not group_id:
        raise RuntimeError(f"Cannot find group id in CreateAssetGroup response: {group_response}")

    create_asset_response = signed_asset_api(
        "CreateAsset",
        {
            "GroupId": group_id,
            "URL": reference_image_url,
            "AssetType": "Image",
            "Name": ASSET_RECORD_NAME,
            "ProjectName": project_name,
        },
    )
    asset_id = (
        nested(create_asset_response, "Result", "Id")
        or nested(create_asset_response, "Result", "AssetId")
        or nested(create_asset_response, "Id")
        or nested(create_asset_response, "AssetId")
    )
    if not asset_id:
        raise RuntimeError(f"Cannot find asset id in CreateAsset response: {create_asset_response}")

    record = {
        "provider": "Volcengine Ark",
        "asset_library": "private_virtual_portrait_assets",
        "asset_id": asset_id,
        "asset_uri": f"asset://{asset_id}",
        "group_id": group_id,
        "project_name": project_name,
        "status": "Processing",
        "asset_type": "Image",
        "usage": "ep01_sh02 Seedance 2.0 视频生成参考图，来源为 9:16 九宫格连续分镜图",
        "source_image_path": str(SOURCE_IMAGE_PATH.relative_to(ROOT)),
        "archived_original_path": str(ASSET_ORIGINAL_PATH.relative_to(ROOT)),
        "source_image_url": reference_image_url,
        "reuse_note": "后续同一镜头或同一九宫格参考生成视频时，优先复用 asset_uri，不再重复入库。",
        "create_asset_group_response": group_response,
        "create_asset_response": create_asset_response,
        "created_at": int(time.time()),
        "status_history": [],
    }
    write_asset_record(record)

    deadline = time.time() + 1800
    while time.time() < deadline:
        status_response = get_asset(asset_id)
        status = extract_asset_status(status_response)
        record["status"] = status
        record["last_checked_at"] = int(time.time())
        record["last_get_asset_response"] = status_response
        record["status_history"].append({"time": int(time.time()), "status": status})
        write_asset_record(record)
        print(f"{LOG_PREFIX} asset_status={status}", flush=True)
        if status == "Active":
            return record["asset_uri"], record
        if status == "Failed":
            raise RuntimeError(f"Asset processing failed: {json.dumps(status_response, ensure_ascii=False)}")
        time.sleep(15)
    raise TimeoutError(f"Asset processing timeout: {asset_id}")


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
    reference_image_url = upload_reference_image()
    asset_uri, asset_record = ensure_private_asset(reference_image_url)
    prompt = (
        "图片1是一张9:16竖版3x3九宫格连续分镜参考图，请把九个格子理解为同一段视频从左到右、从上到下推进的连续关键帧，"
        "不要保留九宫格边框、分格、拼贴布局或任何文字编号。生成单段9:16竖版电影写实视频："
        "镜头从皇宫大殿远景缓慢推进，暗金王座高悬在长阶尽头，两侧金色殿灯昏沉，高墙压低空间，空气中弥漫衰败灵气；"
        "随着镜头推进，皇城之主（皇座衰老态）端坐在王座上，暗金皇袍沉重垂落，帝王冠冕在昏黄烛火下反光；"
        "他身体微微前倾，手指死死攥紧王座扶手，指节发白，衣袖轻微摩擦，袖口暗金纹路与扶手阴影形成压迫感；"
        "镜头继续压近到半身和面部，他苍老苍白的脸被金色烛火切成明暗两半，黑发夹杂银丝，眼底是不肯死去的执念；"
        "他抬眼望向殿外禁地方向，目光压抑而贪婪，烛火忽然爆裂，金色火星在阴影中飞散；"
        "最后推近到王座与面部定格，他嘴唇微动，压低声音说“朕还不能死”，苍老脸庞半明半暗，手仍攥紧扶手，"
        "整个皇宫大殿充满寿元将尽的皇权压迫感。"
        "保持参考图中的皇城之主身份、暗金皇袍、帝王冠冕、暗金王座、长阶、金色殿灯和黑金高对比光影，"
        "镜头运动为缓慢推进，时间和空间连续，不要改变人物脸、服装、王座和大殿核心关系。"
        "如生成声音，请包含低沉皇权压迫音乐、烛火爆裂声、衣袖摩擦声和一句压抑贪婪的男性低声对白“朕还不能死”，"
        "不要旁白，不要字幕、LOGO、水印，不要九宫格边框。"
    )
    payload = {
        "model": model,
        "content": [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "role": "reference_image",
                "image_url": {"url": asset_uri},
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
        "source_image_path": str(SOURCE_IMAGE_PATH.relative_to(ROOT)),
        "source_image_url": reference_image_url,
        "source_asset_uri": asset_uri,
        "source_asset_record_path": str(ASSET_RECORD_PATH.relative_to(ROOT)),
        "source_asset_record": asset_record,
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
