import argparse
from gg_cli.commands.base import BaseCommand
from gg_cli.config import ConfigManager
from gg_cli.git_ops import GitOps
from gg_cli.utils import log_info, log_success, log_warning, get_interactive_input, parse_commit_time

class InitCommand(BaseCommand):
    def setup_args(self) -> None:
        pass

    def execute(self, args: argparse.Namespace) -> None:
        log_info("Initializing gg-cli for this repository...")
        config_mgr = ConfigManager()
        config_mgr.init_config()
        config = config_mgr.load()

        # Check if the repository has no commits yet (Unborn Branch state)
        if GitOps.is_empty_repo():
            log_warning("No previous commits detected. Interactive initial setup required.")
            print("--- Initial Profile Setup ---")
            
            # 1. Profile Setup
            sys_name = GitOps.get_global_config("user.name") or "System Default"
            sys_email = GitOps.get_global_config("user.email") or "system@default.local"
            
            use_custom_profile = get_interactive_input(
                f"Use custom profile for this repo? (y/n) [System: {sys_name} <{sys_email}>]", 
                "n"
            ).lower()

            if use_custom_profile.startswith('y'):
                custom_name = get_interactive_input("Enter author name for this repo", sys_name if sys_name != "System Default" else "")
                custom_email = get_interactive_input("Enter author email for this repo", sys_email if sys_email != "system@default.local" else "")
                
                config["profile"]["name"] = custom_name
                config["profile"]["email"] = custom_email
                config_mgr.save(config)
                log_info(f"Custom profile saved: {custom_name} <{custom_email}>")
            else:
                log_info("Using default system profile.")

            # 2. Time Setup
            print("--- Initial Commit Time Setup ---")
            custom_time_str = get_interactive_input(
                "Enter custom time for initial commit (YYYY-MM-DD_HH-mm or YY-MM-DD_HH-mm) or leave empty for current system time", 
                ""
            )
            
            formatted_time = parse_commit_time(custom_time_str) if custom_time_str else None

            # 3. Create Initial Root Commit
            log_info("Creating initial root commit to initialize Git object database...")
            env_override = {}
            
            prof_name = config["profile"].get("name")
            prof_email = config["profile"].get("email")
            if prof_name and prof_email:
                env_override["GIT_AUTHOR_NAME"] = prof_name
                env_override["GIT_AUTHOR_EMAIL"] = prof_email
                env_override["GIT_COMMITTER_NAME"] = prof_name
                env_override["GIT_COMMITTER_EMAIL"] = prof_email

            if formatted_time:
                env_override["GIT_AUTHOR_DATE"] = formatted_time
                env_override["GIT_COMMITTER_DATE"] = formatted_time
                log_info(f"Applying custom timestamp: {formatted_time}")

            # Using --allow-empty so we don't need to force-create dummy files like README
            GitOps.run_command(
                ["commit", "--allow-empty", "-m", "Initial commit via gg-cli"], 
                env=env_override
            )
            log_success("Initial root commit created.")

        # Proceed with standard Git Flow initialization
        dev_branch = config["develop_branch"]
        current_branch = GitOps.get_current_branch()

        # If we are on master/main or any branch other than develop, ensure develop exists
        if not GitOps.branch_exists(dev_branch):
            log_info(f"Creating '{dev_branch}' branch from '{current_branch}'...")
            GitOps.run_command(["branch", dev_branch])

        log_info(f"Switching to '{dev_branch}' branch...")
        GitOps.run_command(["checkout", dev_branch])
        log_success("gg-cli initialized successfully.")