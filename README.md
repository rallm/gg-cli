# gg-cli: Advanced Modular Git Assistant CLI

**gg-cli** is a robust, highly extensible command-line interface designed to streamline complex Git workflows, enforce a standardized custom Git Flow, manage repository-isolated author profiles, and manipulate commit timestamps seamlessly.

Built with software engineering best practices—including SOLID principles, clean code architecture, and the Command Pattern—this tool is engineered for developers who require precise control over their version control environments without polluting global system configurations.

---

## Key Features

* **Repository-Isolated Profile Management:** Configure unique author and committer identities per repository. Settings are stored securely inside a hidden `.git/gg/config.json` file, ensuring complete isolation from your global Git configuration.
* **Flexible Timestamp Manipulation:** Easily override author and committer dates for individual commits using an intuitive syntax that accepts both hyphens (`-`) and underscores (`_`) as separators (e.g., `2026-07-04_17-32` or `26_07_04-17-32`).
* **Automated Custom Git Flow:** Simplify branching strategies with automated semantic versioning (`0.0.0`). Start and finish features, releases (major/minor bumps), and hotfixes with single commands that handle branching, merging, tagging, and cleanup automatically.
* **Interactive Unborn Repository Handling:** Safely initialize empty repositories with an interactive setup wizard that guides you through profile selection, initial root commit creation (via `--allow-empty`), and development branch setup.
* **Push Confirmation Guard:** Enable optional safety prompts before pushing branches and tags to remote servers to prevent accidental deployments.
* **Extensible & Modular Design:** Every command is decoupled into its own class, making it effortless to add new features or integrate external APIs in the future.

---

## Architecture & Directory Structure

The project follows a modular structure where commands, configuration management, and Git subprocess operations are strictly separated:

```text
gg-cli/
├── pyproject.toml
├── README.md
└── gg_cli/
    ├── __init__.py
    ├── main.py          # CLI entry point and command router
    ├── config.py        # Isolated JSON configuration manager (.git/gg/)
    ├── git_ops.py       # Subprocess wrapper for Git commands
    ├── utils.py         # Helper functions (time parsing, interactive prompts, logging)
    └── commands/
        ├── __init__.py
        ├── base.py      # Abstract base command class (Command Pattern)
        ├── init_cmd.py  # Repository initialization & unborn branch wizard
        ├── info_cmd.py  # Repository status and configuration display
        ├── edit_cmd.py  # Profile, remote, and setting modifications
        ├── commit_cmd.py# Commit execution and timestamp overriding
        ├── push_cmd.py  # Push operations with optional confirmation
        └── flow_cmd.py  # Git Flow management (feature, release, hotfix, finish)
```

---

## Installation

### Prerequisites

* **Python 3.8+**
* **Git** installed and accessible via system PATH.
* Operating System: Linux (Ubuntu/Debian), macOS, or Windows.

### Local Editable Installation (Recommended for Developers)

1. Clone or download the repository to your local machine.
2. Navigate to the root directory containing `pyproject.toml`.
3. Install the package in editable mode using `pip`:

```bash
pip install -e .
```

*Note for Ubuntu/Debian users: If you encounter an environment managed error, use a virtual environment (`venv`) or append `--user` to the installation command:*

```bash
pip install --user -e .
```

Once installed, the `gg` command will be globally accessible in your terminal.

---

## Usage Guide

### 1. Initialization (`gg init`)

Initialize `gg-cli` inside any existing Git repository. If the repository is completely empty (no previous commits), an interactive wizard will launch to configure your profile and create the initial root commit before setting up the `develop` branch.

```bash
git init
gg init
```

### 2. Viewing Repository Information (`gg info`)

Display the current branch, active semantic version, isolated profile details, configured remotes, and push confirmation settings.

```bash
gg info
```

**Example Output:**

```text
--- GG Repository Info ---
Current Branch   : develop
Flow Version     : 0.1.0
Active Profile   : John Doe <john@example.com>
Push Confirm     : True
Remotes          :
  - origin	git@github.com:username/repository.git (fetch)
  - origin	git@github.com:username/repository.git (push)
--------------------------
```

### 3. Configuration & Profile Management (`gg edit`)

Modify repository-specific settings without affecting your global Git profile.

```bash
# Set an isolated author/committer profile for this specific repository
gg edit --profile-name "John Doe" --profile-email "john.doe@example.com"

# Enable push confirmation safeguard
gg edit --push-confirm true

# Add or remove remotes
gg edit --remote-add origin git@github.com:username/repo.git
gg edit --remote-remove origin
```

### 4. Committing with Custom Timestamps (`gg commit` & `gg ac`)

Execute standard commits or combine staging and committing (`git add .` + `git commit`) while dynamically overriding commit timestamps.

```bash
# Commit staged changes with standard system time
gg commit -m "Implement authentication module"

# Stage all changes and commit with a custom historical timestamp
# Supported formats: YYYY-MM-DD_HH-mm or YY-MM-DD_HH-mm (hyphens and underscores are interchangeable)
gg ac -m "Fix critical routing bug" --time 2026-07-04_17-32
gg ac -m "Update documentation" --time 26_07_04-17_32
```

### 5. Custom Git Flow Management

Manage the project lifecycle using standardized branching conventions and automated version bumping.

#### Starting a Feature

Creates a new branch named `feature/<name>` branching off from `develop`.

```bash
gg feature start user-dashboard
```

#### Starting a Release (Major or Minor)

Automatically bumps the version number in the configuration, creates a branch named `release/<new_version>` from `develop`. Use `m` for minor bumps and `M` for major bumps.

```bash
# Minor release bump (e.g., 0.1.0 -> 0.2.0)
gg release start m

# Major release bump (e.g., 0.2.0 -> 1.0.0)
gg release start M
```

#### Starting a Hotfix

Bumps the patch version automatically and creates a branch named `hotfix/<new_version>` branching directly off from `main`.

```bash
# Patch bump (e.g., 1.0.0 -> 1.0.1)
gg hotfix start
```

#### Finishing a Flow Branch (`gg finish`)

Intelligently detects the active flow branch type and executes the necessary merge, tagging, and cleanup operations:

* **Feature Branches:** Merges back into `develop` (no-ff) and deletes the feature branch.
* **Release & Hotfix Branches:** Merges into both `main` and `develop`, tags the commit on `main` with the version number (e.g., `1.0.0`), and deletes the temporary branch.

```bash
gg finish
```

### 6. Pushing Changes (`gg push`)

Push all local branches and tags to the configured remote repositories simultaneously. If push confirmation is enabled, the CLI will prompt for user verification prior to execution.

```bash
gg push
```

---

## Configuration File Specifications

When initialized, `gg-cli` generates a configuration file at `.git/gg/config.json`. Because it resides within the `.git` directory, it is inherently ignored by Git tracking, ensuring your local author overrides and flow states remain private to your local environment.

**Sample `.git/gg/config.json` Structure:**

```json
{
    "profile": {
        "name": "John Doe",
        "email": "john.doe@example.com"
    },
    "push_confirmation": true,
    "version": "1.0.0",
    "main_branch": "main",
    "develop_branch": "develop"
}
```

---

## Extending the CLI

To add a new command to `gg-cli`:

1. Create a new command file inside `gg_cli/commands/` (e.g., `status_cmd.py`).
2. Inherit from `BaseCommand` and implement `setup_args(self)` and `execute(self, args)`.
3. Register the instantiated command in the `commands` dictionary inside `gg_cli/main.py`.

---

## License

This project is open-source and available under the [MIT License](./LICENSE). You are free to modify, distribute, and integrate this tool into your personal or enterprise workflows.