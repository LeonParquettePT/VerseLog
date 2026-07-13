# VerseLog

*[🇫🇷 Lire en français](README.fr.md)*

A free, open-source, community-collaborative logistics assistant for [Star Citizen](https://robertsspaceindustries.com/). VerseLog reads your contract board, validates what it reads, and hands back a route and cargo plan that maximizes aUEC earned per minute — built to run alongside the game on modest hardware, not to fight it for resources.

## Status

Core logic, capture/data-source adapters, the application entrypoint, a Tkinter results UI, and a guided Windows installer are built and tested (4 epics done, 25 stories, 176 tests) — see the [project docs](https://leonparquettept.github.io/VerseLog/) for the full review. Packaged builds are available now for both Windows and Linux, single file, no Python install required (Tesseract and Ollama are still separate installs):

- **[Download verselog-installer.exe (Windows, recommended)](https://github.com/LeonParquettePT/VerseLog/releases/tag/v0.1.0-windows)** — a guided, step-by-step installer: runs a hardware benchmark, lets you pick which prerequisites to install (checkboxes, nothing installed without your confirmation), and offers to create a shortcut at the end. Place it in the same folder as `verselog.exe`.
- **[Download verselog.exe (Windows, direct)](https://github.com/LeonParquettePT/VerseLog/releases/tag/v0.1.0-windows)** — skip the wizard and run the app itself directly.
- Either Windows .exe may be blocked outright by **Smart App Control** ("we couldn't verify its publisher") since neither binary is code-signed yet — there's no per-app override for that. You'd need to temporarily disable Smart App Control (Windows Security → App & Browser Control) to run it; re-enabling afterward will likely block it again on the next launch (it's still unsigned), so keep it disabled while you use VerseLog or toggle it each time. See the Release notes for details.
- **[Download verselog-linux (Linux)](https://github.com/LeonParquettePT/VerseLog/releases/tag/v0.1.0-linux)** — built via a disposable GitHub Actions runner, verified end-to-end on a real Ubuntu Desktop VM (graphical window included). Run `chmod +x verselog-linux` after downloading. See the Release notes for a copy-pasteable prerequisite install block.

Note: running the local vision tier (Ollama) is memory-hungry once it's actually used for inference — confirmed directly on a 4 GB test VM (fine until the model loads, not enough once it does). The built-in benchmark should already prefer the lighter Tesseract/OCR tier on modest hardware.

The full contract for what this project builds is in [`_bmad-output/specs/spec-verselog/SPEC.md`](_bmad-output/specs/spec-verselog/SPEC.md). Known risks and how they're handled are tracked in [RISKS.md](RISKS.md).

## Contributing

Contributions are welcome — this project is open from day one so anyone can read, understand, and improve it. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for ground rules and how to propose a change.

## License

MIT — see [LICENSE](LICENSE).
