#!/usr/bin/env python3
"""
GitHub Word Art Pattern Generator

This script takes a word (e.g., "SARIF") and renders it on your contribution
graph with three shades:
   - Background: 1 commit per day (light green)
   - Border around the word: 5 commits per day (medium green)
   - The word itself: 10 commits per day (dark green)

The pattern is placed on the last few weeks of your graph.
"""

import subprocess
import datetime
import os
import sys
from typing import List, Dict, Optional, Tuple

# ----- Simple 5x7 bitmap font (uppercase letters & digits) -----
# Each character is a list of 7 strings (rows), each string of length 5.
FONT: Dict[str, List[str]] = {
    'A': [
        "01110",
        "10001",
        "10001",
        "11111",
        "10001",
        "10001",
        "10001"
    ],
    'B': [
        "11110",
        "10001",
        "10001",
        "11110",
        "10001",
        "10001",
        "11110"
    ],
    'C': [
        "01111",
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "01111"
    ],
    'D': [
        "11110",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "11110"
    ],
    'E': [
        "11111",
        "10000",
        "10000",
        "11110",
        "10000",
        "10000",
        "11111"
    ],
    'F': [
        "11111",
        "10000",
        "10000",
        "11110",
        "10000",
        "10000",
        "10000"
    ],
    'G': [
        "01111",
        "10000",
        "10000",
        "10111",
        "10001",
        "10001",
        "01111"
    ],
    'H': [
        "10001",
        "10001",
        "10001",
        "11111",
        "10001",
        "10001",
        "10001"
    ],
    'I': [
        "11111",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
        "11111"
    ],
    'J': [
        "00111",
        "00010",
        "00010",
        "00010",
        "00010",
        "10010",
        "01100"
    ],
    'K': [
        "10001",
        "10010",
        "10100",
        "11000",
        "10100",
        "10010",
        "10001"
    ],
    'L': [
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "11111"
    ],
    'M': [
        "10001",
        "11011",
        "10101",
        "10001",
        "10001",
        "10001",
        "10001"
    ],
    'N': [
        "10001",
        "11001",
        "10101",
        "10011",
        "10001",
        "10001",
        "10001"
    ],
    'O': [
        "01110",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01110"
    ],
    'P': [
        "11110",
        "10001",
        "10001",
        "11110",
        "10000",
        "10000",
        "10000"
    ],
    'Q': [
        "01110",
        "10001",
        "10001",
        "10001",
        "10101",
        "10010",
        "01101"
    ],
    'R': [
        "11110",
        "10001",
        "10001",
        "11110",
        "10100",
        "10010",
        "10001"
    ],
    'S': [
        "01111",
        "10000",
        "10000",
        "01110",
        "00001",
        "00001",
        "11110"
    ],
    'T': [
        "11111",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100"
    ],
    'U': [
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01110"
    ],
    'V': [
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01010",
        "00100"
    ],
    'W': [
        "10001",
        "10001",
        "10001",
        "10101",
        "10101",
        "11011",
        "10001"
    ],
    'X': [
        "10001",
        "10001",
        "01010",
        "00100",
        "01010",
        "10001",
        "10001"
    ],
    'Y': [
        "10001",
        "10001",
        "01010",
        "00100",
        "00100",
        "00100",
        "00100"
    ],
    'Z': [
        "11111",
        "00001",
        "00010",
        "00100",
        "01000",
        "10000",
        "11111"
    ],
    '0': [
        "01110",
        "10001",
        "10011",
        "10101",
        "11001",
        "10001",
        "01110"
    ],
    '1': [
        "00100",
        "01100",
        "00100",
        "00100",
        "00100",
        "00100",
        "01110"
    ],
    '2': [
        "01110",
        "10001",
        "00001",
        "00010",
        "00100",
        "01000",
        "11111"
    ],
    '3': [
        "01110",
        "10001",
        "00001",
        "00110",
        "00001",
        "10001",
        "01110"
    ],
    '4': [
        "00010",
        "00110",
        "01010",
        "10010",
        "11111",
        "00010",
        "00010"
    ],
    '5': [
        "11111",
        "10000",
        "11110",
        "00001",
        "00001",
        "10001",
        "01110"
    ],
    '6': [
        "00111",
        "01000",
        "10000",
        "11110",
        "10001",
        "10001",
        "01110"
    ],
    '7': [
        "11111",
        "00001",
        "00010",
        "00100",
        "01000",
        "01000",
        "01000"
    ],
    '8': [
        "01110",
        "10001",
        "10001",
        "01110",
        "10001",
        "10001",
        "01110"
    ],
    '9': [
        "01110",
        "10001",
        "10001",
        "01111",
        "00001",
        "00010",
        "11100"
    ],
    ' ': [  # space
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
        "00000"
    ],
}

# ----- Helper functions (same as before) -----
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


def create_commits_for_date(date: datetime.date, count: int, file_name: str = "commit_log.txt") -> None:
    if count <= 0:
        return
    for i in range(count):
        with open(file_name, 'a') as f:
            f.write(f"Pattern commit {i+1} on {date}\n")
        run_git_command(["git", "add", file_name])
        date_str = date.strftime("%Y-%m-%dT12:00:00")
        msg = f"Pattern commit {i+1} for {date}"
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = date_str
        env["GIT_COMMITTER_DATE"] = date_str
        cmd = ["git", "commit", "-m", msg]
        subprocess.run(cmd, env=env, check=True, capture_output=True)


def commit_count_for_level(level: int) -> int:
    mapping = {0: 0, 1: 1, 2: 5, 3: 10, 4: 20}
    return mapping.get(level, 0)


def draw_pattern(start_sunday: datetime.date, pattern_lines: List[str]) -> None:
    """Generate commits according to the pattern matrix."""
    # Convert pattern to schedule
    cols = len(pattern_lines[0])
    schedule = []
    for week_offset in range(cols):
        week_date = start_sunday + datetime.timedelta(days=7 * week_offset)
        for day_offset in range(7):
            level = int(pattern_lines[day_offset][week_offset])
            if level > 0:
                date = week_date + datetime.timedelta(days=day_offset)
                schedule.append((date, level))
    print(f"Generating commits for {len(schedule)} cells with commits...")
    for date, level in schedule:
        count = commit_count_for_level(level)
        print(f"  {date}: level {level} -> {count} commits")
        create_commits_for_date(date, count)
    print("Pattern commits created.")


# ----- Word rendering with border -----
def render_word_with_border(word: str) -> List[str]:
    """
    Render the word into a 7-row pattern, add a 1-cell border around the
    entire word, and set background (outside border) to level 1 (1 commit).
    The border will be level 2, and the word's filled pixels will be level 3.
    """
    # 1. Build the word bitmap (concatenate character columns)
    char_width = 5
    gap = 1  # one empty column between letters
    word_columns = []
    for ch in word.upper():
        if ch not in FONT:
            ch = ' '  # fallback to space
        char_rows = FONT[ch]
        for row_idx in range(7):
            # add a gap column after each character except last? We'll add gap after each char.
            # We'll build column by column: for each row, we add the char's row + a gap column
            pass
    # Easier: build row strings.
    rows = [""] * 7
    for ch in word.upper():
        if ch not in FONT:
            ch = ' '
        char_rows = FONT[ch]
        for r in range(7):
            rows[r] += char_rows[r]
        # Add gap column (space) after each character except maybe last? We'll add a gap after each char.
        for r in range(7):
            rows[r] += "0"  # gap column (0 = no word pixel)
    # Remove the trailing gap from the last character (optional)
    # Actually we want a gap between letters, but after last we don't need it.
    # We'll trim the last column if it's a gap.
    # For simplicity, we'll keep it, but we can remove the last gap column.
    # Let's remove the extra gap at the end.
    for r in range(7):
        rows[r] = rows[r][:-1]  # remove last column (gap)

    # Now rows contain the word with 1-column gaps between letters.
    # 2. Add a border around the entire word.
    # We'll add one row of zeros at top and bottom, and one column of zeros at left and right.
    # But we want the border to be level 2 (green). The border will be a 1-cell thick outline.
    # We'll create a new matrix with extra rows and columns.
    word_height = 7
    word_width = len(rows[0])
    new_height = word_height + 2  # top and bottom border
    new_width = word_width + 2    # left and right border
    # Initialize with background level 1
    pattern = [[1 for _ in range(new_width)] for _ in range(new_height)]
    # Set border to level 2 (only perimeter)
    for r in range(new_height):
        for c in range(new_width):
            if r == 0 or r == new_height-1 or c == 0 or c == new_width-1:
                pattern[r][c] = 2
    # Now place the word inside (offset by 1 row, 1 col)
    for r in range(word_height):
        for c in range(word_width):
            if rows[r][c] == '1':
                pattern[r+1][c+1] = 3  # word = dark green

    # Convert to list of strings
    pattern_lines = [''.join(str(val) for val in row) for row in pattern]
    return pattern_lines


# ----- Main -----
def main():
    if not is_git_repo():
        print("Error: Not a Git repository.")
        sys.exit(1)

    print("GitHub Word Art Pattern Generator")
    print("==================================")
    word = input("Enter a word (uppercase letters, digits, spaces): ").strip().upper()
    if not word:
        print("No word entered. Exiting.")
        sys.exit(1)
    # Only allow characters we have in font
    for ch in word:
        if ch not in FONT and ch != ' ':
            print(f"Character '{ch}' is not supported. Use A-Z, 0-9, space.")
            sys.exit(1)

    # Render the word with border
    pattern_lines = render_word_with_border(word)

    # Determine the start Sunday so that the pattern appears at the rightmost side of the graph.
    today = datetime.date.today()
    # Find the most recent Sunday
    days_until_sunday = (today.weekday() + 1) % 7
    last_sunday = today - datetime.timedelta(days=days_until_sunday)
    cols = len(pattern_lines[0])
    start_sunday = last_sunday - datetime.timedelta(days=7 * (cols - 1))

    print(f"\nPattern width: {cols} weeks")
    print(f"Placing pattern from {start_sunday} to {last_sunday}")
    print("Level mapping: 1=background (1 commit), 2=border (5 commits), 3=word (10 commits)")
    print("Pattern preview (0 is background, 2 is border, 3 is word):")
    for line in pattern_lines:
        print(line)

    confirm = input("Proceed to create commits? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

    draw_pattern(start_sunday, pattern_lines)

    print("\nAll commits are in your local repository.")
    print("Push them to remote with:")
    print("  git push origin <your-branch>")


if __name__ == "__main__":
    main()