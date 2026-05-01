#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen


DEFAULT_USER_AGENT = "curl/8.7.1"


def clean_base_url(value: str) -> str:
    base = (value or "https://api.apimart.ai").rstrip("/")
    if base.endswith("/v1"):
        return base[:-3]
    return base


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def request_json(
    method: str,
    url: str,
    api_key: str,
    payload: dict | None = None,
    timeout: int = 180,
    user_agent: str = DEFAULT_USER_AGENT,
) -> dict:
    data = None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": user_agent,
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def download(url: str, output: Path, timeout: int = 120, user_agent: str = DEFAULT_USER_AGENT) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": user_agent})
    with urlopen(request, timeout=timeout) as response:
        output.write_bytes(response.read())


def extract_task_id(response: dict) -> str:
    data = response.get("data") or []
    if not data:
        raise RuntimeError(f"Missing data in submit response: {response}")
    task_id = data[0].get("task_id") or data[0].get("taskId")
    if not task_id:
        raise RuntimeError(f"Missing task_id in submit response: {response}")
    return task_id


def extract_image_url(task_data: dict) -> str:
    images = ((task_data.get("result") or {}).get("images") or [])
    for image in images:
        value = image.get("url") if isinstance(image, dict) else None
        if isinstance(value, list) and value:
            return value[0]
        if isinstance(value, str) and value:
            return value
    raise RuntimeError(f"Completed task has no image URL: {task_data}")


def main() -> int:
    load_env_file(Path.cwd() / ".env")

    parser = argparse.ArgumentParser(description="Submit and poll an APIMart GPT-Image-2 image generation task.")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--model", default=os.getenv("APIMART_IMAGE_MODEL", "gpt-image-2"))
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--quality", default="low")
    parser.add_argument("--output-format", default="png")
    parser.add_argument("--base-url", default=os.getenv("APIMART_BASE_URL") or os.getenv("OPENAI_IMAGE_BASE_URL") or "https://api.apimart.ai")
    parser.add_argument("--api-key", default=os.getenv("APIMART_API_KEY") or os.getenv("OPENAI_IMAGE_API_KEY"))
    parser.add_argument("--interval", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--user-agent", default=os.getenv("APIMART_USER_AGENT", DEFAULT_USER_AGENT))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.api_key:
        print("Missing APIMART_API_KEY or OPENAI_IMAGE_API_KEY", file=sys.stderr)
        return 2

    base_url = clean_base_url(args.base_url)
    payload = {
        "model": args.model,
        "prompt": args.prompt,
        "n": 1,
        "size": args.size,
        "quality": args.quality,
        "output_format": args.output_format,
    }

    submit = request_json(
        "POST",
        f"{base_url}/v1/images/generations",
        args.api_key,
        payload,
        timeout=args.timeout,
        user_agent=args.user_agent,
    )
    task_id = extract_task_id(submit)
    print(f"submitted task_id={task_id}")

    deadline = time.time() + args.timeout
    while time.time() < deadline:
        status_response = request_json(
            "GET",
            f"{base_url}/v1/tasks/{task_id}",
            args.api_key,
            timeout=args.timeout,
            user_agent=args.user_agent,
        )
        task_data = status_response.get("data") or {}
        status = str(task_data.get("status") or "").lower()
        progress = task_data.get("progress")
        print(f"status={status} progress={progress}")

        if status == "completed":
            image_url = extract_image_url(task_data)
            print(f"image_url={image_url}")
            if args.output:
                download(image_url, args.output, user_agent=args.user_agent)
                print(f"downloaded={args.output}")
            return 0

        if status in {"failed", "cancelled"}:
            print(json.dumps(task_data.get("error") or task_data, ensure_ascii=False), file=sys.stderr)
            return 1

        time.sleep(args.interval)

    print(f"Timed out waiting for {task_id}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
