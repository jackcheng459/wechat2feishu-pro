# OpenClaw Skill：WeChat2Feishu-Pro (即时转存版)

## Skill 名称
`wechat2feishu-pro`

## 描述
微信公众号高保真转存机器人。采取“先转存、后调整”的策略，确保文章在用户发送链接后立即安全落盘至飞书云端。

---

## 🤖 自动化工作流

### 1. 触发与执行
- **触发**：检测到 `mp.weixin.qq.com` 链接。
- **决策逻辑**：
    - 机器人应**立即**依次调用 `scrape` 和 `save` 命令。
    - **存储位置选择**：
        1. 优先使用用户在会话中提到的位置。
        2. 若未提及，则使用用户记忆（Memory）中的 `default_save_path`。
        3. 若无记忆，则默认调用 `python main.py save --dest-type root` 存入用户飞书主页。

### 2. 执行指令序列
```bash
# 第一步：抓取
/Users/zhanghanlin/Documents/VibeCoding2/wechat2feishu/.venv/bin/python /Users/zhanghanlin/Documents/VibeCoding2/wechat2feishu/main.py scrape "{URL}"

# 第二步：立即转存 (以存入主页为例)
/Users/zhanghanlin/Documents/VibeCoding2/wechat2feishu/.venv/bin/python /Users/zhanghanlin/Documents/VibeCoding2/wechat2feishu/main.py save --dest-type root
```

### 3. 反馈结果
转存完成后，告知用户：
- 确认文章已成功备份。
- 展示最终的 `document_url`。
- 提示：“文章已自动为您存入 [主页/默认目录]。如需移动到特定知识库，请直接告诉我指令。”

---

## 预期结果
用户发送一个链接，在 30 秒内直接获得一个可以点击阅读的飞书文档链接。
