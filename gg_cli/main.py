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

    commands_map = {
        "init": (InitCommand, subparsers.add_parser("init", help="Initialize gg in repository")),
        "info": (InfoCommand, subparsers.add_parser("info", help="Show repository information")),
        "edit": (EditCommand, subparsers.add_parser("edit", help="Edit profiles, remotes, and settings")),
        "commit": (lambda p: CommitCommand(p, auto_add=False), subparsers.add_parser("commit", help="Commit changes")),
        "ac": (lambda p: CommitCommand(p, auto_add=True), subparsers.add_parser("ac", help="Add all and commit changes")),
        "push": (PushCommand, subparsers.add_parser("push", help="Push all branches and tags")),
        "feature": (FeatureCommand, subparsers.add_parser("feature", help="Manage feature branches")),
        "release": (ReleaseCommand, subparsers.add_parser("release", help="Manage release branches")),
        "hotfix": (HotfixCommand, subparsers.add_parser("hotfix", help="Manage hotfix branches")),
        "finish": (FinishCommand, subparsers.add_parser("finish", help="Finish current flow branch"))
    }

    for cmd_name, (cmd_class, cmd_parser) in commands_map.items():
        cmd_class(cmd_parser)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    cmd_class, _ = commands_map[args.command]
    if callable(cmd_class) and not isinstance(cmd_class, type):
        cmd_instance = cmd_class(subparsers.choices[args.command])
    else:
        cmd_instance = cmd_class(subparsers.choices[args.command])

    cmd_instance.execute(args)

if __name__ == "__main__":
    cli_entry()