"""Curated revision of the complete NLP/LLM question bank.

Run: python3 backend/question_bank/improve_nlp_llm.py
The source is read only; output and audit are written next to it.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


SOURCE = Path(__file__).with_name("nlp_llm.json")
OUTPUT = SOURCE.with_name("nlp_llm_improved.json")
AUDIT = SOURCE.with_name("question_revision_audit.json")
LETTERS = "ABCD"
FIELDS = {"id", "question", "option_a", "option_b", "option_c", "option_d", "correct_answer", "category", "subcategory", "difficulty", "tags"}

# Each entry: clarified question (or None), correct option (or None to retain),
# three misconception-based distractors, revised difficulty, audit summary.
REVISIONS = {
"nlp_0001": (None, None, ["Dự đoán ngữ cảnh cục bộ từ từng từ trung tâm như Skip-gram", "Dự đoán từ trung tâm từ một cửa sổ ngữ cảnh như CBOW", "Phân rã trực tiếp ma trận TF-IDF của từng tài liệu"], "medium", "Replaced unrelated choices with neighboring word-representation objectives."),
"nlp_0002": (None, None, ["Tần suất xuất hiện của từng từ trong văn bản", "Danh tính các từ thuộc bộ từ vựng đã chọn", "Sự hiện diện của một từ trong văn bản"], "easy", "Replaced corpus-level choices with properties of bag-of-words representations."),
"nlp_0003": (None, None, ["Tương đối cao vì tần suất trong tài liệu quyết định toàn bộ trọng số", "Tương đối cao vì xuất hiện ở nhiều tài liệu làm IDF tăng", "Tương đối thấp vì TF của từ này bị đặt về không"], "medium", "Replaced implausible values with TF and IDF misconceptions."),
"nlp_0004": (None, None, ["Đưa mọi token về dạng gốc từ điển trước khi lập từ vựng", "Loại các token ít thông tin khỏi văn bản sau khi tách", "Ánh xạ từng token đã tách thành vector ngữ nghĩa"], "easy", "Replaced unrelated tasks with adjacent preprocessing operations."),
"nlp_0005": (None, None, ["Stemming dùng từ điển để chọn lemma, còn lemmatization cắt hậu tố theo luật", "Cả hai chỉ cắt hậu tố; lemmatization khác ở việc giữ nguyên chữ hoa", "Stemming cần gán nhãn từ loại, còn lemmatization chỉ áp dụng luật cắt hậu tố"], "medium", "Replaced absolute claims with plausible confusions about morphology methods."),
"nlp_0006": ("Trong biểu diễn Bag-of-Words cổ điển, mục đích thường gặp của việc loại stopword là gì?", None, ["Giữ lại chủ yếu từ xuất hiện nhiều để ổn định thống kê", "Chuẩn hóa mọi biến thể hình thái về cùng một từ gốc", "Giảm trọng số các từ phổ biến nhưng vẫn giữ đủ mọi token"], "easy", "Focused the context and compared nearby preprocessing and weighting steps."),
"nlp_0007": (None, None, ["Dùng từ trung tâm để dự đoán các từ trong cửa sổ ngữ cảnh", "Dùng một từ ngữ cảnh để dự đoán toàn bộ câu chứa nó", "Dùng cặp từ cùng xuất hiện để khôi phục ma trận đồng xuất hiện"], "easy", "Replaced unrelated tasks with neighboring word-embedding objectives."),
"nlp_0008": (None, None, ["Dùng các từ trong cửa sổ ngữ cảnh để dự đoán từ trung tâm", "Dùng cả câu để dự đoán một nhãn chủ đề duy nhất", "Dùng ma trận đồng xuất hiện toàn cục để phân rã trực tiếp"], "easy", "Replaced unrelated tasks with CBOW and nearby embedding objectives."),
"nlp_0009": ("Trong Word2Vec, Negative Sampling thay đổi cách tối ưu mục tiêu dự đoán từ như thế nào?", "Chỉ cập nhật từ mục tiêu và một số từ âm lấy mẫu thay vì tính trên toàn bộ từ vựng", ["Cập nhật mọi từ trong từ vựng nhưng bỏ qua các cặp ít xuất hiện", "Chỉ lấy mẫu câu không liên quan để tăng số ví dụ huấn luyện", "Thay softmax toàn từ vựng bằng cây phân cấp các lớp từ"], "medium", "Made the sampled-update mechanism distinguishable from related approximations."),
"nlp_0010": (None, "Tích vô hướng của chính hai vector đã được chuẩn hóa L2", ["Khoảng cách Euclid giữa hai vector đã chuẩn hóa", "Bình phương tích vô hướng của hai vector đã chuẩn hóa", "Góc tính bằng radian giữa hai vector đã chuẩn hóa"], "medium", "Replaced distant quantities with related vector similarity measures."),
"nlp_0011": ("Khi đưa văn bản đã token hóa vào BERT qua giao diện mô hình phổ biến, bộ tensor nào thường được cung cấp?", None, ["input_ids và nhãn; attention_mask chỉ được tạo ở đầu ra", "token_type_ids và attention_mask; input_ids chỉ dùng khi giải mã", "input_ids và position_ids; attention_mask chỉ dùng ở decoder"], "easy", "Replaced unrelated inputs with plausible BERT tensor combinations."),
"nlp_0012": (None, None, ["Dự đoán token kế tiếp từ ngữ cảnh bên trái theo causal mask", "Dự đoán toàn bộ chuỗi đầu ra từ một encoder đã che mọi token", "Dự đoán các từ ngữ cảnh từ một token trung tâm"], "easy", "Replaced unrelated outputs with nearby language-model objectives."),
"nlp_0013": (None, None, ["Dự đoán các token bị che bằng ngữ cảnh hai chiều", "Dự đoán thứ tự hai câu từ biểu diễn của cặp câu", "Dự đoán từ trung tâm từ một cửa sổ từ xung quanh"], "easy", "Replaced unrelated tasks with neighboring pretraining objectives."),
"nlp_0014": (None, None, ["Biến đổi từng token độc lập bằng mạng feed-forward sau attention", "Chuẩn hóa từng biểu diễn token để ổn định phân phối kích hoạt", "Gắn thông tin vị trí vào token trước khi tính attention"], "easy", "Replaced generic errors with other Transformer component functions."),
"nlp_0015": (None, None, ["Self-attention chỉ nhìn được token kề trước nếu thiếu mã vị trí", "Softmax attention xóa embedding của các token ở vị trí xa", "Feed-forward network tự mã hóa thứ tự nhưng attention không đọc được"], "medium", "Replaced off-topic choices with positional-information misconceptions."),
"nlp_0016": (None, None, ["Ngăn token hiện tại chú ý đến các token trước nó", "Che token padding để không đóng góp vào attention", "Giới hạn mỗi token chỉ chú ý đến chính nó"], "medium", "Replaced unrelated choices with neighboring attention-mask behaviors."),
"nlp_0017": (None, None, ["Mã hóa một chuỗi thành biểu diễn để phân loại toàn câu", "Sinh chuỗi chỉ từ một prompt mà không có encoder riêng", "Học biểu diễn từ cửa sổ ngữ cảnh cố định mà không sinh chuỗi"], "easy", "Replaced unrelated tasks with adjacent sequence-model architectures."),
"nlp_0018": (None, None, ["Đóng băng BERT và chỉ tính similarity giữa các embedding câu", "Gắn language-model head để dự đoán token kế tiếp cho nhãn", "Chỉ thay tokenizer rồi dùng trực tiếp logits tiền huấn luyện"], "easy", "Replaced absurd choices with nearby adaptation strategies."),
"nlp_0019": (None, None, ["Cung cấp vài ví dụ mẫu nhưng chỉ yêu cầu nhãn cuối cùng", "Yêu cầu mô hình sinh nhiều đáp án cuối rồi bỏ qua bước trung gian", "Thay đổi temperature để làm phân phối token sắc nét hơn"], "easy", "Replaced unrelated choices with nearby prompting techniques."),
"nlp_0020": (None, None, ["Mô tả nhiệm vụ bằng chỉ dẫn mà không đưa ví dụ minh họa", "Cung cấp một ví dụ đầu vào-đầu ra rồi huấn luyện lại trọng số", "Lấy nhiều mẫu giải mã cho cùng một prompt và bỏ phiếu"], "easy", "Replaced unrelated choices with zero-shot and sampling confusions."),
"nlp_0021": (None, None, ["Huấn luyện tiếp trên văn bản thô bằng mục tiêu dự đoán token kế tiếp", "Tối ưu trực tiếp chính sách từ cặp phản hồi được ưa thích", "Mở rộng kho văn bản truy xuất mà không cập nhật trọng số mô hình"], "medium", "Replaced unrelated effects with neighboring post-training methods."),
"nlp_0022": (None, None, ["Xếp hạng lại các đoạn đã tìm bằng một cross-encoder", "Sinh câu trả lời cuối cùng từ prompt và các đoạn đã tìm", "Chấm mức độ đúng của câu trả lời so với nguồn tham chiếu"], "easy", "Replaced unrelated tasks with adjacent RAG pipeline stages."),
"nlp_0023": (None, None, ["Embedding luôn giữ nguyên thứ tự từ chính xác hơn so khớp từ khóa", "Embedding thay thế được mọi bộ lọc chính xác theo tên hoặc mã định danh", "Embedding làm cho mọi từ đồng nghĩa có vector giống hệt nhau"], "medium", "Replaced obvious errors with realistic limits of dense retrieval."),
"nlp_0024": ("Trong RAG, nếu mỗi chunk quá ngắn để chứa đủ một đoạn lập luận, rủi ro trực tiếp là gì?", None, ["Một chunk chứa nhiều chủ đề không liên quan, làm loãng embedding", "Mỗi chunk vượt context window của mô hình dù tài liệu gốc ngắn", "Số chunk giảm khiến index không còn bao phủ toàn tài liệu"], "medium", "Focused the trade-off on lost context versus neighboring chunking errors."),
"nlp_0025": (None, None, ["Chỉ cập nhật bias trong các lớp tuyến tính của mô hình gốc", "Chèn adapter phi tuyến rồi huấn luyện toàn bộ trọng số gốc", "Lượng tử hóa trọng số gốc và không học tham số bổ sung"], "medium", "Replaced unrelated operations with nearby parameter-efficient methods."),
"nlp_0026": (None, None, ["Loại bỏ các trọng số có độ lớn nhỏ để giảm số tham số khác không", "Dùng một mô hình nhỏ học hành vi của mô hình lớn qua distillation", "Chia trọng số thành các ma trận hạng thấp để giảm tham số"], "medium", "Replaced unrelated effects with neighboring model-compression techniques."),
"nlp_0027": (None, None, ["Sinh phản hồi từ prompt theo chính sách hiện tại của LLM", "Chọn dữ liệu văn bản thô cho bước pretraining tiếp theo", "Dự đoán token kế tiếp bằng cross-entropy của câu tham chiếu"], "medium", "Replaced unrelated tasks with adjacent RLHF training roles."),
"nlp_0028": ("Trong quy trình DPO chuẩn, cặp phản hồi được ưa thích và không được ưa thích được dùng như thế nào?", "Tối ưu chính sách so với mô hình tham chiếu mà không huấn luyện reward model riêng", ["Huấn luyện reward model riêng rồi tối ưu chính sách bằng PPO", "Chỉ cập nhật mô hình tham chiếu và giữ chính sách cố định", "Chỉ SFT trên phản hồi được ưa thích mà bỏ thông tin so sánh cặp"], "hard", "Focused the question on DPO's reference-policy objective and adjacent methods."),
"nlp_0029": ("Trong hỏi đáp dựa trên tài liệu, biện pháp nào trực tiếp hướng câu trả lời dựa vào bằng chứng đã truy xuất?", "Dựa câu trả lời vào đoạn truy xuất và trích dẫn bằng chứng liên quan", ["Giảm temperature để mô hình lặp lại dự đoán xác suất cao", "Mở rộng context window nhưng không kiểm tra nguồn của câu trả lời", "Tăng số mẫu giải mã rồi chọn câu trả lời xuất hiện nhiều nhất"], "medium", "Replaced trivial errors with related decoding and context interventions."),
"nlp_0030": (None, None, ["Chọn một phản hồi có sẵn từ bộ nhớ hội thoại của agent", "Sinh mã gọi công cụ nhưng tự coi kết quả dự đoán là đã thực thi", "Lấy thêm văn bản từ context window mà không gọi hệ thống bên ngoài"], "easy", "Replaced unrelated claims with adjacent agent behaviors."),
"nlp_0031": ("Trong giải mã autoregressive bằng Transformer, KV cache giúp tránh phép tính lặp nào?", "Tính lại key và value của các token trước ở từng bước sinh", ["Tính lại query của token mới sau mỗi lớp attention", "Tính lại softmax attention trên các token mới được sinh", "Tính lại logits vocabulary cho token đang được chọn"], "hard", "Focused on the exact computation KV cache reuses."),
"nlp_0032": ("Trong speculative decoding bảo toàn phân phối của mô hình đích, vai trò của mô hình draft là gì?", "Đề xuất nhiều token để mô hình đích kiểm tra và chấp nhận theo quy tắc hiệu chỉnh", ["Sinh token cuối cùng và bỏ qua bước xác minh của mô hình đích", "Tính KV cache của mô hình đích bằng trọng số của mô hình draft", "Chọn token theo beam search rồi chỉ kiểm tra câu hoàn chỉnh"], "hard", "Added target-distribution preservation and nearby decoding confusions."),
"nlp_0033": ("Trong lớp Mixture of Experts dùng top-k routing theo token, router quyết định điều gì?", "Chọn một tập nhỏ expert để xử lý từng token", ["Chọn một expert cố định cho toàn bộ batch ở mọi lớp", "Trộn đầu ra của mọi expert với trọng số bằng nhau", "Chọn các token tiếp theo từ logits của vocabulary"], "medium", "Replaced unrelated choices with routing and expert-mixture confusions."),
"nlp_0034": ("Trong RoPE, thông tin vị trí được đưa vào attention chủ yếu qua phép biến đổi nào?", None, ["Cộng embedding vị trí tuyệt đối vào value sau attention", "Nhân attention logits với một mask dựa trên khoảng cách token", "Quay vector value sau khi cộng trọng số attention"], "hard", "Replaced unrelated choices with nearby positional-attention mechanisms."),
"nlp_0035": (None, None, ["Mô hình luôn có xác suất token đúng cao hơn tại từng vị trí", "Mô hình sinh văn bản mạch lạc hơn trên mọi prompt và tiêu chí", "Mô hình có entropy đầu ra thấp hơn ở mọi ngữ cảnh"], "medium", "Replaced unrelated claims with common perplexity interpretation errors."),
"nlp_0036": ("BLEU được đề xuất ban đầu để đánh giá tự động đầu ra của nhiệm vụ nào?", "Dịch máy giữa các ngôn ngữ tự nhiên", ["Tóm tắt văn bản từ một tài liệu dài", "Nhận dạng từ trong tín hiệu tiếng nói", "Gán nhãn từ loại cho một câu văn"], "easy", "Replaced cross-domain answers with nearby language tasks and metrics."),
"nlp_0037": (None, None, ["Năng lượng tín hiệu theo từng dải tần số Mel", "Biên độ của từng thành phần tần số sau biến đổi Fourier", "Đường bao phổ của tín hiệu trong mỗi khung thời gian"], "easy", "Replaced unrelated data types with adjacent audio representations."),
"nlp_0038": ("MFCC thường được tính từ log năng lượng trên các bộ lọc Mel rồi biến đổi tiếp để mô tả điều gì?", "Bao phổ ngắn hạn của tín hiệu qua các hệ số cepstral", ["Pha tức thời của từng bin Fourier trong mỗi frame", "Cường độ thô của waveform tại từng mẫu thời gian", "Vị trí thời gian chính xác của từng phoneme trong transcript"], "medium", "Specified the MFCC pipeline and replaced off-topic options with audio features."),
"nlp_0039": (None, None, ["Ước lượng một phổ duy nhất cho toàn bộ tín hiệu mà bỏ qua thời gian", "Chuyển trực tiếp mỗi frame thành nhãn phoneme bằng Fourier", "Tính hệ số cepstral bằng DCT mà không cần phổ theo thời gian"], "medium", "Replaced unrelated tasks with neighboring spectral-analysis operations."),
"nlp_0040": (None, None, ["Giữ khoảng cách tần số tuyến tính theo Hz ở mọi dải", "Mô phỏng trực tiếp cường độ âm bằng thang decibel", "Chuẩn hóa năng lượng của mọi dải tần về cùng một giá trị"], "medium", "Replaced unrelated operations with frequency-scale misconceptions."),
"nlp_0041": ("Vì sao CTC loss phù hợp khi transcript có sẵn nhưng chưa có nhãn token cho từng frame?", "CTC cộng xác suất trên các alignment hợp lệ giữa frame và transcript", ["CTC gán mỗi token transcript cho một frame cố định trước huấn luyện", "CTC dự đoán toàn câu từ một vector âm thanh duy nhất", "CTC dùng attention học trực tiếp vị trí token mà không có blank"], "hard", "Focused on alignment marginalization and neighboring alignment mechanisms."),
"nlp_0042": (None, None, ["Tiền huấn luyện có giám sát bằng transcript ở từng frame âm thanh", "Học embedding từ MFCC bằng mục tiêu phân loại speaker ID", "Tối ưu chỉ bằng cách tái tạo trực tiếp waveform từ waveform"], "medium", "Replaced unrelated methods with nearby speech-pretraining objectives."),
"nlp_0043": (None, None, ["Tổng hợp waveform từ văn bản và giọng nói mục tiêu", "Phân đoạn ai nói vào lúc nào trong hội thoại", "Xác minh danh tính người nói giữa hai đoạn âm thanh"], "easy", "Replaced unrelated tasks with neighboring speech applications."),
"nlp_0044": (None, None, ["50%", "20%", "33.3%"], "medium", "Replaced zero-error decoy with plausible WER denominator mistakes."),
"nlp_0045": (None, None, ["Trong đoạn âm thanh có bao nhiêu người nói khác nhau", "Một đoạn tiếng nói thuộc về người nào trong tập đã biết", "Ở những thời điểm nào mỗi người nói bắt đầu và kết thúc"], "easy", "Replaced unrelated tasks with speaker identification and diarization."),
"nlp_0046": (None, None, ["Hai đoạn tiếng nói có cùng một người nói hay không", "Đoạn âm thanh thuộc về người nào trong tập đã biết", "Mỗi vùng tiếng nói chứa những từ nào trong transcript"], "easy", "Replaced unrelated tasks with neighboring speech-analysis goals."),
"nlp_0047": (None, None, ["Dự đoán chuỗi phoneme từ văn bản trước khi sinh âm học", "Tạo biểu diễn âm học từ văn bản và điều kiện giọng nói", "Ước lượng nhịp và trọng âm từ văn bản đầu vào"], "medium", "Replaced unrelated tasks with adjacent TTS pipeline stages."),
"nlp_0048": ("Trong neural audio codec như EnCodec, chuỗi token âm thanh rời rạc chủ yếu biểu diễn điều gì?", "Waveform đã nén dưới dạng latent lượng tử hóa có thể giải mã lại", ["Transcript đã căn chỉnh theo từng frame của waveform", "Đặc trưng chỉ dùng để nhận dạng người nói, không tái tạo âm", "Phân bố xác suất token văn bản sau nhận dạng tiếng nói"], "medium", "Focused on codec tokens versus adjacent speech representations."),
"nlp_0049": ("Với speech language model mô hình hóa trực tiếp audio token, bước nào tạo đầu vào cho language model?", "Mã hóa tiếng nói thành chuỗi token âm thanh để mô hình hóa theo chuỗi", ["Chuyển tiếng nói thành transcript rồi bỏ hoàn toàn biểu diễn âm thanh", "Tính một embedding duy nhất cho cả đoạn rồi dự đoán nhãn speaker", "Lấy phổ Fourier của toàn file làm một token văn bản duy nhất"], "medium", "Specified the speech-token approach and replaced unrelated choices with neighboring pipelines."),
"nlp_0050": (None, None, ["Xác định từ bắt đầu và kết thúc của từng câu nói", "Phân tách danh tính người nói trong các vùng đã có tiếng nói", "Ước lượng phoneme cho từng frame trước khi nhận dạng từ"], "medium", "Replaced unrelated choices with adjacent streaming-speech stages."),
}


def load_questions(path: Path):
    raw = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = [json.loads(line) for line in raw.splitlines() if line.strip()]
        return data, "jsonl", None
    if isinstance(data, list):
        return data, "array", None
    if isinstance(data, dict):
        keys = [key for key, value in data.items() if isinstance(value, list) and all(isinstance(item, dict) for item in value)]
        if len(keys) != 1:
            raise ValueError("Expected exactly one question-list key in JSON object")
        return data[keys[0]], "object", (data, keys[0])
    raise ValueError("Unsupported JSON container")


def validate(questions, originals=None):
    assert len({q["id"] for q in questions}) == len(questions), "Duplicate IDs"
    for q in questions:
        assert FIELDS <= q.keys(), f"Missing metadata: {q.get('id')}"
        assert q["correct_answer"] in LETTERS, q["id"]
        assert q["difficulty"] in {"easy", "medium", "hard"}, q["id"]
        assert isinstance(q["tags"], list), q["id"]
        options = [q[f"option_{letter.lower()}"] for letter in LETTERS]
        assert all(isinstance(value, str) and value.strip() for value in options), q["id"]
        normalized = [re.sub(r"\s+", " ", value).casefold().strip() for value in options]
        assert len(set(normalized)) == 4, q["id"]
        assert q[f"option_{q['correct_answer'].lower()}"].strip(), q["id"]
    if originals is not None:
        assert len(questions) == len(originals)
        for old, new in zip(originals, questions):
            assert {key: new[key] for key in ("id", "category", "subcategory")} == {key: old[key] for key in ("id", "category", "subcategory")}
            assert set(new) == set(old), new["id"]


def main():
    original, fmt, container = load_questions(SOURCE)
    output = SOURCE.with_name(SOURCE.stem + "_improved" + (".jsonl" if fmt == "jsonl" else ".json"))
    validate(original)
    assert set(REVISIONS) == {q["id"] for q in original}, "Every question needs a review entry"
    improved, audit = [], []
    for index, old in enumerate(original):
        question, correct, wrong, difficulty, reason = REVISIONS[old["id"]]
        assert len(wrong) == 3
        revised = old.copy()
        revised["question"] = question or old["question"]
        old_correct = old[f"option_{old['correct_answer'].lower()}"]
        choices = [correct or old_correct, *wrong]
        # Cycle the answer positions; all four letters occur nearly equally.
        target = LETTERS[index % 4]
        distractors = iter(wrong)
        for letter in LETTERS:
            revised[f"option_{letter.lower()}"] = choices[0] if letter == target else next(distractors)
        revised["correct_answer"] = target
        revised["difficulty"] = difficulty
        improved.append(revised)
        audit.append({"id": old["id"], "changed": revised != old, "reason": reason, "old_difficulty": old["difficulty"], "new_difficulty": difficulty})
    validate(improved, original)
    # Intended-answer uniqueness was checked during the curated content review;
    # lexical validation alone cannot prove semantic uniqueness.
    if fmt == "object":
        wrapper, key = container
        wrapper = wrapper.copy()
        wrapper[key] = improved
        result = json.dumps(wrapper, ensure_ascii=False, indent=2) + "\n"
    elif fmt == "jsonl":
        result = "\n".join(json.dumps(q, ensure_ascii=False) for q in improved) + "\n"
    else:
        result = json.dumps(improved, ensure_ascii=False, indent=2) + "\n"
    output.write_text(result, encoding="utf-8")
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    reread, _, _ = load_questions(output)
    validate(reread, original)
    assert reread == improved
    assert len(audit) == len(improved)
    print(f"Total questions: {len(improved)}")
    print(f"Modified: {sum(row['changed'] for row in audit)}")
    print(f"Unchanged: {sum(not row['changed'] for row in audit)}")
    print("Difficulty:")
    for name in ("easy", "medium", "hard"):
        print(f"{name}: {Counter(q['difficulty'] for q in improved)[name]}")
    print("Correct answer distribution:")
    for letter in LETTERS:
        print(f"{letter}: {Counter(q['correct_answer'] for q in improved)[letter]}")
    for check in ("JSON parse", "Unique IDs", "Four non-empty options per question", "Correct-answer references valid option", "No exact duplicate options", "Required metadata preserved", "Audit covers every question"):
        print(f"[PASS] {check}")


if __name__ == "__main__":
    main()
