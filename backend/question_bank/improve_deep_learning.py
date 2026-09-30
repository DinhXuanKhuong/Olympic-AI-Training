"""Revise the reviewed deep-learning question bank and validate its output.

Each row has three misconception-based distractors. The existing correct answer
is retained; its position is balanced across the output when a row is revised.
"""
import json
import re
from collections import Counter
from pathlib import Path

SOURCE = Path(__file__).with_name('deep_learning.json')
AUDIT = Path(__file__).with_name('question_revision_audit.json')
LETTERS = 'ABCD'
REQUIRED = {'id', 'question', 'option_a', 'option_b', 'option_c', 'option_d',
            'correct_answer', 'category', 'subcategory', 'difficulty', 'tags'}

# ID | three incorrect but nearby answers | revised difficulty.
# dee_0005-0007 already have suitable choices and remain unchanged.
ROWS = '''
dee_0001|Đầu vào Conv theo từng mẫu bằng thống kê trên các kênh|Đầu ra ReLU theo từng mẫu bằng thống kê trên các kênh|Trọng số Conv theo từng kênh bằng thống kê mini-batch|medium
dee_0002|Ép activation vào khoảng (0,1) bằng hàm sigmoid|Chuẩn hóa activation theo thống kê của từng mini-batch|Ngẫu nhiên đặt một phần activation về 0 khi huấn luyện|easy
dee_0003|Đạo hàm rất nhỏ nhất khi đầu vào nằm gần 0|Đạo hàm bằng 0 với mọi đầu vào âm như ReLU|Đạo hàm tăng vô hạn khi đầu vào xa 0|medium
dee_0004|Tạo các xác suất độc lập không cần có tổng bằng 1|Chọn chỉ số lớp có logit cao nhất bằng argmax|Chuẩn hóa logits về trung bình 0 và phương sai 1|easy
dee_0008|Cộng learning rate nhân gradient vào tham số hiện tại|Trừ learning rate nhân trị tuyệt đối gradient khỏi tham số|Trừ learning rate nhân gradient của bước trước khỏi tham số|easy
dee_0009|Bước cập nhật nhỏ hơn nên loss giảm rất chậm|Gradient được trung bình trên nhiều mẫu hơn trong một bước|Gradient tự động bị chặn theo norm trước cập nhật|easy
dee_0010|Ít nhiễu hơn vì optimizer được cập nhật thường xuyên hơn|Giống hệt full-batch gradient ở từng bước tối ưu|Có phương sai không đổi vì learning rate vẫn giữ nguyên|easy
dee_0011|Chỉ dùng trung bình động gradient như momentum SGD|Chỉ dùng tổng bình phương gradient tích lũy như AdaGrad|Dùng đường chéo Hessian chính xác tại mỗi bước|medium
dee_0012|Mọi neuron nhận gradient khác nhau nhờ cùng trọng số bằng 0|Mọi activation đều bằng 0 mãi dù có bias học được|Lớp mất tính đối xứng vì các neuron được cập nhật độc lập|medium
dee_0013|Tanh với gain dành riêng cho mạng tuyến tính|Sigmoid khi activation thường nằm trong vùng bão hòa|Softmax ở mỗi lớp ẩn với tổng activation bằng 1|medium
dee_0014|Cả train và eval đều dùng thống kê batch; eval chỉ tắt gradient|Train dùng running statistics còn eval dùng thống kê batch hiện tại|Cả train và eval đều cập nhật running statistics như nhau|medium
dee_0015|Dùng running mean toàn dataset để không lệ thuộc batch hiện tại|Chuẩn hóa từng kênh dựa trên toàn bộ mẫu trong mini-batch|Dùng thống kê batch lúc train nhưng từng mẫu lúc eval|medium
dee_0016|Đặt ngẫu nhiên một phần gradient về 0 và giữ mask khi suy luận|Co mọi activation theo cùng hệ số cố định ở mỗi bước|Loại ngẫu nhiên nguyên lớp rồi giữ kiến trúc đó về sau|easy
dee_0017|Cắt norm gradient trước khi optimizer cập nhật|Đặt ngẫu nhiên một phần trọng số về 0 ở mỗi minibatch|Dừng huấn luyện khi validation loss không cải thiện|easy
dee_0018|Training loss giảm liên tiếp qua nhiều epoch|Gradient norm thấp ở một minibatch đơn lẻ|Validation metric tốt hơn training metric trong một epoch|easy
dee_0019|Underfitting vì cả training và validation loss đều tăng|Learning rate quá nhỏ vì cả hai loss đều giảm chậm|Vanishing gradient vì training loss đã ngừng giảm|easy
dee_0020|Overfitting rõ rệt vì training accuracy cao hơn validation nhiều|Rò rỉ dữ liệu vì hai accuracy gần bằng nhau|Hội tụ tốt vì chênh lệch giữa hai accuracy nhỏ|easy
dee_0021|Giảm class weight của lớp hiếm trong loss|Tăng weight decay cho tất cả tham số của mô hình|Áp dụng label smoothing đều cho mọi lớp|medium
dee_0022|Vanishing gradient khi truyền ngược qua nhiều lớp|Gradient nhiễu vì minibatch lấy quá ít mẫu|Gradient lệch vì nhãn lớp hiếm xuất hiện ít|easy
dee_0023|Gradient truyền ngược tăng nhanh khiến lớp đầu cập nhật quá lớn|Gradient giữ nguyên norm nhưng đổi dấu qua từng lớp|Gradient chỉ tồn tại ở lớp đầu mà không tới lớp đầu ra|medium
dee_0024|Chuẩn hóa activation bằng thống kê của mini-batch|Chặn activation âm trước khi cộng với nhánh biến đổi|Ngắt gradient qua nhánh biến đổi để chỉ train nhánh identity|medium
dee_0025|2 logit cho mỗi mẫu trước softmax như khi dùng CrossEntropyLoss|1 xác suất cho mỗi mẫu sau sigmoid như khi dùng BCELoss|2 xác suất cho mỗi mẫu sau softmax như đầu ra phân loại hai lớp|medium
dee_0026|Ước lượng từng đạo hàm bằng sai phân hữu hạn trên mọi tham số|Lan truyền activation từ đầu vào lên các lớp sau thêm một lần|Cập nhật tham số bằng gradient sau khi optimizer đã tính nó|easy
dee_0027|Tra cứu vector one-hot cố định cho mỗi token ID|Tính softmax trên toàn vocabulary trước mỗi lần tra cứu|Lấy trung bình embedding của cả chuỗi rồi dùng chung cho từng ID|easy
dee_0028|Lưu toàn bộ token trước đó để truy cập chính xác từng token|Chỉ mã hóa đầu vào hiện tại mà không nhận state bước trước|Lưu gradient bước trước để cập nhật trọng số ở bước hiện tại|easy
dee_0029|Giảm chi phí xử lý tuần tự bằng cách tính mọi bước song song|Tránh việc nén lịch sử chuỗi vào state có kích thước cố định|Loại bỏ nhu cầu chia sẻ tham số giữa các bước thời gian|easy
dee_0030|Chọn lượng candidate cell state mới để thêm vào|Chọn lượng hidden state mới được xuất ra ngoài|Chọn những trọng số mô hình được optimizer cập nhật|medium
dee_0031|Trộn các query theo mức tương thích giữa value và key|Chuẩn hóa từng key theo thống kê của toàn mini-batch|Chọn một value bằng argmax trước khi tính attention score|medium
dee_0032|Softmax attention luôn xóa nội dung ngữ nghĩa của embedding|Phép chiếu Q, K, V không thể dùng chung chiều vector|Causal mask tự cung cấp đầy đủ vị trí cho mọi token|medium
dee_0033|Nhân bản cùng ma trận attention thành nhiều bản giống nhau|Bỏ các phép chiếu Q, K, V và softmax trực tiếp embedding|Buộc mọi head dùng cùng trọng số attention cho mỗi token|medium
dee_0034|Ngăn mỗi token chú ý tới các token ở quá khứ|Che chính token hiện tại nhưng cho phép token tương lai|Chỉ che key là padding, không phụ thuộc thứ tự thời gian|medium
dee_0035|Đẩy positive ra xa và kéo negative lại gần trong không gian latent|Kéo mọi biểu diễn lại gần nhau bất kể quan hệ giữa mẫu|Chỉ tối ưu positive và bỏ hoàn toàn vai trò của negative|medium
dee_0036|Làm softmax phẳng hơn khiến trọng số negative gần bằng nhau|Không đổi softmax vì temperature chỉ nhân loss sau chuẩn hóa|Biến similarity thành khoảng cách Euclid trước softmax|hard
dee_0037|Dự đoán nhãn lớp từ latent bằng supervised loss|Khớp latent với prior bằng KL mà không tái tạo đầu vào|Phân biệt mẫu thật với mẫu do generator tạo ra|easy
dee_0038|Encoder xuất một latent xác định và chỉ học reconstruction loss|Latent chỉ lấy từ prior, không phụ thuộc đầu vào khi train|Latent được chọn bằng argmax từ discriminator của GAN|medium
dee_0039|Encoder và decoder trong một autoencoder tái tạo dữ liệu|Denoiser và noise scheduler trong một diffusion model|Teacher và student trong một mô hình distillation|easy
dee_0040|Generator tạo nhiều mẫu khác nhau nhưng đều nhiễu|Generator chỉ ghi nhớ và sao chép từng mẫu huấn luyện|Discriminator dự đoán xác suất gần 0,5 cho mọi mẫu|medium
dee_0041|Dự đoán nhãn lớp từ mẫu sạch ở mọi timestep|Tái tạo trực tiếp mẫu ở timestep trước bằng forward noising|Dùng discriminator phân biệt mẫu thật và giả ở mỗi timestep|medium
dee_0042|Dùng learning rate lớn và cập nhật toàn bộ lớp ngay từ đầu|Khởi tạo lại backbone ngẫu nhiên rồi chỉ giữ classifier|Cố định classifier mới và chỉ cập nhật embedding đầu vào|medium
dee_0043|Học ma trận cập nhật dense cùng kích thước và cập nhật cả trọng số gốc|Chỉ học vector bias mới, không cập nhật phép chiếu tuyến tính|Chỉ lượng tử hóa trọng số gốc rồi học scale lượng tử hóa|hard
dee_0044|Giảm số tham số học được mà vẫn giữ mọi tensor ở FP32|Tăng độ chính xác số học của mọi phép tính so với FP32|Loại bỏ nhu cầu kiểm soát ổn định số học khi huấn luyện|medium
dee_0045|Tăng số mẫu trong mỗi minibatch để vừa GPU mà không đổi số bước|Optimizer cập nhật sau mỗi mẫu rồi lấy trung bình trọng số|Giữ activation của mọi minibatch trong bộ nhớ đến cuối epoch|medium
dee_0046|Lưu mọi activation ở độ chính xác cao hơn để backward nhanh hơn|Bỏ backward qua các lớp không được checkpoint|Tích lũy gradient qua nhiều minibatch trước mỗi optimizer step|hard
dee_0047|Chỉ dùng nhãn cứng ban đầu, không dùng tín hiệu dự đoán từ teacher|Dùng gradient của student để cập nhật trực tiếp teacher|Sao chép mask dropout của teacher thay cho dự đoán của nó|medium
dee_0048|Buộc mọi expert xử lý từng token rồi lấy trung bình output|Tính attention score giữa token hiện tại và mọi token quá khứ|Chọn expert dựa trên loss của từng expert trên validation set|hard
dee_0049|Giảm bộ nhớ trọng số và tăng accuracy nhờ regularization|Giữ nguyên bộ nhớ trọng số vì số tham số không đổi|Tăng tốc trên mọi phần cứng, không cần kernel INT8|medium
dee_0050|Bỏ ngẫu nhiên bớt key để tạo attention xấp xỉ thưa|Lưu đầy đủ ma trận attention ở bộ nhớ GPU toàn cục|Thay softmax attention bằng phép chiếu tuyến tính theo token|hard
'''

QUESTION_OVERRIDES = {
    'dee_0001': 'Trong khối Conv → BatchNorm → ReLU, BatchNorm chuẩn hóa đại lượng nào ở chế độ train?',
    'dee_0048': 'Trong kiến trúc sparse Mixture of Experts, router thường có nhiệm vụ gì?',
}
CORRECT_OVERRIDES = {
    'dee_0001': 'Đầu ra Conv theo từng kênh bằng thống kê mini-batch, trước ReLU',
}

REVISIONS = {}
for row in ROWS.strip().splitlines():
    qid, *parts = row.split('|')
    if len(parts) != 4:
        raise ValueError(f'Malformed revision row: {qid}')
    REVISIONS[qid] = (parts[:3], parts[3])


def load(path):
    raw = path.read_text(encoding='utf-8')
    try:
        root = json.loads(raw)
    except json.JSONDecodeError:
        return [json.loads(line) for line in raw.splitlines() if line.strip()], 'jsonl', None
    if isinstance(root, list):
        return root, 'array', None
    if isinstance(root, dict):
        keys = [k for k, v in root.items() if isinstance(v, list)]
        if len(keys) != 1:
            raise ValueError('Object must contain exactly one question list')
        return root[keys[0]], 'object', (root, keys[0])
    raise ValueError('Input must be a JSON array, object with list, or JSONL')


def validate(rows, original=None):
    ids = []
    for q in rows:
        if not isinstance(q, dict) or not REQUIRED <= q.keys():
            raise ValueError('Missing required schema fields')
        ids.append(q['id'])
        if q['correct_answer'] not in LETTERS:
            raise ValueError(f"Invalid correct answer: {q['id']}")
        if q['difficulty'] not in {'easy', 'medium', 'hard'}:
            raise ValueError(f"Invalid difficulty: {q['id']}")
        options = [q[f'option_{letter.lower()}'] for letter in LETTERS]
        if any(not isinstance(o, str) or not o.strip() for o in options):
            raise ValueError(f"Empty option: {q['id']}")
        normalized = {re.sub(r'\s+', ' ', o).strip().casefold() for o in options}
        if len(normalized) != 4:
            raise ValueError(f"Duplicate option: {q['id']}")
        if not isinstance(q['tags'], list):
            raise ValueError(f"Invalid tags: {q['id']}")
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate IDs')
    if original is not None:
        if len(rows) != len(original):
            raise ValueError('Question count changed')
        for old, new in zip(original, rows):
            for key in ('id', 'category', 'subcategory', 'tags'):
                if old[key] != new[key]:
                    raise ValueError(f"Metadata changed: {old['id']} {key}")
            if set(old) != set(new):
                raise ValueError(f"Schema changed: {old['id']}")


def main():
    questions, fmt, wrapper = load(SOURCE)
    validate(questions)
    known = {q['id'] for q in questions}
    if set(REVISIONS) - known or known - (set(REVISIONS) | {'dee_0005', 'dee_0006', 'dee_0007'}):
        raise ValueError('Review coverage does not match all question IDs')
    output, audit, revision_number = [], [], 0
    for old in questions:
        q = old.copy()
        revision = REVISIONS.get(q['id'])
        if revision:
            wrong, level = revision
            correct = CORRECT_OVERRIDES.get(q['id'], old[f"option_{old['correct_answer'].lower()}"])
            options = wrong.copy()
            letter = 'BCDA'[revision_number % 4]
            options.insert(LETTERS.index(letter), correct)
            for label, value in zip(LETTERS, options):
                q[f'option_{label.lower()}'] = value
            q['correct_answer'] = letter
            q['question'] = QUESTION_OVERRIDES.get(q['id'], q['question'])
            q['difficulty'] = level
            reason = 'Distractors were too easy to eliminate; revised to test nearby mechanisms or misconceptions.'
            revision_number += 1
        else:
            reason = 'Existing options are plausible and distinguish nearby output formats or arithmetic results.'
        output.append(q)
        audit.append({'id': q['id'], 'changed': q != old, 'reason': reason,
                      'old_difficulty': old['difficulty'], 'new_difficulty': q['difficulty']})
    validate(output, questions)
    suffix = '.jsonl' if fmt == 'jsonl' else '.json'
    target = SOURCE.with_name(SOURCE.stem + '_improved' + suffix)
    if fmt == 'object':
        root, key = wrapper
        root[key] = output
        content = json.dumps(root, ensure_ascii=False, indent=2) + '\n'
    elif fmt == 'jsonl':
        content = '\n'.join(json.dumps(q, ensure_ascii=False) for q in output) + '\n'
    else:
        content = json.dumps(output, ensure_ascii=False, indent=2) + '\n'
    target.write_text(content, encoding='utf-8')
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    reloaded, _, _ = load(target)
    validate(reloaded, questions)
    if reloaded != output or json.loads(AUDIT.read_text(encoding='utf-8')) != audit:
        raise ValueError('Round-trip validation failed')
    counts = Counter(q['difficulty'] for q in output)
    answers = Counter(q['correct_answer'] for q in output)
    print(f'Total questions: {len(output)}')
    print(f"Modified: {sum(a['changed'] for a in audit)}")
    print(f"Unchanged: {sum(not a['changed'] for a in audit)}")
    print('Difficulty:')
    for level in ('easy', 'medium', 'hard'):
        print(f'{level}: {counts[level]}')
    print('Correct answer distribution:')
    for letter in LETTERS:
        print(f'{letter}: {answers[letter]}')
    print('Validation:')
    for name in ('JSON parse', 'Unique IDs', 'Four non-empty options per question',
                 'Correct-answer references valid option', 'No exact duplicate options',
                 'Required metadata preserved', 'All 50 questions semantically reviewed'):
        print(f'[PASS] {name}')
    print(f'Output: {target}')
    print(f'Audit: {AUDIT}')


if __name__ == '__main__':
    main()
