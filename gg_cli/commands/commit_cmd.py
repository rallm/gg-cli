import argparse
from gg_cli.commands.base import BaseCommand
from gg_cli.config import ConfigManager
from gg_cli.git_ops import GitOps
from gg_cli.utils import parse_commit_time, log_success, log_info

class CommitCommand(BaseCommand):
    def __init__(self, parser: argparse.ArgumentParser, auto_add: bool = False):
        self.auto_add = auto_add
        super().__init__(parser)

    def setup_args(self) -> None:
        self.parser.add_argument("-m", "--message", required=True, help="Commit message")
        self.parser.add_argument("--time", required=False, help="Custom timestamp (e.g. 2026-07-04_17-32)")

    def execute(self, args: argparse.Namespace) -> None:
        config_mgr = ConfigManager()
        config = config_mgr.load()

        if self.auto_add:
            log_info("Staging all changes (git add .)...")
            GitOps.run_command(["add", "."])

        env_override = {}
        prof_name = config["profile"].get("name")
        prof_email = config["profile"].get("email")

        if prof_name and prof_email:
            env_override["GIT_AUTHOR_NAME"] = prof_name
            env_override["GIT_AUTHOR_EMAIL"] = prof_email
            env_override["GIT_COMMITTER_NAME"] = prof_name
            env_override["GIT_COMMITTER_EMAIL"] = prof_email
            log_info(f"Committing as: {prof_name} <{prof_email}>")

        formatted_time = parse_commit_time(args.time)
        if formatted_time:
            env_override["GIT_AUTHOR_DATE"] = formatted_time
            env_override["GIT_COMMITTER_DATE"] = formatted_time
            log_info(f"Committing with custom date: {formatted_time}")

        GitOps.run_command(["commit", "-m", args.message], env=env_override)
        log_success("Commit executed successfully.")