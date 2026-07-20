import argparse
import sys
from gg_cli.commands.init_cmd import InitCommand
from gg_cli.commands.info_cmd import InfoCommand
from gg_cli.commands.edit_cmd import EditCommand
from gg_cli.commands.commit_cmd import CommitCommand
from gg_cli.commands.push_cmd import PushCommand
from gg_cli.commands.flow_cmd import FeatureCommand, ReleaseCommand, HotfixCommand, FinishCommand

def cli_entry():
    parser = argparse.ArgumentParser(
        prog="gg",
        description="Advanced Git Assistant CLI with modular Git Flow and Profile Management"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Instantiate each command class exactly once.
    # The __init__ method of BaseCommand will automatically trigger setup_args() for each subparser.
    commands = {
        "init": InitCommand(subparsers.add_parser("init", help="Initialize gg in repository")),
        "info": InfoCommand(subparsers.add_parser("info", help="Show repository information")),
        "edit": EditCommand(subparsers.add_parser("edit", help="Edit profiles, remotes, and settings")),
        "commit": CommitCommand(subparsers.add_parser("commit", help="Commit changes"), auto_add=False),
        "ac": CommitCommand(subparsers.add_parser("ac", help="Add all and commit changes"), auto_add=True),
        "push": PushCommand(subparsers.add_parser("push", help="Push all branches and tags")),
        "feature": FeatureCommand(subparsers.add_parser("feature", help="Manage feature branches")),
        "release": ReleaseCommand(subparsers.add_parser("release", help="Manage release branches")),
        "hotfix": HotfixCommand(subparsers.add_parser("hotfix", help="Manage hotfix branches")),
        "finish": FinishCommand(subparsers.add_parser("finish", help="Finish current flow branch"))
    }

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Execute the triggered command directly from our initialized instances
    commands[args.command].execute(args)

if __name__ == "__main__":
    cli_entry()