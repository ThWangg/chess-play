# KẾ HOẠCH TRIỂN KHAI DỰ ÁN (PLAN.MD)
## ĐỒ ÁN CƠ SỞ 4: XÂY DỰNG ỨNG DỤNG CỜ VUA ĐA NỀN TẢNG (CROSS-PLATFORM CHESS APPLICATION)

> **Thông tin đồ án:**
> - **Sinh viên thực hiện:** Phan Nguyễn Thành Quang (24ITE077) & Tô Văn Hiền (24ITE035) - Lớp 24GITe
> - **Giảng viên hướng dẫn:** TS. Đặng Đại Thọ
> - **Khoa:** Khoa học Máy tính - Trường Đại học Công nghệ Thông tin & Truyền thông Việt - Hàn (VKU)
> - **Mục đích tài liệu:** Tài liệu kế hoạch chi tiết, đặc tả kiến trúc hệ thống và lộ trình triển khai chuẩn hóa dùng cho việc thực thi code với **Claude Code / AI Coding Assistant**.

---

## 📌 NGUYÊN TẮC THIẾT KẾ CỐT LÕI: HOÀN TOÀN KHÔNG DÙNG GIAO DIỆN WEB

Dự án **KHÔNG sử dụng trình duyệt web, không viết website (HTML/CSS/JS, React, Vue)**. Hệ thống chỉ gồm đúng 2 ứng dụng giao diện người dùng độc lập (Native GUI Apps) và 1 Backend chạy ngầm:
1. **Ứng dụng Desktop Windows (Python Native App):**
   - Viết hoàn toàn bằng **Python 3.10+** kết hợp thư viện GUI desktop **PySide6 (Qt6)**.
   - Chạy trực tiếp như một phần mềm Windows (.exe / python desktop window).
   - Tích hợp toàn bộ: Bàn cờ thi đấu, Đấu Bot AI Offline, Ghép trận, và **Giao diện Quản trị viên (Admin Panel View)** trực tiếp trong app dành cho tài khoản Admin.
2. **Ứng dụng Mobile Android (Android Studio Native App):**
   - Dự án xây dựng trong **Android Studio** bằng ngôn ngữ **Kotlin** thuần (Native Android, Jetpack Compose / Material 3).
   - Biên dịch và cài đặt trực tiếp dưới dạng file `.apk` trên điện thoại/máy ảo Android.
3. **Central Backend & Signaling Server (Headless Python Service):**
   - Viết bằng **Python (FastAPI / Redis / PostgreSQL)**.
   - Chạy ngầm trong Terminal (Headless, không có giao diện web), chỉ cung cấp API JSON cho 2 App và làm trạm trung chuyển tín hiệu kết nối P2P.
4. **Lưu ý về thuật ngữ "WebRTC":**
   - "WebRTC" ở đây là **giao thức mạng ngang hàng P2P (Peer-to-Peer Protocol)** được quy định trong Đề cương chi tiết của giảng viên. Cả app Python (dùng thư viện native `aiortc`) và app Android (dùng native `google-webrtc SDK`) sẽ kết nối P2P trực tiếp với nhau thông qua giao thức này mà **không cần bất kỳ trình duyệt web nào**.

---

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE)

Hệ thống bao gồm các phân hệ chính:
1. **Windows Client (Python Native Desktop App - PySide6):**
   - Giao diện người dùng: Đăng nhập/Đăng ký, Menu chính, Sảnh chờ (Lobby), Bàn cờ FIDE tương tác.
   - Chế độ chơi Offline với Bot AI (Minimax + Alpha-Beta Pruning).
   - Chế độ chơi Online PvP: Kết nối P2P qua `aiortc` tới đối thủ Android.
   - Chế độ Quản trị (Admin Mode): Tích hợp trực tiếp màn hình Dashboard quản trị xem thống kê, ván cờ gian lận, hàng đợi ghép trận.
2. **Android Client (Android Studio - Native Kotlin App):**
   - Xây dựng trên Android Studio với Jetpack Compose.
   - Đầy đủ tính năng: Đấu Bot AI Offline, Tìm trận Online, Tham gia phòng bằng mã phòng (Room Code).
   - Kết nối P2P qua Google WebRTC Android Native SDK để đấu trực tiếp với máy tính Windows.
3. **Hạ tầng P2P (WebRTC DataChannel):**
   - Kết nối trực tiếp máy-đối-máy (Android <-> Windows) qua Google STUN (`stun:stun.l.google.com:19302`).
   - Gửi nhận các gói tin nước đi dạng nhị phân/JSON với độ trễ thấp (< 80ms).
4. **Central Backend Server (Python FastAPI / Redis / PostgreSQL):**
   - Chạy ngầm (Headless Service).
   - Xử lý xác thực người dùng (JWT), quản lý phòng, hàng đợi tìm trận (Redis Matchmaking Queue).
   - Signaling Hub (Socket.io) điều phối trao đổi Offer/Answer/ICE để thiết lập kênh P2P.
5. **Data Warehouse (DWH) & ETL Pipeline:**
   - PostgreSQL thiết kế theo mô hình **Star Schema (Partitioned)**.
   - Python script nạp **50.000 ván đấu Lichess** phục vụ phân tích OLAP.
6. **AI Anti-Cheat Subsystem:**
   - Trích xuất 4 nhóm đặc trưng hành vi (Centipawn Loss, Tỷ lệ trùng nước đi Stockfish, Độ biến động thời gian đi quân, Tỷ lệ sai lầm trong thế cờ khó).
   - Huấn luyện mô hình Machine Learning (XGBoost, Random Forest).
   - Tự động chạy nền kiểm tra gian lận sau mỗi trận PvP kết thúc.

```
                      +------------------------------------------+
                      |            GOOGLE STUN SERVER            |
                      |        (stun.l.google.com:19302)         |
                      +------------------------------------------+
                                       ^        ^
                            ICE / STUN |        | ICE / STUN
                                       v        v
    +--------------------------------+            +----------------------------------+
    |   WINDOWS DESKTOP APP (PYTHON) |            |     ANDROID MOBILE APP (KOTLIN)  |
    | - PySide6 Native GUI           |    P2P     | - Android Studio Project         |
    | - Player View & Admin View     | <========> | - Jetpack Compose UI             |
    | - Offline AI (python-chess)    |  DataChan  | - Offline AI (Kotlin Engine)     |
    | - P2P Client (aiortc)          |            | - P2P Client (WebRTC Android SDK)|
    +--------------------------------+            +----------------------------------+
                   \                                         /
                    \   REST API (JSON) & Socket.io Signaling/
                     \----------------------\ /-------------/
                                            v v
                      +------------------------------------------+
                      |        CENTRAL BACKEND (PYTHON FASTAPI)  |
                      |          (Chạy ngầm - Headless)          |
                      | - REST API: Auth, Profiles, Matchmaking  |
                      | - Socket.io Signaling: P2P Coordinator   |
                      | - Post-game AI Anti-Cheat Auto Scanner   |
                      +------------------------------------------+
                               |                        |
                               v                        v
                      +------------------+    +----------------------+
                      |  REDIS (IN-MEM)  |    |  POSTGRESQL (DWH)    |
                      | - Matchmaking Q  |    | - Star Schema Tables |
                      | - Room Caching   |    | - 50,000 Lichess PGN |
                      +------------------+    +----------------------+
```

---

## 2. QUY CHUẨN CÔNG NGHỆ (TECH STACK)

| Thành phần | Môi trường / Ngôn ngữ | Thư viện & Công cụ chi tiết |
| :--- | :--- | :--- |
| **App Windows Desktop** | Python 3.10+ | **PySide6** (Qt6 Desktop GUI), `aiortc` (WebRTC Native), `python-chess`, `python-socketio` |
| **App Android Mobile** | Android Studio / Kotlin | **Jetpack Compose**, Coroutines/Flow, `org.webrtc:google-webrtc` (Native Android SDK) |
| **Backend Server (Ngầm)**| Python 3.10+ | **FastAPI**, Uvicorn, Python-SocketIO, Pydantic v2, SQLAlchemy 2.0 (asyncpg) |
| **Cache & Hàng đợi** | Redis 7.x | `redis-py` (Quản lý hàng đợi ghép trận & Session phòng đấu) |
| **Cơ sở dữ liệu & DWH** | PostgreSQL 15+ | **Star Schema (Partitioned)**, pgAdmin để xem dữ liệu |
| **ETL & Data Pipeline** | Python 3.10+ | `chess.pgn` (`python-chess`), `pandas`, `zstandard`, `multiprocessing` |
| **AI Anti-Cheat** | Python ML | `scikit-learn`, `xgboost`, `stockfish` engine wrapper, `numpy` |
| **Thuật toán Bot Offline**| Python & Kotlin | Minimax + Alpha-Beta Pruning, Piece-Square Tables (PST) |

---

## 3. CẤU TRÚC THƯ MỤC DỰ ÁN (MONOREPO DIRECTORY TREE)

```
dacs_4/
├── docs/                           # Tài liệu đề cương, báo cáo, đặc tả
│   ├── dcct_dacs_4.pdf
│   └── p2p_protocol_spec.md
├── client_windows/                 # ỨNG DỤNG DESKTOP WINDOWS (PYTHON + PYSIDE6)
│   ├── src/
│   │   ├── core/                   # Logic luật cờ FIDE, bàn cờ nội bộ
│   │   ├── ai/                     # Thuật toán Minimax + Alpha-Beta AI Bot
│   │   ├── network/                # aiortc WebRTC P2P client & Socket.io client
│   │   ├── ui/                     # Giao diện PySide6
│   │   │   ├── board_view.py       # Bàn cờ đồ họa, kéo thả, highlight ô
│   │   │   ├── lobby_view.py       # Sảnh chờ, tìm trận, tạo phòng
│   │   │   ├── history_view.py     # Lịch sử ván đấu & xem lại
│   │   │   └── admin_view.py       # MÀN HÌNH QUẢN TRỊ ADMIN (tích hợp trong desktop app)
│   │   └── main.py                 # Điểm khởi chạy ứng dụng Windows
│   ├── assets/                     # Bộ cờ (SVG/PNG), âm thanh (move.wav, capture.wav)
│   └── requirements.txt
├── client_android/                 # ỨNG DỤNG ANDROID (ANDROID STUDIO / KOTLIN)
│   ├── app/
│   │   ├── src/main/java/com/vku/chess/
│   │   │   ├── data/               # Network API, Socket.io, Local Storage
│   │   │   ├── domain/             # FIDE Chess Engine & Minimax Bot (Kotlin)
│   │   │   ├── ui/                 # Giao diện Jetpack Compose (Bàn cờ, Phòng, Lịch sử)
│   │   │   └── webrtc/             # Google WebRTC PeerConnection & DataChannel Wrapper
│   │   └── build.gradle.kts
│   └── build.gradle.kts
├── server/                         # BACKEND API & SIGNALING CHẠY NGẦM (FASTAPI)
│   ├── app/
│   │   ├── api/                    # Endpoints REST (auth, users, rooms, stats, admin)
│   │   ├── core/                   # Cấu hình, bảo mật JWT, kết nối DB/Redis
│   │   ├── models/                 # SQLAlchemy ORM Models
│   │   ├── schemas/                # Pydantic Schemas
│   │   ├── services/               # Quản lý trận đấu, hàng đợi Redis
│   │   ├── signaling/              # Socket.io Hub điều phối SDP Offer/Answer
│   │   └── main.py                 # File khởi chạy FastAPI server ngầm
│   ├── requirements.txt
│   └── Dockerfile
├── dwh_etl/                        # KHO DỮ LIỆU & PIPELINE NẠP 50K VÁN LICHESS
│   ├── sql/
│   │   ├── create_star_schema.sql  # DDL Star Schema PostgreSQL (Fact/Dims)
│   │   └── olap_features.sql       # Truy vấn OLAP trích xuất 4 nhóm đặc trưng
│   ├── pipeline/
│   │   ├── lichess_downloader.py   # Tải mẫu 50.000 ván từ Lichess Open Database
│   │   ├── pgn_parser.py           # Parser PGN streaming đa luồng
│   │   └── etl_loader.py           # Bulk insert vào PostgreSQL
│   └── requirements.txt
├── ai_anti_cheat/                  # HỆ THỐNG MACHINE LEARNING PHÁT HIỆN GIAN LẬN
│   ├── features/                   # Trích xuất 4 nhóm đặc trưng hành vi
│   │   ├── engine_evaluator.py     # Tính điểm Centipawn Loss & Engine Match Rate
│   │   └── feature_extractor.py    # Phân tích biến động thời gian & Blunder
│   ├── training/
│   │   ├── train_xgboost.py        # Huấn luyện mô hình XGBoost
│   │   ├── train_random_forest.py  # Huấn luyện mô hình Random Forest
│   │   └── evaluate_model.py       # Đánh giá Accuracy, F1, ROC-AUC
│   ├── inference/
│   │   └── anticheat_service.py    # Dịch vụ chấm điểm gian lận ván đấu
│   └── requirements.txt
├── tests/                          # KỊCH BẢN ĐO KIỂM HIỆU NĂNG & TEST
│   ├── test_p2p_latency.py         # Đo kiểm RTT giữa Windows và Android qua P2P
│   └── test_fide_rules.py          # Kiểm thử các thế cờ đặc biệt
├── plan.md                         # Kế hoạch chi tiết này
└── README.md
```

---

## 4. ĐẶC TẢ CHI TIẾT TỪNG PHÂN HỆ

### 4.1. Core Logic Cờ Vua & AI Offline
- **Tuân thủ luật FIDE toàn diện:**
  - Nước đi chuẩn của 6 loại quân cờ.
  - Luật đặc biệt: Nhập thành (Kingside & Queenside), Bắt tốt qua đường (En Passant), Phong cấp tốt (Promotion).
  - Trạng thái kết thúc ván: Chiếu bí (Checkmate), Hòa cờ (Stalemate, 50-move rule, lặp lại thế cờ 3 lần, thiếu quân hòa cờ).
  - Xuất/nhập ký hiệu chuẩn FEN và PGN.
- **Bot AI Offline (Chơi ngoại tuyến không cần Internet):**
  - **Minimax kết hợp Alpha-Beta Pruning:** Cắt tỉa các nhánh không tối ưu để đạt độ sâu tìm kiếm cao hơn.
  - **Hàm đánh giá (Heuristic Evaluation):** Tính điểm lực lượng (Material) kết hợp Piece-Square Tables (PST) để định vị quân cờ kiểm soát trung tâm.
  - Cung cấp 3 cấp độ: Dễ ($depth=2$), Vừa ($depth=3-4$), Khó ($depth=4-5$ kết hợp Quiescence Search).

---

### 4.2. Hạ Tầng Mạng P2P WebRTC Toàn Diện (Hỗ Trợ Đầy Đủ 3 Mô Hình Kết Nối)
- **Hỗ trợ linh hoạt 3 kịch bản thi đấu (Device-Agnostic Networking):**
  Do giao thức WebRTC DataChannel và định dạng gói tin nước đi (JSON) được chuẩn hóa thống nhất, hệ thống tự nhiên hỗ trợ đầy đủ 3 mô hình kết nối:
  1. **Python <-> Python (Windows vs Windows):** Hai người chơi trên máy tính đấu với nhau.
  2. **Android <-> Android (Mobile vs Mobile):** Hai người chơi trên điện thoại Android đấu với nhau.
  3. **Android <-> Python (Cross-platform):** Người chơi trên điện thoại Android đấu trực tiếp với người chơi trên máy tính Windows (Điểm nhấn trọng tâm của ĐCCT).
- **Cơ chế hoạt động P2P:**
  - Bất kể 2 thiết bị thuộc nền tảng nào, nước đi đều được gửi **trực tiếp máy-tới-máy** qua kênh `WebRTC DataChannel`.
  - Giúp giảm thiểu tối đa độ trễ (Latency < 50-80ms), mang lại cảm giác mượt mà tức thì khi đối thủ di chuyển quân.
- **Google STUN Server:**
  - Địa chỉ: `stun:stun.l.google.com:19302`.
  - Nhiệm vụ: Giúp App Android và App Windows vượt NAT để tìm thấy địa chỉ IP công khai của nhau.
- **Signaling Hub (FastAPI + Socket.io chạy ngầm):**
  - Chỉ làm nhiệm vụ "mai mối" ban đầu: Chuyển tiếp SDP Offer, SDP Answer và các ICE Candidates giữa 2 thiết bị. Sau khi kênh DataChannel mở thành công, dữ liệu nước cờ đi trực tiếp giữa 2 máy.
- **Định dạng gói tin nước đi qua DataChannel (JSON):**
  ```json
  {
    "type": "MOVE",
    "move_uci": "e2e4",
    "san": "e4",
    "fen_after": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
    "clock_remaining_ms": 298450,
    "timestamp": 1730700000123
  }
  ```
- **Fallback an toàn:** Nếu thiết bị ở mạng mạng 4G/NAT đối xứng không kết nối P2P được, hệ thống tự động fallback chuyển tiếp tin nhắn qua Socket.io của Server mà ván cờ không bị gián đoạn.

---

### 4.3. Kho Dữ Liệu DWH (PostgreSQL Star Schema Partitioned)
- **Mục tiêu:** Lưu trữ và phục vụ phân tích OLAP cho 50.000 ván đấu Lichess.
- **Thiết kế Star Schema:**
  - **Fact Table: `fact_games`**:
    - `game_id` (PK), `white_player_id`, `black_player_id`, `opening_id`, `time_id`, `winner`, `termination_type`, `white_rating`, `black_rating`, `total_moves`, `average_move_time_white`, `average_move_time_black`, `is_cheat_flagged`.
  - **Fact Table: `fact_moves` (Partitioned by Range theo ngày/tháng)**:
    - `move_id` (PK), `game_id` (FK), `move_number`, `player_color`, `move_uci`, `move_time_ms`, `centipawn_loss`, `engine_best_move`, `is_engine_top1_match`.
  - **Dimension Tables**: `dim_players`, `dim_openings` (ECO code, tên khai cuộc), `dim_time` (ngày, giờ, tháng, năm).
- **ETL Pipeline:** Python script đọc dữ liệu nén `.pgn.zst` của Lichess, sử dụng `multiprocessing` để phân tích song song và `COPY`/bulk insert nạp đủ 50.000 ván đấu nhanh chóng vào PostgreSQL.

---

### 4.4. Hệ Thống AI Anti-Cheat (Phát Hiện Gian Lận)
Đặc tả chi tiết **4 nhóm đặc trưng hành vi (Behavioral Features)**:
1. **Engine Agreement Rate (Tỷ lệ trùng khớp Engine):** Tỷ lệ các nước đi trùng với Top-1 và Top-3 nước đi tối ưu của Stockfish ở độ sâu $depth = 12-14$.
2. **Centipawn Loss (ACPL & Variance):** Độ suy giảm chất lượng thế trận trung bình mỗi nước đi. Người gian lận thường có ACPL rất thấp (< 15-20).
3. **Move Time Variance (Độ biến động thời gian đi quân):** Độ lệch chuẩn thời gian suy nghĩ. Gian lận thường có thời gian đi quân đều một cách cơ học (dù là nước khai cuộc dễ hay thế cờ phức tạp đều tốn khoảng 3-6 giây thao tác máy tính).
4. **Tactical Crisis Blunder Rate (Tỷ lệ sai lầm trong thế cờ khó):** Đánh giá tần suất mắc lỗi nghiêm trọng trong các tình huống chiến thuật phức tạp so với mức rating của người chơi.

- **Mô hình học máy:** Huấn luyện **XGBoost Classifier** và **Random Forest**. Đánh giá bằng Accuracy, F1-Score, ROC-AUC.
- **Cơ chế tự động sau trận:** Khi kết thúc ván đấu PvP, server tự động kích hoạt tiến trình chạy ngầm phân tích toàn bộ nước đi của người thắng cuộc. Nếu xác suất gian lận vượt ngưỡng (e.g. > 0.85), tài khoản sẽ bị tự động gắn cờ `is_cheat_flagged = True`.

---

### 4.5. Phân Hệ Quản Trị Tích Hợp Trên Desktop App Windows (Admin View)
- **Không dùng giao diện web**. Tính năng Admin được tích hợp trực tiếp thành một màn hình **Admin Dashboard** bên trong **App Python Windows (PySide6)**:
  - Khi đăng nhập bằng tài khoản có quyền `role = "admin"`, app sẽ hiển thị thêm tab **Quản trị (Admin Panel)**.
  - **Nội dung hiển thị:**
    - Thống kê tổng số ván cờ, số người dùng, tỷ lệ gian lận.
    - Giám sát hàng đợi tìm trận trực tiếp (Matchmaking Queue status).
    - Danh sách tài khoản bị gắn cờ gian lận kèm đồ thị trực quan phân tích nước đi (ACPL, biểu đồ thời gian).
    - Thống kê hiệu năng & độ trễ P2P mạng (RTT trung bình, Min, Max).

---

## 5. LỘ TRÌNH THỰC THI CHO CLAUDE CODE (PROMPTS TỪNG PHASE)

---

### Phase 1: Core Chess Logic, UI App Desktop & App Android + Bot AI
> **Thời gian:** 12/10 - 25/10  
> **Mục tiêu:** Xây dựng hoàn chỉnh logic FIDE, bàn cờ đồ họa trên **App Python Windows (PySide6)** và **App Android (Kotlin / Android Studio)**, tích hợp Bot AI Minimax đánh offline.

- [ ] **Task 1.1 (Windows App):** Tạo `client_windows/` với PySide6: bàn cờ 8x8, highlight nước đi, hiển thị quân bị bắt, đồng hồ cờ, popup chọn quân phong cấp tốt.
- [ ] **Task 1.2 (Windows FIDE):** Tích hợp `python-chess` xử lý toàn bộ luật FIDE: nhập thành, bắt tốt qua đường, các điều kiện hòa cờ.
- [ ] **Task 1.3 (Windows AI Bot):** Viết module AI Bot Minimax + Alpha-Beta Pruning trong `client_windows/src/ai/minimax_bot.py` với 3 cấp độ (Dễ, Vừa, Khó).
- [ ] **Task 1.4 (Android App):** Khởi tạo project trong `client_android/` (Android Studio, Kotlin, Jetpack Compose):
  - Vẽ bàn cờ tương tác cảm ứng chạm/kéo thả.
  - Bộ luật FIDE bằng Kotlin.
  - Bot AI Minimax chạy mượt mà trên Background Coroutine.

> **Lời nhắc giao việc cho Claude Code (Prompt Phase 1):**
```text
Tôi đang triển khai Phase 1 của đồ án Cờ vua Đa nền tảng (theo plan.md):
Dự án KHÔNG dùng web. Hãy thực hiện các công việc sau:
1. Tạo ứng dụng Desktop Windows hoàn chỉnh trong client_windows/ bằng Python 3.10+ và PySide6:
   - Giao diện bàn cờ 8x8 đồ họa đẹp mắt: highlight nước đi, hiển thị chấm tròn các ô đi được, hiển thị quân bị ăn, dialog phong cấp tốt.
   - Tuân thủ đầy đủ luật FIDE bằng thư viện python-chess.
   - Module AI Bot Offline (Minimax + Alpha-Beta Pruning, Piece-Square Tables) với 3 mức độ (Dễ, Vừa, Khó), chơi trực tiếp với Bot ngoại tuyến.
2. Khởi tạo cấu trúc project Android Studio thuần (Kotlin, Jetpack Compose) trong client_android/:
   - Bàn cờ cảm ứng kéo thả hoặc chạm để đi quân.
   - Tích hợp luật FIDE và Bot AI Minimax offline tương ứng.
Yêu cầu mã nguồn sạch, chạy độc lập không phụ thuộc web.
```

---

### Phase 2: Central Server (Headless), Matchmaking & Kết Nối P2P WebRTC
> **Thời gian:** 16/10 - 08/11  
> **Mục tiêu:** Xây dựng Backend FastAPI chạy ngầm, quản lý phòng, hàng đợi Redis và kết nối P2P trực tiếp Android Studio App <-> Python Windows App qua Google STUN.

- [ ] **Task 2.1 (Backend Headless):** Tạo `server/` với FastAPI (không có web UI):
  - API Đăng ký, Đăng nhập (JWT), Profile, Lịch sử trận.
  - Quản lý tạo phòng bằng Room Code (6 ký tự) và hàng đợi tìm trận ngẫu nhiên qua Redis.
- [ ] **Task 2.2 (Signaling Hub):** Xây dựng Socket.io Hub trong FastAPI để chuyển tiếp SDP Offer, Answer và ICE Candidates.
- [ ] **Task 2.3 (P2P Windows):** Tích hợp `aiortc` vào App PySide6, cấu hình Google STUN `stun:stun.l.google.com:19302`, mở DataChannel gửi nhận nước đi thời gian thực.
- [ ] **Task 2.4 (P2P Android):** Tích hợp Google WebRTC Android SDK vào Android Studio App, kết nối DataChannel với App Windows.
- [ ] **Task 2.5 (Gameplay Sync):** Đồng bộ nước đi, đồng hồ thời gian ván đấu, kết thúc ván đấu (Checkmate, Resign, Draw).

> **Lời nhắc giao việc cho Claude Code (Prompt Phase 2):**
```text
Tôi đang triển khai Phase 2 của đồ án Cờ vua Đa nền tảng (theo plan.md):
Hãy thực hiện các công việc sau:
1. Viết server FastAPI chạy ngầm (Headless, không giao diện web) trong server/:
   - Auth JWT (đăng ký, đăng nhập với PostgreSQL qua async SQLAlchemy).
   - Redis service quản lý hàng đợi ghép trận (matchmaking queue) và phòng chơi (room code).
   - Socket.io signaling server xử lý trao đổi SDP Offer, Answer và ICE Candidates cho WebRTC.
2. Viết module mạng WebRTC P2P chuẩn hóa (device-agnostic) hỗ trợ đầy đủ 3 kịch bản kết nối:
   - Python Desktop <-> Python Desktop (Win vs Win)
   - Android <-> Android (Mobile vs Mobile)
   - Android <-> Python Desktop (Cross-platform chéo nền tảng)
   - Kết nối tới Google STUN Server: stun:stun.l.google.com:19302.
   - Thiết lập DataChannel truyền nhận nước đi thời gian thực trực tiếp giữa 2 thiết bị.
   - Cơ chế Ping/Pong đo độ trễ mạng (RTT) và cơ chế tự fallback qua Socket.io nếu P2P bị chặn NAT.
Đảm bảo hai app có thể tìm trận, vào phòng và đánh cờ trực tiếp với nhau mượt mà bất kể thiết bị nào.
```

---

### Phase 3: Thiết Kế DWH & Pipeline ETL 50.000 Ván Lichess
> **Thời gian:** 09/11 - 18/11  
> **Mục tiêu:** Thiết kế Star Schema Partitioned trên PostgreSQL, viết script Python nạp 50.000 ván đấu Lichess.

- [ ] **Task 3.1 (SQL Schema):** Viết `dwh_etl/sql/create_star_schema.sql` gồm các bảng chiều (`dim_players`, `dim_openings`, `dim_time`) và bảng sự kiện partitioned (`fact_games`, `fact_moves`).
- [ ] **Task 3.2 (ETL Extractor):** Viết `dwh_etl/pipeline/lichess_downloader.py` tải mẫu 50.000 ván cờ Lichess PGN.
- [ ] **Task 3.3 (ETL Loader):** Viết `dwh_etl/pipeline/pgn_parser.py` và `etl_loader.py` dùng `multiprocessing` nạp nhanh dữ liệu vào PostgreSQL bằng bulk insert.

> **Lời nhắc giao việc cho Claude Code (Prompt Phase 3):**
```text
Tôi đang triển khai Phase 3 của đồ án Cờ vua Đa nền tảng (theo plan.md):
Hãy thực hiện các công việc sau:
1. Viết mã SQL tạo DWH Star Schema trên PostgreSQL trong dwh_etl/sql/create_star_schema.sql:
   - Các bảng chiều: dim_players, dim_openings, dim_time.
   - Bảng sự kiện: fact_games và fact_moves (áp dụng Partitioning theo tháng hoặc khoảng ID).
   - Thiết lập khóa ngoại và các index cần thiết để tối ưu hóa truy vấn phân tích OLAP.
2. Viết bộ công cụ ETL Python hoàn chỉnh trong dwh_etl/pipeline/:
   - Parser đọc streaming file PGN từ Lichess, trích xuất siêu dữ liệu ván đấu và từng nước đi.
   - Tối ưu hóa nạp dữ liệu đa tiến trình (multiprocessing) và bulk insert vào PostgreSQL để nạp 50.000 ván cờ với tốc độ cao và kiểm soát bộ nhớ RAM.
3. Tạo file README hướng dẫn chi tiết cách chạy ETL pipeline từ dòng lệnh terminal.
```

---

### Phase 4: Trích Xuất Đặc Trưng OLAP & Huấn Luyện AI Anti-Cheat
> **Thời gian:** 19/11 - 25/11  
> **Mục tiêu:** Viết câu lệnh OLAP trích xuất 4 đặc trưng hành vi và huấn luyện mô hình XGBoost, Random Forest.

- [ ] **Task 4.1 (OLAP Queries):** Viết `dwh_etl/sql/olap_features.sql` trích xuất các đặc trưng thời gian và blunder từ PostgreSQL DWH.
- [ ] **Task 4.2 (Engine Analyzer):** Viết `ai_anti_cheat/features/engine_evaluator.py` dùng Stockfish tính Centipawn Loss và tỷ lệ trùng khớp nước đi Top-1/Top-3.
- [ ] **Task 4.3 (Model Training):** Huấn luyện mô hình XGBoost và Random Forest trong `ai_anti_cheat/training/`, xuất báo cáo đánh giá Accuracy, F1, ROC-AUC, lưu file model `.joblib`.

> **Lời nhắc giao việc cho Claude Code (Prompt Phase 4):**
```text
Tôi đang triển khai Phase 4 của đồ án Cờ vua Đa nền tảng (theo plan.md):
Hãy thực hiện các công việc sau trong ai_anti_cheat/:
1. Viết các truy vấn SQL OLAP trong dwh_etl/sql/olap_features.sql để tổng hợp các thông số hành vi người chơi từ DWH PostgreSQL.
2. Viết engine_evaluator.py sử dụng python-chess và Stockfish để tính Centipawn Loss (CPL) và tỷ lệ trùng khớp nước đi (Top-1 / Top-3 Match Rate).
3. Đóng gói đầy đủ 4 nhóm đặc trưng hành vi (Engine Match Rate, ACPL, Move Time Variance, Tactical Crisis Blunder Rate) thành tập dữ liệu huấn luyện.
4. Viết script huấn luyện và đánh giá mô hình học máy:
   - Mô hình XGBoost Classifier và Random Forest Classifier.
   - Xuất báo cáo phân loại (Classification Report), ma trận nhầm lẫn (Confusion Matrix) và đường cong ROC-AUC.
   - Lưu model tối ưu nhất để sẵn sàng tích hợp vào server dự đoán sau ván đấu.
```

---

### Phase 5: Tự Động Quét Gian Lận Sau Trận & Màn Hình Admin Trên App Desktop
> **Thời gian:** 19/11 - 25/11  
> **Mục tiêu:** Server tự động kích hoạt kiểm tra gian lận khi trận đấu kết thúc; tích hợp màn hình Admin Dashboard trực tiếp vào App Python Desktop (PySide6).

- [ ] **Task 5.1 (Post-Game Auto Scanner):** Sau khi ván PvP kết thúc, server tự động chạy Background Task trích xuất 4 đặc trưng và đưa qua model ML chấm điểm. Nếu vượt ngưỡng nghi vấn -> gắn cờ `is_cheat_flagged = True`.
- [ ] **Task 5.2 (Admin View Trong Desktop App Windows):**
  - Xây dựng màn hình `admin_view.py` trong `client_windows/src/ui/`:
    - Chỉ hiển thị khi tài khoản đăng nhập có quyền Admin.
    - Hiển thị bảng danh sách các tài khoản gian lận bị gắn cờ, biểu đồ phân tích nước đi.
    - Xem trạng thái hàng đợi ghép trận trực tiếp và thống kê hiệu năng hệ thống.

> **Lời nhắc giao việc cho Claude Code (Prompt Phase 5):**
```text
Tôi đang triển khai Phase 5 của đồ án Cờ vua Đa nền tảng (theo plan.md):
Hãy thực hiện các công việc sau:
1. Xây dựng dịch vụ phân tích tự động sau trận (Post-Game Anti-Cheat Runner) trong backend server:
   - Khi một ván cờ kết thúc, tự động kích hoạt background worker nạp dữ liệu nước đi và thời gian của ván cờ vào mô hình ML đã huấn luyện ở Phase 4.
   - Ghi nhận xác suất gian lận và tự động cập nhật cờ is_cheat_flagged trong database.
2. Xây dựng màn hình Admin View trực tiếp bên trong App Desktop Windows (PySide6, không dùng web):
   - Tạo tab Quản trị dành cho tài khoản Admin trong client_windows/src/ui/admin_view.py.
   - Hiển thị danh sách tài khoản bị gắn cờ gian lận, cho phép xem chi tiết biểu đồ ACPL và thời gian nước đi.
   - Thống kê số lượng người chơi, số trận đấu và trạng thái hàng đợi tìm trận.
```

---

### Phase 6: Đo Kiểm Độ Trễ P2P, Kiểm Thử Toàn Diện & Chuẩn Bị Nghiệm Thu
> **Thời gian:** 26/11 - 01/12  
> **Mục tiêu:** Đo kiểm độ trễ mạng P2P giữa Android và Windows, kiểm thử biên và hoàn thiện tài liệu báo cáo.

- [ ] **Task 6.1 (Đo kiểm RTT P2P):** Viết script gửi 100 gói tin P2P giữa Android và Windows qua STUN, đo RTT trung bình, min, max, xuất bảng số liệu và đồ thị để đưa vào báo cáo đồ án.
- [ ] **Task 6.2 (Kiểm thử hệ thống):** Kiểm tra ngoại lệ mất mạng, kiểm tra các thế cờ đặc biệt FIDE.
- [ ] **Task 6.3 (Tài liệu):** Hoàn thiện file `README.md` hướng dẫn chạy App Windows, App Android Studio và Server.

> **Lời nhắc giao việc cho Claude Code (Prompt Phase 6):**
```text
Tôi đang triển khai Phase 6 của đồ án Cờ vua Đa nền tảng (theo plan.md):
Hãy thực hiện các công việc sau:
1. Viết script kiểm thử và đo độ trễ mạng P2P giữa App Windows và App Android:
   - Đo RTT trung bình, min, max, jitter qua 100 lần gửi nước đi qua WebRTC DataChannel.
   - Xuất dữ liệu thống kê ra file CSV và vẽ biểu đồ hiệu năng.
2. Rà soát chất lượng code:
   - Viết các unit tests cho FIDE rules (nhập thành, bắt tốt qua đường, hòa cờ 50 nước).
   - Kiểm tra xử lý ngoại lệ khi mất kết nối giữa 2 app.
3. Hoàn thiện hướng dẫn triển khai toàn diện trong README.md.
```

---

## 6. PHÂN CÔNG THEO ĐỀ CƯƠNG CHI TIẾT

| Thành viên | Trách nhiệm chính phụ trách |
| :--- | :--- |
| **Phan Nguyễn Thành Quang** (24ITE077) | - Central Backend ngầm (FastAPI, Redis, Socket.io Signaling).<br>- App Desktop Windows (Python PySide6, aiortc WebRTC).<br>- Huấn luyện mô hình AI Anti-Cheat (XGBoost, trích xuất đặc trưng CPL & Engine Agreement). |
| **Tô Văn Hiền** (24ITE035) | - App Mobile Android (Android Studio, Kotlin, Jetpack Compose, WebRTC Android SDK).<br>- Thiết kế DWH PostgreSQL Star Schema & xây dựng ETL Pipeline 50.000 ván Lichess.<br>- Đo kiểm độ trễ P2P Android - Windows & Màn hình Quản trị Admin Dashboard trên App Desktop. |
