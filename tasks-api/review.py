# the review queue: which problems need practice most. Pure functions
# (no database, no HTTP), so they're easy to test and explain.
#
# urgency comes from a problem's most recent attempt:
#   +50 if it wasn't solved
#   +10 for each confidence point below 5 (confidence 2 -> 3 x 10 = 30)
#   +1 per day since the attempt, at most 30

MAX_DAY_POINTS = 30


def urgency(solved: bool, confidence: int, days: int) -> int:
    score = 0 if solved else 50
    score += (5 - confidence) * 10
    score += min(days, MAX_DAY_POINTS)
    return score


# rows: one per problem, with its last attempt's solved, confidence and days.
# returns the "limit" most urgent problems: highest score first, and on a
# tie the smaller id first
def build_queue(rows: list[dict], limit: int) -> list[dict]:
    queue = [
        {
            "problem": {
                "id": row["id"],
                "title": row["title"],
                "platform": row["platform"],
                "topic": row["topic"],
                "difficulty": row["difficulty"],
            },
            "score": urgency(row["solved"], row["confidence"], row["days"]),
        }
        for row in rows
    ]
    # -score puts the highest score first; id breaks ties (smaller first).
    # sorted is O(n log n); see "Review queue" in the README for why
    queue = sorted(queue, key=lambda item: (-item["score"], item["problem"]["id"]))
    return queue[:limit]
