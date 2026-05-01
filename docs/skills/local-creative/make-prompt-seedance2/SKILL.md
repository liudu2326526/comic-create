---
name: make-prompt-seedance2
description: Use when creating or improving structured Seedance 2.0 prompts with template selection, multimodal reference syntax, ad/TVC/ecommerce scripts, product showcase videos, or beginner guidance for 即梦/Seedance prompt writing.
---

# Make Prompt Seedance2

## Purpose

Generate structured, platform-ready Seedance 2.0 prompts by choosing the right template first, then filling it with concrete content, camera language, sound design, reference assets, and model-friendly constraints.

Use this skill especially for:

- single-video Seedance prompt writing where the user wants a reusable structure;
- ecommerce, TikTok/Douyin product videos, TVC, product demos, UI promos, space tours, talking-head, music beat, or short-drama scenes;
- turning a loose idea into a copy-paste prompt with `@图片`, `@视频`, `@音频` references;
- diagnosing why a prompt is vague, unstable, overcomplicated, or hard for Seedance to follow.

For long multi-episode story packages with scripts, asset lists, and continuity, prefer `seedance-storyboard-generator`.

## Core Principle

Start with intent, not wording.

Seedance 2.0 has director-like interpretation and world knowledge, so the prompt should describe the creative objective, reference roles, camera behavior, time structure, sound, and constraints. Do not overload it with encyclopedia detail unless exact control is required.

## Platform Rules

- Use official reference names: `@图片1` to `@图片9`, `@视频1` to `@视频3`, `@音频1` to `@音频3`.
- Keep total files no more than 12: images <= 9, videos <= 3, audio <= 3.
- Video and audio references should be 15 seconds or less.
- Do not depend on realistic real-person facial likeness in Seedance video prompts.
- Prefer Chinese prompts. Keep useful camera terms bilingual only when they improve precision, such as `Slow Orbit 环绕`, `Dolly Zoom 希区柯克变焦`.
- For continuation, use `将@视频1延长X秒` and describe the new action from the previous final frame.

## Prompt Workflow

1. **Classify the task**
   - Narrative/story, product showcase, ecommerce sales, TVC, character action, scenery, UI/product motion, space tour, talking-head, music beat, video extension, or video editing.

2. **Collect only necessary inputs**
   - Content goal: what should happen?
   - Duration and ratio: default `15秒, 9:16竖屏`.
   - Reference assets: image/video/audio roles.
   - Visual style: realistic, animation, ink wash, sci-fi, retro, cinematic, etc.
   - Sound: music, environment, effects, dialogue/voiceover.
   - Commercial goal when relevant: trust, product texture, conversion, authority, urgency, result visualization.

3. **Choose a template**
   - Use `references/structured-prompt.md` for general Seedance templates.
   - Use `references/ads-prompt/structured-prompt-ecommerce.md` for pain-point-driven ecommerce/TikTok sales videos.
   - Use `references/ads-prompt/structured-prompt-tvc.md` for five-shot brand TVC scripts.
   - Use `references/ads-prompt/structured-prompt-带货.md` for 15-second product sales scripts.
   - Use `references/ads-prompt/structured-prompt.md` for lighter ad prompt structure.

4. **Write the prompt**
   - Make the first 2-3 seconds visually strong.
   - Use time blocks for 13-15 second prompts.
   - Define each reference asset's role.
   - Add sound design and constraints.
   - Keep each shot to one main action or visual change.

5. **Review**
   - Does every `@素材` reference exist and have a clear role?
   - Is the product/character ID locked by the right reference?
   - Does the camera language say exactly how the shot moves?
   - Is the prompt short enough for the model to follow?
   - Are commercial claims safe and not unsupported?

## General Prompt Template

```text
【风格】[style]，[duration]秒，[aspect ratio]，[mood]

【时间轴】
0-3秒：[shot scale + camera movement]，[main image/action]，[sound/atmosphere]
3-6秒：[shot scale + camera movement]，[development]，[detail]
6-10秒：[shot scale + camera movement]，[core action/conflict/showcase]
10-13秒：[transition or emotional/product payoff]
13-15秒：[ending frame / brand landing / continuity setup]

【声音】[music] + [sound effects] + [dialogue/voiceover if any]
【参考】@图片1 [role], @视频1 [role], @音频1 [role]
【约束】[no watermark/text if needed], [stable face/body/product], [no blur/flicker], [smooth motion]
```

## Template Selection

| User Goal | Best Reference |
| --- | --- |
| General Seedance prompt, beginner guide, template lookup | `references/structured-prompt.md` |
| Product ad with high conversion goal | `references/ads-prompt/structured-prompt-带货.md` |
| Ecommerce/TikTok sales by pain point | `references/ads-prompt/structured-prompt-ecommerce.md` |
| Brand TVC, 5 shots x 3 seconds | `references/ads-prompt/structured-prompt-tvc.md` |
| Older ecommerce baseline or comparison | `references/ads-prompt/structured-prompt-ecommerce-v0.md` |
| Source tutorial context from authors | `references/source-articles/` |
| Existing paired examples | `examples/a1.md`, `examples/a2.md`, `examples/b1.md`, `examples/b2.md` |

## Ecommerce Pain-Point Routing

When the user asks for product sales or ecommerce video prompts, identify the primary pain point:

| Pain Point | Prompt Direction |
| --- | --- |
| Trust is weak, product looks cheap | Make it look like a branded product in a retail/supermarket/professional display scene. |
| Need full usage story or before/after | Use storyboard/grid narrative or compact timeline scenes. |
| Return/quality anxiety | Show inspection, packaging, shipping, material testing, or quality-control process. |
| Effect is hard to visualize | Use micro-view, transformation, before/after, or macro product effect. |
| Need authority | Use expert interview, lab scene, certificate-like visual language, but avoid false medical claims. |
| Result expectation is vague | Show time-lapse/result visualization with conservative wording. |
| Urgency is weak | Use news/report/social-proof framing, but avoid fake factual claims. |
| Product texture looks cheap | Use macro/probe/luxury-detail camera language. |
| Need immersion | Use FPV/opening/first-person experience. |
| Need batch UGC | Generate multiple creator-style variants with different hooks. |

## TVC Structure

For brand TVC prompts, use five 3-second shots:

| Shot | Function |
| --- | --- |
| SC1 | State, pain point, or atmosphere introduction |
| SC2 | Product interaction and key physical detail |
| SC3 | Visual spectacle, material, micro detail, or transformation |
| SC4 | Emotional release or usage payoff |
| SC5 | Product/brand landing; include slogan only if provided |

Do not invent a slogan. If none is supplied, end with product and logo/light presentation only.

## Prompt Quality Rules

- Replace abstract praise (`高级`, `好看`, `很酷`) with visible traits: lighting, material, lens, composition, motion.
- Avoid dense multi-action shots. One shot should contain one primary action.
- Prefer slow, stable, smooth movement for reliability.
- Use exact product details: material, color, shape, texture, size, label placement.
- Add constraints only when they protect the output; avoid long negative lists that distract from the main action.
- For copyrighted or blocked characters, use neutral labels such as `Figure 1`, `Figure 2` and visual traits instead of names.

## Output Shapes

For most requests, return:

```markdown
## 参考素材
- @图片1：...
- @视频1：...

## Seedance Prompt
[copy-paste prompt]

## 使用说明
- 时长：
- 画幅：
- 模式：
- 需要注意：
```

For ads, also include:

```markdown
## 选用玩法
[pain point -> chosen play]

## 分镜脚本
SC1 ...
SC2 ...
```

## When To Read More

The bundled references are intentionally long. Load only the needed file:

- `references/structured-prompt.md`: full general guide with 16+ templates and examples.
- `references/ads-prompt/structured-prompt-ecommerce.md`: ecommerce playbook and routing.
- `references/ads-prompt/structured-prompt-tvc.md`: brand TVC five-shot script system.
- `references/ads-prompt/structured-prompt-带货.md`: concise sales video script generation.
- `references/source-articles/`: original tutorial articles for deeper context.
