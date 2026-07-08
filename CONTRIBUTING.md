# Contributing to VerseLog

*[🇫🇷 Lire en français](CONTRIBUTING.fr.md)*

VerseLog is open from day one so anyone can read, understand, and improve it — including people, like the project's own author, who are still learning. You don't need to be an expert to contribute; you do need to read [`SPEC.md`](_bmad-output/specs/spec-verselog/SPEC.md) first, since it's the contract every change should trace back to.

## Ground rules

- **Functional first, clean second.** A working, correct change beats a beautifully abstracted one. Don't add flexibility or design patterns for problems the project doesn't have yet.
- **Write plain, direct code.** Comment only what the code can't say for itself (a non-obvious constraint, a workaround, a "why", not a "what"). Avoid boilerplate, defensive handling for cases that can't occur, and restating the obvious — code that reads like it was padded out is harder to trust and harder to maintain, whether a human or an AI wrote it.
- **Respect the constraints in SPEC.md.** In particular: no paid cloud dependency, must stay usable on modest hardware, no mandatory microphone/voice requirement.

## Proposing a change

1. Open an issue first for anything non-trivial, so the approach can be discussed before code is written.
2. Fork the repo, branch off `main`, make your change.
3. Open a pull request describing *what* changed and *why* — link back to the relevant SPEC capability (e.g. `CAP-4`) or open question if applicable.
4. Be patient — this is a small community project, reviews may take a bit.

## Reporting a bug

Open a GitHub issue with what you expected, what happened instead, and your environment (OS, and whether you're on Windows or Linux — both are supported targets).

## Setup instructions

Not written yet — the technical stack hasn't been finalized. This section will be filled in once it is.

## License

By contributing, you agree your contribution is licensed under the project's [MIT License](LICENSE).
