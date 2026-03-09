# wechat2feishu 项目交接文档

## 📋 项目概述

**项目名称**: wechat2feishu
**项目路径**: `/Users/zhanghanlin/Documents/VibeCoding2/wechat2feishu`
**项目目标**: 将微信公众号文章自动抓取并转存到飞书云文档/知识库，支持文本、图片、格式完整保留

---

## 🎯 核心需求

1. **抓取微信公众号文章**：使用 Playwright 绕过微信反爬机制
2. **转换为 Markdown**：保留标题、段落、图片、代码块等格式
3. **上传到飞书**：支持保存到个人云空间文件夹或知识库节点
4. **图片处理**：在 Playwright 浏览器上下文中捕获图片二进制数据（绕过微信 CDN 防盗链）
5. **OpenClaw 技能集成**：作为飞书机器人技能使用

---

## 🛠️ 技术栈

- **Python 3.11+**
- **Playwright**: 浏览器自动化，抓取微信文章
- **飞书开放平台 API**: 文档创建、图片上传、内容写入
- **html2text**: HTML 转 Markdown
- **虚拟环境**: `.venv`

---

## 📁 项目结构

```
wechat2feishu/
├── main.py              # CLI 入口，命令：auth/scrape/list-folders/save
├── scraper.py           # Playwright 抓取微信文章 + 捕获图片二进制数据
├── processor.py         # HTML → Markdown 转换
├── feishu.py            # 飞书 API 封装（授权/上传图片/创建文档/写入块）
├── auth.py              # 飞书 OAuth 授权流程
├── config.py            # 配置管理（app_id/secret/tokens）
├── requirements.txt     # 依赖列表
├── .venv/               # Python 虚拟环境
└── ~/.openclaw/skills/wechat2feishu.md  # OpenClaw 技能配置文件
```

---

## ✅ 已完成功能

### 1. 微信文章抓取
- ✅ 使用 Playwright headless 模式绕过反爬
- ✅ 在页面加载时监听 `response` 事件，直接捕获图片二进制数据（绕过微信 CDN 防盗链）
- ✅ 滚动页面触发懒加载图片
- ✅ 提取标题、作者、时间、正文 HTML

### 2. Markdown 转换
- ✅ 标题（h1-h6）
- ✅ 段落、加粗、斜体、行内代码
- ✅ 图片占位符
- ✅ 代码块（降级为带行内代码样式的段落，避免飞书 API 兼容问题）

### 3. 飞书集成
- ✅ OAuth 授权（scope 包含 `wiki:wiki`）
- ✅ 列出个人云空间文件夹
- ✅ 列出知识库及子节点
- ✅ 创建文档到文件夹/知识库
- ✅ 上传图片（传入 `parent_node=document_id`）
- ✅ 写入文档块（段落、标题、图片）

### 4. Bug 修复记录
- ✅ 修复 `space_id is not int`：自动从 `node_token` 查询 `space_id`
- ✅ 修复段落块字段名：`"paragraph"` → `"text"`
- ✅ 修复图片块字段名：`"token"` → `"file_token"`
- ✅ 修复图片下载失败：在 Playwright 中监听网络响应直接捕获
- ✅ 修复 batch 写入 `index` 参数：统一用 `"index": 0`（追加模式）

---

## ❌ 当前问题

### **图片上传到飞书后无法打开**

**现象**：
- 图片上传 API 返回成功（`code=0`，返回 `file_token`）
- 图片块写入文档成功（无报错）
- 但在飞书客户端/网页端打开文档时，图片显示为损坏或无法加载

**可能原因**：
1. **图片格式问题**：捕获的二进制数据可能不完整或格式错误
2. **Base64 编码问题**：上传时的 base64 编码可能有误
3. **飞书 API 参数问题**：`parent_type="docx_image"` 可能不适用于知识库文档
4. **图片 MIME 类型问题**：上传时未正确设置 `Content-Type`

**相关代码位置**：
- `scraper.py` 第 60-80 行：图片捕获逻辑
- `feishu.py` 第 60-100 行：`upload_image()` 函数
- `feishu.py` 第 350-360 行：`_image_block()` 函数

---

## 🔧 待解决任务

### 任务 1：修复图片上传问题
**优先级**: 🔴 高

**调试步骤**：
1. 检查捕获的图片二进制数据是否完整（保存到本地文件验证）
2. 检查 base64 编码是否正确
3. 测试直接用 HTTP 请求上传图片（不走 base64，用 `multipart/form-data`）
4. 对比飞书官方示例代码的图片上传方式

**参考资料**：
- 飞书文档 API：https://open.feishu.cn/document/server-docs/docs/docs-overview
- 图片上传 API：https://open.feishu.cn/document/server-docs/docs/drive-v1/media/image/upload_all

### 任务 2：GitHub 代码管理
**优先级**: 🟡 中

**操作步骤**：
1. 初始化 Git 仓库（如果未初始化）
2. 创建 `.gitignore`（排除 `.venv/`、`config.json`、`*.pyc` 等）
3. 创建 GitHub 仓库
4. 推送代码到 GitHub
5. 创建 `README.md`（项目说明）

---

## 🚀 快速启动指南

### 环境准备
```bash
cd /Users/zhanghanlin/Documents/VibeCoding2/wechat2feishu
source .venv/bin/activate
```

### 测试完整流程
```bash
# 1. 抓取文章
python main.py scrape https://mp.weixin.qq.com/s/qNJRqekm6I6Y5KrawcmsmQ

# 2. 列出存储位置
python main.py list-folders

# 3. 保存到知识库（示例）
python main.py save --dest-type wiki --dest-token 7614038428996357079 --node-token Sz22w7bEmiPImRkaKZCcVl07nwf
```

### 调试图片问题
```bash
# 修改 scraper.py，在捕获图片后保存到本地验证
# 在第 75 行后添加：
with open(f"/tmp/test_image_{i}.jpg", "wb") as f:
    f.write(image_bytes)
```

---

## 📞 飞书应用配置

**App ID**: `cli_a7a0e4e5d13a500c`
**权限列表**（已开通）：
- `docx:document`
- `drive:drive`
- `wiki:wiki`
- `wiki:node:create`
- `wiki:space:read`

**配置文件**: `~/.wechat2feishu/config.json`

---

## 📝 OpenClaw 技能配置

**技能文件**: `~/.openclaw/skills/wechat2feishu.md`
**触发词**: 用户发送微信公众号链接时自动触发

---

## 🐛 已知限制

1. **微信 CDN 防盗链**：必须在 Playwright 浏览器上下文中捕获图片，无法事后下载
2. **飞书 API 限制**：代码块格式兼容性差，已降级为普通段落
3. **图片上传问题**：当前图片上传后无法在飞书中正常显示（待修复）

---

## 📚 相关文档

- [飞书开放平台文档](https://open.feishu.cn/document/home/index)
- [Playwright Python 文档](https://playwright.dev/python/docs/intro)
- [微信公众号反爬机制分析](https://github.com/search?q=wechat+anti+spider)

---

## 🤝 交接说明

**当前状态**: 功能基本完成，但图片上传后无法在飞书中正常显示
**下一步**: 修复图片上传问题，然后推送代码到 GitHub
**联系方式**: 如有疑问可查看代码注释或飞书 API 文档

---

**文档生成时间**: 2026-03-09
**最后修改**: Claude (Anthropic)
