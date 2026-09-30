"""Revise and validate the new_technology question bank."""

import collections
import json
import re
from pathlib import Path


ROOT = Path(__file__).parent
SOURCE = ROOT / "new_technology.json"
OUTPUT = ROOT / "new_technology_improved.json"
AUDIT = ROOT / "new_technology" / "question_revision_audit.json"
FIELDS = (
    "id", "question", "option_a", "option_b", "option_c", "option_d",
    "correct_answer", "category", "subcategory", "difficulty", "tags",
)

# Each entry was reviewed for a single intended answer and three related misconceptions.
# The answer position is assigned below without changing its meaning.
REVISIONS = {
    "tech_0001": (
        "Trong một hệ thống dùng LLM, đặc điểm nào phân biệt agent với chatbot chỉ trả lời từng lượt?",
        "Có thể chọn và thực hiện chuỗi hành động qua công cụ dựa trên kết quả trung gian",
        ["Luôn truy xuất tài liệu trước mỗi phản hồi theo một pipeline cố định",
         "Định tuyến mỗi yêu cầu tới đúng một công cụ theo quy tắc cố định",
         "Sinh phản hồi từng lượt từ ngữ cảnh mà không tự chọn bước hành động"],
        "medium", "Replaced unrelated options with nearby interaction and workflow patterns.",
    ),
    "tech_0002": (
        "Trong agent loop, sau khi mô hình phát ra lời gọi công cụ hợp lệ, bước nào thường diễn ra tiếp theo?",
        "Hệ thống chạy công cụ và đưa kết quả vào ngữ cảnh cho bước quyết định tiếp theo",
        ["Hệ thống đưa tên công cụ vào ngữ cảnh rồi yêu cầu mô hình đoán kết quả",
         "Hệ thống gửi ngay lời gọi công cụ như câu trả lời cuối cùng cho người dùng",
         "Hệ thống bỏ qua phản hồi công cụ và tiếp tục từ ngữ cảnh trước lời gọi"],
        "easy", "Replaced implausible events with plausible but incorrect loop transitions.",
    ),
    "tech_0003": (
        "Khi nhiệm vụ đã hoàn tất, dấu hiệu nào cho phép agent loop kết thúc ở lượt hiện tại?",
        "Mô hình trả lời cuối cùng mà không yêu cầu thêm công cụ hoặc handoff",
        ["Công cụ đầu tiên đã trả dữ liệu, dù mô hình còn yêu cầu bước khác",
         "Mô hình đã lập kế hoạch, dù chưa thực hiện các hành động cần thiết",
         "Agent đã chuyển cho agent khác, dù tác vụ được chuyển còn đang chạy"],
        "easy", "Focused the stopping condition and replaced arbitrary thresholds.",
    ),
    "tech_0004": (
        "Trong tool calling, vai trò của lời gọi hàm do LLM tạo ra là gì?",
        "Chỉ định công cụ và đối số để runtime thực thi rồi trả kết quả về mô hình",
        ["Thực thi mã của công cụ ngay bên trong trọng số của mô hình",
         "Ghi kết quả công cụ do mô hình suy đoán mà không cần runtime chạy",
         "Đưa mô tả công cụ vào prompt nhưng không truyền đối số để gọi"],
        "easy", "Replaced unrelated architecture changes with tool execution misconceptions.",
    ),
    "tech_0005": (
        "Vì sao khai báo schema tham số rõ ràng giúp giảm lỗi khi agent gọi tool?",
        "Schema chỉ ra tên, kiểu và ràng buộc đối số để lời gọi được kiểm tra",
        ["Schema tự kiểm chứng rằng dữ liệu trả về của tool luôn đúng về nội dung",
         "Schema tự quyết định thứ tự gọi nhiều tool thay cho agent loop",
         "Schema cấp quyền thực thi tool cho mọi yêu cầu sau khi đối số hợp lệ"],
        "medium", "Replaced unrelated distractors with common schema capability confusions.",
    ),
    "tech_0006": (
        "Trong điều phối nhiều agent, handoff thường thay đổi điều gì?",
        "Chuyển quyền xử lý lượt hội thoại cho agent chuyên môn nhận bàn giao",
        ["Gọi agent chuyên môn như tool rồi giữ agent gốc làm chủ lượt trả lời",
         "Cho hai agent chạy song song nhưng giữ nguyên agent chủ trì phản hồi",
         "Sao chép instructions của agent khác mà không đổi agent chủ trì"],
        "medium", "Contrasted handoff with neighboring delegation patterns.",
    ),
    "tech_0007": (
        "Trong mô hình manager gọi specialist như tool, ai thường sở hữu câu trả lời cuối cùng?",
        "Manager nhận kết quả từ specialist và tiếp tục điều phối câu trả lời",
        ["Specialist nhận toàn bộ quyền xử lý sau lời gọi như một handoff",
         "Runtime chọn ngẫu nhiên một specialist để trả lời thay manager",
         "Tool của specialist trực tiếp kết thúc lượt mà manager không nhận kết quả"],
        "medium", "Narrowed the manager-versus-handoff distinction to reply ownership.",
    ),
    "tech_0008": (
        "Lợi ích thiết kế nào có thể có khi chia workflow thành các agent chuyên biệt?",
        "Gán instructions và tools phù hợp cho từng phần việc rồi điều phối kết quả",
        ["Dùng cùng một tập instructions và tools cho mọi agent để tránh phân vai",
         "Chuyển mọi phần việc cho agent đầu tiên và chỉ dùng agent khác để ghi log",
         "Buộc mọi agent cùng quyết định một bước trước khi bất kỳ tool nào chạy"],
        "medium", "Replaced absolute claims with plausible specialization design choices.",
    ),
    "tech_0009": (
        "Model Context Protocol (MCP) chuẩn hóa chủ yếu lớp tương tác nào?",
        "Kết nối ứng dụng AI với tools, resources và prompts do server cung cấp",
        ["Trao đổi nhiệm vụ giữa các agent độc lập thông qua agent card",
         "Chuẩn hóa một workflow agent từ lập kế hoạch tới phê duyệt",
         "Chuẩn hóa nội dung câu trả lời cuối của mọi agent cho người dùng"],
        "medium", "Replaced unrelated technologies with adjacent protocol and integration concepts.",
    ),
    "tech_0010": (
        "Trong MCP, một MCP server thường phơi bày thành phần nào cho client?",
        "Các tools, resources hoặc prompts có thể khám phá và sử dụng qua giao thức",
        ["Lịch trình bắt buộc cho mọi lượt model và tool trong agent loop",
         "Các agent card để agent khác ủy quyền tác vụ theo giao thức A2A",
         "Chính sách phê duyệt chung của mọi client kết nối với server"],
        "medium", "Distinguished server capabilities from nearby host and A2A concepts.",
    ),
    "tech_0011": (
        "Vì sao chuẩn hóa giao diện MCP có thể giảm công sức tích hợp nhiều ứng dụng AI với nhiều dịch vụ?",
        "Một MCP server có thể cung cấp cùng giao diện giao thức cho nhiều client tương thích",
        ["Mỗi client vẫn phải dùng một giao thức khác nhau cho cùng một server",
         "Một server chuẩn tự thay thế mọi bước cấp quyền của dịch vụ phía sau",
         "Mỗi client tự nhận biết mọi API mới mà không cần server khai báo khả năng"],
        "medium", "Replaced obvious claims with integration boundary misconceptions.",
    ),
    "tech_0012": (
        "Trong A2A, Agent Card hỗ trợ chủ yếu việc gì giữa các agent độc lập?",
        "Công bố thông tin và khả năng để agent khác khám phá cách tương tác",
        ["Khai báo schema đối số cho từng MCP tool mà agent có thể gọi",
         "Lưu trạng thái chi tiết của mọi task đang chạy thay cho task ID",
         "Định nghĩa prompt bắt buộc mà mọi agent đối tác phải thực thi"],
        "medium", "Made the A2A question specific and contrasted adjacent discovery mechanisms.",
    ),
    "tech_0013": (
        "Phân biệt nào mô tả đúng trọng tâm của MCP và A2A?",
        "MCP kết nối ứng dụng AI với khả năng server; A2A hỗ trợ agent cộng tác qua tác vụ",
        ["MCP dùng agent card để ủy quyền; A2A phơi bày tools và resources",
         "MCP điều phối agent loop; A2A chuẩn hóa schema đối số của tool",
         "MCP truyền nhiệm vụ có trạng thái; A2A chỉ bổ sung context cho LLM"],
        "medium", "Replaced trivial exclusions with protocol role confusions.",
    ),
    "tech_0014": (
        "Trong workflow agent, tình huống nào phù hợp nhất để chèn human approval trước khi tiếp tục?",
        "Trước khi thực thi lệnh chuyển tiền có tác động thật và khó hoàn tác",
        ["Trước khi lập kế hoạch nội bộ chưa gây thay đổi bên ngoài",
         "Trước khi đọc metadata công khai để tìm công cụ phù hợp",
         "Trước khi tóm tắt dữ liệu đã được phép đọc mà không gửi đi"],
        "easy", "Replaced unrelated examples with decisions at different risk levels.",
    ),
    "tech_0015": (
        "Trong agent, guardrail được dùng để làm gì?",
        "Kiểm tra hoặc chặn input, output hay hành động không đạt quy tắc đã định",
        ["Ghi lại mọi tool call để truy vết nhưng không áp dụng quy tắc chặn",
         "Chọn agent chuyên môn dựa trên yêu cầu rồi bàn giao quyền xử lý",
         "Tóm tắt lịch sử hội thoại để giữ nội dung trong context window"],
        "easy", "Contrasted guardrails with tracing, routing and compaction.",
    ),
    "tech_0016": (
        "Một agent đề xuất gọi `delete_database()` trên dữ liệu production. Kiểm soát nào nên đặt trước bước thực thi?",
        "Chặn tại runtime để kiểm tra policy và yêu cầu phê duyệt phù hợp",
        ["Chỉ ghi trace sau khi xóa để có thể giải thích quyết định về sau",
         "Chỉ kiểm tra cú pháp lời gọi vì đối số hợp lệ đồng nghĩa an toàn",
         "Cho chạy ngay rồi nhờ mô hình đánh giá rủi ro ở lượt tiếp theo"],
        "medium", "Replaced irrelevant options with realistic but inadequate safeguards.",
    ),
    "tech_0017": (
        "Tracing một lần chạy agent giúp quan sát thông tin nào để gỡ lỗi?",
        "Trình tự model calls, tool calls, handoffs và kết quả của từng bước",
        ["Chỉ câu trả lời cuối cùng, không có các bước hoặc sự kiện trung gian",
         "Chỉ số accuracy trung bình trên tập kiểm thử, không có bản ghi từng lượt",
         "Các trọng số đã học của LLM trước và sau mỗi tool call"],
        "easy", "Replaced out-of-domain options with observability misconceptions.",
    ),
    "tech_0018": (
        "Vì sao đánh giá agent chỉ bằng câu trả lời cuối có thể bỏ sót lỗi?",
        "Câu trả lời đúng vẫn có thể đi kèm tool call sai, tốn kém hoặc không an toàn",
        ["Kết quả cuối chỉ phản ánh tốc độ token và không chứa nội dung cần đánh giá",
         "Trace thay thế hoàn toàn việc kiểm tra chất lượng câu trả lời cuối",
         "Mọi tool call đều đúng nếu câu trả lời cuối tình cờ khớp đáp án mẫu"],
        "medium", "Contrasted final-answer scoring with process-quality misconceptions.",
    ),
    "tech_0019": (
        "Trong agent, memory thường giữ loại thông tin nào để hỗ trợ các bước hoặc phiên sau?",
        "Các sự kiện, sở thích hoặc trạng thái hữu ích được truy xuất khi cần",
        ["Toàn bộ transcript nguyên vẹn, luôn đưa lại vào mỗi prompt sau",
         "Chỉ các kết quả tool của lượt hiện tại, bỏ qua thông tin từ phiên trước",
         "Chỉ trạng thái tính toán của model trong một lần sinh token hiện tại"],
        "easy", "Replaced unrelated storage claims with memory and context misconceptions.",
    ),
    "tech_0020": (
        "Vì sao đưa toàn bộ lịch sử rất dài vào mỗi lượt agent thường là lựa chọn kém?",
        "Tăng token, độ trễ và thông tin nhiễu, trong khi chỉ một phần lịch sử còn cần thiết",
        ["Lịch sử dài làm mọi tool ngừng hoạt động ngay cả khi context chưa đầy",
         "Chi phí token giảm khi prompt dài vì các lượt trước đã được xử lý",
         "Độ chính xác luôn tăng theo độ dài lịch sử bất kể thông tin có liên quan"],
        "medium", "Replaced impossible claims with context-cost and relevance misconceptions.",
    ),
    "tech_0021": (
        "Mục tiêu của context compaction khi agent làm nhiệm vụ dài là gì?",
        "Rút gọn lịch sử nhưng giữ trạng thái và thông tin cần cho các bước tiếp theo",
        ["Xóa toàn bộ kết quả tool để lượt sau bắt đầu không có trạng thái",
         "Giữ nguyên mọi token lịch sử nhưng đổi sang định dạng JSON ngắn hơn",
         "Chỉ giảm số token của câu trả lời cuối, không thay đổi ngữ cảnh chạy"],
        "medium", "Replaced unrelated operations with neighboring context-handling strategies.",
    ),
    "tech_0022": (
        "Trong coding agent, một skill dành cho workflow cụ thể thường là gì?",
        "Gói hướng dẫn có thể kèm tài nguyên hoặc script để agent dùng khi phù hợp",
        ["Bản ghi trace của một lần chạy để xem lại các bước thực thi",
         "Một tool call đơn lẻ với đối số được tạo trong lượt hiện tại",
         "Một handoff chuyển quyền xử lý cho agent chuyên môn khác"],
        "medium", "Replaced unrelated objects with nearby agent extensibility concepts.",
    ),
    "tech_0023": (
        "Điểm đặc trưng của computer-use agent so với gọi API có cấu trúc là gì?",
        "Quan sát giao diện và thao tác qua click, nhập liệu hoặc phím như người dùng",
        ["Chỉ gửi tham số JSON tới endpoint mà không cần quan sát giao diện",
         "Chỉ đọc mã nguồn UI rồi suy ra kết quả, không tương tác với màn hình",
         "Chỉ gọi database query và nhận bản ghi dưới dạng dữ liệu có cấu trúc"],
        "easy", "Replaced unrelated statements with interface-versus-API interaction modes.",
    ),
    "tech_0024": (
        "Sandbox giới hạn rủi ro của coding agent chạy lệnh chủ yếu bằng cách nào?",
        "Cô lập quyền truy cập và tài nguyên của tiến trình thực thi lệnh",
        ["Tự xác nhận mã sinh ra đúng trước khi tiến trình thực thi lệnh",
         "Tự sửa mọi lỗi cú pháp nên lệnh không thể thất bại khi chạy",
         "Chỉ ghi log lệnh đã chạy nhưng để tiến trình toàn quyền hệ thống"],
        "medium", "Contrasted isolation with validation, repair and logging.",
    ),
    "tech_0025": (
        "Trong programmatic tool calling, điều gì cho phép điều phối nhiều lần gọi tool mà không cần mô hình xử lý từng kết quả riêng lẻ?",
        "Mã thực thi gọi tool trong vòng lặp hoặc nhánh rồi tổng hợp kết quả cần thiết",
        ["Mô hình phát từng lời gọi riêng và đọc từng kết quả trước lời gọi kế tiếp",
         "Runtime tự chọn một tool duy nhất dựa trên tên hàm gần với prompt",
         "Mô hình lưu mọi kết quả trung gian vào prompt trước khi mã tiếp tục chạy"],
        "hard", "Distinguished code-orchestrated calls from ordinary sequential tool use.",
    ),
    "tech_0026": (
        "So với RAG có bước retrieval cố định, agentic RAG khác ở quyền quyết định nào?",
        "Agent có thể chọn lúc truy xuất, sửa truy vấn và lặp lại retrieval theo kết quả",
        ["Retriever luôn chạy đúng một lần trước khi model nhìn thấy câu hỏi",
         "Agent chỉ chọn prompt sinh đáp án sau một truy vấn cố định đã định sẵn",
         "Agent chỉ xếp hạng lại tài liệu, còn truy vấn và thời điểm truy xuất cố định"],
        "medium", "Replaced unrelated claims with decisions at different RAG stages.",
    ),
    "tech_0027": (
        "Trong pattern ReAct, cặp bước nào được xen kẽ để giải quyết nhiệm vụ?",
        "Lập luận về bước tiếp theo và thực hiện hành động để nhận quan sát mới",
        ["Lập toàn bộ kế hoạch một lần rồi thực thi mà không cập nhật từ quan sát",
         "Chỉ suy luận qua các bước trong prompt mà không hành động với môi trường",
         "Chỉ hành động theo công cụ cố định mà không điều chỉnh từ quan sát"],
        "easy", "Replaced acronym decoys with nearby workflow patterns.",
    ),
    "tech_0028": (
        "Agent phải chờ tác vụ bên ngoài vài giờ. Thiết kế nào hỗ trợ tiếp tục đúng tiến trình mà không giữ request mở liên tục?",
        "Lưu trạng thái chạy bền vững và resume khi có tín hiệu tác vụ hoàn thành",
        ["Chỉ lưu prompt gốc rồi chạy lại mọi hành động trước đó khi nhận tín hiệu",
         "Giữ trạng thái duy nhất trong bộ nhớ tiến trình và ngắt kết nối chờ tín hiệu",
         "Coi tác vụ đã xong khi timeout và sinh câu trả lời từ kết quả cũ"],
        "medium", "Replaced implausible options with persistence and recovery trade-offs.",
    ),
    "tech_0029": (
        "Trong thiết kế voice agent thời gian thực, yêu cầu nào nổi bật hơn pipeline ASR → LLM → TTS chạy tuần tự theo lượt?",
        "Giảm độ trễ và xử lý luồng nói liên tục, kể cả ngắt lời khi cần",
        ["Chờ người dùng kết thúc hẳn rồi mới bắt đầu mọi bước xử lý",
         "Chỉ tối ưu chất lượng bản chép lời, bỏ qua thời gian phản hồi bằng giọng nói",
         "Chỉ tối ưu tổng thời gian huấn luyện của ASR, LLM và TTS"],
        "medium", "Replaced unrelated claims with latency and turn-taking trade-offs.",
    ),
    "tech_0030": (
        "Khi agent điều khiển robot hoặc thiết bị thí nghiệm, cơ chế bổ sung nào cần được ưu tiên trước lệnh tác động vật lý?",
        "Kiểm tra giới hạn an toàn và quyền điều khiển trước khi gửi lệnh tới thiết bị",
        ["Chỉ đánh giá câu trả lời văn bản sau khi thiết bị đã thực hiện lệnh",
         "Chỉ lưu trace của lệnh để có thể điều tra nếu thao tác vượt giới hạn",
         "Chỉ yêu cầu model mô tả mức tự tin mà không kiểm tra lệnh ở runtime"],
        "medium", "Replaced irrelevant options with realistic but insufficient physical controls.",
    ),
}


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
        candidates = [value for value in data.values() if isinstance(value, list)]
        if len(candidates) == 1:
            return candidates[0], "object-list"
    raise ValueError("Expected a JSON array, an object containing one list, or JSONL")


def normalized(s):
    return re.sub(r"\s+", " ", s.casefold()).strip()


def validate(original, improved, audit):
    assert len(original) == len(improved) == len(audit) == len(REVISIONS)
    ids = [q["id"] for q in improved]
    assert len(ids) == len(set(ids)), "Duplicate IDs"
    assert set(ids) == set(REVISIONS)
    for old, new, record in zip(original, improved, audit):
        assert set(new) == set(old) == set(FIELDS), new.get("id")
        assert all(new[k] == old[k] for k in ("id", "category", "subcategory", "tags"))
        assert new["difficulty"] in {"easy", "medium", "hard"}
        assert new["correct_answer"] in "ABCD"
        assert isinstance(new["question"], str) and new["question"].strip()
        options = [new[f"option_{c}"] for c in "abcd"]
        assert all(isinstance(option, str) and option.strip() for option in options)
        assert len({normalized(option) for option in options}) == 4
        assert options["ABCD".index(new["correct_answer"])] == REVISIONS[new["id"]][1]
        assert record["changed"] == (new != old)
        assert record["old_difficulty"] == old["difficulty"]
        assert record["new_difficulty"] == new["difficulty"]
    return collections.Counter(q["difficulty"] for q in improved), collections.Counter(q["correct_answer"] for q in improved)


def main():
    original, fmt = load_questions(SOURCE)
    assert fmt == "array", f"Source format changed: {fmt}; update output writer"
    improved, audit = [], []
    for index, old in enumerate(original):
        question, answer, distractors, difficulty, reason = REVISIONS[old["id"]]
        assert len(distractors) == 3
        correct_index = (index + 1) % 4
        options = iter(distractors)
        ordered = [answer if position == correct_index else next(options) for position in range(4)]
        new = dict(old)
        new.update(question=question, difficulty=difficulty,
                   correct_answer="ABCD"[correct_index])
        new.update({f"option_{c}": value for c, value in zip("abcd", ordered)})
        improved.append(new)
        audit.append({"id": old["id"], "changed": new != old, "reason": reason,
                      "old_difficulty": old["difficulty"], "new_difficulty": difficulty})
    difficulty, answers = validate(original, improved, audit)
    OUTPUT.write_text(json.dumps(improved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    AUDIT.parent.mkdir(exist_ok=True)
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    roundtrip, _ = load_questions(OUTPUT)
    assert roundtrip == improved
    assert json.loads(AUDIT.read_text(encoding="utf-8")) == audit
    print(f"Total questions: {len(improved)}")
    print(f"Modified: {sum(row['changed'] for row in audit)}")
    print(f"Unchanged: {sum(not row['changed'] for row in audit)}")
    print("Difficulty:", dict(sorted(difficulty.items())))
    print("Correct answer distribution:", {c: answers[c] for c in "ABCD"})
    print("[PASS] JSON parse, unique IDs, schema, options, answer references, metadata, audit")


if __name__ == "__main__":
    main()
