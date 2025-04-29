# Contributing Guide

Thanks a ton for thinking about contributing to this project! This doc lays out how we keep the code clean, readable, and easy to work with — especially for folks still getting the hang of programming. It isn’t meant to be intimidating, just a way for all of us to stay on the same page and avoid weird surprises later.

---

## Code Style

We mostly follow the [PEP 8 style guide](https://peps.python.org/pep-0008/) for Python code, and to make life easier, we use [Black](https://black.readthedocs.io/en/stable/) to auto-format everything. No debates about whitespace or line breaks — Black handles it for us.

- **Max line length is 88 characters** (for both code and strings)
- **Comments get a 72-character soft limit**

**Why:** Consistent formatting makes reading, diffing, and reviewing code way easier. Plus, with Black doing the heavy lifting, you won’t have to fight with linters.

**Example:**

Bad:
```python
text = "This is a very long string that goes on and on without being split, and that's hard to read."
```

Good:
```python
text = (
    "This is a very long string that goes on and on without being split, and that's "
    + "hard to read."
)
```

---

### Multiline Strings

Triple-quoted multiline strings (`"""like this"""`) are fine, but use them *only* if your string naturally has more than **3 lines**. Since they can’t be wrapped cleanly to fit the 88-character limit, they're better suited for docstrings or big blocks of text.

**Why:** Keeps the code tidy and avoids awkward, unreadable blobs of text.

---

## Imports

Imports should be grouped and ordered like this:

1. **Python Standard Library modules**
2. **Local modules (other Python files in this project)**
3. **Third-party packages (installed via pip)**

Within each group:

- Use `from ... import ...` statements **before** regular `import` statements
- Sort alphabetically

**Why:** Keeps the top of each file clean and easy to scan. You can instantly tell what’s built-in, what’s local, and what’s from external libraries.

**Example:**

```python
from os import path
from time import sleep

from . import helpers
from .config import SETTINGS

from aiohttp import ClientSession
import discord
```

Want to nerd out a bit? Here’s [PEP 8’s section on imports](https://peps.python.org/pep-0008/#imports).

---

## Type Hints and Docstrings

Every function should have type hints for its parameters and return type. Even the super simple ones.

**Why:**  
It makes your code easier to read, your editor smarter (with autocomplete and error catching), and helps avoid silly bugs.

On top of that, every function should have a **NumPy-style docstring** explaining what it does, what parameters it takes, what it returns, and any exceptions it might raise.

**Example:**

```python
def add_numbers(x: int, y: int) -> int:
    """Add two numbers together.

    Parameters
    ----------
    x : int
        The first number.
    y : int
        The second number.

    Returns
    -------
    int
        The sum of `x` and `y`.
    """
    return x + y
```

If you’ve never worked with type hints before, [this is a good intro](https://realpython.com/python-type-checking/).

---

## Constants and Naming

- **Constants** → `MACRO_CASE`
- **Everything else** → `snake_case`

Also: keep constants up at the top of their scope. Either at the top of the file, or at the top of the function they live in.

**Why:** It makes important values easier to spot, tweak, and reuse without scrolling through a whole file.

---

## Git Workflow

We use a slightly tweaked version of [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow).

- Main branches (`main`, `stable`, etc.) are always deployable and clean.
- Releases are made from those branches.
- No random experimental code should land in them directly.

**Why:**  
Keeps our main codebases stable and makes it easier to track what’s live, what’s in progress, and what’s safe to test.

---

## AI-Assisted Contributions

Yes, you can use AI tools (like ChatGPT, Copilot, etc.) to help with your code. But here’s the deal:

- If your contribution is **more than 25% AI-generated**, we won’t accept it.
- Always double-check and clean up anything AI gives you before committing it.

**Why:**  
While AI can be a helpful sidekick, code should ultimately reflect human judgment. It needs to be maintainable, clear, and something contributors actually understand.

## Technical Spec Document ([`TECHNICAL_SPEC.md`](TECHNICAL_SPEC.md))

This project uses a [`TECHNICAL_SPEC.md`](TECHNICAL_SPEC.md) file — basically a high-level overview of how everything works under the hood. You can think of it like a running explanation of the system’s structure, major moving parts, and how they fit together. It’s kind of like pseudocode, but more detailed and meant to be read by humans first.

**What it’s for:**  
The spec gives contributors a quick way to understand how the project is built without having to trace through the entire codebase. It covers what the different pieces do, how they connect, and why certain things were done a specific way. It's also a good place to track any weird edge cases or decisions we should remember later.

**What goes in it:**  

- Descriptions of the main parts of the project and what they handle  
- Diagrams or images (as the project grows) to show how data moves around or how stuff’s organized  
- Explanations for important decisions or design choices  
- Pseudocode-style outlines for any big processes or tricky logic  
- Notes on stuff we plan to build or clean up later  

**Why bother?**  
Because having this kind of doc makes life easier for everyone. It helps new contributors get up to speed faster, keeps us on the same page, and saves future-you from having to remember why you did something weird six months ago.

**Keeping it up to date:**  
Whenever you make a big change or add a new feature, take a minute to update the spec. If you’re not sure how to explain something or whether it’s worth adding — just ask in the pull request or drop a note in the file. It doesn’t have to be perfect, it just has to be clear.

If you’re curious about how people write good tech specs, this post’s a nice intro:  
- [Diátaxis Framework — Explanation guide](https://diataxis.fr/explanation/)