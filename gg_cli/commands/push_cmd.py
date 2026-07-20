import argparse
import sys
from gg_cli.commands.base import BaseCommand
from gg_cli.config import ConfigManager
from gg_cli.git_ops import GitOps
from gg_cli.utils import log_info, log_success, log_warning

class PushCommand(BaseCommand):
    def setup_args(self) -> None:
        pass

    def _clean_merged_remote_branches(self, config_mgr: ConfigManager) -> None:
        """
        Identifies and deletes remote branches that have already been 
        merged into develop or main branches on the remote server.
        """
        log_info("Checking for merged remote branches to clean up...")
        
        GitOps.run_command(["fetch", "--prune"], check=False)
        
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
            log_info("No merged remote branches needed cleanup.")

    def execute(self, args: argparse.Namespace) -> None:
        config_mgr = ConfigManager()
        config = config_mgr.load()

        if config.get("push_confirmation", False):
            try:
                ans = input("Are you sure you want to push all branches/tags and clean merged remote branches? [y/N]: ").strip().lower()
                if ans != 'y':
                    log_info("Push operation aborted by user.")
                    return
            except KeyboardInterrupt:
                print()
                sys.exit(1)

        log_info("Pushing all local branches...")
        GitOps.run_command(["push", "--all"])
        
        log_info("Pushing all tags...")
        GitOps.run_command(["push", "--tags"])
        
        self._clean_merged_remote_branches(config_mgr)
        
        log_success("All branches and tags pushed, and remote server cleaned successfully.")