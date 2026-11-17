"""
SVG data cho 12 quân cờ (embedded, không cần file ngoài).
Mỗi hàm trả về bytes SVG cho quân tương ứng.
"""
_PIECES: dict[str, str] = {
    # WHITE pieces
    "wK": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#fff;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <path d="M22.5 11.63V6M20 8h5"/>
    <path d="M22.5 25s4.5-7.5 3-10.5c0 0-1-2.5-3-2.5s-3 2.5-3 2.5c-1.5 3 3 10.5 3 10.5"/>
    <path d="M12.5 37c5.5 3.5 14.5 3.5 20 0v-7s9-4.5 6-10.5c-4-6.5-13.5-3.5-16 4V17s-5.5-13.5-14-5.5c-3 4 1 8 1 8v5c-5 1-7 5.5-5 7s3 5.5 10 7z"/>
    <path d="M12.5 30c5.5-3 14.5-3 20 0M12.5 33.5c5.5-3 14.5-3 20 0M12.5 37c5.5-3 14.5-3 20 0"/>
  </g>
</svg>""",
    "wQ": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#fff;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <circle cx="6" cy="12" r="2.75"/>
    <circle cx="14" cy="9" r="2.75"/>
    <circle cx="22.5" cy="8" r="2.75"/>
    <circle cx="31" cy="9" r="2.75"/>
    <circle cx="39" cy="12" r="2.75"/>
    <path d="M9 26c8.5-8.5 15.5-8.5 27 0l2.5-12.5L31 25l-.3-14.1-5.2 13.6-3-14.5-3 14.5-5.2-13.6L14 25 6.5 13.5 9 26z"/>
    <path d="M9 26c0 2 1.5 2 2.5 4 1 1.5 1 1 .5 3.5-1.5 1-1.5 2.5-1.5 2.5-1.5 1.5.5 2.5.5 2.5 6.5 1 16.5 1 23 0 0 0 1.5-1 0-2.5 0 0 .5-1.5-1-2.5-.5-2.5-.5-2 .5-3.5 1-2 2.5-2 2.5-4-8.5 1.5-18.5 1.5-27 0z"/>
    <path d="M11 38.5a35 35 1 0 0 23 0M11 29a35 35 1 0 1 23 0M12.5 31.5h20M11.5 34.5a35 35 1 0 0 22 0M10.5 37.5a35 35 1 0 0 24 0"/>
  </g>
</svg>""",
    "wR": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#fff;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <path d="M9 39h27v-3H9v3zM12 36v-4h21v4H12zM11 14V9h4v2h5V9h5v2h5V9h4v5"/>
    <path d="M34 14l-3 3H14l-3-3"/>
    <path d="M31 17v12.5H14V17"/>
    <path d="M31 29.5l1.5 2.5h-20l1.5-2.5"/>
    <path d="M11 14h23"/>
  </g>
</svg>""",
    "wB": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#fff;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <circle cx="22.5" cy="8" r="2.5"/>
    <path d="M22.5 10.5s.5 1.5-1.5 4.5-2.5 5-2.5 7a3 3 0 1 0 8 0c0-2-.5-4-2.5-7s-1.5-4.5-1.5-4.5z"/>
    <path d="M13.5 36l-2 1.5c-.5 1 2 1 3 1h16c1 0 3.5 0 3-1l-2-1.5"/>
    <path d="M12.5 37c5.5-3 14.5-3 20 0"/>
    <path d="M13 36c5.5-3 15.5-3 19 0"/>
    <path d="M13.5 32c5-3 13.5-3 18 0 1-2 1-3.5-5.5-5.5-6.5-2-7.5-4.5-7.5-4.5"/>
    <path d="M13.5 32c5-3 13.5-3 18 0 1-2 1-3.5-5.5-5.5-6.5-2-7.5-4.5-7.5-4.5z" style="fill:none"/>
    <path d="M22.5 15.5c-3.5 2-7.5 7-7.5 15.5h15c0-8.5-4-13.5-7.5-15.5z"/>
  </g>
</svg>""",
    "wN": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#fff;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <path d="M22 10c10.5 1 16.5 8 16 29H15c0-9 10-6.5 8-21"/>
    <path d="M24 18c.38 5.1-5.55 7.85-8 4-3.38-5.5-2.5-12.5 3.5-13 2.84-.63 5.78 1 7 4"/>
    <path d="M9.5 25.5a.5.5 0 1 1-1 0 .5.5 0 1 1 1 0z" style="fill:#000"/>
    <path d="M14.933 15.75a.5 1.5 30 1 1-.866-.5.5 1.5 30 1 1 .866.5z" style="fill:#000"/>
  </g>
</svg>""",
    "wP": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#fff;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <path d="M22 9c-2.21 0-4 1.79-4 4 0 .89.29 1.71.78 2.38C17.33 16.5 16 18.59 16 21c0 2.03.94 3.84 2.41 5.03C15.41 27.09 11 31.58 11 39.5H34c0-7.92-4.41-12.41-7.41-13.47C28.06 24.84 29 23.03 29 21c0-2.41-1.33-4.5-3.78-5.62.49-.67.78-1.49.78-2.38 0-2.21-1.79-4-4-4z"/>
  </g>
</svg>""",
    # BLACK pieces
    "bK": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#000;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <path d="M22.5 11.63V6" style="stroke:#fff"/>
    <path d="M20 8h5" style="stroke:#fff"/>
    <path d="M22.5 25s4.5-7.5 3-10.5c0 0-1-2.5-3-2.5s-3 2.5-3 2.5c-1.5 3 3 10.5 3 10.5"/>
    <path d="M12.5 37c5.5 3.5 14.5 3.5 20 0v-7s9-4.5 6-10.5c-4-6.5-13.5-3.5-16 4V17s-5.5-13.5-14-5.5c-3 4 1 8 1 8v5c-5 1-7 5.5-5 7s3 5.5 10 7z"/>
    <path d="M12.5 30c5.5-3 14.5-3 20 0M12.5 33.5c5.5-3 14.5-3 20 0M12.5 37c5.5-3 14.5-3 20 0" style="stroke:#fff"/>
  </g>
</svg>""",
    "bQ": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#000;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <circle cx="6" cy="12" r="2.75"/>
    <circle cx="14" cy="9" r="2.75"/>
    <circle cx="22.5" cy="8" r="2.75"/>
    <circle cx="31" cy="9" r="2.75"/>
    <circle cx="39" cy="12" r="2.75"/>
    <path d="M9 26c8.5-8.5 15.5-8.5 27 0l2.5-12.5L31 25l-.3-14.1-5.2 13.6-3-14.5-3 14.5-5.2-13.6L14 25 6.5 13.5 9 26z"/>
    <path d="M9 26c0 2 1.5 2 2.5 4 1 1.5 1 1 .5 3.5-1.5 1-1.5 2.5-1.5 2.5-1.5 1.5.5 2.5.5 2.5 6.5 1 16.5 1 23 0 0 0 1.5-1 0-2.5 0 0 .5-1.5-1-2.5-.5-2.5-.5-2 .5-3.5 1-2 2.5-2 2.5-4-8.5 1.5-18.5 1.5-27 0z"/>
    <path d="M11 38.5a35 35 1 0 0 23 0M11 29a35 35 1 0 1 23 0M12.5 31.5h20M11.5 34.5a35 35 1 0 0 22 0M10.5 37.5a35 35 1 0 0 24 0" style="stroke:#fff"/>
  </g>
</svg>""",
    "bR": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#000;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <path d="M9 39h27v-3H9v3zM12.5 32l1.5-2.5h17l1.5 2.5h-20zM12 36v-4h21v4H12z"/>
    <path d="M14 29.5v-13h17v13H14z" style="stroke:#fff;stroke-width:1;stroke-linejoin:miter"/>
    <path d="M11 14V9h4v2h5V9h5v2h5V9h4v5H11z"/>
    <path d="M34 14l-3 3H14l-3-3" style="stroke:#fff"/>
  </g>
</svg>""",
    "bB": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#000;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <circle cx="22.5" cy="8" r="2.5"/>
    <path d="M22.5 10.5s.5 1.5-1.5 4.5-2.5 5-2.5 7a3 3 0 1 0 8 0c0-2-.5-4-2.5-7s-1.5-4.5-1.5-4.5z"/>
    <path d="M13.5 36l-2 1.5c-.5 1 2 1 3 1h16c1 0 3.5 0 3-1l-2-1.5"/>
    <path d="M13.5 32c5-3 13.5-3 18 0 1-2 1-3.5-5.5-5.5-6.5-2-7.5-4.5-7.5-4.5z"/>
    <path d="M22.5 15.5c-3.5 2-7.5 7-7.5 15.5h15c0-8.5-4-13.5-7.5-15.5z"/>
    <path d="M13 36c5.5-3 15.5-3 19 0M13.5 37c5.5-3 14.5-3 18 0" style="stroke:#fff"/>
  </g>
</svg>""",
    "bN": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#000;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <path d="M22 10c10.5 1 16.5 8 16 29H15c0-9 10-6.5 8-21"/>
    <path d="M24 18c.38 5.1-5.55 7.85-8 4-3.38-5.5-2.5-12.5 3.5-13 2.84-.63 5.78 1 7 4"/>
    <path d="M9.5 25.5a.5.5 0 1 1-1 0 .5.5 0 1 1 1 0z" style="fill:#ececec"/>
    <path d="M14.933 15.75a.5 1.5 30 1 1-.866-.5.5 1.5 30 1 1 .866.5z" style="fill:#ececec"/>
  </g>
</svg>""",
    "bP": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
  <g style="fill:#000;stroke:#000;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">
    <path d="M22 9c-2.21 0-4 1.79-4 4 0 .89.29 1.71.78 2.38C17.33 16.5 16 18.59 16 21c0 2.03.94 3.84 2.41 5.03C15.41 27.09 11 31.58 11 39.5H34c0-7.92-4.41-12.41-7.41-13.47C28.06 24.84 29 23.03 29 21c0-2.41-1.33-4.5-3.78-5.62.49-.67.78-1.49.78-2.38 0-2.21-1.79-4-4-4z"/>
  </g>
</svg>""",
}


def get_svg(piece_symbol: str) -> bytes:
    """
    piece_symbol: 'wK','wQ','wR','wB','wN','wP','bK','bQ','bR','bB','bN','bP'
    """
    return _PIECES[piece_symbol].encode()

