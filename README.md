# Comic Create

漫剧创建流程工作区，用于把小说、故事创意或分集脚本整理成可执行的短剧/漫剧提示词包。

## 项目目标

这个目录保存从创意到提示词交付的完整链路：

1. 故事策划
2. 角色、场景、道具设计
3. 分集分镜剧本
4. 连贯性与诊断
5. 分镜图片、视频、音频提示词组装

项目本身不直接生成图片、视频或音频，只产出给外部 AI 生成工具使用的结构化文本和 JSON。

## 目录结构

```text
.
├── input/
│   ├── source/        # 原始小说、故事文本、创意输入
│   └── references/    # 视觉参考、风格参考、平台要求
├── planning/          # 故事大纲、分集规划
├── characters/        # 角色设计卡
├── scenes/            # 场景设计卡
├── props/             # 关键道具设计卡
├── style/             # 全局视觉风格
├── scripts/
│   └── ep01/          # 第 1 集分镜剧本
├── continuity/        # 分集状态、伏笔、诊断报告
└── output/            # 最终提示词包
```

## 标准流程

### Phase 1 策划

输出：

- `planning/story-outline.md`
- `planning/episodes-plan.md`

### Phase 2 设计

输出：

- `characters/{角色名}.json`
- `scenes/{场景名}.json`
- `props/{道具名}.json`
- `style/style-guide.json`

### Phase 3 剧本

输出：

- `scripts/epNN/script.json`
- `scripts/epNN/script.md`（可选）
- `continuity/epNN-state.json`

### Phase 4 诊断

输出：

- `continuity/diagnosis-epNN.md`

小说改编项目建议必做诊断，原创项目可按需要执行。

### Phase 5 组装

输出：

- `output/project-manifest.json`
- `output/epNN-prompt-package.json`

## 核心约束

- 分镜图片提示词必须使用角色名和状态，例如 `陈易（觉醒前）`。
- 视频提示词必须基于分镜图片提示词派生。
- 角色、场景、道具引用要能追溯到对应设计文件。
- `script.json` 是每集剧本的权威数据源。
- `output/` 下 JSON 必须是合法 JSON。

## 推荐使用方式

1. 把原始小说或创意放入 `input/source/`。
2. 先完成 `planning/`，确认故事方向和分集结构。
3. 再补齐角色、场景、道具和风格文件。
4. 按 `scripts/ep01/`、`scripts/ep02/` 的方式逐集推进。
5. 每集完成后在 `continuity/` 记录状态，再组装到 `output/`。
