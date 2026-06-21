# Contributing

We welcome contributions to **Crossbar.io**! This guide explains how to get involved.

## Getting in Touch

- **GitHub Issues**: Report bugs or request features at
  https://github.com/crossbario/crossbar/issues
- **GitHub Discussions**: Ask questions and discuss at
  https://github.com/crossbario/crossbar/discussions

## Filing Issues

We track **issues** in the GitHub issue tracker [here](https://github.com/crossbario/crossbar/issues).

An issue is either a **bug** (an unexpected / unwanted behavior of the software or incorrect documentation) or a **feature** (a desire for new functionality / behavior in the software or new documentation).

A **question** though is *not* an issue - please use GitHub Discussions for questions.

### Filing Bugs

When reporting issues, please include:

1. Crossbar.io version (`crossbar version`)
2. Python version (`python --version`)
3. Operating system and version
4. Crossbar.io node configuration (sanitized)
5. Minimal steps to reproduce the issue
6. Full traceback if applicable

### Filing Features

When proposing a new **feature**, please provide:

1. Your actual **use case** and your **goals**
2. *Why* this is important for you
3. Optionally, a proposed solution

## Contributing Code

1. **File or find an issue** first, and get agreement that the change is wanted
2. **Fork the repository** on GitHub
3. **Create a feature branch** from `master`
4. **Make your changes** following the code style
5. **Add tests** that prove your change (see [Bug Fix Workflow (Test-Driven)](#bug-fix-workflow-test-driven))
6. **Run the test suite** locally to ensure nothing is broken
7. **Add an AI-assistance disclosure** audit file (see [AI-Assistance Disclosure](#ai-assistance-disclosure))
8. **Submit a pull request** referencing the originating issue

We use the Fork & Pull Model. This means that you fork the repo, make changes to your fork, and then make a pull request here on the main repo.

### AI-Assistance Disclosure

Every pull request must include an **audit file** declaring whether AI-assistance
tools (e.g. GitHub Copilot, Claude, ChatGPT, Cursor) were used to help create it.

Add a file at `.audit/<github-username>_<branch>.md` (for example
`.audit/jane_fix-1234.md`) containing:

```markdown
- [ ] I did **not** use any AI-assistance tools to help create this pull request.
- [x] I **did** use AI-assistance tools to *help* create this pull request.
- [x] I have read, understood and followed the project's [AI Policy](https://github.com/crossbario/autobahn-python/blob/main/AI_POLICY.md) when creating code, documentation etc. for this pull request.

Submitted by: @<github-username>
Date: <YYYY-MM-DD>
Related issue(s): #<issue-number>
Branch: <github-username>:<branch>
```

Tick the box that applies. The `Related issue(s):` line must reference the
issue the PR addresses.

> **Filename:** use `<github-username>_<branch>.md` with an **underscore**, and
> only cross-platform-safe characters (`A-Z a-z 0-9 . _ -`). Do **not** copy the
> GitHub `owner:branch` label literally — a `:` (or `/`) in the filename breaks
> `git checkout` on Windows. The `:` belongs only *inside* the file, on the
> `Branch:` line.

### Contributor Assignment Agreement

Before you can contribute any changes to the Crossbar.io project, we need a CAA (Contributor Assignment Agreement) from you.

The CAA gives us the rights to your code, which we need e.g. to react to license violations by others, for possible future license changes and for dual-licensing of the code.

#### What we need you to do

1. Download the [Individual CAA (PDF)](https://github.com/crossbario/crossbar/raw/master/legal/individual_caa.pdf).
2. Fill in the required information that identifies you and sign the CAA.
3. Scan the CAA to PNG, JPG or TIFF, or take a photo of the box on page 2.
4. Email the scan or photo to `contact@crossbario.com` with the subject line "Crossbar.io project contributor assignment agreement"

*If you write contributions as part of your work for a company, you also need to send us an [Entity CAA (PDF)](https://github.com/crossbario/crossbar/raw/master/legal/entity_caa.pdf) signed by somebody responsible in the company.*

**You only need to do this once - all future contributions are covered!**

## Bug Fix Workflow (Test-Driven)

When fixing a bug, follow this test-driven workflow to create a convincing,
reviewable PR that proves both the bug *and* the fix, and guards against
regressions:

### 1. File the issue & agree

- File a GitHub issue describing the bug.
- Discuss and reach agreement: "yes, the current behavior *is* wrong".
- Reference any related issues or user reports.

### 2. Open a PR with a failing test

- Create a feature branch.
- Write a test that **demonstrates the bug** (the test must FAIL).
- Include any audit/fixture files needed.
- Push the PR.

### 3. Prove the bug exists (red)

- Run the tests locally → verify they FAIL.
- Let GitHub Actions run → verify CI FAILS.
- **Leave a PR comment** with your local failure output **and** a link to the
  failing CI run.

### 4. Implement the fix

- Fix the bug.
- Push the fix to the same PR.

### 5. Prove the fix works (green)

- Run the tests locally → verify they PASS.
- Let GitHub Actions run → verify CI PASSES.
- **Leave a PR comment** with your local success output **and** a link to the
  passing CI run.

### 6. Request review

- Comment: "Ready for review & merge!" and ping a maintainer if needed.

### Why this workflow?

It leaves maintainers with a **completely convincing PR**, because:

- there *is* a behavior considered incorrect (the bug);
- the test *proves* the current implementation behaves incorrectly;
- the fix *proves* the new implementation resolves it;
- the test stays in the suite, so we **won't regress** later.

The same red→green discipline applies to features: write the test for the new
behavior first (red), then implement until it passes (green).

### Example PR comments

After step 3 (bug confirmed):

````markdown
## Bug confirmed

Local test run:

```
$ just test
...
FAILED test_foo.py::test_bar - AssertionError: expected X, got Y
```

CI also fails: https://github.com/crossbario/crossbar/actions/runs/<id>
````

After step 5 (fix verified):

````markdown
## Fix verified

Local test run:

```
$ just test
...
PASSED test_foo.py::test_bar
```

CI passes: https://github.com/crossbario/crossbar/actions/runs/<id>

Ready for review & merge!
````

## Development Setup

Crossbar.io uses [`just`](https://github.com/casey/just) to drive development
tasks (run `just` to list all recipes):

```bash
git clone https://github.com/crossbario/crossbar.git
cd crossbar
# create a managed virtualenv and install crossbar + dev/test tooling
just install-dev
```

## Running Tests

```bash
# Run the full test suite
just test

# Run tests for a specific Python (e.g. CPython 3.12, PyPy 3.11)
just test cpy312
just test pypy311
```

Crossbar.io must run on both **CPython** and **PyPy** - run the relevant tests on
both before submitting.

## Code Style

- Follow PEP 8
- Use meaningful variable and function names
- Add docstrings for public APIs
- Keep lines under 100 characters

## License

By contributing to Crossbar.io, you agree that your contributions will be
licensed under the EUPL-1.2 License. See the [LICENSE](LICENSE) file for details.
