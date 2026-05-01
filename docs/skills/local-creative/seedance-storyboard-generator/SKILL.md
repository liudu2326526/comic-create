---
name: seedance-storyboard-generator
description: Use when turning a novel, story, article, historical episode, or rough idea into a multi-episode Seedance 2.0 video series with script, asset plan, per-episode storyboard prompts, continuity checks, or video-extension handoff.
---

# Seedance Storyboard Generator

## Purpose

Turn source material into production-ready short-video packages for Seedance 2.0: story analysis, episode script, numbered visual assets, per-episode timeline prompts, and continuity notes.

This skill is for story-to-series work. For a single standalone Seedance prompt, use the simpler `seedance` skill unless the user asks for script, assets, or multi-episode continuity.

## Default Assumptions

If the user does not specify production parameters, proceed with these defaults and state them briefly:

| Parameter | Default |
| --- | --- |
| Series length | 5 episodes |
| Episode length | 15 seconds |
| Aspect ratio | 9:16 vertical |
| Structure | 5-episode compressed three-act arc |
| Delivery style | Chinese Markdown files or sections |
| Visual consistency | One shared style prefix across all assets |

Ask a question only when the source story or intended topic is too ambiguous to identify the protagonist, conflict, or ending.

## Source Material Pass

Extract and preserve:

- Core hook: 2-4 Chinese characters, such as `绝境反杀`, `复仇爽剧`, `悬疑惊悚`, `治愈温馨`.
- Story synopsis: background, inciting conflict, protagonist profile, main event chain, ending.
- One-line selling point: emotional call + core conflict + visual climax.
- Characters: visual appearance, identity/background, relationship to protagonist, traits, memorable line.
- Key locations and props.
- Episode emotional arc: every episode needs a beginning, escalation, peak, and release.

For long novels, summarize first by plot beats and character arcs, then compress into the target episode count. Do not attempt to cover every scene.

## Production Workflow

1. **Script**
   - Create `[Title]_剧本.md`.
   - Use the exact script body conventions below.
   - Keep each episode focused on one emotional or plot beat.

2. **Asset plan**
   - Create `[Title]_素材清单.md`.
   - Number assets by type:
     - `C01-C99`: characters, usually multiple poses or states per important character.
     - `S01-S99`: scenes and locations.
     - `P01-P99`: props and symbolic objects.
   - Every asset prompt must start with the same visual style prefix unless the user explicitly wants mixed styles.
   - Make each major character identifiable through distinct colors, silhouette, clothing, accessories, or body language.

3. **Seedance storyboards**
   - Create `[Title]_E[XX]_分镜.md` for each episode.
   - Each episode includes: upload asset list, Seedance timeline prompt, sound design, references, and ending-frame description.
   - For episode 2 and later, use video extension when continuity is intended: `将@视频1延长15s`.

4. **Quality pass**
   - Check all `@图片X` references against the upload table.
   - Check every `C/S/P` asset ID used in storyboards exists in the asset plan.
   - Check each 15-second timeline covers the full duration.
   - Check episode ending frame connects to the next episode opening.
   - Reduce risky or vague wording that may trigger generation failure or poor instruction following.

## Script Format

The script must include these sections:

```markdown
# [Title] - 剧本

一、核心梗
[2-4 character hook]

二、故事梗概
故事背景：[time, location, initial situation]
开场冲突：[inciting incident]
主角画像：[protagonist and core state]
主线事件：[plot progression -> climax -> result]
结局：[outcome and transformation]

三、一句话卖点
[punchy marketing hook]

四、人物小传
**角色名**
视觉形象：[age, appearance, clothing, visual markers]
身份背景：[role, relationship, backstory]
核心标签：[2-4 tags]
性格特点：[personality and pressure-state transformation]
金句：[memorable line]

五、剧本大纲
前期（起）：[setup]
中期（承/转）：[development and turn]
后期（高潮）：[climax]
尾声（收尾）：[resolution]

六、剧本正文
```

Each episode body uses:

```markdown
第X集
X-X [日/夜] [内/外] [场景名称]
道具：[key props]
出场人物：[characters]

△ 【空镜】[atmosphere shot with composition, camera, light, sound]
△ [shot description with concrete camera movement]
角色名（os）：[inner monologue/off-screen thought]
△ [reaction or action shot]
角色名（情绪）：[dialogue]
△ [action sequence using -> for chained motion]
【字幕：xxx】
△ 【闪回】[flashback shot]
【闪回结束】
△ 【空镜】[closing atmosphere]
```

Rules:

- Every visual shot starts with `△ `.
- Use concrete shot scale: `远景`, `全景`, `中景`, `近景`, `特写`, `大特写`.
- Use concrete camera movement: `推镜头`, `拉镜头`, `摇镜头`, `移镜头`, `跟镜头`, `环绕镜头`, `升降镜头`, `希区柯克变焦`, `一镜到底`, `手持晃动`.
- Use dialogue labels accurately: `os` for internal/off-screen thought, `vo` for voiceover when the speaker is not in frame, or an emotion marker such as `怒`, `惊`, `哽咽`.
- Include sensory detail: light, color, sound, weather, texture, temperature, and emotional pressure.

## Asset Prompt Format

Use this structure for each visual asset:

```markdown
### [ID] - [Name]

[Shared style prefix], [specific subject description in Chinese or English], [pose/state], [clothing/props], [lighting/background], [technical requirements]
```

Common style prefixes:

- `Chinese ink wash painting style mixed with anime cel-shading`
- `cinematic photorealistic style with dramatic lighting`
- `3D Chinese animation rendering, high detail, stylized realism`
- `retro film still, muted color palette, cinematic lighting`

For character assets, include at least full body, key emotional state, and action/side/back view when the character appears repeatedly.

## Seedance Episode Format

Each episode storyboard should be directly pasteable into Seedance:

```markdown
# [Title]_E[XX]_分镜

## 素材上传列表

| 上传位置 | 素材ID | 素材描述 |
| --- | --- | --- |
| 图片1 | C01 | [purpose] |
| 图片2 | S01 | [purpose] |

## Seedance Prompt

[For E02+ when chaining] 将@视频1延长15s。

[style], 15秒，9:16竖屏，[overall mood]

0-3秒：[opening image] - [camera movement], [action], [sound/atmosphere]
3-6秒：[development] - [camera movement], [action], [emotion]
6-9秒：[conflict or reveal] - [camera movement], [key detail]
9-12秒：[climax] - [camera movement], [impact]
12-15秒：[landing frame] - [camera movement], [continuity setup]

【声音】[music] + [sound effects] + [dialogue/voiceover]
【参考】@图片1 [role], @图片2 [role]

## 尾帧描述
[subject, background, light, composition, mood, continuity purpose]
```

Keep prompts clear rather than bloated. If an episode prompt exceeds roughly 300-400 Chinese characters and becomes hard to follow, split or simplify the beat.

## Seedance Constraints

- Use official reference names: `@图片1` to `@图片9`, `@视频1` to `@视频3`, `@音频1` to `@音频3`.
- Keep uploaded files within platform limits: up to 9 images, up to 3 videos, up to 3 audio files, and mixed references no more than 12 files total.
- Video/audio references should not exceed 15 seconds total.
- Avoid writing "realistic celebrity face" or relying on exact real-person facial likeness.
- For video extension, upload the previous episode as `@视频1` and start with `将@视频1延长15s`.
- If generation fails due to moderation, use binary search on prompt segments and replace suspicious terms with neutral descriptions.

## When To Read References

- Read `references/story-to-video-script.md` when converting a story into a complete script package or when the source material is narrative-heavy.
- Read `references/seedance-manual.md` when the user needs Seedance platform mechanics, multimodal reference syntax, template variants, or capability limits.
- Read `references/storyboard-optimization.md` when improving a prompt that is vague, unstable, or visually collapsing.
- Read `examples/good-script-linchong.md` or `examples/linchong-e01-storyboard.md` when an example of the target style or output shape is needed.

## Common Failure Modes

- **No asset discipline:** storyboards cite assets that do not exist. Fix by producing the asset plan before per-episode prompts.
- **Style drift:** character and scene images use different visual languages. Fix with one shared style prefix and explicit character markers.
- **Weak continuity:** episode N ending cannot lead into episode N+1 opening. Fix with ending-frame descriptions and video-extension prompts.
- **Vague camera language:** generic "镜头移动" produces weak results. Replace with exact shot scale and movement.
- **Overloaded prompt:** too many actions in 15 seconds causes instruction misses. Keep one main beat per episode.
