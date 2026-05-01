# 本地创作 Skills 归档

本目录归档当前机器中与图片生成、视频生成、小说创作、短剧/漫剧提示词生产相关的 Codex skills，便于项目内直接查阅流程规范、提示词模板、API 说明和脚本。

## 已归档目录

- `imagegen/`：通用图片生成和编辑 skill。
- `apimart-gpt-image-2/`：APIMart `gpt-image-2` 图片生成、轮询和调试流程。
- `seedance2.0-prompt-skill/`：Seedance 2.0 图片/视频提示词生成规范。
- `make-prompt-seedance2/`：Seedance 2.0 结构化提示词模板和多模态引用写法。
- `sd2-pe/`：Seedance 2.0 多模态视频提示词优化框架。
- `seedance-api-integration/`：火山方舟 Seedance 视频/图片 API 和私域素材入库说明。
- `seedance-video-generation/`：Seedance 视频生成工程集成、任务轮询和资产持久化规范。
- `seedance-storyboard-generator/`：小说、故事或文章转多集视频分镜提示词流程。
- `ai-drama-prompt-factory/`：小说/原创短剧到角色、场景、道具、分镜、视频提示词包的完整流程。
- `chinese-novelist-skill/`：中文小说分章节创作流程。
- `open-novel-writing/`：中文长篇小说创作、规划、正文生成和质量评审流程。

## Git 规则

本项目不再提交实际图片、视频、音频等二进制素材。skill 目录中的文字规范、模板、脚本和元数据会进入 Git；示例图片等媒体文件只保留在本地。

## 本地安装

如需把本目录归档的 skills 恢复到当前机器的 Codex skill 目录，可在项目根目录执行：

```bash
bash docs/skills/local-creative/install-local-skills.sh
```

脚本会把每个包含 `SKILL.md` 的子目录复制到 `$CODEX_HOME/skills/`，未设置 `CODEX_HOME` 时默认使用 `~/.codex/skills/`。
