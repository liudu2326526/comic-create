#!/usr/bin/env python3
import importlib.util
from pathlib import Path


BASE_SCRIPT = Path(__file__).with_name("run_ep01_sh02_seedance_direct_refs_story_prompt.py")
spec = importlib.util.spec_from_file_location("direct_refs_runner", BASE_SCRIPT)
runner = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(runner)


runner.META_PATH = runner.OUT_DIR / "ep01_sh03_seedance2_direct_refs_story_prompt.metadata.json"
runner.VIDEO_PATH = runner.OUT_DIR / "ep01_sh03_seedance2_direct_refs_story_prompt.mp4"
runner.LAST_FRAME_PATH = runner.OUT_DIR / "ep01_sh03_seedance2_direct_refs_story_prompt_last_frame.png"
runner.ASSET_RECORD_PATH = runner.ROOT / "volcengine-private-assets/records/ep01_sh03_direct_refs_story_prompt.json"
runner.LOG_PREFIX = "[ep01_sh03_direct_refs]"
runner.SHOT_ID = "ep01_sh03"
runner.VIDEO_DURATION = 7
runner.ASSET_GROUP_NAME = "comic-create-ep01-sh03-direct-refs"
runner.ASSET_GROUP_DESCRIPTION = "ep01_sh03 非九宫格路径，柳如烟人物参考图使用私域素材，皇城场景图使用公网 URL"
runner.ASSET_RECORD_USAGE = "ep01_sh03 非九宫格视频生成：柳如烟人物参考图入私域素材库，避免公网真人隐私拦截"

runner.REFERENCE_IMAGES = [
    {
        "label": "图片1",
        "role": "character_face",
        "path": runner.ROOT
        / "characters/修罗女帝之绝世无双/柳如烟/images/柳如烟_封王修士_面部头像.png",
        "object_key": "comic-create/seedance-refs/ep01_sh03/01_柳如烟_封王修士_面部头像.png",
        "usage": "柳如烟（封王修士）的面部身份、冷静眼神、东方女性五官和封王修士气质",
    },
    {
        "label": "图片2",
        "role": "character_fullbody",
        "path": runner.ROOT
        / "characters/修罗女帝之绝世无双/柳如烟/images/柳如烟_封王修士_9x16全身.png",
        "object_key": "comic-create/seedance-refs/ep01_sh03/02_柳如烟_封王修士_9x16全身.png",
        "usage": "玄紫长袍、封王修士服饰、站姿比例、冷峻女主出场气场",
    },
    {
        "label": "图片3",
        "role": "scene",
        "path": runner.ROOT / "scenes/修罗女帝之绝世无双/皇城/images/皇城_横屏远景_场景图_gpt-image-2.png",
        "object_key": "comic-create/seedance-refs/ep01_sh03/03_皇城_横屏远景_场景图_gpt-image-2.png",
        "usage": "皇宫大殿的暗金王座、长阶、金色殿灯、高墙压迫和昏沉衰败灵气",
    },
]


def build_prompt() -> str:
    return (
        "7秒，9:16竖版短剧视频，仙侠旧世界，电影写实风格，冷峻女主出场，暗金皇城压迫感。"
        "参考图片1锁定柳如烟（封王修士）的脸：东方女性五官，神情冷静克制，眼神清醒而坚定；"
        "参考图片2锁定她的玄紫长袍、封王修士服饰、身形比例和衣袍层次；"
        "参考图片3锁定皇城大殿：暗金王座、长阶、金色殿灯、高墙压迫、昏沉衰败灵气。"
        "0-2秒：皇宫大殿全景建立，暗金王座在高处压住空间，长阶向下延伸，金色殿灯昏沉，"
        "厚重宫门在柳如烟（封王修士）身后缓缓关闭，发出低沉回响；"
        "2-5秒：镜头采用平稳Tracking跟拍，从侧后方跟随柳如烟（封王修士）沿皇城长阶走下，"
        "她的玄紫长袍被风掀起，衣摆和袖口层层翻动，步伐稳定，不回头，身后宫门继续合拢，"
        "暗金阴影从门缝处压过来；"
        "5-7秒：镜头跟到她的正侧面和半身，她停在长阶下方，抬眼望向远处禁地方向，目光冷静，"
        "像已经知道自己被推向最危险的棋盘。旁白以低沉清晰的短剧叙述声说："
        "\"柳如烟，皇城封王修士，距离更高境界只差一步，却已被推向最危险的棋盘。\""
        "全片保持同一人物、同一玄紫长袍、同一皇城大殿空间，镜头语言是连续平稳跟拍，"
        "人物与环境关系完整，不要切成九宫格，不要分格边框，不要文字编号，不要字幕、LOGO、水印。"
        "音效包含沉重宫门关闭、长袍被风掀动，背景音乐为女主出场的冷峻弦乐，音量不要盖过旁白。"
    )


runner.build_prompt = build_prompt


if __name__ == "__main__":
    raise SystemExit(runner.main())
