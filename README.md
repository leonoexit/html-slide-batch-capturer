# Batch HTML Slide Screenshot Tool

Tool tự động chụp ảnh slide từ hàng loạt file HTML - dành cho người không chuyên về lập trình.

## Mô tả

Tool này giúp bạn:
- Tự động quét **tất cả** file `.html` trong thư mục
- Chụp ảnh từng slide (các thẻ `div` có class `.slide`)
- Lưu ảnh vào thư mục riêng biệt cho mỗi file HTML
- Không cần chạy thủ công từng file một

**Ví dụ:** Nếu bạn có `batch_1.html`, `batch_2.html`, `batch_3.html` trong cùng thư mục, tool sẽ tự động xử lý cả 3 file và tạo:
```
output_images/
├── batch_1/
│   ├── slide_01.png
│   ├── slide_02.png
│   └── ...
├── batch_2/
│   ├── slide_01.png
│   └── ...
└── batch_3/
    └── ...
```

---

## Cài đặt (Chỉ làm 1 lần duy nhất)

### Bước 1: Cài Python
- **Mac:** Python thường có sẵn. Mở Terminal và gõ `python3 --version` để kiểm tra
- **Windows:** Tải tại https://www.python.org/downloads/ (chọn bản Python 3.10 trở lên)

### Bước 2: Mở Terminal/Command Prompt
- **Mac:** Nhấn `Cmd + Space`, gõ "Terminal"
- **Windows:** Nhấn `Win + R`, gõ `cmd`, nhấn Enter

### Bước 3: Di chuyển vào thư mục chứa tool
```bash
# Mac/Linux:
cd /đường/dẫn/đến/thư/mục/này

# Windows:
cd C:\đường\dẫn\đến\thư\mục\này
```

**Ví dụ thực tế:**
```bash
# Mac:
cd /Users/tannguyen/Downloads/html-slide-batch-capturer

# Windows:
cd C:\Users\TanNguyen\Downloads\html-slide-batch-capturer
```

### Bước 4: Cài đặt thư viện cần thiết
Copy từng dòng này và paste vào Terminal/CMD, nhấn Enter:

```bash
pip install -r requirements.txt
```

Nếu lỗi, thử:
```bash
pip3 install -r requirements.txt
```

### Bước 5: Cài browser engine cho Playwright
```bash
playwright install chromium
```

Nếu lỗi, thử:
```bash
python3 -m playwright install chromium
```

**Xong! Bạn chỉ cần làm 5 bước trên 1 lần duy nhất.**

---

## Cách sử dụng (Mỗi lần chạy)

### 1. Chuẩn bị
Đặt tất cả file HTML của bạn vào thư mục chứa tool (cùng thư mục với file `capture_all.py`)

**Ví dụ cấu trúc thư mục:**
```
html-slide-batch-capturer/
├── capture_all.py          ← File tool
├── requirements.txt
├── README.md
├── astro_batch_1.html      ← File HTML của bạn
├── astro_batch_2.html      ← File HTML của bạn
└── marketing_slides.html   ← File HTML của bạn
```

### 2. Chạy tool
Mở Terminal/CMD, di chuyển vào thư mục tool, rồi gõ:

```bash
python capture_all.py
```

Hoặc nếu lỗi, thử:
```bash
python3 capture_all.py
```

### 3. Chờ và xem kết quả
Tool sẽ:
- Tự động tìm tất cả file `.html`
- Hiển thị tiến độ trên màn hình
- Tạo thư mục `output_images/` chứa tất cả ảnh

**Kết quả:**
```
output_images/
├── astro_batch_1/
│   ├── slide_01.png
│   ├── slide_02.png
│   └── slide_03.png
├── astro_batch_2/
│   ├── slide_01.png
│   └── slide_02.png
└── marketing_slides/
    ├── slide_01.png
    ├── slide_02.png
    ├── slide_03.png
    └── slide_04.png
```

---

## Câu hỏi thường gặp (FAQ)

### Q1: Tôi muốn xử lý file HTML ở thư mục khác, không phải thư mục chứa tool?
**Trả lời:** Copy tất cả file HTML vào thư mục chứa `capture_all.py` hoặc copy `capture_all.py` vào thư mục chứa file HTML của bạn.

### Q2: Tool báo lỗi "No HTML files found"?
**Trả lời:** Kiểm tra:
- File HTML có đuôi `.html` không? (không phải `.htm` hay `.HTML`)
- Bạn đang ở đúng thư mục chứa file HTML chưa? Gõ `ls` (Mac) hoặc `dir` (Windows) để xem danh sách file

### Q3: Tool báo lỗi "playwright not found"?
**Trả lời:** Bạn chưa cài đặt. Chạy lại:
```bash
pip install -r requirements.txt
playwright install chromium
```

### Q4: Tôi muốn thay đổi kích thước ảnh hoặc format?
**Trả lời:** Liên hệ người viết tool để custom (cần chỉnh code).

### Q5: Slide của tôi không phải class `.slide` mà là class khác?
**Trả lời:** Cần sửa code trong file `capture_all.py` dòng 97:
```python
slides = page.locator(".slide").all()  # Đổi ".slide" thành class của bạn
```

### Q6: Thư mục `output_images` đã có ảnh cũ, chạy lại có bị ghi đè không?
**Trả lời:** **Có**, ảnh cũ sẽ bị ghi đè. Nếu muốn giữ lại, đổi tên thư mục `output_images` cũ thành tên khác trước khi chạy lại.

---

## Yêu cầu hệ thống

- **Python:** 3.8 trở lên
- **Hệ điều hành:** Windows 10+, macOS 10.14+, hoặc Linux
- **Dung lượng:** ~300MB (cho Chromium browser engine)
- **RAM:** Tối thiểu 2GB khả dụng

---

## Cấu trúc file HTML yêu cầu

Tool hoạt động với file HTML có cấu trúc slide như sau:

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        .slide {
            width: 1200px;
            height: 1200px;
            /* ... */
        }
    </style>
</head>
<body>
    <div class="slide"><!-- Slide 1 --></div>
    <div class="slide"><!-- Slide 2 --></div>
    <div class="slide"><!-- Slide 3 --></div>
</body>
</html>
```

**Lưu ý:** Mỗi slide phải có class `slide` (hoặc bạn tự sửa code nếu dùng class khác).

---

## Hỗ trợ

Nếu gặp lỗi, hãy:
1. Đọc kỹ phần **FAQ** ở trên
2. Kiểm tra lại các bước cài đặt
3. Copy **toàn bộ** thông báo lỗi và hỏi người viết tool

---

## License

MIT License - Dùng thoải mái, miễn phí.

---

**Chúc bạn sử dụng tool hiệu quả!** 🚀
