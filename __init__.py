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
            r, g, b = [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]
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
    if not color_value:
        return ""
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
        chars = {'h': '─', 'v': '│', 'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯', 'vr': '┤', 'vl': '├', 'hb': '┴', 'ht': '┬', 'hc': '┼'}
    else:
        chars = {'h': '─', 'v': '│', 'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘', 'vr': '┤', 'vl': '├', 'hb': '┴', 'ht': '┬', 'hc': '┼'}
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
            if len(p) == 1:
                p_t = p_r = p_b = p_l = int(p[0])
            elif len(p) == 2:
                p_t, p_r = map(int, p)
                p_b, p_l = p_t, p_r
            elif len(p) == 4:
                p_t, p_r, p_b, p_l = map(int, p)
    except (ValueError, TypeError):
        pass
    try:
        pad_top = int(pt) if pt is not None else p_t
    except (ValueError, TypeError):
        pad_top = p_t
    try:
        pad_right = int(pr) if pr is not None else p_r
    except (ValueError, TypeError):
        pad_right = p_r
    try:
        pad_bottom = int(pb) if pb is not None else p_b
    except (ValueError, TypeError):
        pad_bottom = p_b
    try:
        pad_left = int(pl) if pl is not None else p_l
    except (ValueError, TypeError):
        pad_left = p_l
    return max(0, pad_top), max(0, pad_right), max(0, pad_bottom), max(0, pad_left)
def _parse_markdown_table(lines):
    header_line = lines[0]
    separator_line = lines[1]
    data_lines = lines[2:]
    headers = [h.strip() for h in header_line.strip('|').split('|')]
    alignments = []
    parts = separator_line.strip('|').split('|')
    for part in parts:
        part = part.strip()
        if part.startswith(':') and part.endswith(':'):
            alignments.append("center")
        elif part.startswith(':'):
            alignments.append("left")
        elif part.endswith(':'):
            alignments.append("right")
        else:
            alignments.append("left")
    data_rows = []
    for line in data_lines:
        data_rows.append([cell.strip() for cell in line.strip('|').split('|')])
    return headers, alignments, data_rows
def _render_markdown_table(headers, alignments, data_rows, styles):
    border = styles.get("border", False)
    is_rounded = styles.get("border-radius", False)
    default_border_color = styles.get("color", "")
    border_color_val = styles.get("border-color", default_border_color)
    border_color_code = _get_color_code(border_color_val, False) if border else ""
    border_chars = _get_border_chars(is_rounded, border_color_code) if border else {}
    pad_top, pad_right, pad_bottom, pad_left = _parse_padding(styles)
    cell_padding = ' ' * pad_left
    reset_code = _reset_code if border_color_code or styles.get("color") or styles.get("background-color") or any(v is not None and str(v).lower().strip() not in ('false', '0', '') for k, v in styles.items() if _style_property_map.get(k) == 'attribute') else ""
    text_fg_code = _get_color_code(styles.get("color", ""), False)
    text_bg_code = _get_color_code(styles.get("background-color", ""), True)
    text_attrs = []
    for key, value in styles.items():
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
    column_widths = [max(visible_len(header), max((visible_len(row[i]) if i < len(row) else 0) for row in data_rows)) for i, header in enumerate(headers)]
    output_lines = []
    if border:
        top_border = border_chars['tl']
        for i, width in enumerate(column_widths):
            top_border += border_chars['h'] * (width + 2 * pad_left)
            if i < len(column_widths) - 1:
                top_border += border_chars['ht']
        top_border += border_chars['tr']
        output_lines.append(top_border)
    header_row_str = border_chars['vl'] if border else ""
    for i, header in enumerate(headers):
        aligned_header = _align_line(f"{text_style_prefix}{header}{reset_code}", column_widths[i], alignments[i])
        header_row_str += f"{cell_padding}{aligned_header}{cell_padding}"
        if i < len(headers) - 1:
            header_row_str += border_chars['v'] if border else ""
    header_row_str += border_chars['vr'] if border else ""
    output_lines.append(header_row_str)
    if border:
        separator_border = border_chars['vl']
        for i, width in enumerate(column_widths):
            separator_border += border_chars['h'] * (width + 2 * pad_left)
            if i < len(column_widths) - 1:
                separator_border += border_chars['hc']
        separator_border += border_chars['vr']
        output_lines.append(separator_border)
    for row_data in data_rows:
        data_row_str = border_chars['vl'] if border else ""
        for i, cell_content in enumerate(row_data):
            cell_text = cell_content if i < len(row_data) else ""
            aligned_cell = _align_line(f"{text_style_prefix}{cell_text}{reset_code}", column_widths[i], alignments[i] if i < len(alignments) else "left")
            data_row_str += f"{cell_padding}{aligned_cell}{cell_padding}"
            if i < len(column_widths) - 1:
                data_row_str += border_chars['v'] if border else ""
        data_row_str += border_chars['vr'] if border else ""
        output_lines.append(data_row_str)
    if border:
        bottom_border = border_chars['bl']
        for i, width in enumerate(column_widths):
            bottom_border += border_chars['h'] * (width + 2 * pad_left)
            if i < len(column_widths) - 1:
                bottom_border += border_chars['hb']
        bottom_border += border_chars['br']
        output_lines.append(bottom_border)
    return output_lines
def printc(content, styles=None, markdown=False, **kwargs):
    if styles is None:
        styles = {}
    effective_styles = styles.copy()
    processed_kwargs = {k.replace('_', '-'): v for k, v in kwargs.items()}
    effective_styles.update(processed_kwargs)
    if markdown:
        lines = content.strip().split('\n')
        if len(lines) >= 2 and '|' in lines[0] and re.match(r'\s*\|? *[:\-]+ *\|', lines[1]):
            try:
                headers, alignments, table_data = _parse_markdown_table(lines)
                rendered_table_lines = _render_markdown_table(headers, alignments, table_data, effective_styles)
                for line in rendered_table_lines:
                    sys.stdout.write(line + "\n")
                sys.stdout.flush()
                return
            except:
                pass
    text_fg_code = _get_color_code(effective_styles.get("color", ""), False)
    text_bg_code = _get_color_code(effective_styles.get("background-color", ""), True)
    text_attrs = []
    for key, value in effective_styles.items():
        property_type = _style_property_map.get(key)
        val_str = str(value).lower().strip() if value is not None else ""
        if property_type == "attribute":
            attr_key = None
            if key == "font-weight" and val_str == "bold":
                attr_key = "bold"
            elif key == "font-style" and val_str == "italic":
                attr_key = "italic"
            elif key == "text-decoration":
                if val_str == "underline":
                    attr_key = "underline"
                elif val_str == "line-through":
                    attr_key = "strikethrough"
            elif key == "visibility" and val_str == "hidden":
                pass
            elif key == "visibility" and val_str == "dim":
                attr_key = "dim"
            elif key in _attributes:
                attr_key = key
            if attr_key and val_str not in ('false', '0', ''):
                attr_code = _attributes.get(attr_key)
                if attr_code:
                    text_attrs.append(attr_code)
    text_style_prefix = f"{text_fg_code}{text_bg_code}{''.join(text_attrs)}"
    needs_reset = bool(text_style_prefix or effective_styles.get("border-color"))
    has_border = effective_styles.get("border", False)
    if isinstance(has_border, str) and has_border.lower() in ('false', '0', ''):
        has_border = False
    else:
        has_border = bool(has_border)
    is_rounded = effective_styles.get("border-radius", False)
    if isinstance(is_rounded, str) and is_rounded.lower() in ('false', '0', ''):
        is_rounded = False
    else:
        is_rounded = bool(is_rounded)
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
