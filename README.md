# 🚀 WeChat2Feishu-Pro (适配 OpenClaw)
### 微信文章一键转存飞书，从此告别图片损坏和排版错乱！

WeChat2Feishu-Pro 是一款专门为**非技术用户**打造的自动化工具。它可以帮你把喜欢的微信公众号文章，一键完美转存到你的飞书云文档或知识库（Wiki）中，并在本地自动备份。

---

## 📱 典型使用场景
**把文章链接转发给飞书机器人** → **机器人自动抓取** → **根据智能建议秒级完成转存！**

---

## 🤖 OpenClaw 用户：一键全自动安装
如果你正在使用 OpenClaw 插件，现在可以通过一行指令完成**下载、配置与技能加载**：

1.  **执行安装**：在终端运行：
    ```bash
    gemini skills add https://github.com/jackcheng459/WeChat2Feishu-Pro
    ```
2.  **初始化环境**：进入技能目录并运行环境脚本（OpenClaw 会提示你路径）：
    ```bash
    bash scripts/setup.sh
    ```
3.  **配置授权**：在 `.env` 中填入飞书 App ID/Secret 后，运行：
    ```bash
    python3 scripts/auth.py login
    ```

---

## 🛠️ 三步搞定手动安装（小白级教程）

### 第一步：准备飞书“通行证”
1.  登录 [飞书开放平台](https://open.feishu.cn/app) 创建一个“自建应用”。
2.  获取 **App ID** 和 **App Secret**。
3.  **开通权限**：搜索并开启“查看、编辑、管理云空间、云文档、知识库”的所有必要权限。

### 第二步：一键部署环境
```bash
git clone https://github.com/jackcheng459/WeChat2Feishu-Pro.git
cd WeChat2Feishu-Pro
bash scripts/setup.sh
```

### 第三步：给机器人分配存储权限（⚠️ 重要）
将您的自建应用添加为目标文件夹或知识库空间的**管理员/协作者**。程序会自动将新生成的文档管理权 **100% 授予您本人**。

---

## ✨ 核心优势
- **原图保存**：Playwright 底层拦截，彻底解决微信图片防盗链。
- **比例完美**：自动识别宽高，图片拒绝拉伸变形。
- **Wiki 适配**：解决知识库内容丢失与图片可见性难题。
- **无人值守**：支持 Tenant 静默模式，告别验证弹窗。

---

## 📂 项目结构
- `SKILL.md`: OpenClaw 官方技能定义。
- `scripts/`: 核心执行脚本（抓取、转换、转存）。
- `references/`: 架构手册与开发日志。
- `exports/`: 本地图文备份。

## 🤝 鸣谢
本项目灵感源自开源项目 [wechat2feishu](https://github.com/zhaodl1983/wechat2feishu)，并在其基础上进行了 Pro 级深度重构。
