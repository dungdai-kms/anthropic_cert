# 🎓 Claude with the Anthropic API — Tài liệu học (Tiếng Việt)

Bộ notebook học theo khóa **[Claude with the Anthropic API](https://anthropic.skilljar.com/claude-with-the-anthropic-api)** (Anthropic Skilljar), giải thích bằng tiếng Việt kèm code chạy được.

> 💡 Code dùng **model mới nhất `claude-opus-4-8`** và cú pháp hiện hành (khác một số chỗ so với video khóa học cũ — xem phần [Lưu ý quan trọng](#-lưu-ý-quan-trọng-khác-với-khóa-học-cũ)).

---

## 📚 Mục lục các bài học

| # | Notebook | Nội dung | Chạy được ngay? |
|---|---|---|:---:|
| 1 | [`accessing_claude_api.ipynb`](accessing_claude_api.ipynb) | Truy cập API: client, messages, roles, tokens, system prompt, stateless, streaming | ✅ |
| 2 | [`prompt_evaluation.ipynb`](prompt_evaluation.ipynb) | Đánh giá prompt: dataset → run → grade → aggregate; LLM as a Judge | ✅ |
| 3 | [`prompt_engineering_techniques.ipynb`](prompt_engineering_techniques.ipynb) | Kỹ thuật prompt: rõ ràng, vai trò, few-shot, XML tags, chain-of-thought, chaining | ✅ |
| 4 | [`tool_use_with_claude.ipynb`](tool_use_with_claude.ipynb) | Tool Use: định nghĩa tool, vòng lặp agentic, tool_result, tool runner | ✅ |
| 5 | [`rag_and_agentic_search.ipynb`](rag_and_agentic_search.ipynb) | RAG & Agentic Search: retrieve→augment→generate; biến search thành tool | ✅ |
| 6 | [`model_context_protocol.ipynb`](model_context_protocol.ipynb) | MCP: chuẩn mở Host→Client→Server; `mcp_servers` + `mcp_toolset` | ⚠️ minh họa |
| 7 | [`anthropic_apps_claude_code_computer_use.ipynb`](anthropic_apps_claude_code_computer_use.ipynb) | Claude Code (coding agent) & Computer Use (điều khiển GUI) | ⚠️ minh họa |
| 8 | [`agents_and_workflows.ipynb`](agents_and_workflows.ipynb) | Workflow vs Agent; mẫu Chaining / Routing / Parallelization; 4 tiêu chí | ✅ |
| 9 | [`final_assessment.ipynb`](final_assessment.ipynb) | Ôn tập (Q&A có đáp án), bài Capstone, bản đồ kiến thức toàn khóa | ✅ |

**Ghi chú:** ⚠️ *minh họa* = một số ô cần MCP server thật / sandbox Docker nên không chạy thẳng trong notebook (đã ghi rõ trong từng file).

### 🔬 File giải thích bổ sung (Deep-dive)

| Notebook | Giải thích phần khó nhất |
|---|---|
| [`example_agentic_loop_explained.ipynb`](example_agentic_loop_explained.ipynb) | **"Chụp X-quang" Vòng lặp Agentic** — phần nâng cao & dễ rối nhất khóa học. In ra chính xác `messages` phình to thế nào qua từng bước; giải thích `tool_use_id`, vì sao gửi lại `response.content`, vì sao kết quả công cụ nằm trong message `user`. **Nên đọc sau bài 4 (Tool Use).** |

> 📄 Ngoài ra còn 2 file `.py` đầu tiên (`accessing_claude_api.py`, `prompt_evaluation.py`) — bản script gốc trước khi chuyển sang notebook.

---

## 🚀 Bắt đầu

### 1. Cài đặt
```bash
pip install anthropic jupyter
```

### 2. Đặt API Key
Lấy key tại [console.anthropic.com](https://console.anthropic.com), rồi:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Mở notebook
```bash
cd /Users/daianhdung/Documents/KMS/ai-contest/anthropic_cert
jupyter notebook
```
> Hoặc mở thẳng file `.ipynb` bằng **VS Code / Cursor** (có sẵn hỗ trợ notebook).

### 4. Học theo thứ tự
Đọc ô markdown (giải thích) → chạy ô code (xem kết quả) → đi từ bài 1 đến bài 9.

---

## 🗺️ Lộ trình kiến thức

```
① API cơ bản
     │
② Đánh giá prompt ──────┐  (công cụ đo lường, dùng xuyên suốt)
     │                  │
③ Kỹ thuật prompt       │
     │                  │
④ Tool Use ─────────────┤  (nền tảng cho agent)
     │                  │
⑤ RAG & Agentic Search ─┤  (Tool Use + Retrieval)
     │                  │
⑥ MCP                   │  (chuẩn hóa tool use)
     │                  │
⑦ Anthropic Apps        │  (agent thực tế)
     │                  │
⑧ Agents & Workflows ◀──┘  (tổng hợp tất cả)
     │
⑨ Final Assessment  🎓
```

---

## ⚠️ Lưu ý quan trọng (khác với khóa học cũ)

Khóa Skilljar có thể dùng model & cú pháp cũ. Bộ notebook này đã cập nhật cho **Opus 4.8**:

| Khóa cũ dạy | Cách hiện hành (đã dùng trong notebook) |
|---|---|
| `temperature` / `top_p` để chỉnh độ sáng tạo | `output_config={"effort": "low\|medium\|high\|max"}` |
| **Prefill** (mồi `{"role":"assistant","content":"{"}`) để ép JSON | `output_config={"format": {"type":"json_schema", ...}}` |
| Extended thinking với `budget_tokens` | `thinking={"type": "adaptive"}` |
| Model `claude-3-5-sonnet`... | `claude-opus-4-8` (mạnh nhất hiện tại) |

> Các cách cũ trên sẽ báo **lỗi 400** trên model mới.

---

## 📖 Tài nguyên thêm

- Tài liệu chính thức: [platform.claude.com/docs](https://platform.claude.com/docs)
- Console (lấy API key): [console.anthropic.com](https://console.anthropic.com)
- Claude Code: `npm install -g @anthropic-ai/claude-code`

---

*Tài liệu học cá nhân — giải thích tiếng Việt, code cập nhật Opus 4.8.*
