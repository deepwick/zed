# Deepwick for Zed

A deep navy theme with Visual Studio 2022's syntax colors.

> Deepwick is an unofficial theme derived from
> [Polywick Blue](https://vscode.polywickstudio.net) by Polywick Studio (MIT).
> Not affiliated with Polywick Studio.

![Deepwick in Zed](screenshot.png)

## Install

Copy the theme into Zed's user themes folder:

```sh
mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/zed/themes"
cp themes/deepwick.json "${XDG_CONFIG_HOME:-$HOME/.config}/zed/themes/"
```

Then pick **Deepwick** with `theme selector: toggle`, or set it in
`settings.json`:

```json
{ "theme": "Deepwick" }
```

To work on the theme, use **zed: install dev extension** and choose this
folder.

## Notes

- Tree-sitter without semantic tokens: no capture distinguishes interfaces,
  enums, and structs from other types, so the Mint role appears only where a
  language server supplies semantic tokens.
- C/C++ preprocessor directives are bold Foreground. Function-like macro
  definitions are Magenta (Rust macro calls such as `println!` share the
  capture and are Magenta too); object-like macro names (`#define MAX 3`) get
  only Zed's all-caps constant capture, so they are Cyan.
- Renamed files use Magenta.
- Zed's Python grammar captures control-flow keywords (`if`, `for`,
  `return`, `import`, …) and `and`/`or`/`not`/`is`/`in` (including a for-loop's
  `in`) as plain keywords, so they
  take the keyword color (Blue); builtin types take the type color (Teal).
  Docstrings are captured as strings (Orange).
- Zed releases from March 2026 match captures by longest prefix, and their C/C++
  grammar marks directives `keyword.preproc`; this theme sets that capture bold
  Foreground too, so directives look the same on both.

Tested with Zed 0.223.3.

## License

MIT. See [LICENSE](LICENSE).
