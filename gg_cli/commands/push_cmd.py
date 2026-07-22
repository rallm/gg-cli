import argparse
import sys
from gg_cli.commands.base import BaseCommand
from gg_cli.config import ConfigManager
from gg_cli.git_ops import GitOps
from gg_cli.utils import log_info, log_success, log_warning, log_error

class PushCommand(BaseCommand):
    def setup_args(self) -> None:
        # Add an optional positional argument for the remote name, defaulting to "origin"
        self.parser.add_argument("remote", nargs="?", default="origin", help="Name of the remote to push to (default: origin)")

    def _clean_merged_remote_branches(self, config_mgr: ConfigManager, target_remote: str) -> None:
        """
        Identifies and deletes remote branches that have already been 
        merged into develop or main branches on the target remote server.
        """
        log_info(f"Checking for merged remote branches on '{target_remote}' to clean up...")
        
        # Fetch with prune specifically for the target remote
        GitOps.run_command(["fetch", target_remote, "--prune"], check=False)
        
        dev_branch = config_mgr.get("develop_branch") or "develop"
        main_branch = config_mgr.get("main_branch") or "main"
        protected_branches = {main_branch, dev_branch, "master", "HEAD"}

        merged_dev = GitOps.get_merged_remote_branches(dev_branch)
        merged_main = GitOps.get_merged_remote_branches(main_branch)
        
        all_merged = set(merged_dev + merged_main)
        cleaned_count = 0
        
        for remote_branch in all_merged:
            if "->" in remote_branch:
                continue
            
            parts = remote_branch.split("/", 1)
            if len(parts) != 2:
                continue
            
            remote_name, branch_name = parts[0], parts[1]
            
            # Only clean branches belonging to the specific remote we just pushed to
            if remote_name != target_remote:
                continue
            
            if branch_name in protected_branches:
                continue
            
            log_info(f"Removing merged remote branch '{branch_name}' from '{remote_name}'...")
            code, _, stderr = GitOps.run_command(["push", remote_name, "--delete", branch_name], check=False)
            if code == 0:
                log_success(f"Deleted remote branch '{branch_name}'.")
                cleaned_count += 1
            else:
                log_warning(f"Could not delete '{branch_name}': {stderr}")

        if cleaned_count == 0:
            log_info(f"No merged remote branches needed cleanup on '{target_remote}'.")

    def execute(self, args: argparse.Namespace) -> None:
        config_mgr = ConfigManager()
        config = config_mgr.load()
        target_remote = args.remote

        # 1. Validation: Check if any remotes exist and if the requested remote is valid
        code, stdout, _ = GitOps.run_command(["remote"], check=False)
        available_remotes = [r.strip() for r in stdout.splitlines() if r.strip()]

        if not available_remotes:
            log_error("No remotes configured. Add a remote using 'gg edit --remote-add <name> <url>'.")
            sys.exit(1)

        if target_remote not in available_remotes:
            log_error(f"Remote '{target_remote}' not found. Available remotes: {', '.join(available_remotes)}")
            sys.exit(1)

        # 2. Push Confirmation check
        if config.get("push_confirmation", False):
            try:
                ans = input(f"Are you sure you want to push all branches/tags to '{target_remote}' and clean merged branches? [y/N]: ").strip().lower()
                if ans != 'y':
                    log_info("Push operation aborted by user.")
                    return
            except KeyboardInterrupt:
                print()
                sys.exit(1)

        # 3. Execution
        log_info(f"Pushing all local branches to '{target_remote}'...")
        GitOps.run_command(["push", target_remote, "--all"])
        
        log_info(f"Pushing all tags to '{target_remote}'...")
        GitOps.run_command(["push", target_remote, "--tags"])
        
        self._clean_merged_remote_branches(config_mgr, target_remote)
        
        log_success(f"All branches and tags pushed to '{target_remote}', and server cleaned successfully.")