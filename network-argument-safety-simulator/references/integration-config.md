# Integration Configuration

## Material Priority

1. Direct Markdown (`.md`, `.markdown`) or pasted text
2. Local MarkItDown for ordinary text PDFs
3. User-configured MinerU for scanned or complex PDFs
4. User-configured generic PDF parsing MCP

Do not send a private document to a remote service unless the user has authorized that destination.

## MarkItDown

Recommended local command:

```bash
markitdown input.pdf -o output.md
```

No service address or token is needed.

## MinerU

MinerU 用于扫描件、图片型 PDF、复杂版式（表格、公式、多栏）的解析，效果优于 MarkItDown。需用户自行部署或申请 Agent 服务后，在模拟器「解析与 MCP 设置」对话框里填写。

### 何时用 MinerU（而非 MarkItDown）

- **MarkItDown 够用**：纯文本 PDF、电子版判决书、可复制的文字
- **建议 MinerU**：扫描件、拍照件、含表格/公式/图片的复杂版式、MarkItDown 提取出乱码或丢内容时

### 模式一：自部署 HTTP API（local 模式）

适用于在本机或自有服务器部署 MinerU 的用户。

**配置步骤：**
1. 按 [MinerU 官方文档](https://github.com/opendatalab/MinerU) 部署服务，默认监听 `http://127.0.0.1:8888` 或自定义端口
2. 在模拟器「解析与 MCP 设置」对话框：
   - PDF 解析方式选「MinerU」
   - MinerU 接入方式选「自部署 HTTP API」
   - 服务地址填部署地址，如 `http://127.0.0.1:8888`
   - 访问令牌：若部署设了鉴权则填，否则留空

**内部调用逻辑**（见 `integrations.py` 的 `mineru_extract`）：
- 端点：`{base_url}/file_parse`（POST，multipart 上传）
- 参数：`return_md=true`、`return_middle_json=false`
- 返回：Markdown 文本，或含 Markdown 的 ZIP（自动解压提取）

### 模式二：MinerU Agent 轻量解析 API（agent 模式）

适用于使用 MinerU 官方托管的 Agent 服务，无需自部署。

**配置步骤：**
1. 在 [mineru.net](https://mineru.net) 注册并获取 Agent API 访问权限
2. 在模拟器「解析与 MCP 设置」对话框：
   - PDF 解析方式选「MinerU」
   - MinerU 接入方式选「MinerU Agent 轻量解析 API」
   - 服务地址默认 `https://mineru.net/api/v1/agent`（或按官方文档更新）
   - 访问令牌按服务要求填写

**内部调用逻辑**（见 `integrations.py` 的 `_mineru_agent_extract`）：
1. POST `{base_url}/signed-url` 获取上传地址 `signed_url` 和任务 ID `parse_id`
2. PUT 上传 PDF 到 `signed_url`
3. 轮询 GET `{base_url}/parse/{parse_id}`，`state=done` 后取 `full_md` 或下载结果 ZIP

### 故障回退

勾选「远程解析失败时回退到本机 MarkItDown」（默认开启）后，MinerU 调用失败会自动改用本机 MarkItDown，并提示警告，避免因远程服务异常中断流程。

### 注意事项

- MinerU 默认超时 180 秒，大文件或排队可能更久，可在配置里调大 timeout
- 不要把令牌写入项目文件，令牌只保存在当前浏览器会话（见对话框说明）
- 若用户未配置 MinerU，对扫描件应提示「建议配置 MinerU 或上传已转好的 Markdown」

## Generic PDF Parsing MCP

Recommended configuration fields:

```json
{
  "base_url": "https://example.com/mcp",
  "tool_name": "parse_pdf_to_markdown",
  "authorization": "Bearer ...",
  "file_argument": "file_base64",
  "filename_argument": "filename"
}
```

Call using JSON-RPC:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "parse_pdf_to_markdown",
    "arguments": {
      "file_base64": "...",
      "filename": "material.pdf",
      "mime_type": "application/pdf"
    }
  },
  "id": 1
}
```

Expect Markdown text in the tool result. Adjust argument names to the MCP tool schema.

## YuanDian Case MCP

Recommended address from the bundled project:

```text
https://open.chineselaw.com/mcp/case/stream
```

Recommended tool:

```text
yuandian_case_vector_search
```

Recommended request:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "yuandian_case_vector_search",
    "arguments": {
      "query": "平台 + 行为 + 场景",
      "page": 1,
      "pageSize": 5
    }
  },
  "id": 1
}
```

Ask the user to obtain YuanDian access and provide the full Authorization value. Do not write tokens into the skill or project files.

