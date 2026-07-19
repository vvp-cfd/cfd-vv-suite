"""Minimal pure-Python YAML parser for cfdvv case files.

Handles the subset of YAML used in case.yaml files:
- Comments (#)
- Key: value mappings
- Lists (- item; [item1, item2])
- Nested indentation (2 or 4 spaces)
- Multi-line strings (| and >)
- Quoted and unquoted strings
- Numbers (int, float), booleans (true/false, yes/no), null
"""

import re
from typing import Any, List, Optional, Tuple


def _strip_comment(line: str) -> str:
    """Remove inline comments, respecting quoted strings."""
    in_single = False
    in_double = False
    if "#" not in line:
        return line
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return line[:i].rstrip()
    return line


def _is_quoted(s: str) -> bool:
    return (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'"))


def _parse_scalar(s: str) -> Any:
    """Parse a scalar YAML value."""
    s = s.strip()
    if not s:
        return ""

    if _is_quoted(s):
        return s[1:-1]

    low = s.lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    if low in ("null", "~", ""):
        return None

    if re.match(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$", s) and re.search(r"[.eE]", s):
        return float(s)
    if re.match(r"^-?\d+$", s):
        return int(s)
    if re.match(r"^-?\.\d+([eE][+-]?\d+)?$", s):
        return float(s)
    if re.match(r"^-?\.(inf|Inf|INF)$", s):
        return float("inf")
    if s.lower() == ".nan":
        return float("nan")

    return s


def _parse_flow_list(s: str) -> list:
    """Parse inline list: [a, b, c]."""
    s = s.strip()
    if not (s.startswith("[") and s.endswith("]")):
        return []
    inner = s[1:-1].strip()
    if not inner:
        return []

    items = []
    depth = 0
    current = ""
    in_quote = False
    quote_char = ""
    for ch in inner:
        if ch in ("'", '"') and not in_quote:
            in_quote = True
            quote_char = ch
            current += ch
        elif ch == quote_char and in_quote:
            in_quote = False
            quote_char = ""
            current += ch
        elif ch == "," and not in_quote and depth == 0:
            items.append(_parse_scalar(current.strip()))
            current = ""
        elif ch == "[" and not in_quote:
            depth += 1
            current += ch
        elif ch == "]" and not in_quote:
            depth -= 1
            current += ch
        else:
            current += ch
    if current.strip():
        items.append(_parse_scalar(current.strip()))
    return items


def _get_indent(line: str) -> int:
    """Get indentation level (spaces only)."""
    return len(line) - len(line.lstrip(" "))


def _is_list_item(line: str) -> bool:
    """Check if line starts a list item."""
    stripped = line.lstrip()
    return stripped.startswith("- ") or stripped == "-"


def parse(text: str) -> dict:
    """Parse YAML text. Returns a dict."""
    lines = _preprocess_lines(text)
    result, _ = _parse_value(lines, 0, 0, "")
    if isinstance(result, dict):
        return result
    return {}


def _preprocess_lines(text: str) -> List[str]:
    """Split text into lines, preserving empty lines."""
    return text.split("\n")


def _check_eof(lines: List[str], i: int) -> bool:
    return i >= len(lines)


def _skip_blank(lines: List[str], i: int) -> int:
    while i < len(lines) and (not lines[i].strip() or lines[i].strip().startswith("#")):
        i += 1
    return i


def _line_indent(lines: List[str], i: int) -> int:
    if _check_eof(lines, i):
        return -1
    return _get_indent(lines[i])


def _line_is_list(lines: List[str], i: int) -> bool:
    if _check_eof(lines, i):
        return False
    return _is_list_item(lines[i])


def _parse_value(
    lines: List[str], i: int, base_indent: int, current_key: str
) -> Tuple[Any, int]:
    """Parse the next value starting at line i. Returns (value, next_line_index)."""
    i = _skip_blank(lines, i)

    if _check_eof(lines, i):
        return None, i

    indent = _line_indent(lines, i)

    if indent < base_indent:
        return None, i

    stripped = _strip_comment(lines[i]).strip()

    if not stripped:
        return _parse_value(lines, i + 1, base_indent, current_key)

    if _is_list_item(stripped):
        return _parse_list(lines, i, base_indent)

    colon_idx = _find_colon(lines[i])
    if colon_idx >= 0:
        return _parse_mapping(lines, i, base_indent)

    return _parse_scalar(stripped), i + 1


def _find_colon(line: str) -> int:
    """Find the first unquoted colon. Returns index or -1."""
    in_single = False
    in_double = False
    cleaned = _strip_comment(line)
    for i, ch in enumerate(cleaned):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == ":" and not in_single and not in_double:
            return i
    return -1


def _parse_list(
    lines: List[str], i: int, base_indent: int
) -> Tuple[list, int]:
    """Parse a YAML list: items starting with -."""
    result = []
    expected_indent = _line_indent(lines, i)

    while i < len(lines):
        i = _skip_blank(lines, i)
        if _check_eof(lines, i):
            break

        indent = _line_indent(lines, i)

        if indent < base_indent:
            break

        if indent != expected_indent:
            break

        if not _is_list_item(lines[i]):
            break

        line = _strip_comment(lines[i])
        stripped = line.strip()
        item_text = stripped[2:].strip()

        if not item_text or item_text == "-":
            result.append(None)
            i += 1
            continue

        if item_text == "|" or item_text == ">":
            text, i = _consume_multiline(lines, i + 1)
            result.append(text)
            continue

        if item_text.startswith("[") and item_text.endswith("]"):
            result.append(_parse_flow_list(item_text))
            i += 1
            continue

        colon_idx = _find_colon(item_text)
        has_colon = colon_idx >= 0

        next_indent = _line_indent(lines, i + 1) if i + 1 < len(lines) else -1

        if has_colon and colon_idx > 0:
            key = item_text[:colon_idx].strip()
            val = item_text[colon_idx + 1:].strip()

            if val:
                if next_indent > indent:
                    sub_val, i = _parse_value(lines, i + 1, indent + 2, key)
                    entry = {key: _parse_scalar(val)}
                    if isinstance(sub_val, dict):
                        entry.update(sub_val)
                    result.append(entry)
                    continue
                result.append({key: _parse_scalar(val)})
                i += 1
                continue
            elif next_indent > indent:
                sub_val, i = _parse_value(lines, i + 1, indent + 2, key)
                if sub_val is not None:
                    result.append({key: sub_val})
                else:
                    result.append({key: {}})
                continue

        if next_indent > indent:
            sub_val, i = _parse_value(lines, i + 1, indent + 2, "")
            if isinstance(sub_val, dict):
                result.append(sub_val)
            else:
                result.append(item_text)
        else:
            result.append(_parse_scalar(item_text))
            i += 1

    return result, i


def _parse_mapping(
    lines: List[str], i: int, base_indent: int
) -> Tuple[dict, int]:
    """Parse a YAML mapping: key: value pairs."""
    result = {}
    expected_indent = _line_indent(lines, i) if not _check_eof(lines, i) else base_indent

    while i < len(lines):
        i = _skip_blank(lines, i)
        if _check_eof(lines, i):
            break

        indent = _line_indent(lines, i)

        if indent < base_indent:
            break

        if indent != expected_indent:
            break

        line = _strip_comment(lines[i])
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if _is_list_item(stripped):
            break

        colon_idx = _find_colon(stripped)
        if colon_idx < 0:
            i += 1
            continue

        key = stripped[:colon_idx].strip()
        if _is_quoted(key):
            key = key[1:-1]

        value_part = stripped[colon_idx + 1:].strip()

        next_indent = _line_indent(lines, i + 1) if i + 1 < len(lines) else -1

        if not value_part:
            if next_indent > indent:
                sub_val, i = _parse_value(lines, i + 1, indent + 2, key)
                if sub_val is not None:
                    result[key] = sub_val
                continue
            else:
                result[key] = None
                i += 1
                continue

        if value_part in ("|", ">"):
            text, i = _consume_multiline(lines, i + 1)
            result[key] = text
            continue

        if value_part.startswith("[") and value_part.endswith("]"):
            result[key] = _parse_flow_list(value_part)
            i += 1
            continue

        if next_indent > indent and _line_is_list(lines, i + 1):
            sub_val, i = _parse_value(lines, i + 1, indent, key)
            if isinstance(sub_val, list):
                result[key] = sub_val
            continue

        result[key] = _parse_scalar(value_part)
        i += 1

    return result, i


def _consume_multiline(
    lines: List[str], i: int
) -> Tuple[str, int]:
    """Consume indented multi-line string."""
    if _check_eof(lines, i):
        return "", i

    base_indent = _line_indent(lines, i)
    parts = []

    while i < len(lines):
        stripped = lines[i].rstrip()
        indent = _get_indent(lines[i])
        if not stripped:
            parts.append("")
            i += 1
            continue
        if indent < base_indent:
            break
        parts.append(lines[i][base_indent:].rstrip())
        i += 1

    return "\n".join(parts).strip(), i


def load(stream) -> dict:
    """Load YAML from a file-like object."""
    return parse(stream.read())
