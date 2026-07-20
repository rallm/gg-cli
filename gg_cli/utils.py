import re
import sys
from datetime import datetime
from typing import Optional

def parse_commit_time(time_str: Optional[str]) -> Optional[str]:
    """
    Parses custom time strings like '2026-07-04_17-32' or '26-07-04_17-32'.
    Treats both '-' and '_' as equal separators.
    Returns standard Git date format: 'YYYY-MM-DD HH:MM:SS'.
    """
    if not time_str or not time_str.strip():
        return None

    tokens = re.split(r'[-_]', time_str.strip())
    if len(tokens) != 5:
        log_error("Invalid time format. Expected YYYY-MM-DD_HH-mm or YY-MM-DD_HH-mm")
        sys.exit(1)

    year, month, day, hour, minute = tokens

    if len(year) == 2:
        year = "20" + year
    elif len(year) != 4:
        log_error("Year must be 2 or 4 digits.")
        sys.exit(1)

    try:
        dt = datetime(int(year), int(month), int(day), int(hour), int(minute))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        log_error(f"Invalid date/time values: {e}")
        sys.exit(1)

def get_interactive_input(prompt_text: str, default_value: str = "") -> str:
    """
    Prompts user for input. If user presses Enter without typing,
    returns the provided default_value.
    """
    try:
        display_prompt = f"{prompt_text} [{default_value}]: " if default_value else f"{prompt_text}: "
        user_input = input(display_prompt).strip()
        return user_input if user_input else default_value
    except KeyboardInterrupt:
        print()
        log_error("Operation cancelled by user.")
        sys.exit(1)

def log_info(msg: str) -> None:
    print(f"[INFO] {msg}")

def log_success(msg: str) -> None:
    print(f"[SUCCESS] {msg}")

def log_warning(msg: str) -> None:
    print(f"[WARNING] {msg}")

def log_error(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)