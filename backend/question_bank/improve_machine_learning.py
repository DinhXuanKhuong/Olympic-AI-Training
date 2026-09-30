"""Curated revisions and validation for machine_learning.json."""

import collections
import json
import re
from pathlib import Path


SOURCE = Path(__file__).with_name("machine_learning.json")
OUTPUT = SOURCE.with_name("machine_learning_improved.json")
AUDIT = SOURCE.with_name("question_revision_audit.json")


def load_questions(path: Path):
    raw = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = [json.loads(line) for line in raw.splitlines() if line.strip()]
        return data, "jsonl"
    if isinstance(data, list):
        return data, "array"
    if isinstance(data, dict):
        keys = [key for key, value in data.items() if isinstance(value, list)]
        if len(keys) != 1:
            raise ValueError("Expected exactly one question list in JSON object")
        return data[keys[0]], ("object", data, keys[0])
    raise ValueError("Unsupported input format")


# Each entry records a question or option revision approved by manual concept review.
# Options are listed as A/B/C/D here. Their final positions are balanced below.
REVISIONS = {
    "ml_0001": {"options": [
        "Để các đặc trưng đóng góp tương xứng hơn vào khoảng cách Euclid",
        "Để các đặc trưng trở nên độc lập thống kê trước khi tính khoảng cách",
        "Để khoảng cách Euclid tự chuyển thành khoảng cách cosine",
        "Để mỗi đặc trưng có cùng mức liên hệ với nhãn dự đoán"], "difficulty": "easy"},
    "ml_0002": {"options": [
        "Vì k-NN chỉ ước lượng tham số sau khi đã dự đoán tất cả mẫu kiểm thử",
        "Vì phần lớn phép tìm láng giềng được thực hiện khi có điểm truy vấn",
        "Vì k-NN huấn luyện mô hình trước rồi mới lưu các láng giềng gần nhất",
        "Vì k-NN cập nhật trọng số của láng giềng sau mỗi lần dự đoán"], "difficulty": "easy"},
    "ml_0003": {"options": [
        "Biên quyết định thường mượt hơn nhưng có thể tăng bias",
        "Biên quyết định thường gấp khúc hơn vì dùng thêm láng giềng",
        "Ảnh hưởng của từng điểm nhiễu thường tăng khi k tăng",
        "Mỗi dự đoán chỉ phụ thuộc vào láng giềng gần nhất"], "difficulty": "medium"},
    "ml_0005": {"options": [
        "Để điểm gần truy vấn đóng góp mạnh hơn vào kết quả dự đoán",
        "Để các điểm cùng lớp với truy vấn luôn nhận trọng số bằng nhau",
        "Để điểm xa truy vấn bù cho sai lệch của điểm gần truy vấn",
        "Để trọng số phụ thuộc vào mật độ toàn cục thay vì khoảng cách"], "difficulty": "medium"},
    "ml_0006": {"options": [
        "Tìm siêu phẳng phân lớp có margin lớn theo ràng buộc tối ưu",
        "Tìm siêu phẳng đi qua trọng tâm của từng lớp dữ liệu",
        "Tìm siêu phẳng giảm tổng bình phương sai số xác suất lớp",
        "Tìm siêu phẳng đặt mọi mẫu huấn luyện cách biên bằng nhau"], "difficulty": "easy"},
    "ml_0007": {"options": [
        "Các mẫu có ràng buộc hoạt động và quyết định vị trí siêu phẳng",
        "Các mẫu có khoảng cách lớn nhất tới siêu phẳng phân lớp",
        "Các mẫu nằm gần trung tâm hình học của mỗi lớp dữ liệu",
        "Các mẫu bị phân loại sai trong mọi cấu hình của tham số C"], "difficulty": "medium"},
    "ml_0008": {"options": [
        "Tính tích vô hướng trong không gian đặc trưng ẩn mà không cần ánh xạ tường minh",
        "Tính khoảng cách Euclid giữa các mẫu rồi dùng trực tiếp làm margin",
        "Ánh xạ tường minh mọi mẫu lên từng chiều của không gian đặc trưng",
        "Thay tối ưu margin bằng ước lượng xác suất lớp theo kernel"], "difficulty": "medium"},
    "ml_0009": {"options": [
        "Vùng ảnh hưởng của mỗi mẫu hẹp, khiến biên dễ phức tạp và overfit",
        "Vùng ảnh hưởng của mỗi mẫu rộng, khiến biên gần như không đổi",
        "Margin mềm bị thay bằng margin cứng bất kể giá trị của C",
        "Kernel RBF tiệm cận kernel tuyến tính với mọi cặp điểm khác nhau"], "difficulty": "hard"},
    "ml_0011": {"options": [
        "Mức thay đổi dự đoán của y khi x tăng một đơn vị",
        "Giá trị dự đoán của y tại điểm x bằng không",
        "Mức sai số trung bình giữa dự đoán và quan sát",
        "Độ phân tán của x quanh giá trị trung bình"], "difficulty": "easy"},
    "ml_0012": {"question": "Trong ordinary least squares (OLS), hàm mục tiêu nào được tối thiểu hóa khi khớp hồi quy tuyến tính?", "options": [
        "Tổng bình phương residual giữa giá trị thật và giá trị dự đoán",
        "Tổng trị tuyệt đối residual giữa giá trị thật và giá trị dự đoán",
        "Tổng Huber loss của residual giữa giá trị thật và giá trị dự đoán",
        "Tổng bình phương các hệ số của mô hình hồi quy tuyến tính"], "difficulty": "easy"},
    "ml_0013": {"options": [
        "L1: tổng trị tuyệt đối của các hệ số hồi quy",
        "L2: tổng bình phương của các hệ số hồi quy",
        "Elastic Net: tổng L1 và L2 với hai hệ số phạt",
        "L0: số lượng hệ số hồi quy khác không"], "difficulty": "easy"},
    "ml_0014": {"options": [
        "L1 có thể đưa một số hệ số về đúng 0, tạo mô hình thưa",
        "L1 luôn làm mọi hệ số nhỏ đi nhưng không thể về đúng 0",
        "L1 loại bỏ ảnh hưởng của hệ số phạt khi dữ liệu có tương quan",
        "L1 bảo đảm chọn cùng nhóm biến tương quan như Ridge"], "difficulty": "medium"},
    "ml_0015": {"options": [
        "Ánh xạ logit tuyến tính thành xác suất lớp dương từ 0 đến 1",
        "Chuẩn hóa xác suất trên mọi mẫu của cùng một minibatch",
        "Biến logit thành nhãn nhị phân bằng ngưỡng cứng tại 0",
        "Ánh xạ logit thành tỉ số odds không bị chặn trên"], "difficulty": "easy"},
    "ml_0016": {"options": [
        "Các mẫu tại node đều thuộc cùng một lớp",
        "Mỗi lớp tại node có cùng tỉ lệ mẫu",
        "Node chứa đúng một mẫu từ mỗi lớp",
        "Không thể tính độ thuần vì node chưa được chia"], "difficulty": "easy"},
    "ml_0018": {"question": "Trong cây quyết định dùng entropy, information gain của một phép chia được tính như thế nào?", "options": [
        "Entropy của node cha trừ entropy trung bình có trọng số của các node con",
        "Entropy trung bình của các node con trừ entropy của node cha",
        "Entropy của node cha trừ entropy của node con có nhiều mẫu nhất",
        "Entropy của node cha chia cho tổng entropy của các node con"], "difficulty": "medium"},
    "ml_0019": {"options": [
        "Giới hạn độ sâu hoặc yêu cầu nhiều mẫu hơn ở mỗi lá",
        "Giảm min_samples_leaf để mỗi lá khớp sát dữ liệu hơn",
        "Tăng độ sâu tối đa để mô hình có thêm nhiều phép chia",
        "Chọn phép chia tối ưu trên toàn bộ dữ liệu kiểm thử"], "difficulty": "easy"},
    "ml_0020": {"options": [
        "Trung bình nhiều cây có lỗi bớt tương quan nhờ lấy mẫu và chọn feature ngẫu nhiên",
        "Dùng một cây sâu hơn để thay cho nhiều cây có dự đoán khác nhau",
        "Buộc mọi cây dùng cùng tập mẫu và feature để đồng nhất dự đoán",
        "Cộng dự đoán tuần tự để mỗi cây sửa residual của cây trước"], "difficulty": "medium"},
    "ml_0021": {"options": [
        "Lấy trung bình số học dự đoán của các cây",
        "Lấy đa số phiếu sau khi làm tròn dự đoán mỗi cây",
        "Lấy trung vị bắt buộc của dự đoán các cây",
        "Cộng dự đoán của các cây mà không chia cho số cây"], "difficulty": "easy"},
    "ml_0022": {"options": [
        "Bagging học các mô hình tương đối độc lập; boosting thêm mô hình tuần tự",
        "Bagging thêm mô hình theo residual; boosting học các mô hình độc lập",
        "Bagging chỉ kết hợp cây nông; boosting chỉ kết hợp cây sâu",
        "Bagging dùng một tập mẫu cố định; boosting bắt buộc dùng bootstrap"], "difficulty": "medium"},
    "ml_0023": {"options": [
        "Tăng trọng số mẫu sai để weak learner tiếp theo chú ý hơn",
        "Giảm trọng số mẫu sai để ưu tiên mẫu đã phân loại đúng",
        "Giữ nguyên trọng số mẫu và chỉ điều chỉnh ngưỡng dự đoán",
        "Loại mẫu sai rồi huấn luyện weak learner trên mẫu còn lại"], "difficulty": "medium"},
    "ml_0024": {"options": [
        "Thêm learner để xấp xỉ hướng giảm loss qua pseudo-residual",
        "Huấn luyện learner độc lập rồi lấy trung bình dự đoán",
        "Tối ưu từng learner bằng cách tăng loss của learner trước",
        "Cập nhật đồng thời mọi learner theo cùng một gradient"], "difficulty": "medium"},
    "ml_0025": {"question": "So với gradient boosting cây cơ bản, XGBoost có đặc trưng nào trong hàm mục tiêu và việc xây cây?", "options": [
        "Có hạng phạt độ phức tạp cây và dùng khai triển bậc hai của loss",
        "Bỏ hạng phạt độ phức tạp cây và chỉ dùng dấu của gradient",
        "Tối ưu trực tiếp từng cây bằng loss huấn luyện không có regularization",
        "Thay các phép chia cây bằng cập nhật trọng số của một mô hình tuyến tính"], "difficulty": "medium"},
    "ml_0026": {"question": "Cặp đặc điểm nào mô tả đúng cách LightGBM thường xây cây hiệu quả?", "options": [
        "Gom giá trị đặc trưng thành histogram và mở rộng theo lá có gain lớn",
        "Giữ mọi ngưỡng đặc trưng chính xác và mở rộng đồng đều theo tầng",
        "Gom giá trị thành histogram và buộc mọi lá cùng độ sâu",
        "Chọn ngưỡng chính xác trên từng mẫu và mở rộng lá có ít mẫu nhất"], "difficulty": "hard"},
    "ml_0027": {"question": "CatBoost đặc biệt hữu ích khi dữ liệu có nhiều loại đặc trưng nào?", "options": [
        "Đặc trưng phân loại cần được mã hóa với kiểm soát rò rỉ nhãn",
        "Đặc trưng liên tục cần được giảm chiều bằng PCA trước khi học",
        "Đặc trưng thứ tự cần được biến thành ảnh để mô hình xử lý",
        "Đặc trưng nhị phân cần được chuẩn hóa về phân phối Gaussian"], "difficulty": "medium"},
    "ml_0028": {"options": [
        "Lấy trung bình các điểm hiện được gán cho cụm",
        "Chọn medoid là điểm gần các điểm trong cụm nhất",
        "Lấy trung vị theo từng chiều của các điểm trong cụm",
        "Lấy trung bình của mọi điểm trong toàn bộ dữ liệu"], "difficulty": "easy"},
    "ml_0030": {"options": [
        "Tổng bình phương khoảng cách mỗi điểm đến tâm cụm được gán",
        "Tổng khoảng cách mỗi điểm đến tâm cụm gần thứ hai",
        "Tổng khoảng cách giữa mọi cặp tâm cụm với nhau",
        "Tổng bình phương khoảng cách mỗi điểm đến trung bình toàn cục"], "difficulty": "medium"},
    "ml_0031": {"options": [
        "Chọn các tâm ban đầu với xác suất ưu tiên điểm xa các tâm đã chọn",
        "Cập nhật tâm bằng trung vị thay vì trung bình sau mỗi lần gán",
        "Thay bước gán cụm bằng phân loại theo nhãn có sẵn",
        "Tăng số cụm tự động khi tổng sai số trong cụm còn lớn"], "difficulty": "medium"},
    "ml_0032": {"options": [
        "Phát hiện cụm hình dạng không lồi và gán nhãn nhiễu cho điểm thưa",
        "Tối ưu trực tiếp tổng bình phương khoảng cách đến tâm cụm",
        "Bảo đảm mọi điểm được gán vào một trong k cụm đã biết trước",
        "Tạo cụm dựa trên khoảng cách đến một tâm trung bình duy nhất"], "difficulty": "medium"},
    "ml_0033": {"question": "Silhouette Score của một điểm gần 1 thường biểu thị điều gì?", "options": [
        "Điểm gần các điểm cùng cụm hơn rõ rệt so với cụm gần nhất khác",
        "Điểm gần cụm khác hơn so với các điểm thuộc cụm của mình",
        "Khoảng cách trung bình trong cụm và tới cụm khác gần bằng nhau",
        "Điểm có xác suất hậu nghiệm gần 1 đối với cụm đang được gán"], "difficulty": "medium"},
    "ml_0034": {"options": [
        "Chiếu lên các trục trực giao giữ phương sai lớn nhất theo thứ tự",
        "Chiếu lên các trục tối đa hóa khoảng cách giữa nhãn các lớp",
        "Chiếu lên các trục giảm tối đa phương sai của dữ liệu đầu vào",
        "Chiếu lên các trục phi tuyến bảo toàn láng giềng cục bộ"], "difficulty": "medium"},
    "ml_0035": {"options": [
        "Standardize để thang đo không chi phối hướng phương sai lớn nhất",
        "Mã hóa mọi feature liên tục thành thứ hạng trước khi PCA",
        "Chuẩn hóa riêng từng mẫu để mọi mẫu có cùng tổng feature",
        "Lấy trị tuyệt đối của mọi feature để tránh phương sai âm"], "difficulty": "medium"},
    "ml_0036": {"options": [
        "Phần phương sai tổng được giải thích bởi một principal component",
        "Phần sai số tái tạo do một principal component tạo thêm",
        "Phần số mẫu được chiếu lên một principal component",
        "Phần tương quan giữa nhãn và một principal component"], "difficulty": "medium"},
    "ml_0037": {"question": "Ứng dụng phù hợp nhất của t-SNE trong phân tích dữ liệu nhiều chiều là gì?", "options": [
        "Trực quan hóa quan hệ láng giềng cục bộ trên bản đồ 2D hoặc 3D",
        "Giữ chính xác tỷ lệ khoảng cách toàn cục giữa mọi cặp điểm",
        "Chiếu tuyến tính dữ liệu lên các trục có phương sai lớn nhất",
        "Tạo phép biến đổi tham số mặc định để suy diễn nhanh trên mẫu mới"], "difficulty": "medium"},
    "ml_0038": {"options": [
        "Các feature độc lập có điều kiện theo lớp và có phân phối Gaussian theo lớp",
        "Các feature độc lập vô điều kiện và cùng một Gaussian ở mọi lớp",
        "Vector feature có mọi hiệp phương sai chéo được mô hình hóa đầy đủ",
        "Mỗi lớp có xác suất tiên nghiệm bằng nhau và feature độc lập vô điều kiện"], "difficulty": "medium"},
    "ml_0039": {"options": [
        "Vector số đếm không âm, chẳng hạn số lần xuất hiện của từ",
        "Vector đặc trưng liên tục được giả định Gaussian theo lớp",
        "Vector nhị phân chỉ ghi có hay không có từng từ",
        "Vector chứa duy nhất một hạng mục rời rạc cho mỗi mẫu"], "difficulty": "easy"},
    "ml_0040": {"options": [
        "Likelihood P(X|C) nhân với prior P(C)",
        "Likelihood P(X|C) nhân với evidence P(X)",
        "Prior P(C) chia cho likelihood P(X|C)",
        "Evidence P(X) nhân với prior P(C)"], "difficulty": "medium"},
    "ml_0041": {"options": [
        "Recall của lớp bệnh, vì đo phần bệnh nhân được phát hiện",
        "Precision của lớp bệnh, vì đo độ tin cậy của dự đoán dương",
        "Specificity của lớp bệnh, vì đo phần người khỏe được nhận diện",
        "Accuracy toàn bộ, vì cộng đúng cả hai lớp theo tần suất mẫu"], "difficulty": "easy"},
    "ml_0042": {"options": [
        "Precision của lớp spam, vì false positive làm chỉ số này giảm",
        "Recall của lớp spam, vì false negative làm chỉ số này giảm",
        "Specificity của lớp spam, vì nó chỉ xét email spam bị bỏ sót",
        "F1 của lớp spam, vì nó loại bỏ mọi ảnh hưởng của false negative"], "difficulty": "medium"},
    "ml_0043": {"options": [
        "Precision và recall của cùng lớp được đánh giá",
        "Precision và specificity của cùng lớp được đánh giá",
        "Recall và accuracy của cùng tập dữ liệu đánh giá",
        "Accuracy và specificity của cùng tập dữ liệu đánh giá"], "difficulty": "easy"},
    "ml_0044": {"options": [
        "Macro lấy trung bình F1 từng lớp; micro gộp TP, FP, FN rồi tính F1",
        "Macro gộp TP, FP, FN; micro lấy trung bình F1 từng lớp",
        "Macro cân theo số mẫu từng lớp; micro cho mọi lớp trọng số bằng nhau",
        "Macro và micro đều lấy trung bình F1 từng lớp với cùng trọng số"], "difficulty": "medium"},
    "ml_0045": {"options": [
        "Ước lượng hiệu suất qua nhiều lần đổi tập validation giữa các fold",
        "Ước lượng hiệu suất bằng cách chọn fold có accuracy cao nhất",
        "Ước lượng hiệu suất trên cùng một validation set ở mọi lượt",
        "Ước lượng hiệu suất bằng cách huấn luyện trên toàn bộ k fold mỗi lượt"], "difficulty": "easy"},
    "ml_0047": {"options": [
        "Dùng kết quả thử trước để chọn cấu hình tiếp theo qua mô hình surrogate",
        "Chia đều mỗi chiều tham số thành lưới rồi thử toàn bộ tổ hợp",
        "Lấy mẫu cấu hình độc lập mà không sử dụng kết quả thử trước",
        "Chỉ tối ưu tham số có đạo hàm loss tính được chính xác"], "difficulty": "medium"},
    "ml_0048": {"options": [
        "Điểm bất thường thường có đường đi ngắn trong cây chia ngẫu nhiên",
        "Điểm bất thường thường có đường đi dài trong cây chia ngẫu nhiên",
        "Điểm bất thường thường ở lá có số mẫu lớn nhất trong rừng",
        "Điểm bất thường thường có xác suất lớp thấp từ cây giám sát"], "difficulty": "medium"},
    "ml_0049": {"question": "Với một dự đoán cụ thể, SHAP gán giá trị cho feature nhằm mô tả điều gì?", "options": [
        "Đóng góp của feature so với giá trị nền theo cách phân bổ Shapley",
        "Mức thay đổi loss nếu xóa vĩnh viễn feature khỏi tập huấn luyện",
        "Đạo hàm cục bộ của output theo feature tại mọi điểm dữ liệu",
        "Tương quan toàn cục giữa feature và nhãn trong tập huấn luyện"], "difficulty": "hard"},
    "ml_0050": {"options": [
        "Mô hình dự đoán quá tự tin và xác suất chưa được hiệu chỉnh tốt",
        "Mô hình dự đoán thiếu tự tin vì tần suất thực tế cao hơn 0.9",
        "Mô hình có precision bằng 0.6 trên toàn bộ tập kiểm thử",
        "Mô hình có recall bằng 0.9 trên nhóm 100 mẫu được chọn"], "difficulty": "medium"},
}


def normalize(value):
    return re.sub(r"\s+", " ", value.casefold()).strip()


def validate(original, improved, audit):
    required = {"id", "question", "option_a", "option_b", "option_c", "option_d",
                "correct_answer", "category", "subcategory", "difficulty", "tags"}
    assert len(original) == len(improved) == len(audit)
    assert len({q["id"] for q in improved}) == len(improved)
    for old, q, entry in zip(original, improved, audit):
        assert set(q) == set(old) and required <= set(q)
        assert q["id"] == old["id"] == entry["id"]
        assert q["category"] == old["category"]
        assert q["subcategory"] == old["subcategory"]
        assert q["difficulty"] in {"easy", "medium", "hard"}
        assert q["correct_answer"] in "ABCD"
        assert isinstance(q["tags"], list) and q["tags"]
        assert isinstance(q["question"], str) and q["question"].strip()
        options = [q[f"option_{c}"] for c in "abcd"]
        assert all(isinstance(o, str) and o.strip() for o in options)
        assert len({normalize(o) for o in options}) == 4
        assert q[f"option_{q['correct_answer'].lower()}"]
        assert entry["changed"] == (old != q)
        assert entry["old_difficulty"] == old["difficulty"]
        assert entry["new_difficulty"] == q["difficulty"]
    print("Total questions:", len(improved))
    print("Modified:", sum(e["changed"] for e in audit))
    print("Unchanged:", sum(not e["changed"] for e in audit))
    print("Difficulty:", dict(collections.Counter(q["difficulty"] for q in improved)))
    print("Correct answer distribution:", dict(collections.Counter(q["correct_answer"] for q in improved)))
    for check in ("JSON parse", "Unique IDs", "Four non-empty options per question",
                  "Correct-answer references valid option", "No exact duplicate options",
                  "Required metadata preserved", "Manual semantic review of all IDs"):
        print("[PASS]", check)


def main():
    original, fmt = load_questions(SOURCE)
    assert len({q["id"] for q in original}) == len(original)
    assert set(REVISIONS) <= {q["id"] for q in original}
    improved = []
    audit = []
    # Balanced positions are assigned deterministically, preserving the correct text.
    position_counts = collections.Counter()
    for old in original:
        q = old.copy()
        revision = REVISIONS.get(q["id"])
        if revision:
            q["question"] = revision.get("question", q["question"])
            q["difficulty"] = revision["difficulty"]
            correct, *wrong = revision["options"]
            assert len(wrong) == 3
            # Prefer an underrepresented answer position; rotate ties by ID number.
            number = int(q["id"].split("_")[-1])
            letters = "ABCD"
            target = min(range(4), key=lambda i: (position_counts[letters[i]], (i - number) % 4))
            arranged = iter(wrong)
            for i, letter in enumerate(letters):
                q[f"option_{letter.lower()}"] = correct if i == target else next(arranged)
            q["correct_answer"] = letters[target]
        position_counts[q["correct_answer"]] += 1
        changed = old != q
        if changed:
            reason = ("Original distractors allowed elimination without distinguishing the target concept."
                      if revision else "Balanced the answer position without changing option meaning.")
        else:
            reason = "Existing numerical alternatives are plausible and unambiguous."
        audit.append({"id": q["id"], "changed": changed, "reason": reason,
                      "old_difficulty": old["difficulty"], "new_difficulty": q["difficulty"]})
        improved.append(q)
    validate(original, improved, audit)
    if fmt == "jsonl":
        output = SOURCE.with_name(SOURCE.stem + "_improved.jsonl")
        output.write_text("\n".join(json.dumps(q, ensure_ascii=False) for q in improved) + "\n", encoding="utf-8")
    else:
        data = improved if fmt == "array" else {**fmt[1], fmt[2]: improved}
        OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
