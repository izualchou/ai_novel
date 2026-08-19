# MEMORY.md

## 项目概况
- 工作区 `d:\Documents\AI_novel\ai_novel` 为小说创作项目根目录（git 仓库，尚无提交内容）。

## Skills（用户级，位于 C:\Users\izual\.codebuddy\skills\）
- `novel-writing`：小说创作全流程（构思→设定→大纲→逐章写作→一致性检查）。
- `outline-driven-novel`（2026-08-19 创建，同日审查修复后为当前版本）：根据用户提供的小说大纲（文本或文件路径）逐章生成正文。核心原则：以 `novels/<书名>/创作基线.md` 为唯一事实来源（按 `references/baseline-template.md` 十节模板维护），每章后同步人物状态与伏笔登记表；默认每章 2000-3000 字（按正文汉字数计）、张弛有度；支持文风/节奏/字数控制、修改扩写重写、从指定章节续写、可选创作说明；章节默认落盘至 `novels/<书名>/chapters/第N章-章节名.md`（数字补零、文件名净化非法字符），`进度.md` 记录进度支持中断恢复；共 5 个模式（含全书收尾）。references 共 7 个文档（outline-parsing、baseline-template、chapter-craft、style-and-pacing、consistency、creation-notes、storage-and-recovery）。

## 约定
- 工作记忆按日记录于 `.codebuddy/memory/YYYY-MM-DD.md`。
