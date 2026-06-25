"""
=====================================================================
 BÀI HỌC: ACCESSING CLAUDE WITH THE API
 Khóa: Claude with the Anthropic API (Anthropic Skilljar)
=====================================================================

File này đi qua toàn bộ các khái niệm cốt lõi của phần
"Accessing Claude with the API", từ cơ bản đến nâng cao một chút.

Cách dùng:
    1. Cài SDK:        pip install anthropic
    2. Đặt API key:    export ANTHROPIC_API_KEY="sk-ant-..."
    3. Chạy từng phần: bỏ comment hàm bạn muốn chạy ở cuối file
"""

import anthropic


# =====================================================================
# 1. TẠO CLIENT (Khởi tạo kết nối tới Anthropic)
# =====================================================================
# - "client" là đối tượng đại diện cho kết nối của bạn tới API.
# - Mặc định, SDK tự đọc API key từ biến môi trường ANTHROPIC_API_KEY.
#   => Không hardcode key trong code (tránh lộ key khi push lên git).

client = anthropic.Anthropic()
# Tương đương nếu muốn truyền key thủ công (KHÔNG khuyến khích):
# client = anthropic.Anthropic(api_key="sk-ant-...")


# =====================================================================
# 2. GỌI API ĐẦU TIÊN (Basic Message Request)
# =====================================================================
def basic_request():
    """Gửi 1 câu hỏi đơn giản và in câu trả lời."""

    response = client.messages.create(
        model="claude-opus-4-8",   # Chọn model (xem phần giải thích bên dưới)
        max_tokens=1024,           # Giới hạn độ dài câu trả lời
        messages=[                 # Lịch sử hội thoại
            {
                "role": "user",                       # Ai nói: "user" (bạn) hoặc "assistant" (Claude)
                "content": "Thủ đô của Việt Nam là gì?",  # Nội dung
            }
        ],
    )

    # response.content là 1 DANH SÁCH các "block".
    # Với câu trả lời text thông thường, ta lấy block đầu tiên.
    print(response.content[0].text)


# =====================================================================
# 3. HIỂU CẤU TRÚC RESPONSE (Message object)
# =====================================================================
def inspect_response():
    """In ra các trường quan trọng của đối tượng response."""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Chào Claude!"}],
    )

    print("id:          ", response.id)            # ID duy nhất của message
    print("model:       ", response.model)         # Model thực sự đã trả lời
    print("role:        ", response.role)          # Luôn là "assistant"
    print("stop_reason: ", response.stop_reason)   # Lý do dừng (xem phần 7)
    print("content:     ", response.content)       # Danh sách block nội dung
    print("usage:       ", response.usage)         # Số token đã dùng (để tính chi phí)

    # Cách an toàn để lấy text: duyệt qua các block và check type
    for block in response.content:
        if block.type == "text":
            print("Câu trả lời:", block.text)


# =====================================================================
# 4. SYSTEM PROMPT (Định hình tính cách / vai trò cho Claude)
# =====================================================================
def with_system_prompt():
    """
    System prompt là chỉ dẫn cấp cao, định hình cách Claude trả lời
    cho TOÀN BỘ cuộc hội thoại (giọng văn, vai trò, ràng buộc...).
    Nó KHÔNG nằm trong messages mà là tham số 'system' riêng.
    """

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        system="Bạn là một giáo viên tiểu học. Hãy giải thích thật đơn giản, "
               "dùng ví dụ gần gũi với trẻ em.",
        messages=[
            {"role": "user", "content": "Giải thích trí tuệ nhân tạo là gì?"}
        ],
    )
    print(response.content[0].text)


# =====================================================================
# 5. CÁC THAM SỐ QUAN TRỌNG (model, max_tokens)
# =====================================================================
# model:      Chọn "bộ não". Mạnh nhất hiện tại: claude-opus-4-8.
#             Cân bằng tốc độ/chi phí: claude-sonnet-4-6.
#             Nhanh & rẻ nhất: claude-haiku-4-5.
#
# max_tokens: Số token TỐI ĐA cho câu trả lời. 1 token ~ 0.75 từ tiếng Anh.
#             Nếu đặt quá thấp, câu trả lời bị cắt giữa chừng
#             (stop_reason sẽ là "max_tokens").
#
# LƯU Ý: Trên các model mới (Opus 4.6+), KHÔNG còn dùng temperature/top_p
#        như các khóa cũ dạy. Muốn điều chỉnh độ "suy nghĩ" thì dùng
#        output_config={"effort": "..."} (xem phần 8).


# =====================================================================
# 6. HỘI THOẠI NHIỀU LƯỢT (Multi-turn Conversation)
# =====================================================================
def multi_turn():
    """
    API là STATELESS: nó KHÔNG tự nhớ lượt trước.
    => Mỗi lần gọi, bạn phải gửi LẠI toàn bộ lịch sử hội thoại.
    Quy tắc: phải xen kẽ user -> assistant -> user -> assistant...
    """

    messages = [
        {"role": "user", "content": "Tên tôi là An."},
    ]

    # --- Lượt 1 ---
    res1 = client.messages.create(
        model="claude-opus-4-8", max_tokens=1024, messages=messages
    )
    print("Claude:", res1.content[0].text)

    # Thêm câu trả lời của Claude vào lịch sử
    messages.append({"role": "assistant", "content": res1.content[0].text})

    # --- Lượt 2 --- (Claude vẫn nhớ "An" vì ta gửi lại lịch sử)
    messages.append({"role": "user", "content": "Tên tôi là gì?"})
    res2 = client.messages.create(
        model="claude-opus-4-8", max_tokens=1024, messages=messages
    )
    print("Claude:", res2.content[0].text)


# =====================================================================
# 7. STOP REASON (Vì sao Claude dừng?)
# =====================================================================
# Trường response.stop_reason cho biết lý do dừng:
#   - "end_turn"    : Claude trả lời xong tự nhiên (bình thường).
#   - "max_tokens"  : Đụng giới hạn max_tokens -> câu trả lời bị cắt.
#   - "stop_sequence": Gặp chuỗi dừng tùy chỉnh.
#   - "tool_use"    : Claude muốn gọi 1 công cụ (bài học sau).
#   - "refusal"     : Claude từ chối vì lý do an toàn.


# =====================================================================
# 8. STREAMING (Hiện câu trả lời theo từng chữ, như ChatGPT gõ)
# =====================================================================
def streaming():
    """
    Thay vì chờ toàn bộ câu trả lời, streaming trả về từng phần nhỏ
    ngay khi model sinh ra -> trải nghiệm mượt, không bị "treo" chờ.
    """

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Viết một bài thơ ngắn về mùa thu."}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        print()  # xuống dòng khi xong


# =====================================================================
# CHẠY THỬ: bỏ comment hàm bạn muốn test
# =====================================================================
if __name__ == "__main__":
    basic_request()
    # inspect_response()
    # with_system_prompt()
    # multi_turn()
    # streaming()
