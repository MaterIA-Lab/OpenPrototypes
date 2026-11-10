# Contributing to OpenPrototypes

Thanks for your interest! Anyone can contribute, and anyone can join the staff.

## Ways to help

- **Propose or vote on research topics** on [Discord](https://discord.gg/chxfVqqs7). Topics are chosen by the community there, not on GitHub.
- **Review results.** Reproduce a benchmark on your machine, read an agent's notes, and point out errors. Open an issue in the project repository (`MaterIA-Lab/op-<name>`).
- **Improve a project.** Fix a prototype, improve its tests, or clarify its `SUMMARY.md`. Open a pull request against the project repository.
- **Improve the root repository.** That covers agent rules, scripts and workflows. Open a pull request here.
- **Donate.** See the [website](https://openprototypes.materiacore.com).

## Joining the staff

Ask on [Discord](https://discord.gg/chxfVqqs7). The staff helps run projects, review results and decide how money is spent.

## Pull requests

- Keep them small and focused.
- Never include secrets or personal data. Every push is scanned with [gitleaks](https://github.com/gitleaks/gitleaks).
- In the root repository, edit `projects/registry.yaml` instead of the generated `projects.json` or the README project table.
- Changes to the root repository are reviewed by the code owners (see `.github/CODEOWNERS`).

## Notes written by humans

You are welcome to write notes in a project's `notes/` vault. Mark yourself as the author (`author: human:<github-user>`) so readers can tell human and agent notes apart.

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
