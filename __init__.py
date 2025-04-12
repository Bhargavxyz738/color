"""
* Copyright (c) 2025 Bhargav 
* Licensed under the MIT License – see the LICENSE file for details. 
"""
import sys
import re
_basic_colors = {
    "black": "\033[30m", "red": "\033[31m", "green": "\033[32m",
    "yellow": "\033[33m", "blue": "\033[34m", "magenta": "\033[35m",
    "cyan": "\033[36m", "white": "\033[37m",
}
_basic_bg_colors = {
    f"bg_{k}": v.replace("[3", "[4") for k, v in _basic_colors.items()
}
_attributes = {
    "bold": "\033[1m", "dim": "\033[2m", "italic": "\033[3m",
    "underline": "\033[4m", "blink": "\033[5m", "reverse": "\033[7m",
    "strikethrough": "\033[9m"
}
_reset_code = "\033[0m"
_style_property_map = {
    "color": "foreground",
    "background-color": "background",
    "font-weight": "attribute",       
    "font-style": "attribute",         
    "text-decoration": "attribute",    
    "visibility": "attribute",       
    "padding": "box", "padding-top": "box", "padding-right": "box",
    "padding-bottom": "box", "padding-left": "box",
    "border": "box", 
    "border-color": "box",
    "border-radius": "box", 
    "text-align": "box",
}
_ansi_escape_regex = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
def strip_ansi(s):
    return _ansi_escape_regex.sub('', s)
def visible_len(s):
    clean = strip_ansi(s)
    try:
      return sum(2 if ord(c) > 127 else 1 for c in clean)
    except TypeError:
      return 0
def _parse_hex_color(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        try:
            r, g, b = [int(c * 2, 16) for c in hex_color]
            return r, g, b
        except ValueError:
            return None
    elif len(hex_color) == 6:
        try:
            r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
            return r, g, b
        except ValueError:
            return None
    return None 
def _parse_rgb_color(rgb_color):
    match = re.match(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*[\d.]+\s*)?\)', rgb_color)
    if match:
        try:
            r, g, b = map(int, match.groups())
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            return r, g, b
        except (ValueError, TypeError):
              return None
    return None
def _parse_color_string(color_str):
    if not isinstance(color_str, str):
        return None
    color_str = color_str.lower().strip()
    if color_str.startswith('#'):
        return _parse_hex_color(color_str)
    elif color_str.startswith('rgb'):
        return _parse_rgb_color(color_str)
    return None 
def _get_color_code(color_value, is_background=False):
    if not color_value: return ""
    color_value_str = str(color_value).lower().strip() 
    prefix_code = "\033[48;2;" if is_background else "\033[38;2;"
    basic_map = _basic_bg_colors if is_background else _basic_colors
    basic_key = f"bg_{color_value_str}" if is_background else color_value_str
    if basic_key in basic_map:
        return basic_map[basic_key]
    rgb = _parse_color_string(color_value_str)
    if rgb:
        r, g, b = rgb
        return f"{prefix_code}{r};{g};{b}m"
    return ""
def _align_line(line, width, align="left"):
    vis_len = visible_len(line)
    total_pad = max(0, width - vis_len)
    if align == "right":
        return ' ' * total_pad + line
    elif align == "center":
        left_pad = total_pad // 2
        right_pad = total_pad - left_pad
        return ' ' * left_pad + line + ' ' * right_pad
    else:
        return line + ' ' * total_pad
def _get_border_chars(is_rounded, border_color_code=""):
    reset = _reset_code if border_color_code else ""
    if is_rounded:
        chars = {'h': '─', 'v': '│', 'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯'}
    else:
        chars = {'h': '─', 'v': '│', 'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘'}
    styled_chars = {}
    for k, v in chars.items():
        styled_chars[k] = f"{border_color_code}{v}{reset}"
    return styled_chars
def _parse_padding(styles):
    p = styles.get("padding")
    pt = styles.get("padding-top")
    pr = styles.get("padding-right")
    pb = styles.get("padding-bottom")
    pl = styles.get("padding-left")
    p_t, p_r, p_b, p_l = 0, 0, 0, 0
    try:
        if isinstance(p, (int, float)):
            p_t = p_r = p_b = p_l = int(p)
        elif isinstance(p, (tuple, list)):
            if len(p) == 1: p_t = p_r = p_b = p_l = int(p[0])
            elif len(p) == 2: p_t, p_r = map(int, p); p_b, p_l = p_t, p_r
            elif len(p) == 4: p_t, p_r, p_b, p_l = map(int, p)
    except (ValueError, TypeError):
        pass
    try: pad_top = int(pt) if pt is not None else p_t
    except (ValueError, TypeError): pad_top = p_t
    try: pad_right = int(pr) if pr is not None else p_r
    except (ValueError, TypeError): pad_right = p_r
    try: pad_bottom = int(pb) if pb is not None else p_b
    except (ValueError, TypeError): pad_bottom = p_b
    try: pad_left = int(pl) if pl is not None else p_l
    except (ValueError, TypeError): pad_left = p_l
    return max(0, pad_top), max(0, pad_right), max(0, pad_bottom), max(0, pad_left)
def text(content, styles=None, **kwargs):
    if styles is None: styles = {}
    effective_styles = styles.copy()
    processed_kwargs = {k.replace('_', '-'): v for k, v in kwargs.items()}
    effective_styles.update(processed_kwargs)
    text_fg_code = _get_color_code(effective_styles.get("color", ""), False)
    text_bg_code = _get_color_code(effective_styles.get("background-color", ""), True)
    text_attrs = []
    for key, value in effective_styles.items():
        property_type = _style_property_map.get(key)
        val_str = str(value).lower().strip() if value is not None else ""
        if property_type == "attribute":
            attr_key = None
            if key == "font-weight" and val_str == "bold": attr_key = "bold"
            elif key == "font-style" and val_str == "italic": attr_key = "italic"
            elif key == "text-decoration":
                if val_str == "underline": attr_key = "underline"
                elif val_str == "line-through": attr_key = "strikethrough"
            elif key == "visibility" and val_str == "hidden": pass 
            elif key == "visibility" and val_str == "dim": attr_key = "dim" 
            elif key in _attributes: attr_key = key
            if attr_key and val_str not in ('false', '0', ''):
                 attr_code = _attributes.get(attr_key)
                 if attr_code: text_attrs.append(attr_code)
    text_style_prefix = f"{text_fg_code}{text_bg_code}{''.join(text_attrs)}"
    needs_reset = bool(text_style_prefix or effective_styles.get("border-color")) 
    has_border = effective_styles.get("border", False)
    if isinstance(has_border, str) and has_border.lower() in ('false', '0', ''): has_border = False
    else: has_border = bool(has_border)
    is_rounded = effective_styles.get("border-radius", False)
    if isinstance(is_rounded, str) and is_rounded.lower() in ('false', '0', ''): is_rounded = False
    else: is_rounded = bool(is_rounded)
    is_rounded = is_rounded and has_border
    default_border_color = effective_styles.get("color", "")
    border_color_val = effective_styles.get("border-color", default_border_color)
    border_color_code = _get_color_code(border_color_val, False) if has_border else ""
    text_align = effective_styles.get("text-align", "left")
    pad_top, pad_right, pad_bottom, pad_left = _parse_padding(effective_styles)
    content_str = str(content)
    lines = content_str.split('\n')
    styled_lines = [f"{text_style_prefix}{line}{_reset_code if needs_reset else ''}" for line in lines]
    max_content_width = 0
    if styled_lines:
        raw_lines = [strip_ansi(line) for line in styled_lines]
        max_content_width = max(visible_len(raw) for raw in raw_lines) if raw_lines else 0
    inner_width = max_content_width + pad_left + pad_right
    effective_bg_code = text_bg_code
    effective_bg_reset = _reset_code if effective_bg_code else ""
    output_lines = []
    border_chars = {}
    if has_border:
        border_chars = _get_border_chars(is_rounded, border_color_code)
        top_border = f"{border_chars['tl']}{border_chars['h'] * inner_width}{border_chars['tr']}"
        output_lines.append(top_border)
    for _ in range(pad_top):
        pad_content = f"{effective_bg_code}{' ' * inner_width}{effective_bg_reset}"
        if has_border:
            output_lines.append(f"{border_chars['v']}{pad_content}{border_chars['v']}")
        elif effective_bg_code:
             output_lines.append(pad_content)
    for i, styled_line in enumerate(styled_lines):
        raw_line = lines[i]
        aligned_styled_line = _align_line(styled_line, max_content_width, text_align)
        left_pad_str = f"{effective_bg_code}{' ' * pad_left}{effective_bg_reset}"
        right_pad_str = f"{effective_bg_code}{' ' * pad_right}{effective_bg_reset}"
        full_inner_line = f"{left_pad_str}{aligned_styled_line}{right_pad_str}"
        if has_border:
            output_lines.append(f"{border_chars['v']}{full_inner_line}{border_chars['v']}")
        else:
            output_lines.append(full_inner_line)
    for _ in range(pad_bottom):
        pad_content = f"{effective_bg_code}{' ' * inner_width}{effective_bg_reset}"
        if has_border:
            output_lines.append(f"{border_chars['v']}{pad_content}{border_chars['v']}")
        elif effective_bg_code:
             output_lines.append(pad_content)
    if has_border:
        bottom_border = f"{border_chars['bl']}{border_chars['h'] * inner_width}{border_chars['br']}"
        output_lines.append(bottom_border)
    for line in output_lines:
        sys.stdout.write(line + "\n")
    sys.stdout.flush()
