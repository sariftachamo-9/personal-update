#!/usr/bin/env python3
"""
GitHub Contribution Graph Filler – Three Modes with Progress, Auto‑Push & Even Zero‑Day Distribution

Modes:
  1 – Word Art: draw a word with a green border on the rightmost weeks.
  2 – Random commits: each day gets a random number (min–max) of commits,
      with some days set to 0 commits per month (spread or random).
  3 – Uniform fill: every day gets exactly 1 commit (light green).
"""

import subprocess
import datetime
import os
import sys
import random
from typing import List, Dict, Optional, Set

# ----- 5x7 bitmap font (uppercase, digits, space) -----
FONT: Dict[str, List[str]] = {
    'A': ["01110","10001","10001","11111","10001","10001","10001"],
    'B': ["11110","10001","10001","11110","10001","10001","11110"],
    'C': ["01111","10000","10000","10000","10000","10000","01111"],
    'D': ["11110","10001","10001","10001","10001","10001","11110"],
    'E': ["11111","10000","10000","11110","10000","10000","11111"],
    'F': ["11111","10000","10000","11110","10000","10000","10000"],
    'G': ["01111","10000","10000","10111","10001","10001","01111"],
    'H': ["10001","10001","10001","11111","10001","10001","10001"],
    'I': ["11111","00100","00100","00100","00100","00100","11111"],
    'J': ["00111","00010","00010","00010","00010","10010","01100"],
    'K': ["10001","10010","10100","11000","10100","10010","10001"],
    'L': ["10000","10000","10000","10000","10000","10000","11111"],
    'M': ["10001","11011","10101","10001","10001","10001","10001"],
    'N': ["10001","11001","10101","10011","10001","10001","10001"],
    'O': ["01110","10001","10001","10001","10001","10001","01110"],
    'P': ["11110","10001","10001","11110","10000","10000","10000"],
    'Q': ["01110","10001","10001","10001","10101","10010","01101"],
    'R': ["11110","10001","10001","11110","10100","10010","10001"],
    'S': ["01111","10000","10000","01110","00001","00001","11110"],
    'T': ["11111","00100","00100","00100","00100","00100","00100"],
    'U': ["10001","10001","10001","10001","10001","10001","01110"],
    'V': ["10001","10001","10001","10001","10001","01010","00100"],
    'W': ["10001","10001","10001","10101","10101","11011","10001"],
    'X': ["10001","10001","01010","00100","01010","10001","10001"],
    'Y': ["10001","10001","01010","00100","00100","00100","00100"],
    'Z': ["11111","00001","00010","00100","01000","10000","11111"],
    '0': ["01110","10001","10011","10101","11001","10001","01110"],
    '1': ["00100","01100","00100","00100","00100","00100","01110"],
    '2': ["01110","10001","00001","00010","00100","01000","11111"],
    '3': ["01110","10001","00001","00110","00001","10001","01110"],
    '4': ["00010","00110","01010","10010","11111","00010","00010"],
    '5': ["11111","10000","11110","00001","00001","10001","01110"],
    '6': ["00111","01000","10000","11110","10001","10001","01110"],
    '7': ["11111","00001","00010","00100","01000","01000","01000"],
    '8': ["01110","10001","10001","01110","10001","10001","01110"],
    '9': ["01110","10001","10001","01111","00001","00010","11100"],
    ' ': ["00000","00000","00000","00000","00000","00000","00000"],
}

def run_git_command(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Git error: {' '.join(cmd)}")
        print(e.stderr)
        sys.exit(1)

def is_git_repo() -> bool:
    result = run_git_command(["git", "rev-parse", "--git-dir"], check=False)
    return result.returncode == 0

def get_git_email() -> str:
    result = run_git_command(["git", "config", "user.email"], check=False)
    if result.returncode == 0:
        return result.stdout.strip()
    return ""

def create_commits_for_date(date: datetime.date, count: int, file_name: str = "commit_log.txt") -> None:
    if count <= 0:
        return
    for i in range(count):
        with open(file_name, 'a') as f:
            f.write(f"Commit {i+1} on {date}\n")
        run_git_command(["git", "add", file_name])
        date_str = date.strftime("%Y-%m-%dT12:00:00")
        msg = f"Commit {i+1} for {date}"
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = date_str
        env["GIT_COMMITTER_DATE"] = date_str
        cmd = ["git", "commit", "-m", msg]
        subprocess.run(cmd, env=env, check=True, capture_output=True)

def commit_count_for_level(level: int) -> int:
    mapping = {0: 0, 1: 1, 2: 5, 3: 10, 4: 20}
    return mapping.get(level, 0)

def render_word_with_border(word: str) -> List[str]:
    rows = [""] * 7
    for ch in word.upper():
        if ch not in FONT:
            ch = ' '
        char_rows = FONT[ch]
        for r in range(7):
            rows[r] += char_rows[r]
        for r in range(7):
            rows[r] += "0"
    for r in range(7):
        rows[r] = rows[r][:-1]

    word_height, word_width = 7, len(rows[0])
    new_height, new_width = word_height + 2, word_width + 2
    pattern = [[1 for _ in range(new_width)] for _ in range(new_height)]
    for r in range(new_height):
        for c in range(new_width):
            if r == 0 or r == new_height-1 or c == 0 or c == new_width-1:
                pattern[r][c] = 2
    for r in range(word_height):
        for c in range(word_width):
            if rows[r][c] == '1':
                pattern[r+1][c+1] = 3
    return [''.join(str(val) for val in row) for row in pattern]

def get_date_input(prompt: str, default: Optional[datetime.date] = None) -> datetime.date:
    while True:
        user_input = input(prompt).strip()
        if not user_input and default is not None:
            return default
        try:
            return datetime.datetime.strptime(user_input, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD.")

def get_int_input(prompt: str, default: int, min_val: int = 0) -> int:
    while True:
        user_input = input(f"{prompt} (default {default}): ").strip()
        if not user_input:
            return default
        try:
            val = int(user_input)
            if val < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            return val
        except ValueError:
            print("Invalid integer.")

def get_bool_input(prompt: str, default: bool = True) -> bool:
    while True:
        user_input = input(f"{prompt} (y/n, default {'y' if default else 'n'}): ").strip().lower()
        if not user_input:
            return default
        if user_input in ('y','yes'):
            return True
        if user_input in ('n','no'):
            return False
        print("Please enter y or n.")

def choose_mode() -> int:
    print("\nChoose a mode:")
    print("  1 – Word Art (draw a word with border)")
    print("  2 – Random commits per day (set min/max, and optionally some days with 0)")
    print("  3 – Uniform 1 commit per day (light green)")
    while True:
        choice = input("Enter 1, 2, or 3: ").strip()
        if choice in ('1','2','3'):
            return int(choice)
        print("Invalid choice.")

def get_zero_days_per_month() -> int:
    return get_int_input("Number of days per month with 0 commits", default=0, min_val=0)

def generate_zero_days_for_month(year: int, month: int, zero_count: int, spread: bool = True) -> Set[datetime.date]:
    """Return a set of dates in the given month that should have 0 commits."""
    if zero_count <= 0:
        return set()
    if month == 12:
        next_month = datetime.date(year+1, 1, 1)
    else:
        next_month = datetime.date(year, month+1, 1)
    first_day = datetime.date(year, month, 1)
    last_day = next_month - datetime.timedelta(days=1)
    total_days = (last_day - first_day).days + 1
    zero_count = min(zero_count, total_days)
    if spread:
        # Evenly spread the zero days across the month
        if zero_count == total_days:
            # All days zero
            return set([first_day + datetime.timedelta(days=i) for i in range(total_days)])
        # We want zero_count days as evenly spaced as possible
        # Choose indices that divide the month into (zero_count+1) roughly equal intervals
        indices = []
        for i in range(1, zero_count+1):
            idx = int(i * (total_days + 1) / (zero_count + 1)) - 1
            idx = max(0, min(total_days-1, idx))
            indices.append(idx)
        # Ensure unique indices (if duplicates, shift)
        # Simple fix: make them unique by checking
        unique_indices = []
        for idx in indices:
            if idx not in unique_indices:
                unique_indices.append(idx)
        # If duplicates, fill remaining with random unique indices
        while len(unique_indices) < zero_count:
            new_idx = random.randint(0, total_days-1)
            if new_idx not in unique_indices:
                unique_indices.append(new_idx)
        return set([first_day + datetime.timedelta(days=i) for i in unique_indices])
    else:
        # Random selection
        all_days = [first_day + datetime.timedelta(days=i) for i in range(total_days)]
        chosen = random.sample(all_days, zero_count)
        return set(chosen)

def push_commits(branch: str = "main") -> bool:
    print(f"Pushing to remote origin {branch}...")
    cmd = ["git", "push", "origin", branch]
    try:
        subprocess.run(cmd, check=True, capture_output=False)
        print("Push successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Push failed: {e}")
        return False

def main():
    if not is_git_repo():
        print("Error: Not a Git repository.")
        sys.exit(1)

    # Check Git email
    email = get_git_email()
    if email:
        print(f"Current Git user.email: {email}")
        print("Make sure this email is verified on GitHub (Settings → Emails).")
    else:
        print("Warning: Git user.email not set. Please set it with:")
        print("  git config --global user.email 'your-email@example.com'")
        sys.exit(1)

    print("GitHub Contribution Graph Filler")
    print("=================================")

    mode = choose_mode()

    today = datetime.date.today()
    default_start = today - datetime.timedelta(days=364)
    default_end = today

    start_date = get_date_input(f"Enter start date (YYYY-MM-DD) [default {default_start}]: ", default=default_start)
    end_date = get_date_input(f"Enter end date (YYYY-MM-DD) [default {default_end}]: ", default=default_end)

    if start_date > end_date:
        print("Start date must be before end date. Swapping.")
        start_date, end_date = end_date, start_date

    days = (end_date - start_date).days + 1
    if days > 365:
        print(f"Warning: You requested {days} days. GitHub only shows the last 365 days.")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Aborted.")
            sys.exit(0)

    pattern_lines = None
    pattern_cols = 0
    start_sunday = None
    last_sunday = None
    min_commits = max_commits = 0
    zero_days_per_month = 0
    spread_zero_days = True

    if mode == 1:
        # Word Art mode
        word = input("Enter a word (uppercase letters, digits, spaces): ").strip().upper()
        if not word:
            print("No word entered. Exiting.")
            sys.exit(1)
        for ch in word:
            if ch not in FONT and ch != ' ':
                print(f"Character '{ch}' not supported. Use A-Z, 0-9, space.")
                sys.exit(1)
        pattern_lines = render_word_with_border(word)
        pattern_cols = len(pattern_lines[0])
        print(f"\nPattern preview (1=background, 2=border, 3=word):")
        for line in pattern_lines:
            print(line)
        print(f"Pattern width: {pattern_cols} weeks")

        days_until_sunday = (end_date.weekday() + 1) % 7
        last_sunday = end_date - datetime.timedelta(days=days_until_sunday)
        start_sunday = last_sunday - datetime.timedelta(days=7 * (pattern_cols - 1))
        if start_sunday < start_date:
            shift = (start_date - start_sunday).days // 7 + 1
            start_sunday += datetime.timedelta(days=7 * shift)
            if start_sunday + datetime.timedelta(days=7*(pattern_cols-1)) > end_date:
                print("Error: Pattern too wide for the given date range.")
                sys.exit(1)

    elif mode == 2:
        # Random commits mode
        min_commits = get_int_input("Minimum commits per day", default=5, min_val=0)
        max_commits = get_int_input("Maximum commits per day", default=20, min_val=min_commits if min_commits > 0 else 1)
        zero_days_per_month = get_zero_days_per_month()
        if zero_days_per_month > 0:
            spread_zero_days = get_bool_input("Spread zero days evenly across the month?", default=True)
        print(f"Each day will get a random number between {min_commits} and {max_commits} commits.")
        if zero_days_per_month > 0:
            if spread_zero_days:
                print(f"Additionally, {zero_days_per_month} days per month (spread evenly) will have 0 commits.")
            else:
                print(f"Additionally, {zero_days_per_month} random days per month will have 0 commits.")

    else:
        # Mode 3: uniform 1 commit per day – nothing extra to set
        pass

    print(f"\nGenerating commits from {start_date} to {end_date} ({days} days).")
    if mode == 1:
        print(f"Pattern placed from {start_sunday} to {last_sunday}.")
    confirm = input("Proceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Aborted.")
        sys.exit(0)

    # Generate commits for each day with progress printing
    current_date = start_date
    total_days = 0
    total_commits = 0

    current_month = None
    zero_days_for_month = set()

    while current_date <= end_date:
        if mode == 1:
            level = 1
            if current_date >= start_sunday and current_date <= last_sunday:
                week_offset = (current_date - start_sunday).days // 7
                day_offset = (current_date - start_sunday).days % 7
                if week_offset < pattern_cols and day_offset < 7:
                    level = int(pattern_lines[day_offset][week_offset])
            count = commit_count_for_level(level)
        elif mode == 2:
            if (current_date.year, current_date.month) != current_month:
                current_month = (current_date.year, current_date.month)
                zero_days_for_month = generate_zero_days_for_month(current_date.year, current_date.month, zero_days_per_month, spread_zero_days)
            if current_date in zero_days_for_month:
                count = 0
            else:
                count = random.randint(min_commits, max_commits)
        else:
            count = 1

        if count > 0:
            create_commits_for_date(current_date, count)
            total_days += 1
            total_commits += count
            print(f"  {current_date}: {count} commits (total so far: {total_commits})")
        else:
            print(f"  {current_date}: 0 commits (skipped)")
        current_date += datetime.timedelta(days=1)

    print(f"\nDone! Generated commits for {total_days} days, total {total_commits} commits.")
    print("All commits are in your local repository.")

    push_now = input("Do you want to push these commits now? (y/n): ").strip().lower()
    if push_now == 'y':
        branch = input("Enter branch name (default main): ").strip() or "main"
        if push_commits(branch):
            print("✅ Your contribution graph will update in a few minutes.")
        else:
            print("Push failed. You can push manually with:")
            print(f"  git push origin {branch}")
    else:
        print("Push manually with:")
        print("  git push origin <your-branch>")

if __name__ == "__main__":
    main()