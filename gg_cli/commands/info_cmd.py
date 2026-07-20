import argparse
from gg_cli.commands.base import BaseCommand
from gg_cli.config import ConfigManager
from gg_cli.git_ops import GitOps

class InfoCommand(BaseCommand):
    def setup_args(self) -> None:
        pass

    def execute(self, args: argparse.Namespace) -> None:
        config_mgr = ConfigManager()
        config = config_mgr.load()

        branch = GitOps.get_current_branch()
        remotes = GitOps.get_remotes()
        
        prof_name = config["profile"].get("name") or "Default (Git Global/Local)"
        prof_email = config["profile"].get("email") or "Default (Git Global/Local)"

        print("--- GG Repository Info ---")
        print(f"Current Branch   : {branch}")
        print(f"Flow Version     : {config.get('version', '0.0.0')}")
        print(f"Active Profile   : {prof_name} <{prof_email}>")
        print(f"Push Confirm     : {config.get('push_confirmation', False)}")
        print("Remotes          :")
        if remotes:
            for r in set(remotes):
                print(f"  - {r}")
        else:
            print("  No remotes configured.")
        print("--------------------------")