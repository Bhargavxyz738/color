# Python Color Module

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Optional: Add license badge -->
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/) <!-- Optional: Specify Python version -->

A simple yet powerful Python module for printing colorful and styled text, including padding and borders, directly to the terminal using ANSI escape codes.

## Features

*   **Basic Colors:** Supports standard foreground (`red`, `blue`, etc.) and background (`bg_red`, `bg_blue`, etc.) terminal colors.
*   **24-bit True Color:** Accepts Hex (`#rgb`, `#rrggbb`) and RGB (`rgb(r,g,b)`) color values for both foreground and background.
*   **Text Attributes:** Apply styles like `bold`, `italic`, `underline`, `strikethrough`, `dim`, `blink`, and `reverse`.
*   **CSS-like Styling:** Use familiar property names like `color`, `background-color`, `font-weight`, `font-style`, `text-decoration`.
*   **Box Model:**
    *   Add `padding` around the text (supports shorthand and individual sides: `padding-top`, `padding-right`, `padding-bottom`, `padding-left`).
    *   Draw `borders` around the text content and padding.
    *   Customize `border-color`.
    *   Option for `border-radius` (rounded corners).
    *   Align text within the box (`text-align`: 'left', 'center', 'right').
*   **ANSI Handling:** Includes utilities to strip ANSI codes (`strip_ansi`) and calculate the *visible* length of styled strings (`visible_len`), crucial for correct alignment and border rendering.
*   **Flexible API:** Pass styles via a dictionary or directly as keyword arguments.
*   **Direct Output:** Prints directly to `sys.stdout`.

## Requirements

*   Python 3.6+
*   A terminal that supports ANSI escape codes (most modern terminals do). True Color (24-bit) support is required for Hex/RGB colors to display accurately.

## Installation

Currently, this module is provided as a single file. To use it:

1.  Save the code as `color.py` in your project directory.
2.  Import the `text` function from the module:

    ```python
    from color import text
    ```

Alternatively, place `color.py` in a directory included in your Python path.

## Usage

The primary function is `text()`.

```python
from color import text

# Basic usage (defaults to terminal's default colors)
text("Hello, World!")

# --- Basic Colors and Attributes ---

# Red text
text("This is red text.", color="red")

# Green text, bold
text("This is bold green text.", color="green", font_weight="bold")

# Yellow text on a blue background
text("Warning!", color="yellow", background_color="bg_blue", font_weight="bold")

# Using attributes
text("Underlined text", text_decoration="underline")
text("Italic text", font_style="italic")
text("Strikethrough text", text_decoration="line-through")
text("Dimmed text", visibility="dim") # Or use 'dim=True'

# --- Hex and RGB Colors ---

# Using Hex colors
text("Magenta text (Hex)", color="#FF00FF")
text("Cyan background (Hex)", background_color="#00FFFF", color="black")
text("Short Hex", color="#f0c", background_color="#333")

# Using RGB colors
text("Orange text (RGB)", color="rgb(255, 165, 0)")
text("Text on purple background (RGB)", color="white", background_color="rgb(128, 0, 128)")

# --- Padding ---

# Add padding (applies to all sides)
text("Padded text", padding=1, background_color="bg_cyan", color="black")

# Specific padding
text(
    "More padding",
    padding_top=0,
    padding_right=4,
    padding_bottom=1,
    padding_left=2,
    background_color="bg_yellow",
    color="black"
)

# --- Borders ---

# Simple border (uses text color or default terminal color)
text("Text with a border", border=True, color="blue")

# Border with padding and specific border color
text(
    "Boxed Content",
    padding=1,
    border=True,
    border_color="green",
    color="yellow"
)

# Rounded border
text(
    "Rounded Box",
    padding=1,
    border=True,
    border_radius=True,
    border_color="#ff8800", # Orange border
    color="white",
    background_color="bg_blue"
)

# --- Text Alignment ---

# Center-aligned text within a box
text(
    "Centered\nMulti-line text\nAligned Center",
    padding=1,
    border=True,
    border_color="magenta",
    text_align="center",
    width=30 # Note: Width is calculated automatically, this is just for example
)

# Right-aligned text
text(
    "Right Aligned",
    padding_left=10, # Add space for alignment to be visible
    padding_right=1,
    border=True,
    text_align="right",
    background_color="bg_white",
    color="black"
)


# --- Combining Styles & Using the 'styles' Dictionary ---

# Styles can be passed as a dictionary
style_config = {
    "color": "rgb(200, 200, 255)",
    "background-color": "#333333",
    "font-weight": "bold",
    "text-decoration": "underline",
    "padding": (1, 2), # (vertical, horizontal) shorthand
    "border": True,
    "border-radius": True,
    "border-color": "yellow",
    "text-align": "center"
}
text("Complex Styled Box\nUsing a style dictionary.", styles=style_config)

# Keyword arguments override 'styles' dict values
text(
    "Override Example",
    styles=style_config,
    color="red", # Override color from the dictionary
    border_radius=False # Override border-radius
)

# --- Multiline Content ---
text("First line.\nSecond line is a bit longer.\nThird line.", padding=1, border=True)

```

## API Reference

### `text(content, styles=None, **kwargs)`

Prints the given `content` string to `sys.stdout` formatted according to the provided styles.

*   **`content`** (`str`): The text string to be styled and printed. Can contain newline characters (`\n`).
*   **`styles`** (`dict`, optional): A dictionary where keys are CSS-like style property names (strings, e.g., `"background-color"`, `"font-weight"`) and values are the desired style values.
*   **`**kwargs`**: Style properties can also be passed directly as keyword arguments (using underscores, e.g., `background_color="blue"`, `font_weight="bold"`). Keyword arguments take precedence over styles defined in the `styles` dictionary if there are conflicts.

## Supported Styles

Styles can be provided either via the `styles` dictionary (using hyphenated keys) or as keyword arguments (using underscored keys).

| Property (`kwargs` / `styles` key) | Value Type                | Description                                                                                                                                                                                             | Example (`kwargs`)                               |
| :--------------------------------- | :------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :----------------------------------------------- |
| `color`                            | `str`                     | Text foreground color. See [Color Formats](#color-formats).                                                                                                                                             | `color="red"` / `color="#ffcc00"`                |
| `background_color`                 | `str`                     | Text background color. Use basic names prefixed with `bg_` or Hex/RGB values. See [Color Formats](#color-formats).                                                                                       | `background_color="bg_blue"` / `background_color="rgb(50,50,50)"` |
| `font_weight`                      | `str`                     | Set to `"bold"` for bold text.                                                                                                                                                                          | `font_weight="bold"`                             |
| `font_style`                       | `str`                     | Set to `"italic"` for italic text.                                                                                                                                                                      | `font_style="italic"`                            |
| `text_decoration`                  | `str`                     | Set to `"underline"` or `"line-through"` (strikethrough).                                                                                                                                               | `text_decoration="underline"`                    |
| `visibility`                       | `str`                     | Set to `"dim"` for dimmed text. (`"hidden"` is parsed but currently has no visual effect).                                                                                                              | `visibility="dim"`                               |
| `bold`                             | `bool`                    | Shortcut for `font_weight="bold"`.                                                                                                                                                                      | `bold=True`                                      |
| `italic`                           | `bool`                    | Shortcut for `font_style="italic"`.                                                                                                                                                                     | `italic=True`                                    |
| `underline`                        | `bool`                    | Shortcut for `text_decoration="underline"`.                                                                                                                                                             | `underline=True`                                 |
| `strikethrough`                    | `bool`                    | Shortcut for `text_decoration="line-through"`.                                                                                                                                                          | `strikethrough=True`                             |
| `dim`                              | `bool`                    | Shortcut for `visibility="dim"`.                                                                                                                                                                        | `dim=True`                                       |
| `blink`                            | `bool`                    | Enable blinking text (terminal support varies).                                                                                                                                                         | `blink=True`                                     |
| `reverse`                          | `bool`                    | Reverse foreground and background colors.                                                                                                                                                               | `reverse=True`                                   |
| `padding`                          | `int`, `tuple`, `list`    | Inner spacing. `int`: all sides. `(v, h)`: top/bottom, left/right. `(t, r, b, l)`: top, right, bottom, left.                                                                                              | `padding=1` / `padding=(0, 2)`                   |
| `padding_top`                      | `int`                     | Top padding. Overrides `padding`.                                                                                                                                                                       | `padding_top=1`                                  |
| `padding_right`                    | `int`                     | Right padding. Overrides `padding`.                                                                                                                                                                     | `padding_right=2`                                |
| `padding_bottom`                   | `int`                     | Bottom padding. Overrides `padding`.                                                                                                                                                                    | `padding_bottom=1`                               |
| `padding_left`                     | `int`                     | Left padding. Overrides `padding`.                                                                                                                                                                      | `padding_left=2`                                 |
| `border`                           | `bool`                    | `True` to draw a border around padding and content.                                                                                                                                                     | `border=True`                                    |
| `border_color`                     | `str`                     | Color for the border. Defaults to `color` if set, otherwise terminal default. See [Color Formats](#color-formats).                                                                                        | `border_color="green"` / `border_color="#cccccc"` |
| `border_radius`                    | `bool`                    | `True` to use rounded corners for the border (requires `border=True`).                                                                                                                                  | `border_radius=True`                             |
| `text_align`                       | `str`                     | Horizontal alignment within the box: `"left"` (default), `"center"`, `"right"`.                                                                                                                         | `text_align="center"`                            |

## Color Formats

The `color`, `background_color`, and `border_color` properties accept colors in the following formats:

1.  **Basic Color Names** (string):
    *   Foreground: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`
    *   Background: `bg_black`, `bg_red`, `bg_green`, `bg_yellow`, `bg_blue`, `bg_magenta`, `bg_cyan`, `bg_white`
2.  **Hex Colors** (string):
    *   `#rgb` (e.g., `#f0c`)
    *   `#rrggbb` (e.g., `#ff00cc`)
3.  **RGB Colors** (string):
    *   `rgb(r, g, b)` where `r`, `g`, `b` are integers from 0-255 (e.g., `rgb(255, 0, 204)`)
    *   `rgba(...)` is parsed, but the alpha channel is ignored.

## Helper Functions (Internal/Advanced Use)

The module also contains helper functions primarily for internal use, but they might be useful separately:

*   `strip_ansi(s)`: Removes all ANSI escape codes from a string `s`.
*   `visible_len(s)`: Calculates the visible character length of a string `s`, ignoring ANSI codes and accounting for wide characters (like CJK).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (or add the license text here).
