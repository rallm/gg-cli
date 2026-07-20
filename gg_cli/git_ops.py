import subprocess
import sys
import os
from typing import List, Optional, Tuple

class GitOps:
    @staticmethod
    def run_command(args: List[str], env: Optional[dict] = None, check: bool = True) -> Tuple[int, str, str]:
        custom_env = os.environ.copy()
        if env:
            custom_env.update(env)

        try:
            process = subprocess.Popen(
                ["git"] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=custom_env
            )
            stdout, stderr = process.communicate()
            if check and process.returncode != 0:
                print(f"[GIT ERROR] {stderr.strip()}", file=sys.stderr)
                sys.exit(process.returncode)
            return process.returncode, stdout.strip(), stderr.strip()
        except FileNotFoundError:
            print("[ERROR] Git is not installed or not in system PATH.", file=sys.stderr)
            sys.exit(1)

    @classmethod
    def is_git_repo(cls) -> bool:
        code, _, _ = cls.run_command(["rev-parse", "--is-inside-work-tree"], check=False)
        return code == 0

    @classmethod
    def get_repo_root(cls) -> str:
        _, stdout, _ = cls.run_command(["rev-parse", "--show-toplevel"])
        return stdout

    @classmethod
    def get_current_branch(cls) -> str:
        _, stdout, _ = cls.run_command(["branch", "--show-current"])
        return stdout

    @classmethod
    def branch_exists(cls, branch_name: str) -> bool:
        code, _, _ = cls.run_command(["show-ref", "--verify", f"refs/heads/{branch_name}"], check=False)
        return code == 0

    @classmethod
    def get_remotes(cls) -> List[str]:
        _, stdout, _ = cls.run_command(["remote", "-v"], check=False)
        return stdout.splitlines() if stdout else []