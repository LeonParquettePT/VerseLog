# VerseLog

*[🇫🇷 Lire en français](README.fr.md)*

A free, open-source, community-collaborative logistics assistant for [Star Citizen](https://robertsspaceindustries.com/). VerseLog reads your contract board, validates what it reads, and hands back a route and cargo plan that maximizes aUEC earned per minute — built to run alongside the game on modest hardware, not to fight it for resources.

## Status

Core logic, capture/data-source adapters, the application entrypoint, and a Tkinter results UI are built and tested (4 epics done, 114 tests) — see the [project docs](https://leonparquettept.github.io/VerseLog/) for the full review. A packaged Windows build is available now: **[Download verselog.exe](https://github.com/LeonParquettePT/VerseLog/releases/latest)** — single file, no Python install required (Tesseract and Ollama are still separate installs). Windows may show a false-positive antivirus/SmartScreen warning on first run (unsigned executable) — see the Release notes for how to allow it. Linux packaging isn't published yet. The full contract for what this project builds is in [`_bmad-output/specs/spec-verselog/SPEC.md`](_bmad-output/specs/spec-verselog/SPEC.md). Known risks and how they're handled are tracked in [RISKS.md](RISKS.md).

## Contributing

Contributions are welcome — this project is open from day one so anyone can read, understand, and improve it. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for ground rules and how to propose a change.

## License

MIT — see [LICENSE](LICENSE).
