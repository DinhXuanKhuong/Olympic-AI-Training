"""Curated revisions and validation for data_processing.json."""
from __future__ import annotations
import json
import random
from collections import Counter
from pathlib import Path

SOURCE = Path(__file__).with_name('data_processing.json')
OPTIONS = ('option_a', 'option_b', 'option_c', 'option_d')
# Entry: question, options with intended correct option first, difficulty, short audit reason.
REVISIONS = {
1: ("Trong Pandas, lệnh nào trả về đúng 5 dòng đầu tiên của DataFrame df theo thứ tự hiện có?", ["df.head()", "df.tail()", "df.sample(n=5)", "df.nlargest(5, 'score')"], "easy", "Replaced unrelated or nonexistent methods with plausible row-selection operations."),
2: ("Với DataFrame df, biểu thức nào trả về tuple (số dòng, số cột)?", ["df.shape", "df.size", "df.ndim", "df.count()"], "easy", "Used neighboring DataFrame size and dimension attributes as distractors."),
3: ("Phương thức nào của Pandas hiển thị kiểu dữ liệu, số giá trị non-null và mức dùng bộ nhớ theo cột?", ["df.info()", "df.describe()", "df.dtypes", "df.count()"], "easy", "Replaced unrelated plotting and preview options with related inspection methods."),
4: ("Với DataFrame có nhãn chỉ mục là số nguyên, điểm khác nhau cốt lõi giữa df.loc và df.iloc là gì?", ["loc chọn theo nhãn; iloc chọn theo vị trí nguyên", "loc chọn theo vị trí; iloc chọn theo nhãn", "loc dùng nhãn dòng; iloc dùng nhãn cột", "loc và iloc đều chọn theo vị trí nguyên"], "medium", "Replaced obvious claims with realistic label-versus-position confusions."),
5: ("Trong Pandas, thao tác nào loại các dòng có ít nhất một giá trị thiếu?", ["df.dropna(how='any')", "df.dropna(how='all')", "df.dropna(axis=1, how='any')", "df.fillna(0)"], "medium", "Contrasted dropna settings and missing-value imputation within the same task."),
6: ("Một cột số có giá trị thiếu và vài ngoại lệ rất lớn. Thống kê nào phù hợp nhất để điền khuyết nếu cần bền vững với ngoại lệ?", ["Trung vị của các giá trị quan sát", "Trung bình của các giá trị quan sát", "Giá trị lớn nhất trong các giá trị quan sát", "Trung bình có trọng số theo tần suất"], "easy", "Made all options observed-value statistics while retaining the robust-statistic distinction."),
7: ("Trong Pandas, lệnh nào trả về DataFrame sau khi bỏ các dòng trùng nhau theo mọi cột?", ["df.drop_duplicates(subset=None)", "df.duplicated(keep='first')", "df.drop_duplicates(subset=['id'])", "df.dropna(how='any')"], "medium", "Used related duplicate-detection and row-removal operations instead of invented APIs."),
8: ("Với DataFrame df có department và salary, biểu thức nào tính lương trung bình riêng cho từng department?", ["df.groupby('department')['salary'].mean()", "df.groupby('department')['salary'].sum()", "df['salary'].mean()", "df.groupby('salary')['department'].count()"], "medium", "Contrasted grouping keys and aggregation functions within the same calculation."),
9: ("Khi ghép customers và orders theo customer_id, kiểu join nào chỉ giữ những khóa có ở cả hai bảng?", ["Inner join", "Left join", "Right join", "Full outer join"], "easy", "Replaced an awkward qualifier with four directly comparable join types."),
10: ("Hai DataFrame có cùng các cột cần được ghép bằng cách nối thêm dòng. Biểu thức nào thực hiện việc đó?", ["pd.concat([df1, df2], axis=0)", "pd.concat([df1, df2], axis=1)", "df1.join(df2)", "df1.merge(df2)"], "medium", "Replaced unrelated operations with column concatenation and join alternatives."),
11: ("Trong Pandas, lệnh nào sắp xếp các dòng của df theo giá trị cột score tăng dần?", ["df.sort_values('score')", "df.sort_index()", "df['score'].rank()", "df.nlargest(5, 'score')"], "medium", "Compared value sorting with index sorting, ranking, and top-k selection."),
12: ("Muốn đếm số lần xuất hiện của từng giá trị trong Series df['category'], lệnh nào phù hợp?", ["df['category'].value_counts()", "df['category'].count()", "df['category'].nunique()", "df.groupby('category').ngroups"], "medium", "Used neighboring counting operations with distinct outputs."),
13: ("Cột age chứa các chuỗi số nguyên hợp lệ và không có giá trị thiếu. Lệnh nào chuyển Series đó sang kiểu int?", ["df['age'].astype(int)", "df['age'].astype(str)", "df['age'].astype(float)", "df['age'].convert_dtypes()"], "easy", "Replaced unrelated methods with plausible dtype conversions and clarified input assumptions."),
14: ("Cột timestamp chứa chuỗi ngày giờ như '2026-09-30 08:30:00'. Lệnh nào phân tích chuỗi thành giá trị datetime?", ["pd.to_datetime(df['timestamp'])", "df['timestamp'].astype(str)", "df['timestamp'].str[:10]", "pd.to_numeric(df['timestamp'])"], "easy", "Used related parsing and string-conversion operations instead of unrelated calls."),
15: ("Với phép toán số học trên mảng NumPy lớn, vì sao vectorization thường nhanh hơn vòng lặp Python trên từng phần tử?", ["Phần việc được thực thi trong mã tối ưu ở mức thấp, giảm overhead vòng lặp Python", "Các phần tử vẫn được lặp qua interpreter Python riêng lẻ sau khi vector hóa", "NumPy tự chuyển mọi phép toán mảng sang thực thi trên GPU", "Vectorization luôn làm giảm bậc độ phức tạp của phép toán"], "medium", "Replaced implausible effects with misconceptions about interpreter overhead and execution."),
16: ("Cho a có shape (100, 1) và b có shape (1, 20). Với phép cộng NumPy a + b, shape kết quả là gì?", ["(100, 20), nhờ mở rộng tương thích theo từng chiều", "(100, 1), vì shape của toán hạng bên trái được giữ", "(1, 20), vì shape của toán hạng bên phải được giữ", "Không hợp lệ vì hai mảng không có cùng shape"], "medium", "Replaced unrelated descriptions with precise broadcasting-shape misconceptions."),
17: ("Với đặc trưng số x có độ lệch chuẩn khác 0, standardization kiểu z-score thường tính giá trị mới như thế nào?", ["(x - mean) / standard deviation", "(x - min) / (max - min)", "x / max(abs(x))", "(x - median) / IQR"], "medium", "Contrasted z-score with neighboring feature-scaling formulas."),
18: ("Với Min-Max Scaling về [0,1] trên tập huấn luyện, giá trị x được biến đổi theo công thức nào?", ["(x - min) / (max - min)", "(x - mean) / standard deviation", "(x - median) / IQR", "x / max(abs(x))"], "medium", "Replaced unrelated outcomes with comparable scaling formulas."),
19: ("Với đặc trưng số có nhiều ngoại lệ lớn, scaler nào chuẩn hóa dựa trên trung vị và IQR thay vì mean và độ lệch chuẩn?", ["RobustScaler", "StandardScaler", "MinMaxScaler", "MaxAbsScaler"], "medium", "Used related scalers and made the robust-statistics mechanism explicit."),
20: ("Với biến màu sắc nominal không có thứ tự, cách mã hóa nào tạo cột chỉ báo riêng cho từng giá trị mà không áp đặt thứ bậc?", ["One-Hot Encoding", "Ordinal Encoding", "Frequency Encoding", "Target Encoding"], "easy", "Replaced scaling and PCA with neighboring categorical encoders."),
21: ("Biến education có thứ tự THPT < Đại học < Thạc sĩ < Tiến sĩ. Cách mã hóa nào biểu diễn trực tiếp thứ tự này bằng mã số tăng dần?", ["Ordinal Encoding với thứ tự mức được khai báo", "One-Hot Encoding với mỗi mức một cột", "Frequency Encoding theo số lần xuất hiện", "Hashing Encoding vào chỉ số bucket"], "medium", "Used other categorical encodings as plausible alternatives."),
22: ("Vì sao cần dành riêng test set trước khi huấn luyện và chọn mô hình?", ["Ước lượng khả năng tổng quát hóa trên dữ liệu chưa tham gia huấn luyện hay chọn mô hình", "Điều chỉnh hyperparameter trực tiếp trên test set để chọn cấu hình tốt nhất", "Dùng test set để tính tham số chuẩn hóa trước khi fit mô hình", "Bảo đảm phân phối test luôn giống hệt phân phối train trong tương lai"], "medium", "Replaced unrelated claims with evaluation and leakage misconceptions."),
23: ("Khi chia tập phân loại có tỷ lệ lớp 95:5, phương pháp nào chủ đích giữ tỷ lệ lớp gần tương đương ở train và test?", ["Stratified split theo nhãn lớp", "Random split không xét nhãn lớp", "Group split theo mã người dùng", "Time-based split theo thời điểm ghi nhận"], "medium", "Compared four real splitting strategies and their different constraints."),
24: ("Mean và độ lệch chuẩn được tính trên cả train lẫn test trước khi chuẩn hóa. Đánh giá test bị ảnh hưởng chủ yếu vì điều gì?", ["Thống kê của test đã tác động đến bước tiền xử lý dùng khi huấn luyện", "Các nhãn test đã được dùng trực tiếp để cập nhật trọng số mô hình", "Mô hình không còn nhận được bất kỳ dữ liệu nào từ train", "Tỷ lệ lớp trong test được giữ cố định sau phép chuẩn hóa"], "medium", "Explained leakage through preprocessing rather than offering unrelated terminology."),
25: ("Trong đánh giá bằng train, validation và test, quy trình fit StandardScaler nào tránh rò rỉ thông tin?", ["Fit trên train; dùng scaler đó transform validation và test", "Fit riêng trên từng tập; dùng mỗi scaler cho tập tương ứng", "Fit trên train và validation; transform test bằng scaler đó", "Fit trên toàn bộ ba tập; sau đó transform từng tập"], "medium", "Used plausible but leaky fitting scopes as distractors."),
26: ("Khi điền giá trị thiếu bằng median trước đánh giá test, median dùng cho cả train và test phải được ước lượng từ đâu?", ["Các giá trị quan sát trong train", "Các giá trị quan sát trong test", "Các giá trị quan sát trong train và test gộp lại", "Median tính riêng trên từng tập sau khi chia"], "medium", "Focused distractors on plausible but leaky estimation scopes."),
27: ("Trong scikit-learn, cần chuẩn hóa cột số và one-hot encode cột phân loại trong cùng một bước tiền xử lý. Thành phần nào ghép hai phép biến đổi theo nhóm cột?", ["ColumnTransformer", "Pipeline", "FeatureUnion", "SimpleImputer"], "medium", "Replaced unrelated use cases with neighboring sklearn composition tools."),
28: ("Khi dùng cross-validation trong scikit-learn, đặt imputer và estimator trong Pipeline giúp điều gì?", ["Imputer được fit riêng trên phần train của mỗi fold trước khi đánh giá fold đó", "Imputer được fit một lần trên toàn bộ dữ liệu trước mọi fold", "Estimator được fit trên cả train và validation của mỗi fold", "Pipeline tự chọn hyperparameter tốt nhất mà không cần cơ chế tìm kiếm"], "medium", "Focused on fold-specific fitting and realistic pipeline misconceptions."),
29: ("Theo quy tắc Tukey 1.5×IQR với IQR = Q3 - Q1, khoảng hàng rào để gắn cờ ngoại lệ là gì?", ["[Q1 - 1.5×IQR, Q3 + 1.5×IQR]", "[Q1 - 1.5×IQR, Q3 - 1.5×IQR]", "[Q1 + 1.5×IQR, Q3 + 1.5×IQR]", "[Q1 - 0.5×IQR, Q3 + 0.5×IQR]"], "medium", "Replaced unrelated ranges with near-miss IQR fences."),
30: ("Winsorization thường làm gì với giá trị nằm ngoài các percentile ngưỡng đã chọn?", ["Thay giá trị vượt ngưỡng bằng giá trị tại ngưỡng tương ứng", "Xóa hẳn các dòng có giá trị vượt ngưỡng", "Thay mọi giá trị vượt ngưỡng bằng median toàn cột", "Chuẩn hóa toàn cột bằng mean và độ lệch chuẩn"], "medium", "Contrasted capping with trimming, median replacement, and scaling."),
31: ("Với đặc trưng x > 0 lệch phải mạnh, phép biến đổi nào biến tỷ số giữa hai giá trị thành chênh lệch cộng và thường nén đuôi phải?", ["Log transformation", "Z-score standardization", "Min-Max Scaling", "Linear rescaling bằng một hằng số"], "medium", "Specified the log mechanism to avoid ambiguity with other skew-reduction methods."),
32: ("Khi nhân bản ngẫu nhiên mẫu lớp hiếm để cân bằng train set, rủi ro nào tăng vì mô hình gặp lặp lại cùng quan sát?", ["Học quá sát các mẫu lớp hiếm được lặp", "Giảm phương sai như khi có thêm nhiều mẫu lớp hiếm độc lập", "Loại bỏ tự động nhiễu nhãn trong các mẫu lớp hiếm", "Giảm mức tương quan giữa các bản sao của cùng một mẫu"], "medium", "Used consequences of resampling as distractors rather than unrelated data changes."),
33: ("Với đánh giá bằng một holdout test set, nên áp dụng SMOTE theo thứ tự nào để tránh leakage?", ["Chia train/test, rồi chỉ fit và resample trên train", "SMOTE toàn bộ dữ liệu, rồi mới chia train/test", "Chia train/test, rồi SMOTE riêng từng tập", "Chia train/test, rồi fit SMOTE trên test và áp dụng cho train"], "medium", "Compared realistic resampling orders and clarified the holdout setting."),
34: ("Các chuỗi '  Alice ', 'alice', 'ALICE' cần được quy về cùng dạng để so khớp tên. Tổ hợp thao tác nào trực tiếp xử lý cả hai khác biệt?", ["strip khoảng trắng ngoài và casefold chữ", "strip khoảng trắng ngoài rồi giữ nguyên kiểu chữ", "casefold chữ rồi giữ nguyên khoảng trắng ngoài", "chuẩn hóa Unicode NFC rồi giữ nguyên khoảng trắng và kiểu chữ"], "easy", "Used partial string-cleaning steps as close distractors."),
35: ("Với categorical feature có rất nhiều giá trị mới liên tục, feature hashing có lợi thế nào so với lập vocabulary tường minh?", ["Ánh xạ vào số chiều cố định mà không phải lưu toàn bộ vocabulary", "Tạo một chiều riêng bảo đảm không collision cho mỗi giá trị mới", "Học embedding dày đặc bằng gradient cho từng giá trị", "Gán mã theo tần suất quan sát mà vẫn giữ số chiều cố định"], "medium", "Compared hashing with vocabulary, learned embeddings, and frequency encoding."),
36: ("One-hot encode một cột có hàng chục nghìn category tạo ma trận đặc trưng ra sao và nên lưu thế nào để tiết kiệm bộ nhớ?", ["Chủ yếu là số 0; dùng sparse representation", "Chủ yếu là số 0; dùng dense representation", "Chủ yếu là số 1; dùng sparse representation", "Chủ yếu là số 1; dùng dense representation"], "medium", "Used the sparsity and storage trade-off as comparable alternatives."),
37: ("So với CSV, đặc điểm nào của Parquet thường giúp truy vấn phân tích chỉ đọc vài cột hiệu quả hơn?", ["Lưu theo cột nên có thể tránh đọc các cột không cần", "Lưu theo hàng nên mỗi bản ghi được đọc nguyên khối", "Lưu dưới dạng văn bản phân tách nên parse nhanh hơn", "Lưu mỗi dòng thành một tài liệu độc lập có chỉ mục"], "medium", "Focused options on competing storage layouts and column selection."),
38: ("Truy vấn chỉ chọn 3 trong 100 cột của bảng Parquet. Tối ưu nào trực tiếp giảm lượng dữ liệu cột phải đọc?", ["Projection pushdown bỏ qua 97 cột không được chọn", "Predicate pushdown bỏ qua các hàng không thỏa điều kiện lọc", "Row-group pruning bỏ qua nhóm hàng theo thống kê min/max", "Dictionary encoding thay chuỗi lặp bằng mã ngắn"], "medium", "Contrasted column pruning with other real Parquet optimizations."),
39: ("Apache Arrow nổi bật nhờ định dạng nào phục vụ trao đổi dữ liệu hiệu quả giữa các hệ thống phân tích?", ["Định dạng cột trong bộ nhớ với layout chung", "Định dạng cột trên đĩa tối ưu cho lưu trữ lâu dài", "Định dạng văn bản phân tách cho trao đổi bảng", "Định dạng hàng trong bộ nhớ tối ưu cho cập nhật bản ghi"], "medium", "Distinguished Arrow's in-memory layout from neighboring table formats."),
40: ("Trong Polars Lazy API, vì sao chuỗi thao tác thường được tối ưu trước khi chạy collect()?", ["Các bước tạo logical plan để optimizer đẩy lọc và chọn cột xuống sớm", "Mỗi bước được thực thi ngay rồi optimizer viết lại kết quả đã có", "Chỉ phép toán cuối được giữ lại còn các bước trước bị bỏ", "Dữ liệu được tự động sao chép thành nhiều bản để tránh lập plan"], "medium", "Used execution-planning misconceptions rather than unrelated capabilities."),
41: ("Trong phân tích cục bộ, ưu điểm nào của DuckDB phù hợp khi cần SQL trên nhiều file Parquet?", ["Truy vấn trực tiếp file và chỉ đọc các phần cần thiết cho truy vấn", "Bắt buộc import toàn bộ file vào bảng thường trú trước khi truy vấn", "Chỉ hỗ trợ SQL sau khi chuyển Parquet thành DataFrame Pandas", "Luôn đọc đủ mọi cột vào RAM trước khi thực hiện phép lọc"], "medium", "Compared direct external-file queries with plausible import and scan misconceptions."),
42: ("CSV 80 GB lớn hơn RAM 16 GB. Với Pandas, cách nào cho phép tính tổng một cột mà không giữ toàn bộ bảng trong RAM?", ["Đọc theo chunksize và cộng tổng từng chunk", "Dùng read_csv mặc định rồi mới gọi sum trên DataFrame", "Dùng memory_map=True và giữ toàn bộ DataFrame sau parse", "Đọc head(1000), lấy tổng rồi nhân theo tỷ lệ số dòng"], "medium", "Replaced absurd choices with tempting but incorrect memory and sampling strategies."),
43: ("Cột country có 10 triệu dòng nhưng chỉ 20 giá trị khác nhau. Vì sao đổi từ object sang category thường tiết kiệm bộ nhớ?", ["Lưu mã số cho từng dòng và bảng giá trị category dùng chung", "Nén từng chuỗi riêng trong mỗi ô mà không dùng bảng mã", "Chỉ lưu 20 chuỗi duy nhất mà không cần mã cho từng dòng", "Tăng độ dài mã hóa của từng chuỗi để tránh trùng lặp"], "medium", "Tested the categorical storage mechanism with related encoding misconceptions."),
44: ("Trong data pipeline, schema validation chủ yếu kiểm tra loại điều kiện nào trước khi dữ liệu đi tiếp?", ["Kiểu cột, cột bắt buộc và các ràng buộc giá trị đã khai báo", "Độ chính xác dự đoán của mô hình trên mọi batch dữ liệu", "Mức thay đổi phân phối feature so với tập huấn luyện", "Quan hệ nhân quả giữa mọi cột đầu vào và nhãn"], "medium", "Contrasted schema checks with neighboring model and data-quality checks."),
45: ("Data lineage trong hệ thống dữ liệu trả lời câu hỏi nào tốt nhất?", ["Một trường dữ liệu đến từ nguồn nào và qua các biến đổi nào", "Một trường dữ liệu có bao nhiêu giá trị null ở batch hiện tại", "Một trường dữ liệu có cùng phân phối với batch trước hay không", "Một trường dữ liệu có khớp kiểu khai báo trong schema hay không"], "medium", "Contrasted lineage with profiling, drift, and schema validation."),
46: ("Sau triển khai, phân phối feature age thay đổi so với lúc train; quan hệ giữa feature và nhãn chưa được xác định là đổi. Tên hiện tượng quan sát được là gì?", ["Covariate drift của age", "Concept drift của quan hệ age với nhãn", "Label shift của tỷ lệ các lớp mục tiêu", "Data leakage từ test sang quá trình train"], "medium", "Distinguished observed feature drift from concept and label shift."),
47: ("Trong stream processing, event time và processing time khác nhau ở điểm nào?", ["Event time ghi lúc sự kiện xảy ra; processing time ghi lúc hệ thống xử lý", "Event time ghi lúc hệ thống xử lý; processing time ghi lúc sự kiện xảy ra", "Cả hai đều là lúc sự kiện được ghi vào kho lưu trữ cuối", "Cả hai đều được tính bằng thời gian chạy của toán tử xử lý"], "medium", "Replaced unrelated definitions with neighboring timestamp semantics."),
48: ("Feature Store giúp giảm training-serving skew chủ yếu bằng cách nào?", ["Quản lý định nghĩa và phục vụ feature nhất quán cho train và inference", "Lưu version của model để train và inference dùng cùng trọng số", "Tính feature độc lập ở train và serving rồi lưu vào hai bảng riêng", "Giữ cùng tên cột ở train và serving dù logic tính feature khác nhau"], "medium", "Focused on feature consistency and adjacent serving concepts."),
49: ("Với hai embedding khác vector 0, tiền xử lý nào khiến dot product của chúng bằng cosine similarity ban đầu?", ["Chuẩn hóa từng vector theo chuẩn L2 về độ dài 1", "Trừ mean từng chiều rồi giữ nguyên độ dài vector", "Chia mỗi chiều cho độ lệch chuẩn của chiều đó", "Chuẩn hóa từng vector theo chuẩn L1 về tổng trị tuyệt đối 1"], "medium", "Contrasted L2 normalization with nearby vector normalizations."),
50: ("Muốn tái tạo chính xác train/validation split trong lần chạy sau kể cả khi thứ tự file nguồn đổi, cách nào đáng tin cậy nhất?", ["Lưu danh sách ID của các mẫu thuộc từng split", "Chỉ lưu random seed nhưng không cố định thứ tự dữ liệu đầu vào", "Chỉ lưu tỷ lệ train/validation và chia ngẫu nhiên lần nữa", "Chỉ lưu số mẫu của từng split nhưng không lưu ID mẫu"], "medium", "Clarified order changes and compared reproducibility controls with weaker metadata."),
}

REQUIRED = {'id', 'question', *OPTIONS, 'correct_answer', 'category', 'subcategory', 'difficulty', 'tags'}
LETTERS = 'ABCD'


def load_questions(path: Path):
    raw = path.read_text(encoding='utf-8-sig')
    try:
        root = json.loads(raw)
    except json.JSONDecodeError:
        rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
        if not rows:
            raise ValueError('Empty JSONL input')
        return rows, 'jsonl', None, None
    if isinstance(root, list):
        return root, 'array', None, None
    if isinstance(root, dict):
        candidates = [key for key, value in root.items() if isinstance(value, list) and all(isinstance(x, dict) for x in value)]
        if len(candidates) != 1:
            raise ValueError('Object input must have exactly one question-list field')
        return root[candidates[0]], 'object', root, candidates[0]
    raise ValueError('Input must be a JSON array, object with one question list, or JSONL')


def validate(rows, original=None):
    if not isinstance(rows, list) or not rows:
        raise ValueError('Questions must be a nonempty list')
    ids = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not REQUIRED.issubset(row):
            raise ValueError(f'Question {index}: missing required fields')
        if not isinstance(row['id'], str) or not row['id'].strip():
            raise ValueError(f'Question {index}: invalid ID')
        ids.append(row['id'])
        if not isinstance(row['question'], str) or not row['question'].strip():
            raise ValueError(f"{row['id']}: empty question")
        if row['correct_answer'] not in LETTERS:
            raise ValueError(f"{row['id']}: invalid correct_answer")
        values = [row[key] for key in OPTIONS]
        if any(not isinstance(v, str) or not v.strip() for v in values):
            raise ValueError(f"{row['id']}: empty option")
        normalized = [' '.join(v.casefold().split()) for v in values]
        if len(set(normalized)) != 4:
            raise ValueError(f"{row['id']}: duplicate options")
        if not values[LETTERS.index(row['correct_answer'])].strip():
            raise ValueError(f"{row['id']}: answer references missing option")
        if row['difficulty'] not in {'easy', 'medium', 'hard'}:
            raise ValueError(f"{row['id']}: invalid difficulty")
        if any(not isinstance(row[key], str) or not row[key].strip() for key in ('category', 'subcategory')):
            raise ValueError(f"{row['id']}: invalid category metadata")
        if not isinstance(row['tags'], list) or any(not isinstance(t, str) or not t.strip() for t in row['tags']):
            raise ValueError(f"{row['id']}: invalid tags")
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate IDs')
    if original is not None:
        if len(original) != len(rows):
            raise ValueError('Question count changed')
        for before, after in zip(original, rows):
            for key in ('id', 'category', 'subcategory', 'tags'):
                if before[key] != after[key]:
                    raise ValueError(f"{before['id']}: required metadata changed: {key}")
            if set(before) != set(after):
                raise ValueError(f"{before['id']}: schema changed")


def improve(rows):
    result, audit = [], []
    seen = set()
    answer_positions = [0] * 13 + [1] * 13 + [2] * 12 + [3] * 12
    if len(rows) != len(answer_positions):
        raise ValueError('Balanced answer-position plan needs one slot per question')
    random.Random(20260930).shuffle(answer_positions)
    for i, before in enumerate(rows):
        number = int(before['id'].removeprefix('data_'))
        if number not in REVISIONS:
            raise ValueError(f"Missing editorial review for {before['id']}")
        seen.add(number)
        question, choices, difficulty, reason = REVISIONS[number]
        if len(choices) != 4 or len(set(choices)) != 4:
            raise ValueError(f"{before['id']}: invalid curated choices")
        answer_index = answer_positions[i]
        ordered = choices[1:]
        ordered.insert(answer_index, choices[0])
        after = dict(before)
        after.update(question=question, difficulty=difficulty, correct_answer=LETTERS[answer_index])
        after.update(zip(OPTIONS, ordered))
        changed = after != before
        audit.append({'id': before['id'], 'changed': changed,
                      'reason': reason if changed else 'Existing question and distractors were retained.',
                      'old_difficulty': before['difficulty'], 'new_difficulty': after['difficulty']})
        result.append(after)
    if seen != set(REVISIONS):
        raise ValueError('Revision list does not match all questions')
    return result, audit


def main():
    rows, fmt, root, list_key = load_questions(SOURCE)
    validate(rows)
    improved, audit = improve(rows)
    validate(improved, rows)
    out = SOURCE.with_name(SOURCE.stem + '_improved' + ('.jsonl' if fmt == 'jsonl' else '.json'))
    if fmt == 'jsonl':
        payload = '\n'.join(json.dumps(x, ensure_ascii=False) for x in improved) + '\n'
    else:
        if fmt == 'object':
            root = dict(root)
            root[list_key] = improved
            payload = json.dumps(root, ensure_ascii=False, indent=2) + '\n'
        else:
            payload = json.dumps(improved, ensure_ascii=False, indent=2) + '\n'
    out.write_text(payload, encoding='utf-8')
    audit_path = SOURCE.with_name('question_revision_audit.json')
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    reloaded, _, _, _ = load_questions(out)
    validate(reloaded, rows)
    if json.loads(audit_path.read_text(encoding='utf-8')) != audit:
        raise ValueError('Audit round-trip mismatch')
    print(f'Total questions: {len(improved)}')
    print(f"Modified: {sum(x['changed'] for x in audit)}")
    print(f"Unchanged: {sum(not x['changed'] for x in audit)}")
    print('\nDifficulty:')
    counts = Counter(x['difficulty'] for x in improved)
    for key in ('easy', 'medium', 'hard'):
        print(f'{key}: {counts[key]}')
    print('\nCorrect answer distribution:')
    counts = Counter(x['correct_answer'] for x in improved)
    for key in LETTERS:
        print(f'{key}: {counts[key]}')
    print('\nValidation:')
    for label in ('JSON parse', 'Unique IDs', 'Four non-empty options per question',
                  'Correct-answer references valid option', 'No exact duplicate options',
                  'Required metadata preserved', 'Audit and output round-trip'):
        print(f'[PASS] {label}')
    print('Semantic uniqueness: editorially reviewed for all 50 questions; not machine-verifiable')
    print(f'Output: {out}')
    print(f'Audit: {audit_path}')


if __name__ == '__main__':
    main()
