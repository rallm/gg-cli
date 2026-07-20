import argparse
import sys
from gg_cli.commands.base import BaseCommand
from gg_cli.config import ConfigManager
from gg_cli.git_ops import GitOps
from gg_cli.utils import log_info, log_success

class PushCommand(BaseCommand):
    def setup_args(self) -> None:
        pass

    def execute(self, args: argparse.Namespace) -> None:
        config_mgr = ConfigManager()
        config = config_mgr.load()

        if config.get("push_confirmation", False):
            try:
                ans = input("Are you sure you want to push all branches and tags? [y/N]: ").strip().lower()
                if ans != 'y':
                    log_info("Push operation aborted by user.")
                    return
            except KeyboardInterrupt:
                print()
                sys.exit(1)

        log_info("Pushing all branches...")
        GitOps.run_command(["push", "--all"])
        log_info("Pushing all tags...")
        GitOps.run_command(["push", "--tags"])
        log_success("All branches and tags pushed successfully.")