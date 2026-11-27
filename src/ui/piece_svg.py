"""
SVG data cho 12 quân cờ — Bộ cburnett chuẩn Lichess/FIDE (CC BY-SA 3.0).
Tác giả gốc: Colin M.L. Burnett.
Mỗi quân được nhúng sẵn dưới dạng chuỗi SVG, không cần file ngoài.
"""

_PIECES: dict[str, str] = {

    # ═══════════════════════════════════════════════════════════
    # WHITE PIECES
    # ═══════════════════════════════════════════════════════════
    "wK": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <!-- cross -->
  <line x1="22.5" y1="6" x2="22.5" y2="13" stroke="#000" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="19.5" y1="8" x2="25.5" y2="8"  stroke="#000" stroke-width="1.5" stroke-linecap="round"/>
  <!-- body -->
  <path d="M12.5 37c5.5 3.5 14.5 3.5 20 0v-7c3.5-2 8.5-5 6-11-3.5-5.5-12-3-15 3.5V17c0 0-5-13-13-5-3 4 0 8 0 8v5c-5 1.5-7 5.5-5 7.5s4 5 7 6.5z"
        fill="#fff" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- collar lines -->
  <path d="M12.5 30c5.5-3 14.5-3 20 0" fill="none" stroke="#000" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M12.5 33.5c5.5-3 14.5-3 20 0" fill="none" stroke="#000" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M12.5 37c5.5-3 14.5-3 20 0"  fill="none" stroke="#000" stroke-width="1.5" stroke-linecap="round"/>
</svg>""",

    "wQ": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#fff;stroke:#000;stroke-width:1.5;stroke-linejoin:round">
    <path d="M8 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM24.5 7.5a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM41 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM16 8.5a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM33 8.5a2 2 0 1 1-4 0 2 2 0 0 1 4 0z"/>
    <path d="M9 26c8.5-8.5 15.5-8.5 27 0l2.5-12.5L31 25l-.3-14.1-5.2 13.6-3-14.5-3 14.5-5.2-13.6L14 25 6.5 13.5z" style="stroke-linecap:butt"/>
    <path d="M9 26c0 2 1.5 2 2.5 4 1 1.5 1 1 .5 3.5-1.5 1-1.5 2.5-1.5 2.5-1.5 1.5.5 2.5.5 2.5 6.5 1 16.5 1 23 0 0 0 1.5-1 0-2.5 0 0 .5-1.5-1-2.5-.5-2.5-.5-2 .5-3.5 1-2 2.5-2 2.5-4-8.5 1.5-18.5 1.5-27 0z"/>
    <path d="M11.5 30c3.5-1 18.5-1 22 0M12 33.5c4-1.5 17-1.5 21 0M13 37c4-1 15-1 19 0" style="fill:none"/>
  </g>
</svg>""",

    "wR": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#fff;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <path d="M9 39h27v-3H9v3zM12.5 32l1.5-2.5h17l1.5 2.5h-20zM12 36v-4h21v4H12z" style="stroke-linecap:butt"/>
    <path d="M14 29.5v-13h17v13H14z" style="stroke-linecap:butt;stroke-linejoin:miter"/>
    <path d="M14 16.5L11 14h23l-3 2.5H14zM11 14V9h4v2h5V9h5v2h5V9h4v5H11z" style="stroke-linecap:butt"/>
    <path d="M12 35.5h21M13 31.5h19M14 29.5h17M14 16.5h17M11 14h23" style="fill:none;stroke:#000;stroke-width:1;stroke-linejoin:miter"/>
  </g>
</svg>""",

    "wB": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:none;fill-rule:evenodd;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <g style="fill:#fff;stroke-linecap:butt">
      <path d="M9 36c3.39-.97 10.11.43 13.5-2 3.39 2.43 10.11 1.03 13.5 2 0 0 1.65.54 3 2-.68.97-1.65.99-3 .5-3.39-.97-10.11.46-13.5-1-3.39 1.46-10.11.03-13.5 1-1.354.49-2.323.47-3-.5 1.354-1.94 3-2 3-2z"/>
      <path d="M15 32c2.5 2.5 12.5 2.5 15 0 .5-1.5 0-2 0-2 0-2.5-2.5-4-2.5-4 5.5-1.5 6-11.5-5-15.5-11 4-10.5 14-5 15.5 0 0-2.5 1.5-2.5 4 0 0-.5.5 0 2z"/>
      <path d="M25 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z"/>
    </g>
    <path d="M17.5 26h10M15 30h15m-7.5-14.5v5M20 18h5" style="stroke-linejoin:miter"/>
  </g>
</svg>""",

    "wN": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:none;fill-rule:evenodd;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <path d="M22 10c10.5 1 16.5 8 16 29H15c0-9 10-6.5 8-21" style="fill:#fff"/>
    <path d="M24 18c.38 5.12-5.4 6.75-8 4-6.5-6.4-12-14 4-14 1.94 0 3.5.5 4.5 1" style="fill:#fff"/>
    <path d="M9.5 25.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0z" style="fill:#000;stroke:#000"/>
    <path d="M14.933 15.75a.5 1.5 30 1 1-.866-.5.5 1.5 30 0 1 .866.5z" style="fill:#000;stroke:#000"/>
    <path d="M15 15.5c.39 1.57 1.52 2.57 3.5 3.5-2.5.5-7.5 1.5-7.5 7-2.5-1-6-5.5-3.5-9C9 14 15.5 11 17 10" style="fill:#fff"/>
  </g>
</svg>""",

    "wP": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <path d="M22.5 9c-2.21 0-4 1.79-4 4 0 .89.29 1.71.78 2.38C17.33 16.5 16 18.59 16 21c0 2.03.94 3.84 2.41 5.03C15.41 27.09 11 31.58 11 39.5H34c0-7.92-4.41-12.41-7.41-13.47C28.06 24.84 29 23.03 29 21c0-2.41-1.33-4.5-3.28-5.62.49-.67.78-1.49.78-2.38 0-2.21-1.79-4-4-4z" style="opacity:1;fill:#fff;fill-opacity:1;fill-rule:nonzero;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"/>
</svg>""",

    # ═══════════════════════════════════════════════════════════
    # BLACK PIECES
    # ═══════════════════════════════════════════════════════════
    "bK": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <!-- cross -->
  <line x1="22.5" y1="6" x2="22.5" y2="13" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="19.5" y1="8" x2="25.5" y2="8"  stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
  <!-- body -->
  <path d="M12.5 37c5.5 3.5 14.5 3.5 20 0v-7c3.5-2 8.5-5 6-11-3.5-5.5-12-3-15 3.5V17c0 0-5-13-13-5-3 4 0 8 0 8v5c-5 1.5-7 5.5-5 7.5s4 5 7 6.5z"
        fill="#000" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- collar lines white -->
  <path d="M12.5 30c5.5-3 14.5-3 20 0" fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M12.5 33.5c5.5-3 14.5-3 20 0" fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M12.5 37c5.5-3 14.5-3 20 0"  fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
</svg>""",

    "bQ": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#000;stroke:#000;stroke-width:1.5;stroke-linejoin:round">
    <path d="M8 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM24.5 7.5a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM41 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM16 8.5a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM33 8.5a2 2 0 1 1-4 0 2 2 0 0 1 4 0z"/>
    <path d="M9 26c8.5-8.5 15.5-8.5 27 0l2.5-12.5L31 25l-.3-14.1-5.2 13.6-3-14.5-3 14.5-5.2-13.6L14 25 6.5 13.5z" style="stroke-linecap:butt"/>
    <path d="M9 26c0 2 1.5 2 2.5 4 1 1.5 1 1 .5 3.5-1.5 1-1.5 2.5-1.5 2.5-1.5 1.5.5 2.5.5 2.5 6.5 1 16.5 1 23 0 0 0 1.5-1 0-2.5 0 0 .5-1.5-1-2.5-.5-2.5-.5-2 .5-3.5 1-2 2.5-2 2.5-4-8.5 1.5-18.5 1.5-27 0z"/>
    <path d="M11.5 30c3.5-1 18.5-1 22 0M12 33.5c4-1.5 17-1.5 21 0M13 37c4-1 15-1 19 0" style="fill:none;stroke:#fff"/>
  </g>
</svg>""",

    "bR": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#000;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <path d="M9 39h27v-3H9v3zM12.5 32l1.5-2.5h17l1.5 2.5h-20zM12 36v-4h21v4H12z" style="stroke-linecap:butt"/>
    <path d="M14 29.5v-13h17v13H14z" style="stroke-linecap:butt;stroke-linejoin:miter"/>
    <path d="M14 16.5L11 14h23l-3 2.5H14zM11 14V9h4v2h5V9h5v2h5V9h4v5H11z" style="stroke-linecap:butt"/>
    <path d="M12 35.5h21M13 31.5h19M14 29.5h17M14 16.5h17M11 14h23" style="fill:none;stroke:#fff;stroke-width:1;stroke-linejoin:miter"/>
  </g>
</svg>""",

    "bB": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:none;fill-rule:evenodd;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <g style="fill:#000;stroke-linecap:butt">
      <path d="M9 36c3.39-.97 10.11.43 13.5-2 3.39 2.43 10.11 1.03 13.5 2 0 0 1.65.54 3 2-.68.97-1.65.99-3 .5-3.39-.97-10.11.46-13.5-1-3.39 1.46-10.11.03-13.5 1-1.354.49-2.323.47-3-.5 1.354-1.94 3-2 3-2z"/>
      <path d="M15 32c2.5 2.5 12.5 2.5 15 0 .5-1.5 0-2 0-2 0-2.5-2.5-4-2.5-4 5.5-1.5 6-11.5-5-15.5-11 4-10.5 14-5 15.5 0 0-2.5 1.5-2.5 4 0 0-.5.5 0 2z"/>
      <path d="M25 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z"/>
    </g>
    <path d="M17.5 26h10M15 30h15m-7.5-14.5v5M20 18h5" style="stroke:#fff;stroke-linejoin:miter"/>
  </g>
</svg>""",

    "bN": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:none;fill-rule:evenodd;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <path d="M22 10c10.5 1 16.5 8 16 29H15c0-9 10-6.5 8-21" style="fill:#000"/>
    <path d="M24 18c.38 5.12-5.4 6.75-8 4-6.5-6.4-12-14 4-14 1.94 0 3.5.5 4.5 1" style="fill:#000"/>
    <path d="M9.5 25.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0z" style="fill:#fff;stroke:#fff"/>
    <path d="M14.933 15.75a.5 1.5 30 1 1-.866-.5.5 1.5 30 0 1 .866.5z" style="fill:#fff;stroke:#fff"/>
    <path d="M15 15.5c.39 1.57 1.52 2.57 3.5 3.5-2.5.5-7.5 1.5-7.5 7-2.5-1-6-5.5-3.5-9C9 14 15.5 11 17 10" style="fill:#000"/>
  </g>
</svg>""",

    "bP": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <path d="M22.5 9c-2.21 0-4 1.79-4 4 0 .89.29 1.71.78 2.38C17.33 16.5 16 18.59 16 21c0 2.03.94 3.84 2.41 5.03C15.41 27.09 11 31.58 11 39.5H34c0-7.92-4.41-12.41-7.41-13.47C28.06 24.84 29 23.03 29 21c0-2.41-1.33-4.5-3.28-5.62.49-.67.78-1.49.78-2.38 0-2.21-1.79-4-4-4z" style="opacity:1;fill:#000;fill-opacity:1;fill-rule:nonzero;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"/>
</svg>""",
}


def get_svg(symbol: str) -> bytes:
    """Trả về SVG bytes cho ký hiệu quân cờ (vd: 'wK', 'bP')."""
    svg_str = _PIECES.get(symbol, "")
    return svg_str.encode("utf-8")
