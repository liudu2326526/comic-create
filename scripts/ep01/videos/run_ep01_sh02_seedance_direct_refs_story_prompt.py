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
META_PATH = OUT_DIR / "ep01_sh02_seedance2_direct_refs_story_prompt.metadata.json"
VIDEO_PATH = OUT_DIR / "ep01_sh02_seedance2_direct_refs_story_prompt.mp4"
LAST_FRAME_PATH = OUT_DIR / "ep01_sh02_seedance2_direct_refs_story_prompt_last_frame.png"
ASSET_RECORD_PATH = ROOT / "volcengine-private-assets/records/ep01_sh02_direct_refs_story_prompt.json"
ASSET_API_HOST = "ark.cn-beijing.volcengineapi.com"
ASSET_API_VERSION = "2024-01-01"
ASSET_API_REGION = "cn-beijing"
ASSET_API_SERVICE = "ark"
LOG_PREFIX = "[ep01_sh02_direct_refs]"
SHOT_ID = "ep01_sh02"
VIDEO_DURATION = 6
ASSET_GROUP_NAME = "comic-create-ep01-sh02-direct-refs"
ASSET_GROUP_DESCRIPTION = "ep01_sh02 非九宫格路径，人物参考图使用私域素材，场景图使用公网 URL"
ASSET_RECORD_USAGE = "ep01_sh02 非九宫格视频生成：人物参考图入私域素材库，避免公网真人隐私拦截"

REFERENCE_IMAGES = [
    {
        "label": "图片1",
        "role": "character_face",
        "path": ROOT
        / "characters/修罗女帝之绝世无双/皇城之主/images/皇城之主_皇座衰老态_面部头像.png",
        "object_key": "comic-create/seedance-refs/ep01_sh02/01_皇城之主_皇座衰老态_面部头像.png",
        "usage": "皇城之主（皇座衰老态）的苍老面容、黑发夹杂银丝、苍白脸色、执拗贪婪眼神",
    },
    {
        "label": "图片2",
        "role": "character_fullbody",
        "path": ROOT
        / "characters/修罗女帝之绝世无双/皇城之主/images/皇城之主_皇座衰老态_9x16全身.png",
        "object_key": "comic-create/seedance-refs/ep01_sh02/02_皇城之主_皇座衰老态_9x16全身.png",
        "usage": "暗金皇袍、玉带、黑金靴、帝王冠冕和高位统治者姿态",
    },
    {
        "label": "图片3",
        "role": "scene",
        "path": ROOT / "scenes/修罗女帝之绝世无双/皇城/images/皇城_横屏远景_场景图_gpt-image-2.png",
        "object_key": "comic-create/seedance-refs/ep01_sh02/03_皇城_横屏远景_场景图_gpt-image-2.png",
        "usage": "皇宫大殿的暗金王座、长阶、金色殿灯、高墙压迫和昏沉衰败灵气",
    },
]
REFERENCE_VIDEOS = []


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


def preserve_existing_outputs() -> dict:
    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    preserved = {}
    for label, path in {
        "video": VIDEO_PATH,
        "last_frame": LAST_FRAME_PATH,
        "metadata": META_PATH,
    }.items():
        if not path.exists():
            continue
        backup_path = path.with_name(f"{path.stem}_backup_{timestamp}{path.suffix}")
        shutil.copy2(path, backup_path)
        preserved[label] = str(backup_path.relative_to(ROOT))
    return preserved


def write_asset_record(record: dict) -> None:
    ASSET_RECORD_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSET_RECORD_PATH.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def upload_reference_images() -> list[dict]:
    endpoint = os.environ["OBS_ENDPOINT"]
    bucket = os.environ["OBS_BUCKET"]
    public_base_url = os.environ["OBS_PUBLIC_BASE_URL"].rstrip("/")
    client = ObsClient(
        access_key_id=os.environ["OBS_AK"],
        secret_access_key=os.environ["OBS_SK"],
        server=endpoint,
    )

    uploaded = []
    for item in REFERENCE_IMAGES:
        if not item["path"].exists():
            raise FileNotFoundError(item["path"])
        response = client.putFile(
            bucket,
            item["object_key"],
            str(item["path"]),
            headers={"Content-Type": "image/png"},
        )
        status = getattr(response, "status", None)
        if status is None or int(status) >= 300:
            error_code = getattr(response, "errorCode", None)
            error_message = getattr(response, "errorMessage", None)
            raise RuntimeError(
                f"OBS upload failed status={status} code={error_code} message={error_message}"
            )

        url = f"{public_base_url}/{item['object_key']}"
        head = requests.head(url, timeout=60)
        if head.status_code >= 400:
            raise RuntimeError(f"Uploaded reference image is not publicly readable: {head.status_code} {url}")
        uploaded.append(
            {
                "label": item["label"],
                "role": item["role"],
                "local_path": str(item["path"].relative_to(ROOT)),
                "object_key": item["object_key"],
                "url": url,
                "usage": item["usage"],
            }
        )
    return uploaded


def upload_reference_videos() -> list[dict]:
    endpoint = os.environ["OBS_ENDPOINT"]
    bucket = os.environ["OBS_BUCKET"]
    public_base_url = os.environ["OBS_PUBLIC_BASE_URL"].rstrip("/")
    client = ObsClient(
        access_key_id=os.environ["OBS_AK"],
        secret_access_key=os.environ["OBS_SK"],
        server=endpoint,
    )

    uploaded = []
    for item in REFERENCE_VIDEOS:
        if not item["path"].exists():
            raise FileNotFoundError(item["path"])
        response = client.putFile(
            bucket,
            item["object_key"],
            str(item["path"]),
            headers={"Content-Type": item.get("content_type", "video/mp4")},
        )
        status = getattr(response, "status", None)
        if status is None or int(status) >= 300:
            error_code = getattr(response, "errorCode", None)
            error_message = getattr(response, "errorMessage", None)
            raise RuntimeError(
                f"OBS video upload failed status={status} code={error_code} message={error_message}"
            )

        url = f"{public_base_url}/{item['object_key']}"
        head = requests.head(url, timeout=60)
        if head.status_code >= 400:
            raise RuntimeError(f"Uploaded reference video is not publicly readable: {head.status_code} {url}")
        uploaded.append(
            {
                "label": item["label"],
                "role": item.get("role", "reference_video"),
                "local_path": str(item["path"].relative_to(ROOT)),
                "object_key": item["object_key"],
                "url": url,
                "usage": item["usage"],
            }
        )
    return uploaded


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


def ensure_private_assets(references: list[dict]) -> tuple[list[dict], dict]:
    project_name = os.getenv("ARK_ASSET_PROJECT_NAME", "default")
    portrait_refs = [item for item in references if item["role"].startswith("character_")]
    scene_refs = [item for item in references if not item["role"].startswith("character_")]
    existing = {}
    if ASSET_RECORD_PATH.exists():
        try:
            existing = json.loads(ASSET_RECORD_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}

    existing_assets = existing.get("assets") or {}
    reusable_assets = {}
    for item in portrait_refs:
        asset_id = (existing_assets.get(item["label"]) or {}).get("asset_id")
        if not asset_id:
            break
        status_response = get_asset(asset_id)
        status = extract_asset_status(status_response)
        if status != "Active":
            break
        reusable_assets[item["label"]] = {
            **existing_assets[item["label"]],
            "status": status,
            "asset_uri": f"asset://{asset_id}",
            "last_get_asset_response": status_response,
            "last_checked_at": int(time.time()),
        }

    if len(reusable_assets) == len(portrait_refs):
        existing["assets"] = reusable_assets
        existing["last_checked_at"] = int(time.time())
        write_asset_record(existing)
        mapped = []
        for item in references:
            if item["label"] in reusable_assets:
                mapped.append({**item, "video_reference_url": reusable_assets[item["label"]]["asset_uri"]})
            else:
                mapped.append({**item, "video_reference_url": item["url"]})
        return mapped, existing

    group_response = signed_asset_api(
        "CreateAssetGroup",
        {
            "Name": ASSET_GROUP_NAME,
            "Description": ASSET_GROUP_DESCRIPTION,
            "GroupType": "AIGC",
            "ProjectName": project_name,
        },
    )
    group_id = nested(group_response, "Result", "Id") or nested(group_response, "Id")
    if not group_id:
        raise RuntimeError(f"Cannot find group id in CreateAssetGroup response: {group_response}")

    record = {
        "provider": "Volcengine Ark",
        "asset_library": "private_virtual_portrait_assets",
        "group_id": group_id,
        "project_name": project_name,
        "usage": ASSET_RECORD_USAGE,
        "create_asset_group_response": group_response,
        "assets": {},
        "status_history": [],
        "created_at": int(time.time()),
    }
    for item in portrait_refs:
        create_asset_response = signed_asset_api(
            "CreateAsset",
            {
                "GroupId": group_id,
                "URL": item["url"],
                "AssetType": "Image",
                "Name": f"{SHOT_ID}_direct_refs_{item['label']}_{item['role']}",
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
        record["assets"][item["label"]] = {
            "role": item["role"],
            "asset_id": asset_id,
            "asset_uri": f"asset://{asset_id}",
            "status": "Processing",
            "source_image_url": item["url"],
            "source_image_path": item["local_path"],
            "create_asset_response": create_asset_response,
        }
    write_asset_record(record)

    deadline = time.time() + 1800
    while time.time() < deadline:
        active_count = 0
        for label, asset in record["assets"].items():
            status_response = get_asset(asset["asset_id"])
            status = extract_asset_status(status_response)
            asset["status"] = status
            asset["last_checked_at"] = int(time.time())
            asset["last_get_asset_response"] = status_response
            if status == "Active":
                active_count += 1
            if status == "Failed":
                write_asset_record(record)
                raise RuntimeError(f"Asset processing failed for {label}: {json.dumps(status_response, ensure_ascii=False)}")
        record["last_checked_at"] = int(time.time())
        record["status_history"].append(
            {
                "time": int(time.time()),
                "statuses": {label: asset["status"] for label, asset in record["assets"].items()},
            }
        )
        write_asset_record(record)
        print(f"{LOG_PREFIX} asset_statuses={record['status_history'][-1]['statuses']}", flush=True)
        if active_count == len(record["assets"]):
            mapped = []
            for item in references:
                asset = record["assets"].get(item["label"])
                mapped.append({**item, "video_reference_url": asset["asset_uri"] if asset else item["url"]})
            return mapped, record
        time.sleep(15)
    raise TimeoutError("Asset processing timeout for direct reference portrait images")


def build_prompt() -> str:
    return (
        "6秒，9:16竖版短剧视频，仙侠旧世界，电影写实风格，暗金皇权压迫感。"
        "参考图片1锁定皇城之主（皇座衰老态）的脸：中老年男性，黑发夹杂银丝，脸色苍白，"
        "眼神执拗贪婪，久居高位但寿元将尽；参考图片2锁定他的暗金皇袍、玉带、黑金靴、"
        "帝王冠冕和端坐高位的统治者姿态；参考图片3锁定皇城大殿：暗金王座、长阶、金色殿灯、"
        "高墙压迫、昏沉衰败灵气。"
        "0-2秒：皇宫大殿中景建立，暗金王座高悬在长阶尽头，金色殿灯昏沉，阴影压低空间，"
        "镜头从殿内中轴线缓慢Dolly In推进到王座区域，皇城之主（皇座衰老态）端坐高位，"
        "暗金皇袍沉重垂落，空气中有衰败灵气；"
        "2-4秒：镜头继续推近到王座中景和手部近景，他身体微微前倾，手指死死攥紧扶手，"
        "指节发白，衣袖与扶手轻微摩擦，冠冕在烛火下反光，整个人被高墙和王座压住；"
        "4-6秒：镜头压近到半身和面部，金色烛火把苍老苍白的脸切成明暗两半，烛火忽然爆裂，"
        "金色火星飞散，他抬眼望向殿外禁地方向，目光压抑而贪婪，嘴唇微动，以中老年男性低沉威严、"
        "压抑贪婪的声音说：\"朕还不能死。\"最后定格在半明半暗的脸和攥紧扶手的手上。"
        "全片保持同一人物、同一服装、同一王座、同一皇宫大殿空间，镜头语言是连续缓慢推进，"
        "不要切成九宫格，不要分格边框，不要文字编号，不要旁白，不要字幕、LOGO、水印。"
        "音效包含低音量烛火爆裂、衣袖摩擦，背景音乐为暗金色皇权压迫音乐，不要盖过对白。"
    )


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

    uploaded_references = upload_reference_images()
    uploaded_videos = upload_reference_videos()
    references, asset_record = ensure_private_assets(uploaded_references)
    prompt = build_prompt()
    payload = {
        "model": model,
        "content": [{"type": "text", "text": prompt}]
        + [
            {
                "type": "image_url",
                "role": "reference_image",
                "image_url": {"url": item["video_reference_url"]},
            }
            for item in references
        ]
        + [
            {
                "type": "video_url",
                "role": "reference_video",
                "video_url": {"url": item["url"]},
            }
            for item in uploaded_videos
        ],
        "duration": VIDEO_DURATION,
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
        "mode": "direct_reference_images_with_storyboard_prompt",
        "reference_images": references,
        "reference_videos": uploaded_videos,
        "asset_record_path": str(ASSET_RECORD_PATH.relative_to(ROOT)),
        "asset_record": asset_record,
        "local_video_path": str(VIDEO_PATH.relative_to(ROOT)),
        "local_last_frame_path": str(LAST_FRAME_PATH.relative_to(ROOT)),
        "prompt": prompt,
        "payload": payload,
        "status_history": [],
    }
    preserved_outputs = preserve_existing_outputs()
    if preserved_outputs:
        meta["preserved_existing_outputs_before_generation"] = preserved_outputs

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    create_url = f"{base}/api/v3/contents/generations/tasks"
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
