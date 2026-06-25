"""
=====================================================================
 BÀI HỌC: PROMPT EVALUATION (Đánh giá Prompt)
 Khóa: Claude with the Anthropic API (Anthropic Skilljar)
=====================================================================

TẠI SAO CẦN ĐÁNH GIÁ PROMPT?
- Khi chỉnh sửa prompt, làm sao biết nó TỐT HƠN hay TỆ HƠN?
- "Nhìn 1-2 ví dụ thấy ổn" -> KHÔNG đáng tin (cảm tính, thiên vị).
- Giải pháp: xây 1 quy trình đánh giá tự động, chạy trên NHIỀU test case,
  cho ra ĐIỂM SỐ -> so sánh khách quan giữa các phiên bản prompt.

QUY TRÌNH ĐÁNH GIÁ GỒM 4 BƯỚC:
  1. Tạo bộ dữ liệu test (test dataset)
  2. Chạy prompt cần đánh giá trên từng test case -> thu output
  3. Chấm điểm output (grading)
  4. Tổng hợp điểm -> kết luận

Cách dùng:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
"""

import json
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-opus-4-8"


# =====================================================================
# BƯỚC 1: TẠO BỘ DỮ LIỆU TEST (Test Dataset)
# =====================================================================
# Mỗi test case mô tả 1 NHIỆM VỤ ("task") mà ta muốn prompt xử lý.
# Có thể kèm "solution_criteria" = tiêu chí để chấm điểm sau này.
#
# 2 cách tạo dataset:
#   a) Viết tay (chính xác nhưng tốn công)
#   b) Nhờ Claude tự sinh ra (nhanh, đa dạng) -> xem generate_dataset()

dataset = [
    {
        "task": "Viết hàm Python tính giai thừa của một số nguyên dương.",
        "solution_criteria": "Phải xử lý đúng trường hợp n=0 (trả về 1) "
                             "và dùng vòng lặp hoặc đệ quy chính xác.",
    },
    {
        "task": "Viết hàm Python kiểm tra một chuỗi có phải palindrome không.",
        "solution_criteria": "Phải không phân biệt hoa thường và xử lý chuỗi rỗng.",
    },
    {
        "task": "Viết hàm Python tìm số lớn nhất trong một danh sách.",
        "solution_criteria": "Phải xử lý danh sách rỗng một cách an toàn.",
    },
]


def generate_dataset():
    """
    (Tùy chọn) Nhờ Claude tự sinh bộ test case.
    Dùng structured output để đảm bảo trả về JSON đúng định dạng.
    """
    prompt = """
Hãy tạo 3 nhiệm vụ lập trình Python ở mức cơ bản để kiểm tra một AI coding assistant.
Mỗi nhiệm vụ gồm:
- "task": mô tả nhiệm vụ
- "solution_criteria": tiêu chí để đánh giá lời giải đúng
""".strip()

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "tasks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "task": {"type": "string"},
                                    "solution_criteria": {"type": "string"},
                                },
                                "required": ["task", "solution_criteria"],
                                "additionalProperties": False,
                            },
                        }
                    },
                    "required": ["tasks"],
                    "additionalProperties": False,
                },
            }
        },
    )
    data = json.loads(response.content[0].text)
    return data["tasks"]


# =====================================================================
# BƯỚC 2: CHẠY PROMPT CẦN ĐÁNH GIÁ
# =====================================================================
# Đây là prompt mà ta muốn ĐO chất lượng. Hàm này nhận 1 test case,
# ghép vào prompt, gọi Claude và trả về output.

def run_prompt(test_case):
    """Chạy prompt-đang-đánh-giá trên 1 test case, trả về output text."""

    # ===== ĐÂY LÀ PROMPT BẠN MUỐN ĐÁNH GIÁ / CẢI THIỆN =====
    prompt = f"""
Hãy giải nhiệm vụ lập trình sau bằng Python.
Chỉ trả về code, kèm comment ngắn gọn giải thích.

Nhiệm vụ: {test_case["task"]}
""".strip()

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# =====================================================================
# BƯỚC 3: CHẤM ĐIỂM (Grading) — 3 PHƯƠNG PHÁP
# =====================================================================

# ---- 3a. CODE-BASED GRADING (Chấm bằng code) ----
# Dùng khi câu trả lời có thể kiểm tra bằng luật cứng:
#   - exact match (khớp tuyệt đối)
#   - contains (chứa từ khóa)
#   - chạy code và so output...
# Ưu: nhanh, rẻ, khách quan tuyệt đối.
# Nhược: chỉ dùng được cho bài toán có đáp án rõ ràng.
def grade_by_code(output):
    """Ví dụ đơn giản: kiểm tra output có chứa từ khóa 'def ' không."""
    score = 10 if "def " in output else 0
    return {"score": score, "reasoning": "Có chứa định nghĩa hàm" if score else "Thiếu hàm"}


# ---- 3b. MODEL-BASED GRADING / "LLM as a Judge" (Dùng AI chấm AI) ----
# Đây là phương pháp MẠNH NHẤT và phổ biến nhất trong khóa học.
# Ý tưởng: dùng 1 con Claude khác làm "giám khảo", chấm điểm output
# dựa trên task + tiêu chí, và bắt nó trả về JSON {score, reasoning}.
def grade_by_model(test_case, output):
    """Dùng Claude làm giám khảo chấm điểm 1-10."""

    grader_prompt = f"""
Bạn là một giám khảo nghiêm khắc đánh giá lời giải lập trình.

<nhiem_vu>
{test_case["task"]}
</nhiem_vu>

<tieu_chi_danh_gia>
{test_case["solution_criteria"]}
</tieu_chi_danh_gia>

<loi_giai_can_cham>
{output}
</loi_giai_can_cham>

Hãy chấm điểm lời giải từ 1 đến 10 dựa trên tính đúng đắn, đầy đủ
và việc đáp ứng tiêu chí. Giải thích lý do ngắn gọn.
""".strip()

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": grader_prompt}],
        # Bắt giám khảo trả về JSON có cấu trúc -> dễ xử lý
        output_config={
            "format": {
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "reasoning": {"type": "string"},
                        "score": {"type": "integer"},
                    },
                    "required": ["reasoning", "score"],
                    "additionalProperties": False,
                },
            }
        },
    )
    return json.loads(response.content[0].text)


# ---- 3c. HUMAN GRADING (Con người chấm) ----
# Chính xác nhất (đặc biệt cho task chủ quan) nhưng chậm và tốn kém.
# Thường dùng để kiểm tra chéo, hoặc tạo "chuẩn vàng" để hiệu chỉnh
# lại model-based grader. (Không code mẫu ở đây.)


# =====================================================================
# BƯỚC 4: GHÉP TẤT CẢ — CHẠY EVAL TRÊN CẢ DATASET
# =====================================================================
def run_test_case(test_case):
    """Chạy + chấm điểm 1 test case."""
    output = run_prompt(test_case)
    grade = grade_by_model(test_case, output)
    return {
        "task": test_case["task"],
        "output": output,
        "score": grade["score"],
        "reasoning": grade["reasoning"],
    }


def run_eval(dataset):
    """Chạy toàn bộ pipeline đánh giá và in báo cáo."""
    results = []
    for i, test_case in enumerate(dataset, 1):
        print(f"\n=== Test {i}/{len(dataset)} ===")
        result = run_test_case(test_case)
        results.append(result)
        print(f"Nhiệm vụ : {result['task']}")
        print(f"Điểm     : {result['score']}/10")
        print(f"Lý do    : {result['reasoning']}")

    # Tổng hợp: điểm trung bình toàn bộ
    avg = sum(r["score"] for r in results) / len(results)
    print(f"\n{'='*50}")
    print(f"ĐIỂM TRUNG BÌNH: {avg:.2f}/10")
    print(f"{'='*50}")
    return results


# =====================================================================
# CHẠY THỬ
# =====================================================================
if __name__ == "__main__":
    # In ra dataset đang dùng
    run_eval(dataset)

    # Thử nhờ Claude tự sinh dataset rồi đánh giá:
    # new_dataset = generate_dataset()
    # run_eval(new_dataset)
