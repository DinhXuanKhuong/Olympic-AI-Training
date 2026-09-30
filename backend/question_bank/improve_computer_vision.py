"""Review and validate the computer vision multiple-choice question bank."""

import collections
import json
from pathlib import Path


SOURCE = Path(__file__).with_name("computer_vision.json")
OUTPUT = SOURCE.with_name("computer_vision_improved.json")
AUDIT = SOURCE.with_name("question_revision_audit.json")

# Each edited item was checked for one intended answer and three related,
# technically incorrect alternatives. Unlisted questions retain their wording.
REVISIONS = {
    "cv_0000": {
        "question": "Trong hậu xử lý detector, kỹ thuật nào giữ box confidence cao nhất rồi loại các box cùng lớp có IoU vượt ngưỡng với nó?",
        "option_a": "Weighted Boxes Fusion",
        "option_b": "Soft-NMS",
        "option_d": "Bounding-box regression",
        "reason": "Replaced unrelated operations with nearby box post-processing methods.",
    },
    "cv_0001": {
        "question": "Trong xử lý ảnh cổ điển, toán tử Sobel theo hai hướng x và y chủ yếu cung cấp thông tin gì?",
        "option_a": "Đạo hàm bậc hai để tìm các điểm zero-crossing tại biên",
        "option_b": "Ước lượng gradient cường độ sáng theo hai hướng không gian",
        "option_c": "Biên mỏng sau bước non-maximum suppression theo hướng gradient",
        "option_d": "Ảnh được làm trơn bằng kernel Gaussian trước bước tính gradient",
        "difficulty": "medium",
        "reason": "Replaced unrelated image operations with adjacent edge-detection steps.",
    },
    "cv_0002": {
        "question": "Trong pipeline Canny cổ điển, bộ lọc nào được áp dụng trước khi tính gradient để giảm nhiễu Gaussian tần số cao?",
        "option_b": "Median filter để giảm nhiễu xung trước khi tính gradient",
        "option_c": "Bilateral filter để giữ biên khi giảm nhiễu cường độ",
        "option_d": "Non-maximum suppression để làm mỏng đáp ứng cạnh",
        "reason": "Replaced distant operations with plausible denoising and edge-processing alternatives.",
    },
    "cv_0003": {
        "option_b": "Chuẩn hóa cường độ về khoảng cố định bằng ánh xạ tuyến tính",
        "option_c": "Cân bằng độ tương phản riêng trong từng ô ảnh như CLAHE",
        "option_d": "Hiệu chỉnh độ sáng bằng một hàm lũy thừa gamma",
        "difficulty": "medium",
        "reason": "Replaced unrelated outcomes with nearby intensity-transformation methods.",
    },
    "cv_0004": {
        "option_a": "Mở rộng biên vùng trắng theo phần tử cấu trúc",
        "option_c": "Lấp các lỗ nhỏ bên trong vùng trắng bằng phép đóng",
        "option_d": "Loại điểm trắng lẻ bằng tổ hợp erosion rồi dilation",
        "reason": "Replaced implausible effects with neighboring morphology operations.",
    },
    "cv_0005": {
        "option_a": "Co biên vùng trắng theo phần tử cấu trúc",
        "option_b": "Loại điểm trắng nhỏ bằng erosion rồi dilation",
        "option_d": "Lấp các lỗ nhỏ bằng dilation rồi erosion",
        "reason": "Replaced unrelated effects with neighboring morphology operations.",
    },
    "cv_0006": {
        "option_b": "Mức độ thuần khiết của màu so với màu xám",
        "option_c": "Độ sáng tương đối của màu trong không gian HSV",
        "option_d": "Cường độ của kênh đỏ trong ảnh RGB tương ứng",
        "reason": "Replaced unrelated image properties with plausible color-component confusions.",
    },
    "cv_0007": {
        "option_a": "Bất biến với mọi phép biến dạng phối cảnh của đối tượng",
        "option_b": "Bất biến hoàn toàn với thay đổi chiếu sáng phi tuyến",
        "option_c": "Bất biến với che khuất phần lớn vùng lân cận keypoint",
        "reason": "Replaced obvious false claims with nearby limits of SIFT invariance.",
    },
    "cv_0008": {
        "option_a": "Phân bố cường độ sáng trong từng ô không xét hướng biến thiên",
        "option_c": "Vị trí và tỉ lệ của các keypoint bất biến theo phép xoay",
        "option_d": "Độ lớn đáp ứng của bộ lọc Gabor ở nhiều tần số",
        "reason": "Replaced distant features with related local image descriptors.",
    },
    "cv_0009": {
        "option_a": "Nhạy với dịch chuyển dù đã quét template khắp ảnh",
        "option_b": "Nhạy với thay đổi cường độ tuyến tính dù dùng normalized correlation",
        "option_c": "Nhạy với cả thay đổi tỉ lệ lẫn góc xoay của đối tượng",
        "option_d": "Nhạy với kích thước ảnh nền dù đối tượng và template không đổi",
        "reason": "Aligned alternatives around transformation sensitivity while preserving a single best answer.",
    },
    "cv_0010": {
        "option_b": "Chuyển động 3D tuyệt đối của vật thể trong hệ tọa độ thế giới",
        "option_c": "Độ dịch chuyển của camera tách khỏi chuyển động vật thể",
        "option_d": "Vùng ảnh có biên độ gradient lớn trong một khung hình",
        "reason": "Replaced unrelated quantities with neighboring motion-estimation concepts.",
    },
    "cv_0011": {
        "option_a": "Hệ số stride dùng khi quét kernel",
        "option_c": "Số pixel padding quanh feature map",
        "option_d": "Kích thước không gian của kernel tích chập",
        "reason": "Aligned distractors to Conv2D configuration versus learned parameters.",
    },
    "cv_0015": {
        "question": "Trong chuỗi Conv2D → BatchNorm → ReLU thường gặp, BatchNorm được áp dụng ở đâu?",
        "option_a": "Trên đầu ra Conv2D trước khi áp dụng ReLU",
        "option_b": "Trên đầu ra ReLU trước khi áp dụng Conv2D",
        "option_c": "Trên trọng số kernel trước khi tính tích chập",
        "option_d": "Trên logits sau Softmax của classifier",
        "reason": "Clarified the architecture and replaced distant placements with stage confusions.",
    },
    "cv_0016": {
        "option_a": "Giảm training loss bằng cách nhân đôi mỗi mẫu y hệt",
        "option_b": "Chuẩn hóa kích thước mọi ảnh mà không tạo biến thể mới",
        "option_c": "Tăng năng lực biểu diễn của backbone bằng thêm tham số",
        "reason": "Replaced implausible claims with nearby training and preprocessing misconceptions.",
    },
    "cv_0017": {
        "option_a": "Tăng receptive field bằng cách thay mọi kernel 3×3 bằng 7×7",
        "option_b": "Chuẩn hóa activation của mỗi residual block theo batch",
        "option_d": "Giảm gradient bằng cách chặn đường truyền qua các block sâu",
        "reason": "Replaced unrelated claims with plausible residual-network mechanism confusions.",
    },
    "cv_0018": {
        "option_a": "Giảm phép nhân bằng cách bỏ lọc không gian, chỉ trộn kênh bằng 1×1",
        "option_b": "Giảm chi phí tính toán so với convolution tiêu chuẩn",
        "option_c": "Giảm tính toán bằng cách bỏ hoàn toàn phép trộn thông tin giữa các kênh",
        "option_d": "Giảm chi phí chủ yếu bằng cách giảm số vị trí không gian đầu ra",
        "reason": "Focused alternatives on the actual source of MobileNet compute savings.",
    },
    "cv_0019": {
        "option_a": "Tăng depth và width cùng hệ số, giữ resolution cố định",
        "option_b": "Tăng width và resolution cùng hệ số, giữ depth cố định",
        "option_c": "Tăng depth và resolution cùng hệ số, giữ width cố định",
        "reason": "Replaced trivial single-axis choices with plausible partial scaling strategies.",
    },
    "cv_0021": {
        "option_a": "Bản đồ đặc trưng ở block tích chập đầu tiên trước pooling",
        "option_c": "Logits của classifier ImageNet sau lớp tuyến tính cuối",
        "option_d": "Phân phối xác suất ImageNet sau lớp Softmax cuối",
        "reason": "Replaced unrelated tensors with nearby ResNet feature extraction points.",
    },
    "cv_0022": {
        "option_a": "Fine-tune toàn bộ backbone ngay với learning rate như khi train mới",
        "option_b": "Đóng băng classifier mới và chỉ cập nhật toàn bộ backbone",
        "option_d": "Giữ classifier ImageNet rồi chỉ hiệu chỉnh BatchNorm statistics",
        "reason": "Replaced implausible strategies with realistic small-data fine-tuning choices.",
    },
    "cv_0023": {
        "question": "Trong NMS chuẩn, sau khi giữ box có confidence cao nhất, các box còn lại cùng lớp thường bị loại theo tiêu chí nào?",
        "option_a": "Confidence thấp hơn box được giữ, bất kể mức chồng lấn",
        "option_b": "Diện tích box nhỏ hơn box được giữ theo một ngưỡng",
        "option_c": "IoU với box được giữ vượt ngưỡng chồng lấn đặt trước",
        "option_d": "Khoảng cách tâm box vượt ngưỡng khoảng cách đặt trước",
        "difficulty": "medium",
        "reason": "Converted a duplicate NMS identification item into a mechanism question.",
    },
    "cv_0025": {
        "option_b": "Chỉ định các proposal cuối cùng sau khi đã áp dụng NMS",
        "option_c": "Mã hóa duy nhất vị trí tâm, không chứa kích thước box",
        "option_d": "Thay thế các dự đoán offset và class trên feature map",
        "reason": "Replaced unrelated operations with SSD anchor-function misconceptions.",
    },
    "cv_0026": {
        "option_a": "Detector một giai đoạn dự đoán trực tiếp từ feature map",
        "option_b": "Detector hai giai đoạn tạo proposal rồi phân loại và hiệu chỉnh box",
        "option_c": "Detector hai giai đoạn: phân loại ảnh rồi tạo proposal",
        "option_d": "Detector một giai đoạn chỉ dự đoán vùng bằng RPN",
        "correct_answer": "B",
        "difficulty": "medium",
        "reason": "Replaced unrelated detector labels with plausible stage-order distinctions.",
    },
    "cv_0027": {
        "option_b": "YOLO tạo region proposals rồi phân loại bằng head riêng ở giai đoạn hai",
        "option_c": "YOLO chỉ phân loại toàn ảnh và suy ra box từ activation map",
        "option_d": "YOLO tách dự đoán box và class thành hai lần chạy backbone",
        "difficulty": "medium",
        "reason": "Replaced unrelated claims with nearby detector architecture confusions.",
    },
    "cv_0028": {
        "option_a": "Gán mỗi prediction với ground truth gần nhất một cách độc lập",
        "option_c": "Ghép nhiều object queries với cùng một ground truth nếu IoU cao",
        "option_d": "Chọn các box confidence cao và loại box trùng bằng NMS",
        "reason": "Replaced distant tasks with assignment and duplicate-removal mechanisms.",
    },
    "cv_0029": {
        "option_a": "DETR dùng anchor mặc định nhưng bỏ bước Hungarian matching",
        "option_b": "DETR dùng RPN để tạo proposal trước decoder Transformer",
        "option_c": "DETR dự đoán pixel mask rồi suy ra box bằng connected components",
        "reason": "Replaced impossible claims with neighboring detector design alternatives.",
    },
    "cv_0030": {
        "option_a": "Độ chính xác phân lớp trung bình trên mọi pixel của ảnh",
        "option_c": "IoU trung bình của các box khớp, không xét confidence",
        "option_d": "Recall tại một ngưỡng confidence cố định, không xét precision",
        "reason": "Replaced unrelated quantities with closely related evaluation metrics.",
    },
    "cv_0031": {
        "option_a": "Semantic Segmentation gán nhãn từng pixel; Instance Segmentation chỉ gán nhãn toàn ảnh",
        "option_b": "Instance Segmentation tách từng cá thể nhưng không gán loại đối tượng",
        "option_d": "Semantic Segmentation phân biệt từng cá thể; Instance Segmentation chỉ phân biệt lớp",
        "reason": "Replaced obvious errors with nearby segmentation-label distinctions.",
    },
    "cv_0032": {
        "question": "Khi vùng foreground rất nhỏ so với background trong binary segmentation, loss nào trực tiếp tối ưu độ chồng lấn giữa hai vùng?",
        "option_a": "Binary Cross-Entropy không trọng số",
        "option_b": "Cross-Entropy có trọng số theo tần suất lớp",
        "option_c": "Focal Loss giảm ảnh hưởng của các pixel dễ",
        "option_d": "Dice Loss dựa trên độ chồng lấn foreground",
        "reason": "Specified the loss property to avoid several valid imbalance remedies.",
    },
    "cv_0034": {
        "option_a": "Mở rộng receptive field bằng tăng stride và giảm kích thước feature map",
        "option_b": "Mở rộng receptive field bằng tăng kích thước kernel và số tham số",
        "option_d": "Giữ receptive field cố định nhưng tăng mật độ lấy mẫu không gian",
        "reason": "Replaced unrelated effects with neighboring receptive-field mechanisms.",
    },
    "cv_0035": {
        "option_a": "Một nhánh chỉ dự đoán class cho toàn bộ ảnh đầu vào",
        "option_c": "Một nhánh chỉ tạo region proposals thay cho RPN",
        "option_d": "Một nhánh dự đoán semantic mask chung cho toàn ảnh",
        "reason": "Replaced cross-domain choices with nearby detection and segmentation heads.",
    },
    "cv_0036": {
        "option_a": "Micro-averaged pixel accuracy trên tất cả lớp",
        "option_b": "Overall pixel accuracy tính trên toàn bộ ảnh",
        "option_d": "Tỉ lệ pixel background được gán đúng",
        "reason": "Replaced training hyperparameters with competing segmentation metrics.",
    },
    "cv_0038": {
        "option_a": "Underfitting do mô hình không khớp cả tập huấn luyện",
        "option_c": "Data leakage làm validation score cao hơn training score",
        "option_d": "Độ lệch nhãn khiến training IoU giảm dần theo epoch",
        "reason": "Replaced impossible diagnoses with related train-validation failure patterns.",
    },
    "cv_0039": {
        "option_a": "Dự đoán token tiếp theo từ chuỗi ghép ảnh và văn bản",
        "option_b": "Tái tạo pixel ảnh từ embedding văn bản bằng decoder",
        "option_d": "Căn chỉnh ảnh-văn bản chỉ bằng nhãn phân lớp ImageNet",
        "reason": "Replaced unrelated training tasks with plausible multimodal objectives.",
    },
    "cv_0040": {
        "option_a": "So sánh embedding ảnh với vector của lớp đã học trong classifier head",
        "option_c": "So sánh embedding ảnh với pixel trung bình của mỗi lớp mới",
        "option_d": "Dùng tên lớp để tạo ảnh mẫu rồi fine-tune image encoder",
        "reason": "Replaced unrelated approaches with plausible zero-shot classification confusions.",
    },
    "cv_0041": {
        "question": "DINOv2 học biểu diễn ảnh chủ yếu từ loại tín hiệu huấn luyện nào?",
        "option_a": "Tín hiệu tự giám sát từ các góc nhìn của ảnh không cần nhãn lớp",
        "option_b": "Nhãn lớp ImageNet dùng trong cross-entropy có giám sát",
        "option_c": "Cặp ảnh-văn bản dùng trong contrastive learning kiểu CLIP",
        "option_d": "Mask pixel ground truth dùng trong segmentation có giám sát",
        "reason": "Replaced unrelated model categories with neighboring supervision signals.",
    },
    "cv_0042": {
        "option_a": "Tạo mask từ nhãn lớp cố định mà không dùng prompt không gian",
        "option_b": "Tạo caption từ ảnh rồi suy ra mask từ câu mô tả",
        "option_c": "Tạo box đối tượng từ prompt văn bản tên lớp mà không tạo mask",
        "reason": "Replaced unrelated tasks with nearby prompt-based vision behaviors.",
    },
    "cv_0043": {
        "option_a": "Dự đoán nhãn lớp của ảnh gốc từ ảnh đã thêm nhiễu",
        "option_c": "Dự đoán trực tiếp ảnh sạch chỉ từ text prompt khi không có nhiễu",
        "option_d": "Phân biệt ảnh thật và ảnh giả bằng discriminator đối kháng",
        "reason": "Replaced unrelated tasks with neighboring image-generation objectives.",
    },
    "cv_0044": {
        "option_a": "Khử nhiễu trực tiếp trên pixel rồi chỉ nén ảnh cuối cùng",
        "option_b": "Khử nhiễu trên embedding văn bản, còn ảnh được tạo không qua decoder",
        "option_d": "Chạy diffusion trên không gian pixel với ít bước lấy mẫu hơn",
        "reason": "Replaced obvious claims with nearby diffusion-space confusions.",
    },
    "cv_0045": {
        "option_b": "Tăng độ đa dạng ảnh mẫu nhưng thường giảm mức bám prompt",
        "option_c": "Giảm ảnh hưởng của nhánh có điều kiện so với nhánh vô điều kiện",
        "option_d": "Thay đổi số bước khử nhiễu mà không đổi điều kiện văn bản",
        "reason": "Replaced implausible outcomes with related guidance-scale tradeoffs.",
    },
    "cv_0046": {
        "option_a": "Biến token văn bản thành patch embedding trước vision encoder",
        "option_b": "Tính attention mask để chặn token tương lai trong decoder",
        "option_c": "Dự đoán trực tiếp class ID từ đặc trưng thị giác chưa căn chỉnh",
        "reason": "Replaced unrelated components with nearby multimodal interface roles.",
    },
    "cv_0047": {
        "option_a": "Captioning trả lời câu hỏi cụ thể; VQA mô tả ảnh tổng quát",
        "option_b": "Captioning tạo nhãn lớp; VQA tạo bounding box theo câu hỏi",
        "option_d": "Captioning tạo mô tả ảnh; VQA chỉ chọn một ảnh phù hợp câu hỏi",
        "reason": "Replaced impossible claims with neighboring vision-language task confusions.",
    },
    "cv_0048": {
        "option_a": "Phát hiện lớp mới chỉ bằng cách thêm một head phân lớp ngẫu nhiên",
        "option_c": "Phát hiện lớp mới từ embedding ảnh mà không cần biểu diễn tên lớp",
        "option_d": "Phát hiện lớp mới bằng cách bỏ dự đoán box và chỉ phân loại ảnh",
        "reason": "Replaced impossible claims with nearby open-vocabulary mechanism confusions.",
    },
    "cv_0049": {
        "option_b": "Phát hiện ký tự đơn lẻ rồi gán class vật thể cho từng ký tự",
        "option_c": "Phân đoạn dòng văn bản rồi sinh caption cho toàn ảnh",
        "option_d": "Nhận dạng chuỗi ký tự trước rồi phát hiện vị trí từ chuỗi",
        "reason": "Replaced unrelated pipelines with neighboring text-localization tasks.",
    },
    "cv_0050": {
        "option_a": "Giảm dung lượng nhưng luôn tăng số phép tính trên thiết bị",
        "option_b": "Giảm số lượng tham số nhưng giữ mỗi trọng số ở FP32",
        "option_d": "Giảm dung lượng và bảo đảm giữ nguyên độ chính xác FP32",
        "reason": "Replaced unrelated effects with realistic quantization tradeoff confusions.",
    },
}

# Preserve answer content while avoiding a position bias.
SWAP_ANSWER_WITH_D = {"cv_0001", "cv_0011", "cv_0028", "cv_0035", "cv_0043", "cv_0047"}


def load_questions(path):
    raw = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = [json.loads(line) for line in raw.splitlines() if line.strip()]
        return data, "jsonl"
    if isinstance(data, list):
        return data, "array"
    if isinstance(data, dict):
        lists = [(key, value) for key, value in data.items() if isinstance(value, list)]
        if len(lists) != 1:
            raise ValueError("Expected exactly one question list in JSON object")
        return data, lists[0][0]
    raise ValueError("Unsupported question-bank format")


def normalize(s):
    return " ".join(s.casefold().split())


def validate(original, revised):
    assert len(original) == len(revised)
    ids = [q["id"] for q in revised]
    assert len(ids) == len(set(ids)), "Duplicate IDs"
    for before, after in zip(original, revised):
        assert set(before) == set(after), f"Schema changed: {after['id']}"
        assert all(before[k] == after[k] for k in ("id", "category", "subcategory"))
        assert isinstance(after["tags"], list) and after["tags"]
        assert after["difficulty"] in {"easy", "medium", "hard"}
        assert after["correct_answer"] in {"A", "B", "C", "D"}
        assert isinstance(after["question"], str) and after["question"].strip()
        options = [after[f"option_{letter}"] for letter in "abcd"]
        assert all(isinstance(x, str) and x.strip() for x in options)
        assert len({normalize(x) for x in options}) == 4, f"Duplicate options: {after['id']}"
        assert after[f"option_{after['correct_answer'].lower()}"]


def main():
    data, kind = load_questions(SOURCE)
    questions = data if isinstance(data, list) else data[kind]
    assert len(questions) == 51
    assert set(REVISIONS) <= {q["id"] for q in questions}
    revised = []
    audit = []
    for item in questions:
        updated = dict(item)
        changes = REVISIONS.get(item["id"])
        if changes:
            updated.update({k: v for k, v in changes.items() if k != "reason"})
        if item["id"] in SWAP_ANSWER_WITH_D:
            correct = updated["correct_answer"].lower()
            updated[f"option_{correct}"], updated["option_d"] = updated["option_d"], updated[f"option_{correct}"]
            updated["correct_answer"] = "D"
        revised.append(updated)
        audit.append({
            "id": item["id"],
            "changed": updated != item,
            "reason": changes["reason"] if updated != item else "Existing options are clear, relevant, and sufficiently competitive.",
            "old_difficulty": item["difficulty"],
            "new_difficulty": updated["difficulty"],
        })
    validate(questions, revised)
    output_data = revised if isinstance(data, list) else {**data, kind: revised}
    output_path = OUTPUT.with_suffix(".jsonl") if kind == "jsonl" else OUTPUT
    output_text = ("\n".join(json.dumps(q, ensure_ascii=False) for q in revised) + "\n") if kind == "jsonl" else (json.dumps(output_data, ensure_ascii=False, indent=2) + "\n")
    output_path.write_text(output_text, encoding="utf-8")
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Re-parse actual files as the final syntax and structural gate.
    if kind == "jsonl":
        saved_questions = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        saved = json.loads(output_path.read_text(encoding="utf-8"))
        saved_questions = saved if isinstance(saved, list) else saved[kind]
    validate(questions, saved_questions)
    assert len(json.loads(AUDIT.read_text(encoding="utf-8"))) == len(questions)
    print(f"Total questions: {len(revised)}")
    print(f"Modified: {sum(x['changed'] for x in audit)}")
    print(f"Unchanged: {sum(not x['changed'] for x in audit)}")
    print("Difficulty:", dict(collections.Counter(x["difficulty"] for x in revised)))
    print("Correct answer distribution:", dict(collections.Counter(x["correct_answer"] for x in revised)))
    print("Validation: JSON parse, unique IDs, four non-empty distinct options, valid answer references, preserved schema and metadata [PASS]")


if __name__ == "__main__":
    main()
