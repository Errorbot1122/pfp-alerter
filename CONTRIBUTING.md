# Contributing Guide

Thanks a ton for thinking about contributing to this project! This doc lays out how we keep the code clean, readable, and easy to work with — especially for folks still getting the hang of programming. It isn’t meant to be intimidating, just a way for all of us to stay on the same page and avoid weird surprises later.

---

## Code Style

We mostly follow the [PEP 8 style guide](https://peps.python.org/pep-0008/) for Python code, and to make life easier, we use [Black](https://black.readthedocs.io/en/stable/) to auto-format everything. No debates about whitespace or line breaks — Black handles it for us.

- **Max line length is 88 characters** (for both code and strings)
- **Comments get a 72-character soft limit**

**Why:** Consistent formatting makes reading, diffing, and reviewing code way easier. Plus, with Black doing the heavy lifting, you won’t have to fight with linters.

**Example:**

❌ Bad:
```python
text = "This is a very long string that goes on and on without being split, and that's hard to read."
```

✔ Good:
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

Commits are also follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) Standard. See the following [cheatsheet](https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13)

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

<!-- TODO: Add Images -->
# Contributing for Noobs

This project welcomes absolute beginners! You don’t need to be a coding pro to contribute — reporting bugs, suggesting ideas, or tweaking text as all very useful.

If you don't know anything about contributing using git and github *(or now very little)* this is a mini-tutorial of how to contribute!

## The easiest way... **Issues**
The easiest way to contribute, even if you don't know how to code at all is by creating an [issue](github.com/Errorbot1122/pfp-alerter/issues)! An issue is basically a bug, and feature reporting place all in one area.

Creating an issue is really simple! **All you need to do is:**

 1. Open the `Issues` tab
 2. Hit `Create Issue` button
 3. Create the issue!

**Here are some tips when writing issues:**

 - You can use Markdown <sub>*(`the _cool_ **formatting** sites like [reddit](redit.com) and ![discord logo](https://static.vecteezy.com/system/resources/previews/019/493/250/non_2x/discord-logo-discord-icon-discord-symbol-free-free-vector.jpg) _**use**_`)*</sub> to add formatting to your issue, or feature request. **([Markdown cheat sheet](https://github.com/lifeparticle/Markdown-Cheatsheet)*
 - You can add picture to issues by just dragging them into the text area! ![thumbs up meme](https://content.imageresizer.com/images/memes/Thumbs-up-emoji-meme-4.jpg)
 - If you want to link some code, or maybe an error message,
    ```
    Surround it in a code block!
    ```
 - To write a good issue, first check if any already exist (search bar, remove the `is:open` part and search) then after that, explain your problem in as much detail as possible and follow any templates *(if any)* that show up when creating it.

Issues are basically the easy way out, however, if you want to become a _real_ contributor you want to start making... 

## Pull Requests 😱

Before you start making pull requests, it is required that you learn [Git](https://git-scm.com/). **Here are some helpful resources:**

 - [Git CLI for Noobs](https://www.youtube.com/watch?v=CvUiKWv2-C0)
 - [VS Code](https://code.visualstudio.com/docs/sourcecontrol/intro-to-git)
 - [PyCharm](https://www.jetbrains.com/help/pycharm/set-up-a-git-repository.html#set-passwords-for-git-remotes)


A pull request is basically like a feature request, except you write the code for them. **Pull requests** are the defacto way people actually contribute to open source projects. *(like this one!)*

Lets say you have an idea on a feature, that you think you can make. **Here are the steps for creating a pull request:**

 1. ### Creating a fork
	**A fork** is basically you own copy of a repository *(all the code)*. You got to make a copy as you most-likely aren't allowed to just directly edit a repository without their permission *(thats what maintainers are for)*

	>  [!NOTE]
	> You only need to create a fork once, after that you will instead skip to **Step 2** for new ideas

	To create a fork, open the original Github Repository, Hit the fork option and enter hit create fork *(no need to change any settings)*.
	
	Now all you need to do is locally clone your fork and you can move on to...

	
 2. ### Create the feature branch
	**A branch** is basically kinda like a fork in your own repo, it allows you go off on a tangent and make changes on stuff without worrying about the consequences of your actions. Think of it like a you saving a game, making a copy and like killing an NPC for fun, just to see what happens. If something cool does happen, you can continue that save ignoring your main one *(that is called merging it git, basically adding changes from one branch to another)*

	The branch should be named on what you plan to do with it. For example, if i want to work on a `/shout` command, you could name it `shout-command`. The name should be pretty sort *(1-2 words)*

 3. ### Make some commits
    **Commits** are essentially the "auto-saves that happen in a game. They log any changes you make to the code in between sections. You do have to manually make them.
	
	As a general rule of thumb, your commits should most likely be pretty small *should* consist of fully working code. For example, if you where working on a shout command, you could maybe commit when you get V1 finished. Then maybe you add documentation, and commit after you finish that. <small>*(tbh the shout command wasn't a good example, but you get the idea)*</small>. As stated above, you should use the [Conventional Commits](https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13) naming structure to keep it consistent.

	> [!WARNING]
	> You must push after finishing your feature, otherwise you cannot proceed to the next step.

 4. ### Create the pull request
	Now that you have finished your feature, you must now create a **pull request**.

	To do this, open the original repo in Github, hit the pull request tab and hit, create pull request. Check the top and make sure it says something like:
    ```
    base repository: Errorbot1122/pfp-alerter base: main <- base repository: YOUR_USERNAME/pfp-alerter base: YOUR_BRANCH
    ```

	<small>*(if this is not correct you can change it by hitting the drop down)*</small>
	
	Now write any changes you made in the pull request description, and hit `Create pull request` and wait! Most likely the owner will either accept it, decline it, or give you feedback. **Make sure to follow any feedback if you want your PR to get accepted.**
	
	Now some repos can have checks that run. Checks are basically scripts that get automatically run to check if your code follows the [Style Guide](#contributing-guide). If you get any fails, you can open it and check for any mistakes you made.

<br/>

---
<br/>
	
**Good job for completing your PR!** If your pull request gets accepted and merged, you’ll want to sync your fork to keep it up-to-date before working on your next idea. **Now if you have more ideas, just do it all over again *(skipping to Step 2)*, for all of time. =D**
<sub><sub><sub>`\j 😭`</sub></sub></sub>