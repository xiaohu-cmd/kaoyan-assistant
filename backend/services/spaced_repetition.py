"""
Ebbinghaus spaced repetition algorithm.

Review intervals (days): 1, 3, 7, 15, 30, 90

On each review:
  feedback = "forgot"     -> reset to interval level 0 (1 day)
  feedback = "blurry"     -> stay at current level
  feedback = "remembered" -> advance to next level (capped at max level)
"""

from datetime import date, datetime, timedelta
from typing import Optional, Tuple

INTERVALS: list[int] = [1, 3, 7, 15, 30, 90]
MAX_LEVEL: int = len(INTERVALS) - 1


def get_next_review_date(
    feedback: str,
    current_level: int,
    current_next_review_date: Optional[str] = None
) -> Tuple[str, int]:
    """
    Calculate the next review date and level based on user feedback.

    Args:
        feedback: One of "forgot", "blurry", "remembered"
        current_level: Current index into INTERVALS (0 to MAX_LEVEL)
        current_next_review_date: Ignored; computed relative to today

    Returns:
        Tuple of (next_review_date as ISO string YYYY-MM-DD, new_level as int)
    """
    if current_level < 0:
        current_level = 0
    if current_level > MAX_LEVEL:
        current_level = MAX_LEVEL

    # Normalize feedback values (frontend may send different names)
    fb = feedback.lower()
    if fb in ("forgot",):
        new_level = 0
    elif fb in ("blurry", "hard"):
        new_level = max(0, current_level)
    elif fb in ("remembered", "good"):
        new_level = min(current_level + 1, MAX_LEVEL)
    else:
        raise ValueError(
            f"Invalid feedback: {feedback}. Must be 'forgot'/'blurry'/'hard'/'remembered'/'good'."
        )

    interval_days = INTERVALS[new_level]
    next_date = date.today() + timedelta(days=interval_days)
    return (next_date.isoformat(), new_level)


def get_due_items_query(table_name: str) -> str:
    """
    Build a parameterized query to fetch items due for review from a given table.
    Each table must have a 'next_review_date' column (TEXT, ISO format or NULL).

    Args:
        table_name: Name of the table to query (must have next_review_date column)

    Returns:
        SQL query string with one ? placeholder for today's date
    """
    allowed_tables = {"vocab_words", "flashcards", "notes_and_errors", "tasks"}
    if table_name not in allowed_tables:
        raise ValueError(
            f"Table '{table_name}' does not support spaced repetition."
        )
    return f"""
        SELECT * FROM {table_name}
        WHERE next_review_date IS NOT NULL
          AND date(next_review_date) <= date(?)
        ORDER BY next_review_date ASC
    """


def get_current_level_from_next_review(next_review_date: Optional[str]) -> int:
    """
    Estimate the current level from an existing next_review_date.
    Used when loading an item that already has a review date set.
    Returns the closest matching INTERVALS index, defaulting to 0.
    """
    if not next_review_date:
        return 0
    try:
        target = datetime.strptime(next_review_date, "%Y-%m-%d").date()
        diff = (target - date.today()).days
        if diff <= 0:
            return 0
        for i, interval in enumerate(INTERVALS):
            if diff <= interval:
                return i
        return MAX_LEVEL
    except (ValueError, TypeError):
        return 0
