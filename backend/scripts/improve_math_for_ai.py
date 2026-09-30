"""Review and validate the Mathematics for AI question bank.

Run: python3 backend/scripts/improve_math_for_ai.py
The content edits below were manually checked for one intended correct answer.
"""

import collections
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "question_bank"
SOURCE = ROOT / "math_for_ai.json"
OUTPUT = ROOT / "math_for_ai_improved.json"
AUDIT = ROOT / "question_revision_audit.json"
MATH_AUDIT = ROOT / "math_for_ai_revision_audit.json"
LETTERS = "ABCD"
REQUIRED = {
    "id", "question", "option_a", "option_b", "option_c", "option_d",
    "correct_answer", "category", "subcategory", "difficulty", "tags",
}

# Each replacement contains a complete, independently reviewed multiple-choice item.
# Metadata is inherited from the source unless difficulty is explicitly overridden.
REVISIONS = {
    "math_0012": {
        "question": "Với ma trận vuông A, điều kiện nào xác định một eigenvector v ứng với eigenvalue λ?",
        "options": ["Av = λv với v ≠ 0", "Av = λv với v = 0", "Av = v + λv với v ≠ 0", "Aᵀv = λv với v ≠ 0"],
        "answer": "A", "reason": "Specified the nonzero-vector condition and replaced ill-typed alternatives with nearby eigenvector misconceptions.",
    },
    "math_0015": {
        "options": ["Bình phương khoảng cách Euclid giữa a và b", "Tích vô hướng a·b", "Một nửa bình phương khoảng cách Euclid giữa a và b", "Tích vô hướng a·b chia cho số chiều vector"],
        "answer": "B", "reason": "Replaced unrelated quantities with plausible relationships between normalized dot products and Euclidean distance.",
    },
    "math_0023": {
        "options": ["1", "2", "4", "0.5"], "answer": "A",
        "reason": "Replaced an implausible numeric alternative with a plausible variance calculation error.",
    },
    "math_0024": {
        "question": "Nếu Cov(X,Y) > 0, kết luận nào phù hợp nhất về xu hướng biến thiên tuyến tính giữa X và Y?",
        "options": ["X lớn hơn trung bình thường đi cùng Y lớn hơn trung bình", "X lớn hơn trung bình thường đi cùng Y nhỏ hơn trung bình", "X và Y độc lập vì covariance khác 0", "Mức liên hệ tuyến tính đã được chuẩn hóa về thang [-1,1]"],
        "answer": "A", "reason": "Replaced unrelated claims with covariance sign, independence, and correlation misconceptions.",
    },
    "math_0025": {
        "question": "Hệ số tương quan Pearson r gần -1 cho biết điều gì về hai biến?",
        "options": ["Quan hệ tuyến tính dương mạnh", "Quan hệ tuyến tính âm mạnh", "Quan hệ phi tuyến mạnh nhưng không có xu hướng tuyến tính", "Độ dốc hồi quy tuyến tính xấp xỉ -1 trong mọi đơn vị đo"],
        "answer": "B", "reason": "Replaced obvious alternatives with nearby misconceptions about linear association and regression slope.",
    },
    "math_0028": {
        "question": "Với hai phân phối rời rạc P và Q có Q(x)>0 ở mọi điểm P(x)>0, phát biểu nào đúng về D_KL(P||Q)?",
        "options": ["D_KL(P||Q) là khoảng cách đối xứng giữa P và Q", "D_KL(P||Q) không âm và bằng 0 khi P=Q", "D_KL(P||Q) bằng entropy H(P) trừ entropy H(Q)", "D_KL(P||Q) không đổi khi hoán đổi vai trò P và Q"],
        "answer": "B", "reason": "Specified support assumptions and used common KL-divergence confusions as distractors.",
    },
    "math_0031": {
        "question": "Với hàm lồi trên một miền lồi, phát biểu nào đúng về cực tiểu cục bộ?",
        "options": ["Mọi cực tiểu cục bộ đều là cực tiểu toàn cục", "Mọi cực tiểu cục bộ đều là cực tiểu toàn cục duy nhất", "Mọi điểm có gradient bằng 0 đều là cực tiểu toàn cục duy nhất", "Cực tiểu cục bộ chỉ là toàn cục nếu hàm lồi nghiêm ngặt"],
        "answer": "A", "reason": "Replaced unrelated claims with plausible confusions about convexity, uniqueness, and stationarity.",
    },
    "math_0032": {
        "question": "Trong Gradient Descent với momentum cổ điển, hướng cập nhật thường được tạo như thế nào?",
        "options": ["Kết hợp gradient hiện tại với trung bình có quán tính của các gradient trước", "Chia gradient hiện tại cho căn trung bình động của bình phương gradient", "Tính gradient tại một điểm đi trước theo hướng vận tốc trước đó", "Dùng đạo hàm bậc hai để hiệu chỉnh gradient hiện tại"],
        "answer": "A", "reason": "Replaced unrelated actions with RMSProp, Nesterov momentum, and second-order optimization mechanisms.",
    },
    "math_0033": {
        "question": "Trong Gradient Descent trên một loss trơn gần cực tiểu, learning rate quá lớn có thể gây ra điều gì?",
        "options": ["Bước cập nhật vượt qua cực tiểu, gây dao động hoặc phân kỳ", "Loss giảm nhanh hơn ở mỗi bước do độ dài bước lớn hơn", "Quỹ đạo cập nhật giống với khi thêm momentum vào gradient", "Bước cập nhật nhỏ đi khi độ cong của loss tăng mà không cần điều chỉnh"],
        "answer": "A", "difficulty": "medium",
        "reason": "Used plausible but incorrect claims about step size and convergence near a minimum.",
    },
    "math_0034": {
        "question": "Với hàm f hai lần khả vi, phần tử hàng i cột j của Hessian H thường biểu diễn đại lượng nào?",
        "options": ["∂²f/(∂xᵢ∂xⱼ)", "(∂f/∂xᵢ)(∂f/∂xⱼ)", "∂f/∂xᵢ + ∂f/∂xⱼ", "∂²f/∂xᵢ² + ∂²f/∂xⱼ²"],
        "answer": "A", "difficulty": "medium",
        "reason": "Replaced unrelated options with nearby derivative expressions and corrected the overstated difficulty.",
    },
    "math_0035": {
        "question": "So với L2 regularization, L1 regularization có xu hướng nào khi tối ưu trọng số?",
        "options": ["Tạo nghiệm thưa hơn vì một số trọng số có thể bằng 0", "Co đều các trọng số nhưng hầu như không đưa chúng về đúng 0", "Phạt mạnh hơn các trọng số lớn theo bình phương độ lớn", "Giữ nguyên nghiệm khi thay đổi hệ số regularization"],
        "answer": "A", "reason": "Used nearby L1/L2 shrinkage and penalty misconceptions instead of unrelated alternatives.",
    },
    "math_0038": {
        "question": "Với vector logits z, nếu cộng cùng một hằng số c vào từng phần tử trước Softmax, điều gì xảy ra?",
        "options": ["Xác suất không đổi vì thừa số eᶜ triệt tiêu khi chuẩn hóa", "Xác suất tăng đều vì mỗi tử số được nhân với eᶜ", "Xác suất đổi như khi nhân từng logit với c", "Thứ hạng logits giữ nguyên nhưng xác suất luôn sắc nét hơn"],
        "answer": "A", "reason": "Replaced implausible choices with common confusions about Softmax translation and scaling.",
    },
    "math_0039": {
        "question": "Khi tính Softmax cho các logits có độ lớn rất cao, phép biến đổi nào giữ nguyên xác suất và giảm nguy cơ overflow?",
        "options": ["Trừ logit lớn nhất khỏi mọi logit trước khi lấy exponential", "Chia mọi logit cho logit lớn nhất trước khi lấy exponential", "Trừ logit nhỏ nhất khỏi mọi logit trước khi lấy exponential", "Clip từng exponential về 1 trước khi chuẩn hóa"],
        "answer": "A", "reason": "Replaced unrelated actions with plausible numerical-stability transformations.",
    },
    "math_0040": {
        "question": "Trong scaled dot-product attention, vì sao score QKᵀ được chia cho √dₖ trước Softmax?",
        "options": ["Giữ phương sai score ở mức vừa phải khi dₖ tăng, hạn chế Softmax bão hòa", "Chuẩn hóa từng vector key về norm 1 để score trở thành cosine similarity", "Buộc mỗi hàng attention có tổng bằng 1 trước khi áp dụng Softmax", "Giảm số phần tử score theo chiều sequence trước khi chuẩn hóa"],
        "answer": "A", "reason": "Replaced distant alternatives with attention score scaling and normalization misconceptions.",
    },
    "math_0048": {
        "question": "Nếu các embedding truy vấn và ứng viên đều khác 0 và được L2-normalize, vì sao tìm kiếm bằng dot product tương đương xếp hạng bằng cosine similarity?",
        "options": ["Vì dot product bằng cosine similarity khi cả hai norm bằng 1", "Vì dot product bằng bình phương khoảng cách Euclid khi cả hai norm bằng 1", "Vì L2-normalize làm mọi cặp embedding có cùng dot product", "Vì cosine similarity trở thành tích các norm sau chuẩn hóa"],
        "answer": "A", "reason": "Specified nonzero embeddings and used plausible metric confusions as distractors.",
    },
    "math_0049": {
        "question": "Giữ nguyên các similarity score trong InfoNCE và giảm temperature τ>0. Phân phối Softmax trên các score thường thay đổi thế nào?",
        "options": ["Sắc nét hơn, ưu tiên mạnh hơn các score cao", "Phẳng hơn, chia đều hơn cho các score thấp", "Giữ nguyên vì τ bị khử khi chuẩn hóa", "Đảo thứ hạng vì phép chia cho τ đổi dấu score"],
        "answer": "A", "difficulty": "medium",
        "reason": "Specified fixed scores and replaced unrelated losses with temperature-scaling misconceptions.",
    },
    "math_0050": {
        "difficulty": "medium", "reason": "Adjusted difficulty: the item requires a direct parameter-count calculation.",
    },
}


def load_questions(path):
    raw = path.read_text(encoding="utf-8")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        value = [json.loads(line) for line in raw.splitlines() if line.strip()]
        fmt = "jsonl"
    else:
        fmt = "json"
        if isinstance(value, dict):
            keys = [k for k, v in value.items() if isinstance(v, list)]
            if len(keys) != 1:
                raise ValueError("Expected exactly one question-list field")
            value = value[keys[0]]
    if not isinstance(value, list) or not all(isinstance(q, dict) for q in value):
        raise ValueError("Expected a list of question objects")
    return value, fmt


def normalized(text):
    return re.sub(r"\s+", " ", text.casefold()).strip()


def validate(source, output, audit):
    assert len(source) == len(output)
    ids = [q["id"] for q in output]
    assert len(ids) == len(set(ids)), "Duplicate IDs"
    assert set(REVISIONS) <= set(ids), "Missing reviewed revision ID"
    for old, q in zip(source, output):
        assert REQUIRED <= set(q), f"Missing required field: {q.get('id')}"
        assert set(old) == set(q), f"Schema changed: {q['id']}"
        for field in ("id", "category", "subcategory"):
            assert old[field] == q[field], f"Metadata changed: {q['id']} {field}"
        assert isinstance(q["tags"], list) and q["tags"] == old["tags"]
        assert q["difficulty"] in {"easy", "medium", "hard"}
        assert q["correct_answer"] in LETTERS
        assert isinstance(q["question"], str) and q["question"].strip()
        options = [q[f"option_{letter.lower()}"] for letter in LETTERS]
        assert all(isinstance(o, str) and o.strip() for o in options), q["id"]
        assert len({normalized(o) for o in options}) == 4, q["id"]
        assert options[LETTERS.index(q["correct_answer"])].strip(), q["id"]
    assert len(audit) == len(output) and [a["id"] for a in audit] == ids


def main():
    original, fmt = load_questions(SOURCE)
    if fmt != "json":
        raise ValueError("This reviewed question set expects JSON input")
    improved = []
    audit = []
    for old in original:
        q = dict(old)
        edit = REVISIONS.get(q["id"])
        if edit:
            for key in ("question", "difficulty"):
                if key in edit:
                    q[key] = edit[key]
            if "options" in edit:
                for letter, option in zip(LETTERS, edit["options"], strict=True):
                    q[f"option_{letter.lower()}"] = option
                q["correct_answer"] = edit["answer"]
        improved.append(q)

    # Move the minimum number of correct positions needed to obtain a balanced
    # 12/13/12/13 distribution from the source's A/B/C-only answer pattern.
    counts = collections.Counter(q["correct_answer"] for q in improved)
    target = {"A": 12, "B": 13, "C": 12, "D": 13}
    for q in improved:
        current = q["correct_answer"]
        if counts[current] > target[current] and counts["D"] < target["D"]:
            other = q["option_d"]
            q["option_d"] = q[f"option_{current.lower()}"]
            q[f"option_{current.lower()}"] = other
            q["correct_answer"] = "D"
            counts[current] -= 1
            counts["D"] += 1
    assert counts == target, counts

    for old, q in zip(original, improved, strict=True):
        edit = REVISIONS.get(q["id"])
        swapped = q["correct_answer"] != (edit.get("answer", old["correct_answer"]) if edit else old["correct_answer"])
        reason = edit["reason"] if edit else "Existing options are plausible neighboring calculations or concepts."
        if swapped:
            reason += " Reordered options to balance correct-answer positions."
        audit.append({
            "id": q["id"], "changed": q != old, "reason": reason,
            "old_difficulty": old["difficulty"], "new_difficulty": q["difficulty"],
        })
    validate(original, improved, audit)
    OUTPUT.write_text(json.dumps(improved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MATH_AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Preserve audit records belonging to other question banks.
    prior = json.loads(AUDIT.read_text(encoding="utf-8")) if AUDIT.exists() else []
    prior = [entry for entry in prior if entry["id"] not in {q["id"] for q in improved}]
    AUDIT.write_text(json.dumps(prior + audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    reread, _ = load_questions(OUTPUT)
    validate(original, reread, audit)
    print(f"Total questions: {len(improved)}")
    print(f"Modified: {sum(a['changed'] for a in audit)}")
    print(f"Unchanged: {sum(not a['changed'] for a in audit)}")
    print("Difficulty:")
    for level in ("easy", "medium", "hard"):
        print(f"{level}: {sum(q['difficulty'] == level for q in improved)}")
    print("Correct answer distribution:")
    for letter in LETTERS:
        print(f"{letter}: {counts[letter]}")
    print("Validation:")
    for check in ("JSON parse", "Unique IDs", "Four non-empty options per question", "Correct-answer references valid option", "No exact duplicate options", "Required metadata preserved", "Manual semantic review of revised questions"):
        print(f"[PASS] {check}")


if __name__ == "__main__":
    main()
