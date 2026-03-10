# OpenClaw Skill：WeChat2Feishu-Pro (智能转存机器人版)

## Skill 名称
`wechat2feishu-pro`

## 描述
微信公众号高保真转存机器人。支持自动抓取、多级存储目标管理（指定目录/默认目录/系统主页）以及超时自动备份。

---

## 🤖 智能决策树 (工作流)

### 1. 触发与抓取
- **触发**：检测到 `mp.weixin.qq.com` 链接。
- **执行**：运行 `python main.py scrape "{URL}"`。
- **展示**：向用户展示文章预览（标题、摘要）。

### 2. 存储目标决策 (核心逻辑)
机器人应按照以下优先级确定存储位置：

#### **优先级 1：即时指定**
- 机器人询问：“您想存到哪？”
- 若用户回复了具体的文件夹名、知识库名或编号，则按该目标执行。

#### **优先级 2：默认路径记忆**
- 若用户未即时指定，但其个人偏好（Memory）中已设置过 `default_save_path`，则提示用户：“将按您的默认偏好存入：{path_name}”。

#### **优先级 3：系统主页 (Root)**
- 若上述两者皆无，提示用户：“由于未检测到指定或默认路径，将为您存入飞书云文档主页”。

---

### 🕒 5 分钟超时自动落盘规则
**这是为了确保即便用户不在线，文章也能成功备份。**
- 发出询问后，启动 **5 分钟** 计时。
- **若用户未回复**：
    1.  **有指定/默认记录**：直接运行 `save` 命令存入该位置。
    2.  **无记录**：运行 `python main.py save --dest-type root` 存入用户主页。
- **落盘后通知**：“由于您超过 5 分钟未确认，我已自动为您完成备份。”

---

## 执行指令示例

### 获取目标
```bash
# 获取文件夹
/Users/zhanghanlin/Documents/VibeCoding2/wechat2feishu/.venv/bin/python /Users/zhanghanlin/Documents/VibeCoding2/wechat2feishu/main.py list-folders
```

### 执行保存
- **存入主页**：`python main.py save --dest-type root`
- **存入文件夹**：`python main.py save --dest-type folder --dest-token {token}`
- **存入知识库**：`python main.py save --dest-type wiki --dest-token {space_id} --node-token {node_token}`

---

## 预期结果
成功后反馈：标题 + 最终文档链接 + “云端与本地已同步备份”提示。
