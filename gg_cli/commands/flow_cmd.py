import argparse
import sys
from gg_cli.commands.base import BaseCommand
from gg_cli.config import ConfigManager
from gg_cli.git_ops import GitOps
from gg_cli.utils import log_info, log_success, log_error, parse_commit_time

class FlowCommand(BaseCommand):
    def setup_args(self) -> None:
        subparsers = self.parser.add_subparsers(dest="flow_action", required=True)
        feat_parser = subparsers.add_parser("start", help="Start a feature, release, or hotfix")
        feat_parser.add_argument("name_or_type", help="Feature name or version bump type (m/M)")

    def execute(self, args: argparse.Namespace) -> None:
        pass

class FeatureCommand(BaseCommand):
    def setup_args(self) -> None:
        subparsers = self.parser.add_subparsers(dest="action", required=True)
        start_p = subparsers.add_parser("start")
        start_p.add_argument("name", help="Name of the feature")

    def execute(self, args: argparse.Namespace) -> None:
        if args.action == "start":
            config_mgr = ConfigManager()
            dev_branch = config_mgr.get("develop_branch")
            branch_name = f"feature/{args.name}"
            log_info(f"Creating and checking out '{branch_name}' from '{dev_branch}'...")
            GitOps.run_command(["checkout", "-b", branch_name, dev_branch])
            log_success(f"Started feature '{args.name}'.")

class ReleaseCommand(BaseCommand):
    def setup_args(self) -> None:
        subparsers = self.parser.add_subparsers(dest="action", required=True)
        start_p = subparsers.add_parser("start")
        start_p.add_argument("bump", choices=["m", "M"], help="m for minor, M for major")

    def execute(self, args: argparse.Namespace) -> None:
        if args.action == "start":
            config_mgr = ConfigManager()
            ver = config_mgr.get("version") or "0.0.0"
            parts = [int(x) for x in ver.split(".")]
            if len(parts) != 3:
                parts = [0, 0, 0]

            if args.bump == "M":
                parts[0] += 1
                parts[1] = 0
                parts[2] = 0
            elif args.bump == "m":
                parts[1] += 1
                parts[2] = 0

            new_ver = f"{parts[0]}.{parts[1]}.{parts[2]}"
            config_mgr.update("version", new_ver)

            dev_branch = config_mgr.get("develop_branch")
            branch_name = f"release/{new_ver}"
            log_info(f"Creating release branch '{branch_name}' from '{dev_branch}'...")
            GitOps.run_command(["checkout", "-b", branch_name, dev_branch])
            log_success(f"Started release '{new_ver}'.")

class HotfixCommand(BaseCommand):
    def setup_args(self) -> None:
        subparsers = self.parser.add_subparsers(dest="action", required=True)
        subparsers.add_parser("start")

    def execute(self, args: argparse.Namespace) -> None:
        if args.action == "start":
            config_mgr = ConfigManager()
            ver = config_mgr.get("version") or "0.0.0"
            parts = [int(x) for x in ver.split(".")]
            if len(parts) != 3:
                parts = [0, 0, 0]

            parts[2] += 1
            new_ver = f"{parts[0]}.{parts[1]}.{parts[2]}"
            config_mgr.update("version", new_ver)

            main_branch = config_mgr.get("main_branch")
            branch_name = f"hotfix/{new_ver}"
            log_info(f"Creating hotfix branch '{branch_name}' from '{main_branch}'...")
            GitOps.run_command(["checkout", "-b", branch_name, main_branch])
            log_success(f"Started hotfix '{new_ver}'.")


class FinishCommand(BaseCommand):
    def setup_args(self) -> None:
        self.parser.add_argument("--time", required=False, help="Custom timestamp (e.g. *-07-04_*-32 or 2026-07-04_17-32-45)")

    def _get_profile_env(self, config_mgr: ConfigManager, formatted_time: str = None) -> dict:
        """
        Retrieves the isolated author/committer profile from config
        and injects custom timestamps to generate commits or tags.
        """
        config = config_mgr.load()
        env_override = {}
        prof_name = config.get("profile", {}).get("name")
        prof_email = config.get("profile", {}).get("email")

        if prof_name and prof_email:
            env_override["GIT_AUTHOR_NAME"] = prof_name
            env_override["GIT_AUTHOR_EMAIL"] = prof_email
            env_override["GIT_COMMITTER_NAME"] = prof_name
            env_override["GIT_COMMITTER_EMAIL"] = prof_email

        if formatted_time:
            env_override["GIT_AUTHOR_DATE"] = formatted_time
            env_override["GIT_COMMITTER_DATE"] = formatted_time

        return env_override

    def execute(self, args: argparse.Namespace) -> None:
        current_branch = GitOps.get_current_branch()
        config_mgr = ConfigManager()
        dev_branch = config_mgr.get("develop_branch")
        main_branch = config_mgr.get("main_branch")
        
        formatted_time = parse_commit_time(args.time)
        env_override = self._get_profile_env(config_mgr, formatted_time)

        if formatted_time:
            log_info(f"Applying custom timestamp for finish operations: {formatted_time}")

        if current_branch.startswith("feature/"):
            log_info(f"Finishing feature branch '{current_branch}'...")
            GitOps.run_command(["checkout", dev_branch])
            GitOps.run_command(["merge", "--no-ff", current_branch], env=env_override)
            GitOps.run_command(["branch", "-d", current_branch])
            log_success(f"Feature merged into '{dev_branch}' and cleaned up.")

        elif current_branch.startswith("release/") or current_branch.startswith("hotfix/"):
            ver = current_branch.split("/")[-1]
            log_info(f"Finishing branch '{current_branch}' for version '{ver}'...")

            log_info(f"Merging into '{main_branch}'...")
            GitOps.run_command(["checkout", main_branch])
            GitOps.run_command(["merge", "--no-ff", current_branch], env=env_override)

            log_info(f"Tagging release '{ver}'...")
            GitOps.run_command(["tag", "-a", ver, "-m", f"Release {ver}"], env=env_override)

            log_info(f"Merging into '{dev_branch}'...")
            GitOps.run_command(["checkout", dev_branch])
            GitOps.run_command(["merge", "--no-ff", current_branch], env=env_override)

            GitOps.run_command(["branch", "-d", current_branch])
            log_success(f"Version '{ver}' released, tagged, and merged successfully.")
        else:
            log_error("Current branch is not a feature, release, or hotfix branch.")
            sys.exit(1)