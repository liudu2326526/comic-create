#!/usr/bin/env python3
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BASE_SCRIPT = ROOT / "scripts/ep01/videos/run_ep01_sh02_seedance_direct_refs_story_prompt.py"
spec = importlib.util.spec_from_file_location("direct_refs_runner", BASE_SCRIPT)
runner = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(runner)


runner.OUT_DIR = runner.ROOT / "scripts/清冷师尊爬我墙/ep01/videos"
runner.META_PATH = runner.OUT_DIR / "ep01_sh03_seedance2_direct_refs_story_prompt.metadata.json"
runner.VIDEO_PATH = runner.OUT_DIR / "ep01_sh03_seedance2_direct_refs_story_prompt.mp4"
runner.LAST_FRAME_PATH = runner.OUT_DIR / "ep01_sh03_seedance2_direct_refs_story_prompt_last_frame.png"
runner.ASSET_RECORD_PATH = runner.ROOT / "volcengine-private-assets/records/qingleng-shizun-ep01_sh03_direct_refs_story_prompt.json"
runner.LOG_PREFIX = "[qingleng_ep01_sh03_direct_refs]"
runner.SHOT_ID = "qingleng_ep01_sh03"
runner.VIDEO_DURATION = 15
runner.ASSET_GROUP_NAME = "comic-create-qingleng-ep01-sh03-direct-refs"
runner.ASSET_GROUP_DESCRIPTION = "清冷师尊爬我墙 ep01_sh03 非九宫格路径，时子初和星澜参考图使用私域素材，寝殿与道具参考图使用公网 URL"
runner.ASSET_RECORD_USAGE = "清冷师尊爬我墙 ep01_sh03 非九宫格视频生成：时子初、星澜参考图入私域素材库，避免公网真人隐私拦截"

runner.REFERENCE_IMAGES = [
    {
        "label": "图片1",
        "role": "character_face",
        "path": runner.ROOT
        / "characters/清冷师尊爬我墙/时子初/images/时子初_寝殿惊醒_面部头像.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh03/01_时子初_寝殿惊醒_面部头像.png",
        "usage": "时子初（寝殿惊醒）的面部身份、屏息克制、隐忍不适和迅速判断的眼神",
    },
    {
        "label": "图片2",
        "role": "character_fullbody",
        "path": runner.ROOT
        / "characters/清冷师尊爬我墙/时子初/images/时子初_寝殿惊醒_9x16全身.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh03/02_时子初_寝殿惊醒_9x16全身.png",
        "usage": "时子初（寝殿惊醒）的寝殿服饰、身形比例、榻上起身和抓起衣裙动作",
    },
    {
        "label": "图片3",
        "role": "character_face",
        "path": runner.ROOT
        / "characters/清冷师尊爬我墙/星澜/images/星澜_寝殿里衣_面部头像.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh03/03_星澜_寝殿里衣_面部头像.png",
        "usage": "星澜（寝殿里衣）的沉睡侧脸、清冷眉眼和不能被惊醒的安静状态",
    },
    {
        "label": "图片4",
        "role": "character_fullbody",
        "path": runner.ROOT
        / "characters/清冷师尊爬我墙/星澜/images/星澜_寝殿里衣_9x16全身.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh03/04_星澜_寝殿里衣_9x16全身.png",
        "usage": "星澜（寝殿里衣）的寝殿里衣、身形比例、沉睡姿态和压在腰间的手臂",
    },
    {
        "label": "图片5",
        "role": "scene",
        "path": runner.ROOT
        / "scenes/清冷师尊爬我墙/星澜寝殿/images/星澜寝殿_横屏远景_场景图_gpt-image-2.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh03/05_星澜寝殿_横屏远景_场景图_gpt-image-2.png",
        "usage": "星澜寝殿的冷纱帐、床榻、清晨冷光和清冷寝殿空间",
    },
    {
        "label": "图片6",
        "role": "prop",
        "path": runner.ROOT
        / "props/清冷师尊爬我墙/环初铃/images/环初铃_1x1_道具图_gpt-image-2.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh03/06_环初铃_1x1_道具图_gpt-image-2.png",
        "usage": "环初铃在神识海中短暂浮现、铃身微光和作为翻盘筹码的视觉锚点",
    },
    {
        "label": "图片7",
        "role": "prop",
        "path": runner.ROOT
        / "props/清冷师尊爬我墙/断裂腰带/images/断裂腰带_1x1_道具图_gpt-image-2.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh03/07_断裂腰带_1x1_道具图_gpt-image-2.png",
        "usage": "断裂腰带落在寝殿地面，提醒时子初特殊时间点和逃离现场的急迫感",
    },
]


def build_prompt() -> str:
    return (
        "15秒，9:16竖版短剧视频，仙侠重生后的清晨寝殿中景，电影写实风格，压低的紧张节奏。"
        "参考图片1锁定时子初（寝殿惊醒）的脸：东方女性五官，屏息克制，隐忍不适，眼神快速恢复判断；"
        "参考图片2锁定时子初的寝殿服饰、身形比例、榻上起身和抓起衣裙动作；"
        "参考图片3和图片4锁定星澜（寝殿里衣）：沉睡侧脸、清冷眉眼、寝殿里衣、沉睡姿态、压在腰间的手臂；"
        "参考图片5锁定星澜寝殿的冷纱帐、床榻、清晨冷光和清冷空间；"
        "参考图片6锁定环初铃：神识海中短暂浮现、铃身泛出微光；参考图片7锁定断裂腰带：落在寝殿地面，提醒特殊时间点。"
        "0-4秒：固定中景，时子初（寝殿惊醒）屏住呼吸，指尖一点点托起星澜（寝殿里衣）压在自己腰间的手臂，"
        "动作极慢，生怕惊醒他；星澜仍在睡梦中，床榻、冷纱帐和清晨冷光保持安静压迫，音效只有克制的屏息声和轻微衣料摩擦；"
        "4-9秒：画面短暂转入神识海，环初铃在幽暗神识空间中浮现，铃身泛出微光，时子初确认东西还在后眼神一沉，"
        "迅速判断自己终于有了这一世的第一枚翻盘筹码；神识画面不要像现代屏幕，要像修真灵识内景；"
        "9-15秒：镜头回到寝殿中景，时子初坐起时身体发软，险些跌回榻上，她强忍不适稳住身体，"
        "余光扫到地上的断裂腰带，脸颊微热又立刻清醒，抓起衣裙准备逃离现场。旁白以低沉清晰的短剧叙述声说："
        "\"环初铃还在，她手里终于有了这一世的第一枚筹码。\""
        "全片保持同一时子初身份、同一星澜身份、同一星澜寝殿空间，动作要克制隐忍，不要夸张；"
        "重点是慢慢挪开手臂、神识海环初铃、断裂腰带、强忍不适起身逃离。"
        "不要切成九宫格，不要分格边框，不要文字编号，不要字幕、LOGO、水印。"
        "音效包含屏息声、衣裙被拾起，背景音乐为压低的紧张节奏，音量不要盖过旁白。"
    )


runner.build_prompt = build_prompt


if __name__ == "__main__":
    raise SystemExit(runner.main())
