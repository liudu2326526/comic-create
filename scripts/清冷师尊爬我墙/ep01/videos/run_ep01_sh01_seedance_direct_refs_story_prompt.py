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
runner.META_PATH = runner.OUT_DIR / "ep01_sh01_seedance2_direct_refs_story_prompt.metadata.json"
runner.VIDEO_PATH = runner.OUT_DIR / "ep01_sh01_seedance2_direct_refs_story_prompt.mp4"
runner.LAST_FRAME_PATH = runner.OUT_DIR / "ep01_sh01_seedance2_direct_refs_story_prompt_last_frame.png"
runner.ASSET_RECORD_PATH = runner.ROOT / "volcengine-private-assets/records/qingleng-shizun-ep01_sh01_direct_refs_story_prompt.json"
runner.LOG_PREFIX = "[qingleng_ep01_sh01_direct_refs]"
runner.SHOT_ID = "qingleng_ep01_sh01"
runner.VIDEO_DURATION = 15
runner.ASSET_GROUP_NAME = "comic-create-qingleng-ep01-sh01-direct-refs"
runner.ASSET_GROUP_DESCRIPTION = "清冷师尊爬我墙 ep01_sh01 非九宫格路径，角色参考图使用私域素材，寝殿场景图使用公网 URL"
runner.ASSET_RECORD_USAGE = "清冷师尊爬我墙 ep01_sh01 非九宫格视频生成：女配系统、时子初、星澜参考图入私域素材库，避免公网真人隐私拦截"

runner.REFERENCE_IMAGES = [
    {
        "label": "图片1",
        "role": "character_interface",
        "path": runner.ROOT
        / "characters/清冷师尊爬我墙/女配系统/images/女配系统_警报界面_9x16全身.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh01/01_女配系统_警报界面_9x16全身.png",
        "usage": "女配系统（警报界面）的红色警报光幕、破碎闪烁、神识空间攻击感",
    },
    {
        "label": "图片2",
        "role": "character_face",
        "path": runner.ROOT
        / "characters/清冷师尊爬我墙/时子初/images/时子初_寝殿惊醒_面部头像.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh01/02_时子初_寝殿惊醒_面部头像.png",
        "usage": "时子初（寝殿惊醒）的面部身份、睫毛、刚醒空茫眼神和重生后的冷光",
    },
    {
        "label": "图片3",
        "role": "character_fullbody",
        "path": runner.ROOT
        / "characters/清冷师尊爬我墙/时子初/images/时子初_寝殿惊醒_9x16全身.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh01/03_时子初_寝殿惊醒_9x16全身.png",
        "usage": "时子初（寝殿惊醒）的寝殿服饰、身形比例、榻上惊醒姿态和清冷气质",
    },
    {
        "label": "图片4",
        "role": "character_face",
        "path": runner.ROOT
        / "characters/清冷师尊爬我墙/星澜/images/星澜_寝殿里衣_面部头像.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh01/04_星澜_寝殿里衣_面部头像.png",
        "usage": "星澜（寝殿里衣）的沉睡侧脸、清冷师尊身份和无意识亲密状态",
    },
    {
        "label": "图片5",
        "role": "character_fullbody",
        "path": runner.ROOT
        / "characters/清冷师尊爬我墙/星澜/images/星澜_寝殿里衣_9x16全身.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh01/05_星澜_寝殿里衣_9x16全身.png",
        "usage": "星澜（寝殿里衣）的寝殿里衣、身形比例、沉睡姿态和手臂揽人动作参考",
    },
    {
        "label": "图片6",
        "role": "scene",
        "path": runner.ROOT
        / "scenes/清冷师尊爬我墙/星澜寝殿/images/星澜寝殿_横屏远景_场景图_gpt-image-2.png",
        "object_key": "comic-create/seedance-refs/qingleng-shizun/ep01_sh01/06_星澜寝殿_横屏远景_场景图_gpt-image-2.png",
        "usage": "星澜寝殿的冷纱帐、榻、清冷寝殿空间和系统警报氛围",
    },
]


def build_prompt() -> str:
    return (
        "15秒，9:16竖版短剧视频，仙侠重生开场，电影写实风格，急促悬疑氛围。"
        "参考图片1锁定女配系统（警报界面）：红色警报光幕、破碎闪烁、神识空间中的攻击感，"
        "不要生成普通电脑屏幕，要像修真神识海里的系统界面；参考图片2锁定时子初（寝殿惊醒）的脸："
        "东方女性五官，刚醒时眼底空茫，随后出现重生后的冷光和压抑笑意；参考图片3锁定时子初的寝殿服饰、"
        "身形比例和榻上惊醒姿态；参考图片4和图片5锁定星澜（寝殿里衣）：清冷师尊气质、沉睡侧脸、寝殿里衣、"
        "身形比例和睡梦中无意识收紧手臂的动作；参考图片6锁定星澜寝殿：冷纱帐、床榻、清冷寝殿空间、低光环境。"
        "0-4秒：黑底神识空间中，女配系统（警报界面）像破碎红色光幕一样剧烈闪烁，"
        "红色警报字符和碎裂光片层层弹出，画面快速推进，神识空间被红光撕开，刺耳系统警报滴滴声压住环境声；"
        "4-9秒：镜头切到星澜寝殿榻上，冷纱帐和暗色寝殿空间一闪而过，快速推进到时子初（寝殿惊醒）的脸，"
        "她睫毛轻颤后猛然睁眼，眼底先是空茫和迟滞，随后意识回笼，唇角极轻地勾起；"
        "同一画面后景或侧后方隐约可见星澜（寝殿里衣）沉睡的轮廓，保持暧昧但克制，不要喧宾夺主；"
        "9-15秒：星澜（寝殿里衣）在睡梦中无意识收紧手臂，把时子初（寝殿惊醒）重新揽回怀中，"
        "动作要清楚表现腰间手臂收紧和身体被轻轻带回；时子初的视线从屋顶冷纱帐慢慢下移，神识警报残影还在视野边缘闪动，"
        "重生后的冷光刚浮起就被错愕打断，她没有惊叫，而是先冷静、再因身后怀抱微微僵住。旁白以低沉清晰的短剧叙述声说："
        "\"警报声消失的那一刻，时子初知道，自己回来了。\""
        "全片保持同一女配系统警报界面、同一时子初面部身份、同一星澜身份、同一寝殿空间，"
        "必须明确时子初和星澜同在床榻上，表现从系统警报、重生错愕、冷静回神，到被星澜无意识揽回怀中的动作打断。"
        "不要切成九宫格，不要分格边框，不要文字编号，不要字幕、LOGO、水印。"
        "音效包含系统警报滴滴声、神识震荡声，背景音乐为急促悬疑开场音乐，音量不要盖过旁白。"
    )


runner.build_prompt = build_prompt


if __name__ == "__main__":
    raise SystemExit(runner.main())
