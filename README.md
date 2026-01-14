# nonebot-plugin-tavily

基于 [Tavily API](https://tavily.com/) 的 NoneBot2 插件，提供强大的实时联网搜索、内容提取和智能抓取能力。

该插件既可以作为普通的 NoneBot 插件独立使用，也可以作为 Tool 供其他 Agent 插件（如 `nonebot-plugin-dify`）调用。

## 💿 安装

### 使用 nb-cli 安装

```bash
nb plugin install nonebot-plugin-tavily
```

### 使用 pip 安装

```bash
pip install nonebot-plugin-tavily
```

## ⚙️ 配置

在 `.env` 文件中添加以下配置：

```env
# Tavily API 密钥 (必填)
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxx

# 默认搜索深度: basic (快速) / advanced (深度)
TAVILY_DEFAULT_DEPTH=basic

# 默认最大抓取页面数
TAVILY_MAX_BREADTH=10

# 搜索返回结果数量
TAVILY_MAX_RESULTS=5

# 搜索时间范围: day/week/month/year (留空不限制)
TAVILY_TIME_RANGE=

# 简单模式: 仅输出内容，不含标题和 URL
TAVILY_SIMPLE_MODE=false

# 内容截断长度
TAVILY_SEARCH_TRUNCATE=200   # 搜索结果
TAVILY_EXTRACT_TRUNCATE=2000 # 提取内容
TAVILY_CRAWL_TRUNCATE=150    # 抓取预览
```

## 🎉 使用指南

### 1. 联网搜索 (`/search`)

获取实时的网络搜索结果。

```
/search <关键词> [--depth basic|advanced]
```

**示例：**
```
/search "NoneBot2 最新版本" --depth advanced
```

### 2. 内容提取 (`/extract`)

提取指定 URL 的核心正文内容，自动去除广告和无关信息。

```
/extract <URL> [--depth basic|advanced]
```

**示例：**
```
/extract "https://example.com/article" --depth advanced
```

### 3. 智能抓取 (`/crawl`)

深度抓取网站内容，支持自然语言指令控制抓取目标。

```
/crawl <URL> [--instructions "指令内容"] [--max_breadth <数量>]
```

**示例：**
```
/crawl "https://company.com" --instructions "查找联系邮箱和地址"
```

## 🛠️ 作为工具集成

本插件基于 `Alconna` 构建，命令参数具有强类型定义，非常适合作为 Agent 工具使用。

如果你使用的是支持工具调用的插件（如 `nonebot-plugin-dify`），只需将以下命令加入工具白名单即可：

- `search`
- `extract`
- `crawl`

## 许可证

MIT
