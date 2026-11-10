# TOKEN EFFICIENCY & CODING RULES

1. Output Format:
   - NEVER rewrite an entire file when modifying code.
   - ALWAYS output unified diffs or minimal surgical edits showing only the changed lines with 2-3 lines of context.
   - Never output boilerplate comments or verbose explanations unless explicitly requested.

2. Communication Style:
   - Be concise and direct.
   - Drop polite filler words, conversational pleasantries, intros, and closing summaries.
   - Jump straight into the solution, code change, diff, or terminal command.

3. Context Retrieval & Token Conservation:
   - When inspecting code, use targeted grep or symbol search first before reading full files.
   - Do NOT read huge files end-to-end; read targeted line ranges.
   - For git operations, run `git status` and `git diff` via terminal instead of re-reading unchanged files.
   - Never regenerate files that are already completed and working.

---

# PROJECT DOMAIN CONTEXT & BENCHMARKING (CROSS-PLATFORM CHESS SYSTEM)

When generating code, analyzing architectures, or evaluating models for this workspace:

1. System Architecture & Constraints:
   - NO WEB / BROWSER UI: 100% Native Desktop & Mobile.
   - Client Android: Native Android Studio project, Kotlin, Jetpack Compose, WebRTC Android SDK (`org.webrtc:google-webrtc`).
   - Client Windows: Native Desktop Python 3.10+, PySide6 (Qt6 GUI), `aiortc` (WebRTC P2P), `python-chess`. Includes embedded Admin View tab.
   - Central Server: Headless Python 3.10+, FastAPI, Socket.io (Signaling Hub), Redis 7 (Queue/Matchmaking/Session Cache), PostgreSQL.
   - Network Protocol: Device-agnostic P2P via WebRTC DataChannel (Google STUN: `stun:stun.l.google.com:19302`) with Socket.io fallback.
     * Supports: Python <-> Python, Android <-> Android, and Android <-> Python (Cross-platform).

2. Data Storage & Synchronization Roles:
   - Real-time Move Sync: P2P WebRTC DataChannel (< 50ms) + In-memory Redis cache (FEN, clock, reconnection state).
   - Game History & User DB: PostgreSQL operational tables (`users`, `games`, `game_moves`).
   - Offline Mode: Local SQLite / JSON (Windows) and Android Room Database (Android).

3. Data Warehouse (DWH) Rules:
   - Schema Pattern: Star Schema with Fact tables (`fact_games`, `fact_moves` with Range Partitioning) and Dimension tables (`dim_players`, `dim_openings`, `dim_time`).
   - Database: PostgreSQL 15+.
   - ETL Source: Lichess Open Database (50,000 games PGN streaming parser, multiprocessing, bulk insert).
   - Focus on OLAP aggregation performance and clean feature extraction queries.

4. Anti-Cheat Machine Learning Standards:
   - Domain: Chess Fair Play & Anomaly Detection.
   - Target Models: XGBoost, Random Forest, or LightGBM (Binary Classification).
   - 4 Core Feature Groups:
     * Feature 1: Engine Agreement Rate (Top-1, Top-2, Top-3 Stockfish match rate at depth 12-14).
     * Feature 2: Centipawn Loss (Average CPL / ACPL & CPL Variance).
     * Feature 3: Move Time Variance (Standard deviation and robotic move-time consistency).
     * Feature 4: Blunder Rate in Tactical Crisis.
   - Evaluation Metrics: Precision (strictly prioritize over Recall to minimize false accusations), F1-Score, ROC-AUC, PR-AUC.
   - Execution: Automatic post-game background worker evaluating the winner's moves and updating `is_cheat_flagged`.

5. Directory Layout Reference:
   - `client_windows/` -> Python Desktop GUI (PySide6)
   - `client_android/` -> Android Studio Native Project (Kotlin)
   - `server/`         -> FastAPI & Socket.io Signaling Hub
   - `dwh_etl/`        -> Star Schema DDL, Lichess ETL Pipeline
   - `ai_anti_cheat/`  -> Stockfish evaluation, feature extraction, ML training
   - `tests/`          -> P2P latency benchmark & FIDE rule tests

