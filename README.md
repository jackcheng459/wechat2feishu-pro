# 🚀 WeChat2Feishu: 微信公众号文章高保真转存飞书工具

一款基于 Python 和 Playwright 开发的自动化工具，旨在解决微信公众号文章转存至飞书云文档/知识库时，图片防盗链失效、排版错乱、代码块截断等痛点。

## ✨ 核心特性

- **🛡️ 完美绕过防盗链**：利用 Playwright 网络拦截技术，直接捕获浏览器上下文中的二进制图片数据，彻底告别 `default.png`。
- **🎨 高保真排版**：支持 H1-H6 标题、粗体、列表、分割线，并自动美化 JSON 代码块。
- **📐 比例精准**：自动识别图片原始宽高，拒绝拉伸变形。
- **📂 知识库 (Wiki) 深度适配**：支持直接移动至指定 Wiki 节点，并解决 Wiki 环境下图片不可见的权限难题。
- **💾 本地离线备份**：转存飞书的同时，在本地自动生成 `README.md` + 原图文件夹，实现云端/本地双重存档。
- **🤖 OpenClaw 集成**：完美兼容 OpenClaw 技能，支持在飞书对话框通过自然语言一键触发。

## 🛠️ 快速开始

### 1. 环境准备
```bash
# 推荐使用 Python 3.11+
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置 .env
在项目根目录创建 `.env` 文件：
```env
FEISHU_APP_ID=您的AppID
FEISHU_APP_SECRET=您的AppSecret
```

### 3. 使用方法
```bash
# 1. 扫码登录授权
python auth.py login

# 2. 抓取文章预览
python main.py scrape <URL>

# 3. 执行转存
python main.py save --dest-type folder --dest-token <Token>
```

## 🤝 鸣谢
本项目灵感源自开源项目 [wechat2feishu](https://github.com/zhaodl1983/wechat2feishu)，并在其基础上针对 OpenClaw 交互、Wiki 兼容性及图片比例修复进行了深度重构。
