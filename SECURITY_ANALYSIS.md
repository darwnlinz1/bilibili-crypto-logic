# Phân tích luồng xác thực phía client — Bilibili.tv

**Loại tài liệu:** Báo cáo nghiên cứu bảo mật (Security Research Write-up)
**Tác giả:** darwnlinz1
**Trạng thái:** Công khai, đã ẩn thông tin nhạy cảm

## 1. Tóm tắt (Executive Summary)

Nghiên cứu này phân tích cách client Bilibili.tv bảo vệ thông tin đăng nhập trước khi gửi lên máy chủ. Kết quả cho thấy client ghép một chuỗi `hash` động lấy từ API với mật khẩu thô, rồi mã hóa cả cụm bằng **RSA-1024, padding PKCS#1 v1.5**, với **khóa công khai được nhúng cứng (hardcoded) trong client**, cuối cùng mã hóa Base64 và gửi đi. Thiết kế này dùng đúng khái niệm RSA nhưng chọn tham số và định dạng payload đã lỗi thời (khóa 1024-bit, padding cũ, mật khẩu thô nằm trong payload). Báo cáo mô tả phương pháp phân tích, đánh giá rủi ro và đề xuất hướng khắc phục theo chuẩn hiện đại.

## 2. Phạm vi & Đạo đức (Scope & Ethics)

- Toàn bộ phân tích thực hiện trên phần mềm/dịch vụ **tôi truy cập hợp pháp bằng tài khoản của chính mình**, phục vụ mục đích học tập và nghiên cứu bảo mật.
- **Không có hệ thống nào bị tấn công.** Không truy cập trái phép, không tấn công máy chủ hay tài khoản của người khác.
- Báo cáo **không kèm mã khai thác, không công bố thông tin đăng nhập thật**. Khóa công khai vốn đã có sẵn phía client và không phải bí mật; mọi mật khẩu/hash trong ví dụ đều là dữ liệu giả.
- Mục tiêu: chứng minh khả năng phân tích một luồng xác thực đóng và đề xuất cải thiện.

## 3. Phương pháp (Methodology)

- **Môi trường:** máy cá nhân, cô lập.
- **Cách tiếp cận:**
  1. Xác định các bước client thực hiện trong luồng đăng nhập (lấy hash động → dựng payload → mã hóa → gửi).
  2. Xác định thuật toán, kích thước khóa và kiểu padding.
  3. Tái hiện độc lập bằng module Python (`cryptography`) để kiểm chứng hiểu biết, thay phần tự viết ASN.1/DER thủ công của client gốc bằng thư viện chuẩn.
- **Tiêu chí "hiểu đúng":** dựng lại đúng định dạng payload (`hash + password`) và tạo được ciphertext hợp lệ với khóa công khai, không cần dùng lại binary gốc.

## 4. Phát hiện kỹ thuật (Technical Findings)

**Thuật toán:** RSA-1024, padding **PKCS#1 v1.5**.

**Cách dựng payload:**

1. Client lấy một chuỗi `hash` **động** từ API.
2. Ghép trực tiếp: `payload = hash + password` (mật khẩu ở dạng **thô**).
3. Mã hóa payload bằng **khóa công khai RSA-1024 nhúng cứng** trong client.
4. Base64 ciphertext rồi gửi lên endpoint xác thực.

**Luồng dữ liệu (mô tả):**

```
[API trả về hash động]
        │
        ▼
[payload = hash + mật khẩu thô]
        │
        ▼
[Mã hóa RSA-1024 / PKCS#1 v1.5 bằng khóa công khai hardcoded]
        │
        ▼
[Mã hóa Base64] ──► gửi lên endpoint đăng nhập
```

**Xử lý khóa:** khóa công khai RSA-1024 nằm sẵn trong client (bản chất là công khai, không phải bí mật). RSA không dùng IV. Không thấy lớp toàn vẹn/xác thực bổ sung.

## 5. Đánh giá bảo mật (Security Assessment)

- **Khóa RSA-1024 quá yếu theo chuẩn hiện nay.** Các hướng dẫn hiện đại khuyến nghị tối thiểu **2048-bit**; 1024-bit đã bị coi là lỗi thời.
- **Padding PKCS#1 v1.5 lỗi thời.** Có tiền sử dính lỗi *padding oracle* (Bleichenbacher); chuẩn hiện đại là **RSA-OAEP**.
- **Mật khẩu thô nằm trong payload.** Việc đặt mật khẩu chưa băm vào cụm mã hóa nghĩa là sau khi giải mã, server thấy mật khẩu thô — làm tăng rủi ro nếu server bị xâm phạm hoặc log sai.
- **`hash` động có thể là chống replay, nhưng chưa đủ.** Nếu không có ràng buộc thời gian/nonce chặt chẽ và toàn vẹn, giá trị của nó bị hạn chế.
- **Chỉ có RSA thì thiếu toàn vẹn.** Mã hóa đơn thuần không chứng thực dữ liệu không bị chỉnh sửa.
- **Ghi chú bối cảnh:** kênh truyền thường đã có TLS. Lớp RSA phía client là phòng thủ bổ sung; nếu tham số yếu, nó chủ yếu tạo cảm giác an toàn hơn là tăng an toàn thực chất (*security theater*).

## 6. Khuyến nghị (Recommendations)

Nếu đây là hệ thống của tôi, tôi sẽ:

1. **Nâng khóa lên RSA ≥ 2048-bit** (hoặc chuyển sang đường cong elliptic hiện đại cho trao đổi khóa).
2. **Thay PKCS#1 v1.5 bằng RSA-OAEP (SHA-256).**
3. **Không đưa mật khẩu thô vào payload.** Xác thực bằng giao thức chuẩn (băm phía server bằng Argon2/bcrypt, hoặc dùng cơ chế như SRP) để server không bao giờ thấy mật khẩu thô.
4. **Dùng mã hóa lai có xác thực:** AES-256-GCM cho dữ liệu + RSA-OAEP để bọc khóa, đảm bảo cả bí mật lẫn toàn vẹn.
5. **Ràng buộc `hash` động với nonce + thời hạn** để chống tấn công phát lại (replay).
6. **Dựa vào TLS làm lớp bảo vệ truyền tải chính**, coi mã hóa phía client là bổ sung chứ không thay thế.

## 7. Kết luận & Bài học (Conclusion & What I Learned)

Qua bài này tôi luyện được: đọc và tái hiện một luồng xác thực đóng, nhận diện vì sao RSA-1024 + PKCS#1 v1.5 + mật khẩu thô là những lựa chọn rủi ro, và hiểu vai trò của nonce/hash động trong chống replay. Bài học lớn nhất: dùng đúng thuật toán chưa đủ — **tham số và định dạng payload** mới quyết định hệ thống thực sự an toàn hay chỉ trông có vẻ an toàn.

> *Tuyên bố miễn trừ: Tài liệu chỉ phục vụ mục đích giáo dục và nghiên cứu bảo mật. Không kèm mã khai thác, không công bố thông tin đăng nhập thật.*
