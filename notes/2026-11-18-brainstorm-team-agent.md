# Brainstorm: AI Agent Team trên Telegram (hướng tới v2.2)

> File ghi lại cuộc thảo luận để không mất ý tưởng khi tắt Claude.
> Bắt đầu: 2026-11-18. Cập nhật mỗi khi có quyết định mới.
> Tài liệu gốc: `Requirement_v2.1.docx` (cùng thư mục cha).

## Vai trò của Claude trong cuộc thảo luận
Chuyên gia AI + chuyên gia hệ thống/thiết kế hệ thống, cùng người dùng xây AI Agent hỗ trợ công việc.
Quy trình: xây yêu cầu → chốt scope → thiết kế → thực hiện (không nhảy cóc).

## Công cụ người dùng có (đã trả phí)
- **Claude Code – subscription** (không còn là API key công ty 500 USD như v2.1) → giới hạn là hạn mức sử dụng theo khung giờ, không phải tiền.
- **Cursor (bản trả phí)** → dùng được Grok; có `cursor-agent` CLI chạy headless (cần kiểm tra trên bản đang cài).
- **Google Pro** → không kèm Gemini API; Gemini CLI đăng nhập bằng tài khoản Google (cần kiểm tra hạn mức).

## Mục đích (lời người dùng)
Tạo assistant hỗ trợ công việc hằng ngày, nối các tool/API thành một luồng hoàn chỉnh để không phải làm thủ công.

## Công việc của người dùng
Lập trình viên: code, review code, xây dựng giải pháp, viết tài liệu giải pháp, slide, viết thuyết minh xin đề tài…

Luồng điển hình (ví dụ lần gần nhất):
- Đầu vào: nhận xét của đối tác trên SharePoint → người dùng copy về đĩa.
- Công cụ: Word.
- Tốn thời gian nhất: suy nghĩ/cân nhắc giải pháp, thiết kế, làm tài liệu thuyết trình.
- Đầu ra: cho người dùng tự dùng – Word, source code…

## Quyết định đã có
1. **Pha trộn 2 chế độ:** phần nghĩ giải pháp/thiết kế → ngồi cùng (tương tác); phần làm tài liệu/slide/code → giao việc, chỉ review kết quả.
2. **Giao diện chính là Telegram, mô hình "team":** người dùng tạo nhóm, trong nhóm có người dùng + nhiều bot; mỗi bot là một AI Agent. Người dùng chia việc, bot làm, vướng thì hỏi ngay trong nhóm để các bên (người hoặc bot khác) giải quyết.
3. **Vai trò KHÔNG cố định trong thiết kế.** Người dùng chưa xác định trước đầu việc; vai trò được đưa vào **khi tạo nhóm chat mới**. (Khớp tinh thần v2.1: tác vụ cụ thể không cố định, cấu hình bằng mẫu.)
4. **Bể bot (pool bot)** (chốt 2026-11-18): tạo sẵn một số bot trung tính qua BotFather, dùng lại cho nhiều nhóm; vai trò gắn theo từng nhóm, không gắn vào bot. Tên bot chung toàn cục nên vai trò phải hiển thị ở chỗ khác (lời chào/tin ghim trong nhóm, tiền tố tin nhắn).
5. **Giao vai bằng mô tả chi tiết do người dùng tự viết** (chốt 2026-11-18): mỗi vai kèm hướng dẫn cách làm (bám nguồn nào, định dạng đầu ra…), không chỉ một chữ. Đề xuất (chưa chốt): lệnh `/team` trong nhóm, lưu thành mẫu dùng lại (`/team <tên-mẫu>`), tin ghim liệt kê vai.
   - **Sửa (2026-11-18): giao việc/giao vai ngay trên chat bằng lời tự nhiên**, KHÔNG soạn file mẫu trước. Ví dụ: "@Bot2 em lo phản biện, bám sát nhận xét đối tác, trả lời dạng bảng". Bộ điều phối hiểu lời giao, tóm tắt vai lại để người dùng xác nhận, rồi ghim. Giao thêm/sửa vai giữa chừng cũng bằng lời. (Đề xuất phụ, chưa chốt: nói "lưu đội này lại" để dùng lại lần sau.)
6. **Khi bot vướng: hỏi bot trước, người sau** (chốt 2026-11-18, phương án A): bot tự hỏi bot khác trong nhóm, tối đa ~3 lượt; quá giới hạn hoặc câu hỏi làm thay đổi quyết định giải pháp đã chốt → bắt buộc tag người dùng. Đánh đổi: tốn hạn mức hơn.
7. **Đường đi tài liệu: kết hợp** (chốt 2026-11-18, phương án C): mỗi nhóm ↔ một thư mục dự án trên VM, đồng bộ 2 chiều với máy người dùng (OneDrive/Syncthing – chưa chọn); vẫn cho thả file nhỏ (<20MB) vào Telegram, tự lưu vào thư mục dự án. Câu hỏi về tài liệu đối tác có được lên VM/Telegram không: người dùng không phản đối (coi như được phép).

## Đề xuất của Claude (chưa được người dùng chốt)
- Một **bộ điều phối trên VM** giữ token của mọi bot; bot không đọc được tin của bot khác trên Telegram, nên trao đổi giữa agent chuyển trong VM, rồi đăng ra nhóm bằng đúng bot. Người dùng vẫn thấy như các bot thảo luận thật. Có log, giới hạn số vòng.
- File **"quyết định giải pháp"** làm điểm bàn giao giữa phần tương tác và phần giao việc.
- Phân tải giữa Claude / Gemini / Grok để tiết kiệm hạn mức Claude.

## Ràng buộc kỹ thuật đã ghi nhận
- Telegram: bot không nhận tin nhắn của bot khác (cần kiểm lại changelog Bot API trước khi chốt).
- Telegram: bot phải tạo thủ công qua @BotFather; tên bot là chung cho mọi nhóm (đổi được qua API `setMyName` nhưng áp dụng toàn cục) → ảnh hưởng ý tưởng "vai trò khác nhau ở mỗi nhóm".
- v2.1 mục 9.8 đặt `/setjoingroups → Disable` và allowlist chỉ theo user ID → phải sửa nếu dùng nhóm.

## Xung đột với v2.1 (phát hiện 2026-11-18, khi đọc lại Requirement_v2.1.docx)
- **FR-32:** file kết quả chỉ báo "đã sẵn sàng" + đường dẫn qua Telegram; "không có file công việc nào được gửi đính kèm qua Telegram".
- **NFR-04:** không dán code/tài liệu công ty vào Telegram (Telegram không mã hoá đầu-cuối với bot).
- **NFR-03:** Gemini cá nhân chỉ dùng tra cứu công khai/việc cá nhân → không đưa tài liệu đối tác cho Gemini.
- Mâu thuẫn với: quyết định 7 (thả file vào Telegram), mô hình "bot thảo luận nội dung trong nhóm", và mong muốn đọc toàn bộ nội dung từ điện thoại. → **Chốt (2026-11-18): mức bảo mật theo từng nhóm.** Khi tạo nhóm, người dùng nói nhóm "nội bộ" (giữ FR-32/NFR-04: trong Telegram chỉ tóm tắt/tham chiếu, nội dung + file ở VM/thư mục đồng bộ, không nhận/gửi file công việc qua Telegram) hay "thoải mái" (nội dung + file đi qua Telegram). Gemini không bao giờ nhận tài liệu công ty, kể cả nhóm thoải mái (Claude đề xuất, giữ NFR-03).
- Hạ tầng v2.1 dùng lại được: Windows VM 16 core/14GB, WSL2, bridge Python gọi `claude -p`, mỗi dự án một thư mục (`~/ai/work/<du-an>/output/`), mẫu tác vụ = Claude Code skills.

## Câu hỏi đang mở
- ~~Khi tạo nhóm mới, khai báo vai trò thế nào?~~ → đã chọn bể bot. Đã chốt: dặn kỹ cách làm (quyết định 5).
- Mẫu Word/slide/thuyết minh đề tài có cố định không, ở dạng file nào? (đã hỏi, chưa trả lời)
- ~~Khi bot vướng: ai trả lời trước?~~ → A (quyết định 6).
- ~~Tài liệu đầu vào/đầu ra?~~ → C (quyết định 7).
- ~~Scope bản đầu?~~ → **Luồng "trả lời nhận xét đối tác → Word"** chạy trọn vẹn trước (chốt 2026-11-18).
- ~~File Word đầu ra có dạng gì?~~ → **Không cố định**: người dùng nói trên chat theo mẫu nào cho từng việc (chỉ file mẫu, mô tả định dạng), giống cách đang giao cho Claude Code. ⇒ Hệ quả thiết kế: mỗi bot cần năng lực như một agent CLI (Claude Code/cursor-agent/Gemini CLI) làm việc trực tiếp trong thư mục dự án: đọc file mẫu, tạo/sửa .docx.

## Phương án kiến trúc (đã trình bày, CHƯA chốt)
- **A (Claude chọn):** một tiến trình Python trên VM/WSL mở rộng bridge v2.1, giữ token mọi bot; mỗi lượt gọi `claude -p --resume` / `cursor-agent` / `gemini` trong thư mục dự án; trao đổi bot↔bot chuyển nội bộ; trạng thái trong file dữ liệu nhỏ; systemd tự khởi động lại.
- B: mỗi bot một tiến trình + Redis – nhiều thứ phải vận hành, không đáng với 1 người dùng.
- C: framework đa agent (CrewAI/AutoGen) – loại vì cần API key, không dùng được subscription/skills.
- Người dùng chưa chọn; họ yêu cầu dừng lại tổng hợp yêu cầu trước.
- **2026-11-18: người dùng bổ sung tầm nhìn: sau này bán hệ thống / mở rộng thành framework, nhiều người dùng.** Lập luận "B không đáng vì 1 người dùng" không còn đúng → phải đánh giá lại phương án sau khi rõ mô hình bán.

## Bước tiếp theo
**Bản tổng hợp yêu cầu: `2026-11-18-yeu-cau-v2.2.md`** (đọc file đó trước khi tiếp tục). Mục [Mở] 1 (đạt = người dùng hoặc bot reviewer báo đạt) và 2 (không đọc được nhóm nội bộ trên ĐT = hạn chế chấp nhận) đã chốt. Còn: chọn kiến trúc → design doc → kế hoạch.

## Khảo sát open source & giải pháp (2026-11-18, theo yêu cầu người dùng: "xây giải pháp, có dùng OSS ngoài như OpenClaw không, rồi làm HLD/LLD để các bên đánh giá")
- **OpenClaw** (MIT, TypeScript, gateway tự host, 20+ kênh, multi-agent qua bindings; Telegram = 1 bot/1 agent cố định, agent-to-agent qua `sessions_send`). Vấn đề: (1) vai gắn cứng vào bot qua cấu hình ⇄ yêu cầu bể bot + giao vai bằng lời theo nhóm; (2) **Anthropic cấm dùng OAuth subscription Claude trong harness bên thứ ba, áp cho OpenClaw từ 04/04/2026** (có nguồn không chính thức nói đã nới 05/2026 – chưa xác nhận) → phải dùng API key = tốn tiền, trái ràng buộc subscription; (3) bề mặt tấn công lớn (TQ hạn chế dùng trong cơ quan nhà nước 03/2026); (4) bán sản phẩm = bán cấu hình OpenClaw, khó khác biệt.
- **praktor** (MIT, Go, 1 bot Telegram, agent Claude Code trong Docker, Linux) – không hợp: 1 bot, không Windows.
- **telegram-ai-bridge** (MIT, 1 bot/agent trong cùng nhóm, đọc chéo qua Redis, chống vòng lặp) – gần ý tưởng nhất, dùng làm tham khảo.
- **Telegram Bot API (05/2026, Bot API 10.x): có "Bot-to-Bot Communication Mode" opt-in** → bot có thể nhận tin bot khác trong nhóm. Thiết kế vẫn chuyển nội bộ (lõi giữ mọi token), không phụ thuộc tính năng này; chưa đọc được trang chính thức (bị chặn mạng) – cần kiểm lại.
- **Claude Code `claude -p`**: là harness chính thức nên dùng subscription cá nhân cho bản đầu hợp lý hơn OpenClaw, nhưng chưa có tuyên bố chính thức cho trường hợp gọi từ orchestrator riêng → rủi ro ghi nhận; bản bán dùng API key/Agent SDK.
- **Claude đề xuất:** tự xây lõi (phương án A) bằng thư viện OSS (aiogram, SQLAlchemy, Pydantic, Claude Code skill docx), tham khảo mẫu thiết kế từ OpenClaw/telegram-ai-bridge; KHÔNG dựng trên OpenClaw. → đang hỏi người dùng xác nhận + định dạng HLD/LLD.
- Người dùng nhấn mạnh (2026-11-18): **"Claude của tôi là Claude Code"** (gói Claude Code, đăng nhập bằng code, không phải API key) → mọi agent Claude phải chạy qua Claude Code CLI; khớp hướng tự xây gọi `claude -p`. Vẫn chờ: xác nhận không dùng OpenClaw + định dạng HLD/LLD.

## Phản biện của chuyên gia về OpenClaw (2026-11-18)
- Chuyên gia đề xuất: OpenClaw (WSL2) làm cổng chat + định tuyến, Claude Code chạy qua ACP (đọc/sửa file, skill, deny-list); Gemini/Grok chỉ cho agent cá nhân/tra cứu công khai. Phải đạt 4 kiểm tra trước khi giao tài liệu thật: người lạ bị từ chối; agent việc không đọc workspace khác; Telegram không nhận file tài liệu; make/git push bị chặn ở cả 2 lớp quyền.
- Claude đánh giá: chuyên gia **đúng** ở điểm subscription — qua ACP, OpenClaw gọi chính Claude Code CLI ⇒ rủi ro điều khoản **ngang phương án A** (A cũng gọi `claude -p`); trước đó Claude xếp đây là nhược điểm nặng nhất của OpenClaw là chưa công bằng. Có nguồn (06/2026, chưa xác nhận) nói `claude -p`/Agent SDK đã chuyển sang pool credit riêng ⇒ phải kiểm tra chính sách Anthropic hiện hành trước khi xây, áp cho cả hai phương án.
- Đã xác minh tài liệu OpenClaw: ACP mặc định permissionMode=approve-reads + nonInteractivePermissions=fail; approve-all = cho ghi/exec không hỏi.
- Chuyên gia thiếu bối cảnh: giả định có `telegram_bridge_v21.py` (thực tế chưa có code v2.1); không tính tầm nhìn bán cho công ty tự cài, nhiều kỹ sư, chủ nhóm.
- Cả hai bên đồng ý: vai động theo nhóm bằng lời, trần 3 lượt, reviewer, chế độ nội bộ, skill Word **vẫn phải tự viết** dù dùng OpenClaw.
- Đề xuất của Claude: POC OpenClaw có giới hạn thời gian (1–2 ngày) với 4 kiểm tra của chuyên gia + 2 kiểm tra riêng (giao vai bằng lời cho bot bể trong nhóm mới không sửa config tay; trần 3 lượt rồi tag chủ). Chờ người dùng quyết.

## Phản biện đầy đủ ý kiến chuyên gia (2026-11-18, theo yêu cầu người dùng)
- Đồng ý: phân tích lỗ hổng mặc định của OpenClaw (workspace không phải hàng rào, agentToAgent/visibility mặc định mở, Telegram nhận nội dung dài + file, ACP không TTY, hai hệ quyền tách rời); Gemini tách theo agent chứ không trộn model; skill Word vẫn phải tự viết; 4 kiểm tra bảo mật nên đưa vào tiêu chí nghiệm thu dù chọn phương án nào.
- Phản biện: (1) chuyên gia dựa trên bối cảnh cũ (tưởng có bridge v2.1; không biết tầm nhìn bán cho công ty, nhiều kỹ sư, chủ nhóm); (2) "hết phần việc khó nhất" sai trọng tâm: OpenClaw lo phần dễ (nhiều bot, mention, session, tự khởi động lại), còn phần khó = vai động theo nhóm, trần 3 lượt, reviewer báo đạt, chế độ nội bộ, quyền chủ nhóm, skill Word – chính chuyên gia xếp vào "phải viết thêm"; (3) bot gắn cứng agent qua config ngược R2/R3 (cốt lõi); (4) gia cố + giữ cấu hình an toàn qua mỗi lần nâng cấp là chi phí lâu dài; (5) bán = bán cấu hình/plugin OpenClaw, phụ thuộc upstream đổi nhanh, khách phải duyệt bảo mật OpenClaw; (6) rủi ro subscription ngang A, không phải ưu điểm riêng; (7) WSL2 + Node + sandbox trên VM 14GB, thư mục dự án ở Windows.
- Kết luận Claude: giữ A; mượn mẫu thiết kế OpenClaw; bổ sung 4 kiểm tra của chuyên gia vào mục 6 design doc. POC OpenClaw chỉ cần nếu các bên đòi bằng chứng; kiểm tra quyết định = giao vai bằng lời cho bot bể ở nhóm mới không sửa config tay. Chờ người dùng quyết.

## HLD phương án A (2026-11-18)
- Người dùng xin HLD theo phương án A để xem. Bản chính lưu local: docs/2026-11-18-HLD-agent-team-v2.2-phuong-an-A.docx (bản online đã xoá theo yêu cầu) (10 mục + sơ đồ kiến trúc; đã đưa 4 kiểm tra bảo mật của chuyên gia vào mục 7 và tiêu chí nghiệm thu mục 10). Chờ người dùng/các bên góp ý; sau đó: LLD hoặc kế hoạch triển khai.
- 2026-11-18: người dùng đánh giá bản HLD 0.1 "không phải HLD" (thiếu chức năng + truy vết yêu cầu, kiến trúc chưa rõ, thiếu hình) → đề xuất 4+1 views. Claude đồng ý, thêm sơ đồ ngữ cảnh + ma trận chức năng↔yêu cầu. Bản mới: docs/2026-11-18-HLD-agent-team-v2.2-phuong-an-A-v0.2.docx (21 trang, 12 hình, F-01..F-22, AD-01..AD-09). Nguồn sinh lại (script vẽ hình + dựng docx) chỉ nằm trong scratchpad, có thể mất. Chờ người dùng review.
- 2026-11-18: người dùng review HLD v0.2, góp 3 ý: (1) chức năng quản lý skill có sẵn và thêm được; (2) xem các vai một bot đang đảm nhiệm; (3) luồng review và "đạt" phải hiện trên nhóm chat. → thành R13–R15. Bản v0.3: docs/2026-11-18-HLD-agent-team-v2.2-phuong-an-A-v0.3.docx (25 trang, 13 hình; F-23..F-27; mục 5.5 Thư viện skill, 5.6 Tra cứu vai; Hình 7 vẽ lại, Hình 8 mới về skill; AD-10..AD-12). Claude tự quyết (chờ người dùng phản đối): skill theo định dạng SKILL.md của Claude Code; chỉ quản trị viên nạp + duyệt; chủ nhóm gắn skill cho vai bằng lời; /vai trả lời từ CSDL không tốn lượt AI; nhóm Nội bộ chỉ hiện tóm tắt góp ý review. Câu hỏi mở mới: chủ nhóm có được tự thêm skill riêng cho nhóm không (đề xuất: không, ở bản đầu).
- 2026-11-19: chuyên gia nhận xét HLD v0.3: đủ để đánh giá A; chưa viết LLD trước khi sửa 4 điểm (2 bộ đếm độc lập; Nội bộ chỉ đăng mẫu cố định; chỉ lõi ghi decisions/ + chốt có xác nhận, R7 vào MVP; reviewer khác tác giả + chủ nhóm mở lại Thread đạt) và các điểm làm rõ (phiên CLI theo (nhóm,bot) + reset khi đổi vai/skill/provider; GroupMember; lượt diễn giải vai không đọc file, ok phải reply tin xác nhận; hết hạn mức không gợi ý Gemini; tín hiệu tách khỏi bài; lượt dở khi restart → lỗi; 9.2 thêm đặt mẫu vào templates/; thử deny-list trên Windows trước LLD; Syncthing ngoài phạm vi Nội bộ). Claude đồng ý cả, bổ sung: trần tổng lượt CLI/Thread (đề xuất 12), tín hiệu qua `claude -p --json-schema` (có trong 2.1.327), Gemini chạy trong thư mục trống. Phản biện nhỏ: Telegram nhóm cho ghim nhiều tin (không phải chỉ một) — vẫn làm 2 tin ghim riêng. Đo VM: RAM 14,6 GB, Claude Code cài qua npm. Bản v0.4: docs/2026-11-19-HLD-agent-team-v2.2-phuong-an-A-v0.4.docx (26 trang, F-28, AD-13..17, 6 kiểm tra bảo mật). Bước tiếp: ca thử Windows (claude -p + deny-list) rồi LLD.
- 2026-11-19: chạy spike cách ly trên Windows (spike/2026-11-19-windows-denylist/, README.md có bảng kết quả). Phát hiện: (1) settings trong workspace bị bỏ luật allow khi workspace chưa trust + agent sửa được → lõi phải cấp settings qua --settings + --restricted; (2) cấm Bash theo tiền tố bị lách (git -c … push đã push được); (3) cho python = đọc được nhóm khác; (4) bỏ hẳn Bash thì đạt mọi kiểm tra; (5) --json-schema chạy tốt; (6) Claude Code tự cập nhật giữa chừng → ghim phiên bản. Đề xuất HLD v0.5: agent không có Bash; docx và script skill chạy qua công cụ MCP do lõi cung cấp. Chờ người dùng quyết.
- 2026-11-19: spike 2 (spike/2026-11-19-docx-mcp/README.md): MCP server docx tự viết (docx_read, docx_build; ràng buộc đường dẫn trong server) + claude -p cấu hình C (không Bash). Sonnet soạn đạt cả 2 ca: mẫu có ô {{}} (28 s, ~0,10 USD) và bản phản hồi cũ làm mẫu (22 s, ~0,05 USD; không sót nội dung cũ); tấn công đọc nhóm B / ghi decisions bị server chặn. Kết luận: phương án "agent không shell + công cụ Word của lõi" dùng được → cập nhật HLD v0.5 (chờ người dùng).
- 2026-11-19: HLD v0.5 (docs/2026-11-19-HLD-agent-team-v2.2-phuong-an-A-v0.5.docx, 27 trang): agent không shell; luật quyền do lõi giữ ngoài workspace (--settings --restricted); F-29 công cụ Word của lõi (MCP); skill: SKILL.md nạp vào ngữ cảnh lượt, script bọc thành công cụ lõi; ghim phiên bản Claude Code; mục 7.4 kết quả thử; AD-18..AD-20. Nguồn sinh HLD đã chép vào docs/hld-src/. Bước tiếp: người dùng review v0.5 → LLD hoặc kế hoạch triển khai.
- 2026-11-19: chuyên gia nhận xét v0.5: giữ phương án; 4 điểm trước khi khoá (tin Nội bộ không được có câu cắt từ lời agent; agent chỉ ghi output/ + review/, chỉ dẫn nhóm + luật + bản gốc quyết định ở data/; khoá một lượt mỗi nhóm; chỉ chủ nhóm tạo lượt agent) + chữ lệch. HLD v0.6 (docs/2026-11-19-HLD-agent-team-v2.2-phuong-an-A-v0.6.docx, 28 trang, 14 hình, Hình 9 mới = chốt quyết định, AD-21..23) sửa tất cả. Claude chốt khác chuyên gia: tin nhắc nhiều bot → một lượt cho từng bot theo thứ tự nhắc (chuyên gia đề xuất chỉ bot đầu tiên); Grok cấm mặc định ở Nội bộ (Nội bộ mặc định chỉ Claude). Nguồn sinh cập nhật ở docs/hld-src/. Chờ người dùng duyệt khoá HLD → LLD / kế hoạch triển khai.
- 2026-11-19: người dùng chuyển sang LLD (HLD v0.6 coi như khoá). LLD v0.1: docs/2026-11-19-LLD-agent-team-v2.2-v0.1.docx (22 trang, 4 hình; nguồn docs/lld-src/). Nội dung: cấu trúc module, config.yaml, data/ + workspace, 16 bảng CSDL, audit jsonl, interface ports, lệnh claude.exe đầy đủ + settings.json + mcp.json + system.md, phiên CLI (fingerprint), luật intents tất định (10 luật), pipeline tin, scheduler khoá nhóm, ask/review/chốt, schema tín hiệu, 13 mẫu tin Nội bộ, provider, docx_mcp (op enum), skill (cấm file mã), lệnh chat, Telegram, mã lỗi, kiểm thử (6 kiểm tra bảo mật), cài đặt, 6 vấn đề mở. Chờ review → kế hoạch triển khai.
- 2026-11-19: chuyên gia review LLD v0.1: đủ chi tiết nhưng 6 lỗ ở đường xử lý tin (attach trước classify; /skill chat riêng không có đường vào + thiếu chat_type; chủ nhóm trả lời cho_nguoi không reset đếm; trần CLI đếm lúc chạy nên vượt; Grok/Gemini chưa có runtime; lượt diễn giải vai chờ trong on_event) + làm rõ (sua_vai, một Thread mở/nhóm, ask con lỗi, 'đạt' khi dang_lam/cho_nguoi, T14 xác nhận vai chỉ chữ chủ nhóm, luật quyền 6.2 chưa spike, pywin32, khoá ghi SQLite, kiểm quyền lệnh). Claude đồng ý cả; chạy spike 3 (spike/2026-11-19-lld-permissions/README.md, ~0,04 USD): settings.json đúng LLD 6.2 + prompt stdin + --append-system-prompt-file + --permission-prompts none trên 2.1.328 → 10/10 đạt (Edit(dir/**) cho cả Write; ngoài allow bị chặn); DISABLE_AUTOUPDATER có trong binary. LLD v0.2: docs/2026-11-19-LLD-agent-team-v2.2-v0.2.docx (25 trang; mục 1.4 bảng 13 thay đổi; 6.8 UnsupportedRuntime; T14, T15; luật intents 12 (thêm gan_skill, sua_vai)). Claude chọn thêm: /vai cũng không hiện instructions do model viết (cùng lỗ với T14); Thread mới đóng Thread cũ = hành vi mới cần người dùng biết (vấn đề mở #8). Chờ review → kế hoạch triển khai.
- 2026-11-19: người dùng xin kế hoạch triển khai. Viết theo skill writing-plans: lộ trình 5 giai đoạn docs/plans/2026-11-19-lo-trinh-trien-khai.md (P1 nền móng CSDL+nhận tin+lệnh; P2 Thread+lập lịch với FakeRuntime; P3 Claude Code thật + vai + chốt; P4 docx_mcp + file; P5 skill + vận hành + nghiệm thu) và kế hoạch chi tiết P1 docs/plans/2026-11-19-p1-nen-mong.md (11 task TDD; repo mã C:\Works\Labour\code; chưa có uv → cài qua pip). Lệch LLD có chủ ý (ghi vào LLD v0.3): SQLAlchemy sync thay aiosqlite; group_log.template_code; members role da_bo; MessageEvent thêm migrate_to_chat_id, chat_title, command_target; ChannelAdapter.bot_rights. Quyết định intents: 'đúng'/'dừng' chỉ nhận có dấu (flat trùng 'dung'). Kế hoạch P2..P5 viết sau khi xong giai đoạn trước. Chờ người dùng duyệt + chọn cách thực thi.

## 2026-11-20 – Chốt: xử lý hết hạn mức (quota)
- [Chốt] Người dùng: hết quota thì **dừng lại và hiện thông báo thôi**.
- Hệ quả thiết kế: lượt = loi (QUOTA), Thread giữ nguyên, gửi T11 (có giờ reset nếu đọc được, không thì bỏ phần giờ). Không tự chạy lại, không chặn/hẹn giờ theo quota_reset_at; chủ nhóm tự "chạy lại" khi muốn.
- Nhận diện nới lỏng: is_error + chuỗi chứa "usage limit" / "rate limit" / "quota" (không phân biệt hoa thường). Không khớp → lỗi chung, cũng dừng + báo. Vì vậy chuỗi lỗi chính xác không còn là vấn đề chặn; chỉ chụp lại khi gặp để thêm vào test.
- Áp dụng ở P3; ghi vào LLD v0.3 (bỏ cơ chế "không lượt mới tới quota_reset_at" ở bảng mã lỗi; mở #1 hạ xuống không chặn).
