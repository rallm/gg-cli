import argparse
from gg_cli.commands.base import BaseCommand
from gg_cli.config import ConfigManager
from gg_cli.git_ops import GitOps
from gg_cli.utils import log_info, log_success

class InitCommand(BaseCommand):
    def setup_args(self) -> None:
        pass

    def execute(self, args: argparse.Namespace) -> None:
        log_info("Initializing gg-cli for this repository...")
        config_mgr = ConfigManager()
        config_mgr.init_config()

        dev_branch = config_mgr.get("develop_branch")
        current_branch = GitOps.get_current_branch()

        if not GitOps.branch_exists(dev_branch):
            log_info(f"Creating '{dev_branch}' branch from '{current_branch}'...")
            GitOps.run_command(["branch", dev_branch])

        log_info(f"Switching to '{dev_branch}' branch...")
        GitOps.run_command(["checkout", dev_branch])
        log_success("gg-cli initialized successfully.")