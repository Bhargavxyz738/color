# color - Enhanced Terminal Printing

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*   Copyright (c) 2025 Bhargav
*   Licensed under the MIT License – see the LICENSE file for details.

## Purpose

`color` is a simple yet powerful Python module designed to enhance terminal output. It allows you to easily print text with various styles, including:

*   Foreground and background colors (using basic names, hex codes, or RGB values).
*   Text attributes like bold, italic, underline, strikethrough, dim, blink, and reverse.
*   CSS-like padding and borders (including rounded corners).
*   Text alignment (left, center, right).
*   Basic rendering of Markdown-style tables with styling.

Its primary goal is to make command-line application output more readable, visually appealing, and structured without requiring complex dependencies.

## Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Bhargavxyz738/color.git
    ```
## How to Use

Import the `printc` function from the module:

```python
from color import printc
```

The `printc` function is the main interface for this module. You pass the content you want to print as the first argument, and styling options as keyword arguments or within a `styles` dictionary.

### Basic Usage

```python
# Print simple text
printc("Hello, World!")

# Print with a basic color
printc("This is green text.", color="green")
printc("This is white text on a blue background.", color="white", background_color="blue")

# Print with text attributes
printc("This is bold and red.", color="red", font_weight="bold") 
printc("This is underlined cyan.", color="cyan", text_decoration="underline")
printc("This is italic magenta.", color="magenta", font_style="italic") 
```

### Styling Arguments

Styles can be provided in two ways:

1.  **Keyword Arguments:** Use keyword arguments corresponding to CSS-like properties, replacing hyphens (`-`) with underscores (`_`).
    ```python
    printc("Styled via kwargs", color="yellow", background_color="#333333", font_weight="bold", padding=1)
    ```
2. Pass a dictionary to the printc function as a parameter. Keys should be CSS-like property names (strings with hyphens).
    ```python
    style_dict = {
        "color": "rgb(100, 150, 250)",
        "background-color": "black",
        "padding": (1, 2), # Top/Bottom=1, Left/Right=2
        "border": True,
        "border-color": "green",
        "font-weight": "bold"
    }
    printc("Styled via dict",style_dict)
    ```

### Supported Style Properties (as kwargs / dict keys)

*   **Colors:**
    *   `color`: Text foreground color.
    *   `background_color` / `background-color`: Text background color.
    *   *Values:* Basic color names (`"red"`, `"blue"`, etc.), hex codes (`"#ff0000"`, `"#f00"`), RGB strings (`"rgb(255, 0, 0)"`).
*   **Attributes:**
    *   `font_weight`: Set to `"bold"` for bold text.
    *   `font_style`: Set to `"italic"` for italic text.
    *   `text_decoration`: Set to `"underline"` or `"line-through"` (strikethrough).
    *   `visibility`: Set to `"dim"` for dimmed text (support varies by terminal).
    *   `blink`: Set to `True` for blinking text (support varies by terminal).
    *   `reverse`: Set to `True` to swap foreground/background (support varies by terminal).
    *   `strikethrough`: Set to `True` for strikethrough text.
*   **Box Model:**
    *   `padding`: Space between text and border. Can be an integer (all sides), or a tuple `(top_bottom, left_right)` or `(top, right, bottom, left)`.
    *   `padding_top` / `padding-top`, `padding_right` / `padding-right`, etc.: Override individual padding sides.
    *   `border`: Set to `True` to draw a border.
    *   `border_color` / `border-color`: Color of the border. Uses `color` if not set.
    *   `border_radius`: Set to `True` (along with `border=True`) for rounded corners.
*   **Alignment:**
    *   `text_align` / `text-align`: Align text within its padded box (`"left"`, `"center"`, `"right"`). Default is `"left"`.

## Tricks and Advanced Features

### 1. Hex and RGB Colors

Go beyond basic terminal colors:

```python
printc("Bright Pink using Hex", color="#FF1493")
printc("Deep Blue using RGB", color="rgb(0, 0, 139)")
printc("Background using Hex", background_color="#404040", color="white")
```

### 2. Padding and Borders

Create boxed content:

```python
# Simple box
printc("This text is in a box.", border=True, padding=1)

# Colored, rounded box with more padding
printc("Fancy Box!", 
       color="black", 
       background_color="yellow", 
       border=True, 
       border_color="blue", 
       border_radius=True, 
       padding=(1, 4), # 1 top/bottom, 4 left/right
       font_weight="bold",
       text_align="center") 
```

### 3. Multi-line Content

`printc` handles multi-line strings correctly with padding and borders:

```python
multi_line_text = "This is the first line.\nThis is the second, slightly longer line.\nShort."
printc(multi_line_text, border=True, padding=1, border_color="magenta")
```

### 4. Text Alignment

Align text within the calculated width (including padding):

```python
printc("Left Aligned (Default)", border=True, padding=1, text_align="left")
printc("Center Aligned", border=True, padding=1, text_align="center")
printc("Right Aligned", border=True, padding=1, text_align="right")
```

### 5. Markdown Table Rendering

Pass `markdown=True` to render simple Markdown tables with the specified styles applied to cells and the optional border:

```python
markdown_table = """
| Header 1 | Header 2 | Header 3 |
| :------- | :------: | -------: |
| Left     | Center   | Right    |
| Foo      | Bar      | Baz      |
| A really long cell | Short | Data |
"""

printc(markdown_table, 
       markdown=True, 
       color="cyan", 
       border=True, 
       border_color="white",
       padding=1)

# Example with background and rounded borders
printc(markdown_table, 
       markdown=True, 
       color="yellow", 
       background_color="#222222",
       border=True, 
       border_radius=True,
       border_color="yellow",
       padding=1)
```

*Note: The Markdown parser is basic and expects the standard header/separator/data format.*

## License

This project is licensed under the MIT License - see the LICENSE file for details.
