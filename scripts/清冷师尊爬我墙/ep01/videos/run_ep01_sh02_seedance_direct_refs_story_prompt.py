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
runner.META_PATH = runner.OUT_DIR / "ep01_sh02_seedance2_direct_refs_story_prompt.metadata.json"
runner.VIDEO_PATH = runner.OUT_DIR / "ep01_sh02_seedance2_direct_refs_story_prompt.mp4"
runner.LAST_FRAME_PATH = runner.OUT_DIR / "ep01_sh02_seedance2_direct_refs_story_prompt_last_frame.png"
runner.ASSET_RECORD_PATH = runner.ROOT / "volcengine-private-assets/records/qingleng-shizun-ep01_sh02_direct_refs_story_prompt.json"
runner.LOG_PREFIX = "[qingleng_ep01_sh02_direct_refs]"
runner.SHOT_ID = "qingleng_ep01_sh02"
runner.VIDEO_DURATION = 15
runner.ASSET_GROUP_NAME = "comic-create-qingleng-ep01-sh02-direct-refs"
runner.ASSET_GROUP_DESCRIPTION = "清冷师尊爬我墙 ep01_sh02 非九宫格路径，时子初和星澜参考图使用私域素材，寝殿和薄被参考图使用公网 URL"
runner.ASSET_RECORD_USAGE = "清冷师尊爬我墙 ep01_sh02 非九宫格视频生成：时子初、星澜参考图入私域素材库，避免公网真人隐私拦截"

runner.REFERENCE_IMAGES = [
    {
        "label": "图片1",
        "role": "character_face",
        "path": runner.ROOT
        / "characters/清冷师尊爬我墙/时子初/images/时子初_寝殿惊醒_面部头像.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh02/01_时子初_寝殿惊醒_面部头像.png",
        "usage": "时子初（寝殿惊醒）的面部身份、错愕眼神、羞窘表情和重生后刚回神的冷光",
    },
    {
        "label": "图片2",
        "role": "character_fullbody",
        "path": runner.ROOT
        / "characters/清冷师尊爬我墙/时子初/images/时子初_寝殿惊醒_9x16全身.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh02/02_时子初_寝殿惊醒_9x16全身.png",
        "usage": "时子初（寝殿惊醒）的寝殿服饰、身形比例、榻上僵住和回头动作",
    },
    {
        "label": "图片3",
        "role": "character_face",
        "path": runner.ROOT
        / "characters/清冷师尊爬我墙/星澜/images/星澜_寝殿里衣_面部头像.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh02/03_星澜_寝殿里衣_面部头像.png",
        "usage": "星澜（寝殿里衣）的沉睡侧脸、冷漠眉眼和睡梦中少了锋利的状态",
    },
    {
        "label": "图片4",
        "role": "character_fullbody",
        "path": runner.ROOT
        / "characters/清冷师尊爬我墙/星澜/images/星澜_寝殿里衣_9x16全身.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh02/04_星澜_寝殿里衣_9x16全身.png",
        "usage": "星澜（寝殿里衣）的寝殿里衣、身形比例、沉睡姿态和手臂圈住腰身动作参考",
    },
    {
        "label": "图片5",
        "role": "scene",
        "path": runner.ROOT
        / "scenes/清冷师尊爬我墙/星澜寝殿/images/星澜寝殿_横屏远景_场景图_gpt-image-2.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh02/05_星澜寝殿_横屏远景_场景图_gpt-image-2.png",
        "usage": "星澜寝殿的冷纱帐、床榻、清晨冷光、清冷寝殿空间",
    },
    {
        "label": "图片6",
        "role": "prop",
        "path": runner.ROOT
        / "props/清冷师尊爬我墙/冰蚕丝薄被/images/冰蚕丝薄被_1x1_道具图_gpt-image-2.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh02/06_冰蚕丝薄被_1x1_道具图_gpt-image-2.png",
        "usage": "冰蚕丝薄被的冷白纹理、半掩在床榻上的质感和暴露重生节点的视觉细节",
    },
]
runner.REFERENCE_VIDEOS = [
    {
        "label": "视频1",
        "role": "reference_video",
        "path": runner.ROOT
        / "scripts/清冷师尊爬我墙/ep01/videos/ep01_sh01_seedance2_direct_refs_story_prompt_v2_with_xinglan_arm.mp4",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh02/video1_ep01_sh01_v2_with_xinglan_arm.mp4",
        "content_type": "video/mp4",
        "usage": "参考 sh01 v2 的床榻空间、时子初刚醒后的错愕状态、星澜睡梦中揽回她的连续动作和镜头衔接节奏",
    }
]


def build_prompt() -> str:
    return (
        "15秒，9:16竖版短剧视频，仙侠重生后的清晨寝殿近景，电影写实风格，暧昧中带紧张。"
        "参考图片1锁定时子初（寝殿惊醒）的脸：东方女性五官，眼底从错愕到尴尬惊慌，"
        "同时残留刚刚重生后的冷光；参考图片2锁定时子初的寝殿服饰、身形比例和榻上僵住姿态；"
        "参考图片3和图片4锁定星澜（寝殿里衣）：沉睡侧脸、冷漠眉眼、寝殿里衣、清冷师尊气质，"
        "睡梦中手臂圈住时子初腰身；参考图片5锁定星澜寝殿：冷纱帐、床榻、清晨冷光、清冷空间；"
        "参考图片6锁定冰蚕丝薄被：冷白纹理、半掩在床榻上、薄被只盖到腰间。"
        "参考视频1作为上一镜 sh01 的直接延伸：延续视频1中时子初被星澜无意识揽回怀中的床榻关系、"
        "清晨低光寝殿氛围、两人相对位置和暧昧但克制的节奏；本镜头要像从视频1尾部自然接着拍到 sh02，"
        "不要重置场景，不要改变人物脸、服装、床榻位置和镜头情绪。"
        "0-4秒：镜头从冰蚕丝薄被的冷白纹理近景开始，缓慢推入，薄被半掩在床榻上，只盖到腰间，"
        "清晨冷光透过纱帐落在床榻边缘，画面安静但有危险的暧昧感，清晨风铃轻响；"
        "4-9秒：镜头拉开到近景，时子初（寝殿惊醒）僵在星澜（寝殿里衣）怀中，"
        "她先低头看见横在自己腰间的手臂，身体明显僵住，随后沿着那只手臂缓慢回头，"
        "衣料轻微摩擦，脸色从错愕转为尴尬惊慌；"
        "9-15秒：星澜沉睡的侧脸进入画面，冷漠眉眼在睡梦中少了锋利，仍保持清冷师尊的压迫感；"
        "时子初瞪圆眼，表情写满“怎么会是这个节点”的错愕和羞窘，她不惊叫，只压住呼吸，"
        "意识到自己竟重生到了最要命的时间点。旁白以低沉清晰的短剧叙述声说："
        "\"她竟重生到了最要命的时间点，爬上师尊榻后的清晨。\""
        "全片保持同一时子初身份、同一星澜身份、同一床榻和寝殿空间，重点是腰间手臂、沉睡侧脸、"
        "冰蚕丝薄被和时子初错愕羞窘表情；禁忌尴尬感要克制，不要低俗，不要夸张肢体纠缠。"
        "镜头语言是从薄被纹理推入，再拉开到两人近景，最后落到星澜侧脸和时子初表情。"
        "不要切成九宫格，不要分格边框，不要文字编号，不要字幕、LOGO、水印。"
        "音效包含清晨风铃轻响、衣料轻微摩擦，背景音乐为暧昧中带紧张的弦乐，音量不要盖过旁白。"
    )


runner.build_prompt = build_prompt


if __name__ == "__main__":
    raise SystemExit(runner.main())
