import re
import sys
import random
from datetime import datetime
from typing import Optional

def parse_commit_time(time_str: Optional[str]) -> Optional[str]:
    """
    Parses custom time strings like '2026-07-04_17-32' or '*-07-29_*-11-30'.
    Treats both '-' and '_' as equal separators.
    Supports '*' to use the current system value for that specific component.
    If seconds are omitted, generates a random second between 0 and 59.
    Returns standard Git date format: 'YYYY-MM-DD HH:MM:SS'.
    """
    if not time_str or not time_str.strip():
        return None

    tokens = re.split(r'[-_]', time_str.strip())
    if len(tokens) not in (5, 6):
        log_error("Invalid time format. Expected YYYY-MM-DD_HH-mm or YYYY-MM-DD_HH-mm-ss")
        sys.exit(1)

    now = datetime.now()

    def resolve_token(val: str, current_val: int) -> int:
        if val == '*':
            return current_val
        return int(val)

    try:
        year_str = tokens[0]
        if year_str == '*':
            year = now.year
        else:
            if len(year_str) == 2:
                year_str = "20" + year_str
            elif len(year_str) != 4:
                log_error("Year must be 2 or 4 digits.")
                sys.exit(1)
            year = int(year_str)

        month = resolve_token(tokens[1], now.month)
        day = resolve_token(tokens[2], now.day)
        hour = resolve_token(tokens[3], now.hour)
        minute = resolve_token(tokens[4], now.minute)

        if len(tokens) == 6:
            second = resolve_token(tokens[5], now.second)
        else:
            second = random.randint(0, 59)

        dt = datetime(year, month, day, hour, minute, second)
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