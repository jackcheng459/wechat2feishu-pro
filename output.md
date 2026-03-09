![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/XuxaLeADVkwj7z6chonK4cDtxWFgvJ4sK4f2YTOic9BibcH1YIouTrU0NojNgJOLVr3Ptu6lSxZrdOh4L4HribpdJtibVcarz6XDcAIYfUqDzLA/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=0)哈喽，大家好！### 我是阿星👋🏻

### 这两天我在体验飞书新上的OpenClaw插件，个人感觉真的比我之前自己装的要好很多。

### 举个例子，比如说我现在让它构建一个写作Agent，每天直接帮我写推文，然后并且自动发布到草稿箱。👇🏻点击播放

### 我把这个项目架构发给他之后，他就直接给我输出了一篇样稿，并且写入了飞书文档和公众号后台。具体原理可以参考之前发过的[我搭了一个 AI 写作机器人，每天自动写文章发到公众号草稿箱](https://mp.weixin.qq.com/s?__biz=MzU3NTE2NjIxMQ==&mid=2247498229&idx=1&sn=662599463fc11952d3e4c0a3bb5b089e&scene=21#wechat_redirect)

![图片](https://mmbiz.qpic.cn/mmbiz_png/XuxaLeADVkzb5CV0ia70vTWj72zFMEyI1O5RMWxRzxiaa8aiaUmjIr5WWjJicibPmeUvCibXyxmplwuwBeHq620TWv2SRCs3sTy2OEPH5ics7jv4BE/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=1)### 我继续提要求，让它把刚才生成的文章整理到多维表格，

### 他也直接分类打标，自动统计字数规规矩矩的给我整理到表格里了。

![图片](https://mmbiz.qpic.cn/mmbiz_png/XuxaLeADVkwdfC2bcOn2xTL3pFibAwX5WIUpwPl5ibWn2fPm7F191iaUPmu6dr6bgHtWQceyXZwkYMC9libsGvnNKk4X0icLGSEegqza0WfdLNLA/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=2)### 接着我给他刚才写的样稿进行了评论，比如这篇文章我批注了，让他帮我修改开头结尾，然后引用文档一起发给他，就可以看到他直接针对我的评论意见，在文档里直接进行了修改，我只用审阅确认就可以了。

![图片](https://mmbiz.qpic.cn/mmbiz_png/XuxaLeADVkxztCUR4jVTpPdnxa2ufNk9cgxqYFtTqQakUYk8ARCWVVxS2j0aLA6sfZYZnMEBWrQeyGWwyooFZBvH54cMwAop3gqrvmgd0Uc/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=3)### 如果你也想实现，可以跟着下面步骤配置一个：

## 一、openclaw配置

### 1.安装Node.js

确保已安装Node.js（建议版本v18及以上）。可通过Node.js官网（https://nodejs.org/en/download/）下载安装。安装完成后，在终端中输入

```

`node -v验证版本。`

```

### 2.以管理员身份安装OpenClaw

打开PowerShell（Windows系统）或终端（Mac/Linux系统），以管理员身份运行以下命令：

```

`npm install -g openclaw`

```

### 3.初始化OpenClaw

安装完成后，执行以下命令进行初始化配置：

```

`openclaw onboard`

```

按照提示选择模型、配置本地网关等参数。若需使用特定模型（如智普GLM），需提前获取API Key并配置。

### 4.安装飞书插件

```

`在终端中执行以下命令安装飞书插件：  openclaw plugins install @m1heng-clawd/feishu若安装失败，可尝试手动安装：  cd ~/.openclaw/pluginsnpm install "@m1heng-clawd/feishu"`

```

## 二、创建飞书机器人

这是实现 **“在飞书里跟你的clawbot”** 的关键。

### **造个应用** ：

登录 **飞书开放平台** ，点击 **「创建企业自建应用」** 。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/XuxaLeADVkwTyteD6DM3v8oLicIPTNUs5WIRibPibR7B36o0yIQSIHhEjrfctAeTuI2azy8YV7cQfQicqzPAEesk34Yv8ibtQCKs0ntIdvJFZicQ4/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=4)### **添加机器人**

在应用里，找到 **“添加应用能力” -> “机器人”** ，打开它。

![图片](https://mmbiz.qpic.cn/mmbiz_png/XuxaLeADVkywmoicUJpDZGRPW1y8jymNpYbhT3VqsDtIibiahFRbjOQcwjw3ykV17NKtlPepwM6U2ic59q96qMu5qD7IfVBNzh7kU9Gswsk1ta4/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=5)### **给足权限**

（在「权限管理」里搜，这几个必须勾上，详细权限看附录）：

1. 获取用户基本信息
2. 获取群组信息
3. 获取与发送单聊、群组消息
4. 查看消息表情回复
5. ……

![图片](https://mmbiz.qpic.cn/mmbiz_png/XuxaLeADVkwFV9HzeUibp8BD9XBEaEeQJ9fWvAKJrHmZmarNgHic4s5ic6FBqYvwhy8vUajBibz6S7UF6KB7JxTA7tIeUSLqLOjiaicj53RIAd1OU/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=6)### **拿好凭证** ：

在 **「凭据与基础信息」** 里，复制 **App ID** 和 **App Secret** ，配置到你的本地openclaw或者云上

如果是云上你会看到在哪里配置，还是直接参考这篇[轻松部署OpenClaw到企业微信丨阿里云新加坡服务器版教程](https://mp.weixin.qq.com/s?__biz=MzU3NTE2NjIxMQ==&mid=2247500642&idx=1&sn=c93aeef015f3a56ffd193e2c67df9adc&scene=21#wechat_redirect)

要在本地安装OpenClaw并安装飞书插件，可以把 **App ID** 和 **App Secret代入第一趴直接在本地执行**

### **5.开启长连接** ：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/XuxaLeADVkw6abCzurAzCuWpFnB6m8o0polXB5VlughtE4HibvO7l1Z4Ofv4fgXib6IVVlYttyr9hia7ibty4E4bctbDoOZZgRor6pQrwh7DDHw/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=7)然后点击右边添加事件加权限。

![图片](https://mmbiz.qpic.cn/mmbiz_png/XuxaLeADVkxHAld7TsQId2nXhGHE9KxsKcHXltENyDxria4K6CE7LKTwqqibZ71ibVJ8TgdNvBAQldmWatEXvibnLjXmzD32LxHOeeyw7n0cFjc/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=8)### **发布上线** ：

进入 **「版本管理与发布」** ， **创建版本** （版本号随便写，比如1.0.0），然后 **保存并发布。**

![图片](https://mmbiz.qpic.cn/mmbiz_png/XuxaLeADVkymDE6fj4pU4icgB6hnExAxc91VhgnzcJQficQN2qOWhnAy8ObNUicVcIEYAAeI0iaCiceW6S0KkIcsrGh0mPGlyqgGRWvKwRZh4PK4/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=9)![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/XuxaLeADVkwlbgN8l6LGh0CtzIuUOrm2LqV3vCiaCKT3GmwDPG2w35yflH6CKgryicKIZX7ibpsstkUzEG1rcjkNnXrF4c0Hbia2bulKGpE5cwY/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=10)## 三、配置飞书插件

执行以下命令配置飞书插件：

```

`openclaw config`

```

按提示选择本地网关，进入Channel配置，选择“飞书（Feishu）”，并输入飞书应用的App ID和App Secret（需在飞书开放平台创建应用后获取）。

注意事项：

· 需在飞书开放平台创建企业自建应用，获取App ID和App Secret，并配置相应权限（如消息收发、群聊管理等）。

· 配置完成后，需重启OpenClaw网关使配置生效：

```

`openclaw gateway`

```

### 安装、更新飞书插件

> 如果历史上已安装了其他飞书插件，在这一步安装过程中将会 **自动禁用** 其他飞书插件，无需额外处理；如果你所在的平台有辅助开发 Agent ，可以试试让Agent辅助安装

执行指令：

```

`npx -y https://sf3-cn.feishucdn.com/obj/open-platform-opendoc/195a94cb3d9a45d862d417313ff62c9c_gfW8JbxtTd.tgz install`

```

通过以上步骤，可实现OpenClaw与飞书的集成，通过飞书发送指令并获取OpenClaw的响应。

它就能给你畅聊了

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/XuxaLeADVky4ruCTr1iaTuGpY0crMu8TSs4KFyg6pxE1rhYrz2YzaVmNf5bCHnpzLznqq65ic5YFhFqibT2iauznibdslFwX7e6ibCmFIyESVAvKA/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=11)### 附录

### 批量权限直接复制这个，以免遗漏添加

```

```json
{
  "scopes": {
  "tenant": [
  "application:application.feedback.feedback_info",
  "application:application:self_manage",
  "bitable:app:readonly",
  "cardkit:card:read",
  "cardkit:card:write",
  "contact:contact.base:readonly",
  "contact:user.base:readonly",
  "docx:document.block:convert",
  "docx:document:readonly",
  "drive:drive:readonly",
  "im:chat:read",
  "im:chat:update",
  "im:message",
  "im:message.group_at_msg:readonly",
  "im:message.group_msg",
  "im:message.p2p_msg:readonly",
  "im:message.pins:read",
  "im:message.pins:write_only",
  "im:message.reactions:read",
  "im:message.reactions:write_only",
  "im:message:readonly",
  "im:message:recall",
  "im:message:send_as_bot",
  "im:message:send_multi_users",
  "im:message:send_sys_msg",
  "im:message:update",
  "im:resource",
  "task:task:read",
  "task:task:write",
  "wiki:wiki:readonly"
],
  "user": [
  "base:app:copy",
  "base:app:create",
  "base:app:read",
  "base:app:update",
  "base:field:create",
  "base:field:delete",
  "base:field:read",
  "base:field:update",
  "base:record:create",
  "base:record:delete",
  "base:record:retrieve",
  "base:record:update",
  "base:table:create",
  "base:table:delete",
  "base:table:read",
  "base:table:update",
  "base:view:read",
  "base:view:write_only",
  "board:whiteboard:node:create",
  "board:whiteboard:node:read",
  "calendar:calendar.event:create",
  "calendar:calendar.event:delete",
  "calendar:calendar.event:read",
  "calendar:calendar.event:reply",
  "calendar:calendar.event:update",
  "calendar:calendar.free_busy:read",
  "calendar:calendar:read",
  "contact:contact.base:readonly",
  "contact:user.base:readonly",
  "contact:user.employee_id:readonly",
  "contact:user:search",
  "docs:document.comment:create",
  "docs:document.comment:read",
  "docs:document.comment:update",
  "docs:document.media:download",
  "docs:document.media:upload",
  "docs:document:copy",
  "docs:document:export",
  "docx:document:create",
  "docx:document:readonly",
  "docx:document:write_only",
  "drive:drive.metadata:readonly",
  "drive:file:download",
  "drive:file:upload",
  "im:chat.members:read",
  "im:chat:read",
  "im:message",
  "im:message.group_msg:get_as_user",
  "im:message.p2p_msg:get_as_user",
  "im:message:readonly",
  "offline_access",
  "search:docs:read",
  "search:message",
  "sheets:spreadsheet.meta:read",
  "sheets:spreadsheet:create",
  "sheets:spreadsheet:read",
  "sheets:spreadsheet:write_only",
  "space:document:delete",
  "space:document:move",
  "space:document:retrieve",
  "task:comment:read",
  "task:comment:write",
  "task:task:read",
  "task:task:write",
  "task:task:writeonly",
  "task:tasklist:read",
  "task:tasklist:write",
  "wiki:node:copy",
  "wiki:node:create",
  "wiki:node:move",
  "wiki:node:read",
  "wiki:node:retrieve",
  "wiki:space:read",
  "wiki:space:retrieve",
  "wiki:space:write_only"
]
}
}
````

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/XuxaLeADVkzM4iaPqVcmzmbiaO3lMZHc7xX4nKv7oKqyxN1r5wgJpmvzSCog5PIhfK404K8Yg5vEfGYQziaCjficJZNToc2xt9icP0AtFTbFxgaY/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=12)

```