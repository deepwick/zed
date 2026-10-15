import json
import tomllib
import urllib.request
from pathlib import Path

import pytest

from deepwick_spec.check_port import check_port
from deepwick_spec.color import normalize_hex
from deepwick_spec.palette import ANSI_SLOTS, load_palette

REPO = Path(__file__).resolve().parents[1]
PALETTE = load_palette()
C = PALETTE.colors
SCHEMA_URL = "https://zed.dev/schema/themes/v0.2.0.json"

SYNTAX_ROLES = {
    "comment": ["comment", "comment.doc"],
    "keyword": ["keyword", "boolean", "variable.special"],
    "controlFlow": ["keyword.control"],
    "operator": ["operator", "punctuation", "punctuation.bracket", "punctuation.delimiter"],
    "type": ["type", "constructor"],
    "interface": ["enum"],
    "function": ["function", "attribute"],
    "variable": ["variable", "property"],
    "constant": ["constant", "variant"],
    "string": ["string"],
    "escape": ["string.escape", "string.special"],
    "regex": ["string.regex"],
    "number": ["number"],
    "tag": ["tag"],
    "preprocessorKeyword": ["keyword.directive", "preproc"],
    "label": ["label"],
    "heading": ["title"],
    "link": ["link_text"],
    "inlineCode": ["text.literal"],
}


def theme_file():
    return json.loads((REPO / "themes" / "deepwick.json").read_text(encoding="utf-8"))


def style():
    themes = theme_file()["themes"]
    assert [t["name"] for t in themes] == ["Deepwick"]
    assert themes[0]["appearance"] == "dark"
    return themes[0]["style"]


def test_extension_manifest():
    with open(REPO / "extension.toml", "rb") as f:
        manifest = tomllib.load(f)
    assert manifest["id"] == "deepwick"
    assert manifest["name"] == "Deepwick"
    assert manifest["schema_version"] == 1
    assert manifest["repository"] == "https://github.com/deepwick/zed"


def test_theme_family_metadata():
    t = theme_file()
    assert t["$schema"] == SCHEMA_URL
    assert t["name"] == "Deepwick"


def test_validates_against_zed_schema():
    jsonschema = pytest.importorskip("jsonschema")
    try:
        request = urllib.request.Request(SCHEMA_URL, headers={"User-Agent": "curl/8 deepwick-tests"})
        with urllib.request.urlopen(request, timeout=10) as response:
            schema = json.load(response)
    except OSError as e:
        pytest.skip(f"schema unavailable: {e}")
    jsonschema.validate(theme_file(), schema)


@pytest.mark.parametrize(
    ("key", "color"),
    [
        ("background", "surface"),
        ("editor.background", "background"),
        ("editor.foreground", "foreground"),
        ("editor.gutter.background", "background"),
        ("editor.active_line.background", "surface"),
        ("editor.line_number", "muted"),
        ("editor.active_line_number", "foreground"),
        ("panel.background", "surface"),
        ("status_bar.background", "surface"),
        ("title_bar.background", "surface"),
        ("tab.active_background", "background"),
        ("tab.inactive_background", "surface"),
        ("border", "overlay"),
        ("border.focused", "blue"),
        ("text", "foreground"),
        ("text.muted", "muted"),
        ("text.accent", "blue"),
        ("search.match_background", "selection"),
        ("terminal.background", "background"),
        ("terminal.foreground", "foreground"),
        ("error", "red"),
        ("warning", "yellow"),
        ("info", "cyan"),
        ("hint", "muted"),
        ("success", "green"),
        ("created", "green"),
        ("deleted", "red"),
        ("modified", "blue"),
        ("created.background", "diffAdded"),
        ("deleted.background", "diffRemoved"),
        ("modified.background", "diffChanged"),
    ],
)
def test_ui_colors(key, color):
    assert style()[key] == C[color]


def test_terminal_ansi():
    s = style()
    for slot in ANSI_SLOTS:
        zed_slot = slot
        assert s[f"terminal.ansi.{zed_slot}"] == PALETTE.ansi[slot], slot
        assert s[f"terminal.ansi.bright_{zed_slot}"] == PALETTE.ansi["bright" + slot.capitalize()], slot
        assert s[f"terminal.ansi.dim_{zed_slot}"] == PALETTE.ansi[slot], slot


@pytest.mark.parametrize("role", sorted(SYNTAX_ROLES))
def test_syntax_roles(role):
    syntax = style()["syntax"]
    expected = PALETTE.syntax[role]
    for key in SYNTAX_ROLES[role]:
        entry = syntax[key]
        assert entry["color"] == C[expected.color], key
        if "italic" in expected.style:
            assert entry["font_style"] == "italic", key
        if "bold" in expected.style:
            assert entry["font_weight"] == 700, key


def test_player_and_every_color_value_in_palette():
    allowed = PALETTE.allowed_hex()

    def walk(value, path):
        if isinstance(value, dict):
            for k, v in value.items():
                yield from walk(v, f"{path}.{k}")
        elif isinstance(value, list):
            for i, v in enumerate(value):
                yield from walk(v, f"{path}[{i}]")
        elif isinstance(value, str) and value.startswith("#"):
            yield path, value

    colors = list(walk(style(), "style"))
    assert colors
    for path, value in colors:
        assert normalize_hex(value) in allowed, f"{path} = {value}"
    assert style()["players"][0]["cursor"] == C["foreground"]


def zed_style(capture):
    parts = capture.split(".")
    best, best_len = None, 0
    for key, value in style()["syntax"].items():
        key_parts = key.split(".")
        if all(p in parts for p in key_parts) and len(key_parts) >= best_len:
            best, best_len = value, len(key_parts)
    return best


def zed_style_prefix(capture):
    """Current Zed (>= 2026-03): longest theme key that is a dot-prefix of the capture."""
    best, best_len = None, -1
    for key, value in style()["syntax"].items():
        if (capture == key or capture.startswith(key + ".")) and len(key) > best_len:
            best, best_len = value, len(key)
    return best


@pytest.mark.parametrize("match", [zed_style, zed_style_prefix], ids=["zed-0.223", "zed-current"])
@pytest.mark.parametrize("capture", ["keyword.directive", "keyword.preproc", "preproc"])
def test_preprocessor_bold_foreground_in_both_matchers(match, capture):
    directive = match(capture)
    assert directive["color"] == C["foreground"] and directive["font_weight"] == 700


def test_c_preprocessor_captures():
    directive = zed_style("keyword.directive")
    assert directive["color"] == C["foreground"] and directive["font_weight"] == 700
    assert zed_style("function.special")["color"] == C["magenta"]


def test_port_conventions():
    assert check_port(REPO, PALETTE.allowed_hex()) == []
