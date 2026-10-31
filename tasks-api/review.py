# the review list: decides how urgent it is to practice each problem again.
# only the last attempt at a problem counts. No database code here, so the
# formula can be tested with plain objects.
from datetime import datetime

from models import Attempt, Problem

# time adds at most 15 points, so it lifts a problem one group at most
# (the groups below are 10 points apart)
MAX_TIME_POINTS = 15


# points for how the last attempt went: higher = more urgent
def outcome_points(solved: bool, confidence: int) -> int:
    if solved and confidence <= 2:
        return 40  # solved, but you don't really know it yet
    if not solved:
        return 30
    if confidence == 3:
        return 20
    return 10  # solved with confidence 4 or 5: you know it well


# score = how it went + 1 point per day since, up to the maximum
def urgency_score(solved: bool, confidence: int, days: int) -> int:
    return outcome_points(solved, confidence) + min(days, MAX_TIME_POINTS)


# builds the ordered list. attempts must come oldest first,
# so the last one saved for each problem is its most recent attempt
def build_review_list(
    problems: list[Problem], attempts: list[Attempt], now: datetime
) -> list[dict]:
    last_attempt = {}
    for attempt in attempts:
        last_attempt[attempt.problem_id] = attempt

    attempted = []
    not_attempted = []
    for problem in problems:
        attempt = last_attempt.get(problem.id)
        if attempt is None:
            not_attempted.append(
                {
                    "problem": problem,
                    "score": None,
                    "last_attempt_at": None,
                }
            )
            continue
        # .days = whole days, so an attempt from earlier today counts as 0
        days = (now - attempt.created_at).days
        attempted.append(
            {
                "problem": problem,
                "score": urgency_score(attempt.solved, attempt.confidence, days),
                "last_attempt_at": attempt.created_at,
            }
        )

    # highest score first; on a tie, the older last attempt comes first
    attempted.sort(key=lambda item: (-item["score"], item["last_attempt_at"]))
    # problems with no attempts go at the bottom, in the order they were added
    not_attempted.sort(key=lambda item: item["problem"].id)
    return attempted + not_attempted
