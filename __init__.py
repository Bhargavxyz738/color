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
_attribute_resets = {
    "bold": "\033[22m",
    "dim": "\033[22m",
    "italic": "\033[23m",
    "underline": "\033[24m",
    "blink": "\033[25m",
    "reverse": "\033[27m",
    "strikethrough": "\033[29m"
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
    "bold": "attribute", "italic": "attribute", "underline": "attribute",
    "strikethrough": "attribute", "dim": "attribute", "blink": "attribute",
    "reverse": "attribute",
}
_ansi_escape_regex = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
def strip_ansi(s):
    return _ansi_escape_regex.sub('', s)
def visible_len(s):
    clean = strip_ansi(str(s))
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
        except ValueError: return None
    elif len(hex_color) == 6:
        try:
            r, g, b = [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]
            return r, g, b
        except ValueError: return None
    return None
def _parse_rgb_color(rgb_color):
    match = re.match(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*[\d.]+\s*)?\)', rgb_color)
    if match:
        try:
            r, g, b = map(int, match.groups())
            r = max(0, min(255, r)); g = max(0, min(255, g)); b = max(0, min(255, b))
            return r, g, b
        except (ValueError, TypeError): return None
    return None
def _parse_color_string(color_str):
    if not isinstance(color_str, str): return None
    color_str = color_str.lower().strip()
    if color_str.startswith('#'): return _parse_hex_color(color_str)
    elif color_str.startswith('rgb'): return _parse_rgb_color(color_str)
    if color_str in _basic_colors or color_str in [k.replace('bg_', '') for k in _basic_bg_colors]:
        return color_str 
    return None 
def _get_color_code(color_value, is_background=False):
    if not color_value: return ""
    color_value_str = str(color_value).lower().strip()
    basic_map = _basic_bg_colors if is_background else _basic_colors
    basic_key = f"bg_{color_value_str}" if is_background else color_value_str
    if basic_key in basic_map: return basic_map[basic_key]
    rgb = None
    if color_value_str.startswith('#'): rgb = _parse_hex_color(color_value_str)
    elif color_value_str.startswith('rgb'): rgb = _parse_rgb_color(color_value_str)
    if rgb:
        r, g, b = rgb
        prefix_code = "\033[48;2;" if is_background else "\033[38;2;"
        return f"{prefix_code}{r};{g};{b}m"
    return "" 
def _parse_inline_markdown(text):
    if not isinstance(text, str): text = str(text)
    text = re.sub(r'(?<!\\)~(.*?)~', f'{_attributes["strikethrough"]}\\1{_attribute_resets["strikethrough"]}', text)
    text = re.sub(r'(?<!\\)\*\*(.*?)\*\*', f'{_attributes["bold"]}\\1{_attribute_resets["bold"]}', text)
    text = re.sub(r'(?<!\\)__(.*?)__', f'{_attributes["bold"]}\\1{_attribute_resets["bold"]}', text)
    text = re.sub(r'(?<!\\)(?<!\w)_(.*?)_(?!\w)', f'{_attributes["italic"]}\\1{_attribute_resets["italic"]}', text)
    text = re.sub(r'(?<!\\)\*(.*?)\*', f'{_attributes["italic"]}\\1{_attribute_resets["italic"]}', text)
    text = text.replace('\\*', '*').replace('\\_', '_').replace('\\~', '~')
    return text
def _align_line(line, width, align="left"):
    vis_len = visible_len(line)
    total_pad = max(0, width - vis_len)
    if align == "right": return ' ' * total_pad + line
    elif align == "center":
        left_pad = total_pad // 2
        right_pad = total_pad - left_pad
        return ' ' * left_pad + line + ' ' * right_pad
    else: return line + ' ' * total_pad 
def _get_border_chars(is_rounded, border_color_code=""):
    reset = _reset_code if border_color_code else ""
    if is_rounded: chars = {'h': '─', 'v': '│', 'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯', 'vr': '┤', 'vl': '├', 'hb': '┴', 'ht': '┬', 'hc': '┼'}
    else: chars = {'h': '─', 'v': '│', 'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘', 'vr': '┤', 'vl': '├', 'hb': '┴', 'ht': '┬', 'hc': '┼'}
    styled_chars = {k: f"{border_color_code}{v}{reset}" for k, v in chars.items()}
    return styled_chars
def _parse_padding(styles):
    p = styles.get("padding")
    pt = styles.get("padding-top")
    pr = styles.get("padding-right")
    pb = styles.get("padding-bottom")
    pl = styles.get("padding-left")
    p_t, p_r, p_b, p_l = 0, 1, 0, 1 
    try: 
        if isinstance(p, (int, float)): p_t = p_r = p_b = p_l = int(p)
        elif isinstance(p, (tuple, list)):
            if len(p) == 1: p_t = p_r = p_b = p_l = int(p[0])
            elif len(p) == 2: p_t, p_r = map(int, p); p_b, p_l = p_t, p_r
            elif len(p) == 3: p_t, p_r, p_b = map(int, p); p_l = p_r
            elif len(p) == 4: p_t, p_r, p_b, p_l = map(int, p)
        elif isinstance(p, str):
             vals = [v.strip() for v in p.split()]
             if len(vals) == 1: p_t = p_r = p_b = p_l = int(vals[0])
             elif len(vals) == 2: p_t, p_r = map(int, vals); p_b, p_l = p_t, p_r
             elif len(vals) == 3: p_t, p_r, p_b = map(int, vals); p_l = p_r
             elif len(vals) == 4: p_t, p_r, p_b, p_l = map(int, vals)
    except (ValueError, TypeError, IndexError): pass 
    try: pad_top = int(pt) if pt is not None else p_t
    except (ValueError, TypeError): pad_top = p_t
    try: pad_right = int(pr) if pr is not None else p_r
    except (ValueError, TypeError): pad_right = p_r
    try: pad_bottom = int(pb) if pb is not None else p_b
    except (ValueError, TypeError): pad_bottom = p_b
    try: pad_left = int(pl) if pl is not None else p_l
    except (ValueError, TypeError): pad_left = p_l
    return max(0, pad_top), max(0, pad_right), max(0, pad_bottom), max(0, pad_left)
def _parse_markdown_table(lines):
    if not lines or len(lines) < 2: raise ValueError("Markdown table requires at least header and separator lines.")
    header_line = lines[0]; separator_line = lines[1]; data_lines = lines[2:]
    if '|' not in header_line or not re.match(r'\s*\|? *[:\-]+ *\|', separator_line): raise ValueError("Input does not look like a valid Markdown table.")
    headers = [h.strip() for h in header_line.strip('|').split('|')]
    num_columns = len(headers)
    alignments = []
    parts = separator_line.strip('|').split('|')
    if len(parts) != num_columns: 
        num_columns = min(len(parts), num_columns)
        headers = headers[:num_columns]
        parts = parts[:num_columns]
    for part in parts:
        part = part.strip()
        if part.startswith(':') and part.endswith(':'): alignments.append("center")
        elif part.endswith(':'): alignments.append("right")
        else: alignments.append("left") 
    data_rows = []
    for line in data_lines:
        if not line.strip() or '|' not in line : continue
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if len(cells) < num_columns: cells.extend([''] * (num_columns - len(cells)))
        data_rows.append(cells[:num_columns])
    return headers, alignments, data_rows
def _render_markdown_table(headers, alignments, data_rows, styles):
    has_border = styles.get("border", True) 
    if isinstance(has_border, str): has_border = has_border.lower() not in ('false', '0', '')
    else: has_border = bool(has_border)
    is_rounded = styles.get("border-radius", False)
    if isinstance(is_rounded, str): is_rounded = is_rounded.lower() not in ('false', '0', '')
    else: is_rounded = bool(is_rounded)
    is_rounded = is_rounded and has_border 
    default_border_color = styles.get("color", "") 
    border_color_val = styles.get("border-color", default_border_color)
    border_color_code = _get_color_code(border_color_val, False) if has_border else ""
    border_chars = _get_border_chars(is_rounded, border_color_code) if has_border else {}
    pad_top, pad_right, pad_bottom, pad_left = _parse_padding(styles)
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
                elif val_str in ("line-through", "strikethrough"): attr_key = "strikethrough"
            elif key == "visibility":
                if val_str == "dim": attr_key = "dim"
            elif key in _attributes: 
                attr_key = key
            if attr_key and val_str not in ('false', '0', '', 'normal', 'none'):
                attr_code = _attributes.get(attr_key)
                if attr_code: text_attrs.append(attr_code)
    text_style_prefix = f"{text_fg_code}{text_bg_code}{''.join(text_attrs)}"
    cell_reset_code = _reset_code 
    num_columns = len(headers)
    column_widths = [0] * num_columns
    for i in range(num_columns):
         header_len = visible_len(_parse_inline_markdown(headers[i])) 
         max_data_len = 0
         if data_rows:
             max_data_len = max(visible_len(_parse_inline_markdown(row[i] if i < len(row) else "")) for row in data_rows)
         column_widths[i] = max(header_len, max_data_len)
    output_lines = []
    col_sep = border_chars.get('v', '|') if has_border else " "
    h_sep = border_chars.get('h', '-') 
    if has_border:
        top_border = border_chars['tl']
        for i, width in enumerate(column_widths):
            top_border += h_sep * (width + pad_left + pad_right)
            if i < num_columns - 1: top_border += border_chars['ht'] 
        top_border += border_chars['tr']
        output_lines.append(top_border)
    header_row_str = border_chars.get('vl', '|') if has_border else ""
    for i, header in enumerate(headers):
        parsed_header = _parse_inline_markdown(header) 
        styled_header = f"{text_style_prefix}{parsed_header}{cell_reset_code}"
        aligned_header = _align_line(styled_header, column_widths[i], alignments[i])
        left_pad_str = f"{text_bg_code}{' ' * pad_left}{cell_reset_code}" if pad_left > 0 else ""
        right_pad_str = f"{text_bg_code}{' ' * pad_right}{cell_reset_code}" if pad_right > 0 else ""
        header_row_str += f"{left_pad_str}{aligned_header}{right_pad_str}"
        if i < num_columns - 1: header_row_str += col_sep
    header_row_str += border_chars.get('vr', '|') if has_border else ""
    output_lines.append(header_row_str)
    if has_border:
        separator_border = border_chars['vl'] 
        for i, width in enumerate(column_widths):
            separator_border += h_sep * (width + pad_left + pad_right)
            if i < num_columns - 1: separator_border += border_chars['hc'] 
        separator_border += border_chars['vr'] 
        output_lines.append(separator_border)
    for row_data in data_rows:
        data_row_str = border_chars.get('vl', '|') if has_border else ""
        for i, cell_content in enumerate(row_data):
            if i >= num_columns: continue 
            parsed_cell = _parse_inline_markdown(cell_content)
            styled_cell = f"{text_style_prefix}{parsed_cell}{cell_reset_code}"
            alignment = alignments[i] if i < len(alignments) else "left"
            aligned_cell = _align_line(styled_cell, column_widths[i], alignment)
            left_pad_str = f"{text_bg_code}{' ' * pad_left}{cell_reset_code}" if pad_left > 0 else ""
            right_pad_str = f"{text_bg_code}{' ' * pad_right}{cell_reset_code}" if pad_right > 0 else ""
            data_row_str += f"{left_pad_str}{aligned_cell}{right_pad_str}"
            if i < num_columns - 1: data_row_str += col_sep
        data_row_str += border_chars.get('vr', '|') if has_border else ""
        output_lines.append(data_row_str)
    if has_border:
        bottom_border = border_chars['bl']
        for i, width in enumerate(column_widths):
            bottom_border += h_sep * (width + pad_left + pad_right)
            if i < num_columns - 1: bottom_border += border_chars['hb'] 
        bottom_border += border_chars['br']
        output_lines.append(bottom_border)
    return output_lines
def _parse_style_string(style_string):
    if not isinstance(style_string, str):
        return {}
    styles = {}
    parts = style_string.strip().lower().split()
    for part in parts:
        if part == "bold": styles["font-weight"] = "bold"
        elif part == "italic": styles["font-style"] = "italic"
        elif part == "underline": styles["text-decoration"] = "underline"
        elif part in ("strikethrough", "line-through"): styles["text-decoration"] = "strikethrough"
        elif part == "dim": styles["visibility"] = "dim"
        elif part == "blink": styles["blink"] = True 
        elif part == "reverse": styles["reverse"] = True 
        elif part == "border": styles["border"] = True
        elif part == "rounded": styles["border-radius"] = True
        elif part == "hidden": styles["visibility"] = "hidden"
        elif part.startswith("text-"):
            color_val = part[len("text-"):]
            if _parse_color_string(color_val) or color_val in _basic_colors:
                styles["color"] = color_val
        elif part.startswith("bg-"):
            color_val = part[len("bg-"):]
            if _parse_color_string(color_val) or color_val in _basic_colors:
                 styles["background-color"] = color_val
            elif f"bg_{color_val}" in _basic_bg_colors:
                 styles["background-color"] = color_val 
        elif part.startswith("border-"):
             potential_color = part[len("border-"):]
             if _parse_color_string(potential_color) or potential_color in _basic_colors:
                 styles["border-color"] = potential_color
        elif part == "text-left": styles["text-align"] = "left"
        elif part == "text-center": styles["text-align"] = "center"
        elif part == "text-right": styles["text-align"] = "right"
        elif part in _basic_colors:
             styles["color"] = part
        elif part in _basic_bg_colors:
             styles["background-color"] = part.replace("bg_", "") 
    return styles
def printc(content, styles=None, markdown=False, **kwargs):
    initial_styles = {}
    if isinstance(styles, str):
        initial_styles = _parse_style_string(styles)
    elif isinstance(styles, dict):
        initial_styles = styles.copy()
    effective_styles = initial_styles
    processed_kwargs = {k.replace('_', '-'): v for k, v in kwargs.items()}
    effective_styles.update(processed_kwargs) 
    if effective_styles.get("visibility") == "hidden":
        return 
    is_markdown_table = False
    if markdown:
        lines = str(content).strip().split('\n')
        if len(lines) >= 2 and '|' in lines[0] and re.match(r'\s*\|? *[:\-]+ *\|', lines[1]):
            try:
                headers, alignments, table_data = _parse_markdown_table(lines)

                rendered_table_lines = _render_markdown_table(headers, alignments, table_data, effective_styles)
                for line in rendered_table_lines:
                    sys.stdout.write(line + "\n")
                sys.stdout.flush()
                return 
            except ValueError:
                 pass 
        is_markdown_table = False 
    content_str = str(content)
    lines = content_str.split('\n')
    if markdown and not is_markdown_table:
        lines = [_parse_inline_markdown(line) for line in lines]
    text_fg_code = _get_color_code(effective_styles.get("color", ""), False)
    text_bg_code = _get_color_code(effective_styles.get("background-color", ""), True)
    text_attrs = []
    needs_reset = False 
    for key, value in effective_styles.items():
        property_type = _style_property_map.get(key)
        val_str = str(value).lower().strip() if value is not None else ""
        if property_type == "attribute":
            attr_key = None
            if key == "font-weight" and val_str == "bold": attr_key = "bold"
            elif key == "font-style" and val_str == "italic": attr_key = "italic"
            elif key == "text-decoration":
                if val_str == "underline": attr_key = "underline"
                elif val_str in ("line-through", "strikethrough"): attr_key = "strikethrough"
            elif key == "visibility":
                 if val_str == "dim": attr_key = "dim"
            elif key in _attributes: 
                attr_key = key
            if attr_key and val_str not in ('false', '0', '', 'normal', 'none'):
                attr_code = _attributes.get(attr_key)
                if attr_code:
                    text_attrs.append(attr_code)
                    needs_reset = True 
    text_style_prefix = f"{text_fg_code}{text_bg_code}{''.join(text_attrs)}"
    if text_fg_code or text_bg_code: needs_reset = True 
    style_reset_code = _reset_code 
    has_border = effective_styles.get("border", False)
    if isinstance(has_border, str): has_border = has_border.lower() not in ('false', '0', '')
    else: has_border = bool(has_border)
    is_rounded = effective_styles.get("border-radius", False)
    if isinstance(is_rounded, str): is_rounded = is_rounded.lower() not in ('false', '0', '')
    else: is_rounded = bool(is_rounded)
    is_rounded = is_rounded and has_border 
    default_border_color = effective_styles.get("color", "") 
    border_color_val = effective_styles.get("border-color", default_border_color)
    border_color_code = _get_color_code(border_color_val, False) if has_border else ""
    if border_color_code: needs_reset = True 
    text_align = effective_styles.get("text-align", "left")
    pad_top, pad_right, pad_bottom, pad_left = _parse_padding(effective_styles)
    max_content_width = 0
    if lines:
        max_content_width = max(visible_len(line) for line in lines)
    inner_width = max_content_width + pad_left + pad_right
    output_lines = []
    border_chars = {}
    if has_border:
        border_chars = _get_border_chars(is_rounded, border_color_code)
        h_sep = border_chars.get('h', '-') 
        top_border = f"{border_chars['tl']}{h_sep * inner_width}{border_chars['tr']}"
        output_lines.append(top_border)
    pad_line_content = f"{text_bg_code}{' ' * inner_width}{style_reset_code if text_bg_code else ''}"
    for _ in range(pad_top):
        if has_border:
            output_lines.append(f"{border_chars['v']}{pad_line_content}{border_chars['v']}")
        elif text_bg_code: 
             output_lines.append(pad_line_content)
    for line in lines:
        aligned_line = _align_line(line, max_content_width, text_align)
        left_pad_str = f"{text_bg_code}{' ' * pad_left}{style_reset_code if text_bg_code else ''}"
        right_pad_str = f"{text_bg_code}{' ' * pad_right}{style_reset_code if text_bg_code else ''}"
        full_inner_line = f"{left_pad_str}{text_style_prefix}{aligned_line}{style_reset_code if needs_reset else ''}{right_pad_str}"
        if has_border:
            output_lines.append(f"{border_chars['v']}{full_inner_line}{border_chars['v']}")
        else:
            output_lines.append(full_inner_line) 
    for _ in range(pad_bottom):
        if has_border:
            output_lines.append(f"{border_chars['v']}{pad_line_content}{border_chars['v']}")
        elif text_bg_code:
             output_lines.append(pad_line_content)
    if has_border:
        h_sep = border_chars.get('h', '-')
        bottom_border = f"{border_chars['bl']}{h_sep * inner_width}{border_chars['br']}"
        output_lines.append(bottom_border)
    for line in output_lines:
        sys.stdout.write(line + "\n")
    sys.stdout.flush()
