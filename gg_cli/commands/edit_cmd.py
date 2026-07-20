import argparse
from gg_cli.commands.base import BaseCommand
from gg_cli.config import ConfigManager
from gg_cli.git_ops import GitOps
from gg_cli.utils import log_success, log_info

class EditCommand(BaseCommand):
    def setup_args(self) -> None:
        self.parser.add_argument("--profile-name", dest="name", help="Set custom author name for this repo")
        self.parser.add_argument("--profile-email", dest="email", help="Set custom author email for this repo")
        self.parser.add_argument("--push-confirm", dest="push_confirm", choices=["true", "false"], help="Enable or disable push confirmation")
        self.parser.add_argument("--remote-add", nargs=2, metavar=("NAME", "URL"), help="Add a new remote")
        self.parser.add_argument("--remote-remove", metavar="NAME", help="Remove an existing remote")

    def execute(self, args: argparse.Namespace) -> None:
        config_mgr = ConfigManager()
        config = config_mgr.load()
        updated = False

        if args.name is not None:
            config["profile"]["name"] = args.name
            log_info(f"Profile name updated to: {args.name}")
            updated = True

        if args.email is not None:
            config["profile"]["email"] = args.email
            log_info(f"Profile email updated to: {args.email}")
            updated = True

        if args.push_confirm is not None:
            val = (args.push_confirm == "true")
            config["push_confirmation"] = val
            log_info(f"Push confirmation set to: {val}")
            updated = True

        if updated:
            config_mgr.save(config)
            log_success("Configuration saved.")

        if args.remote_add:
            name, url = args.remote_add
            GitOps.run_command(["remote", "add", name, url])
            log_success(f"Remote '{name}' added with URL '{url}'.")

        if args.remote_remove:
            GitOps.run_command(["remote", "remove", args.remote_remove])
            log_success(f"Remote '{args.remote_remove}' removed.")