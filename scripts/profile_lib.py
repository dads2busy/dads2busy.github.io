import re


def split_authors(s: str) -> list[str]:
    """Split an author string into a list of individual author names.

    Handles three patterns:
      1. 'Last F, Last F'                               (comma-only)
      2. 'Last, First, Last, First, and Last, First'    (pairs + 'and')
      3. 'Last, F. and Last, F. and Last, F.'           ('and'-separated pairs)
    """
    if not s or not s.strip():
        return []

    s = s.strip()

    # Check if ' and ' is present
    if " and " in s:
        # Patterns 2 and 3: split on ' and ' (with optional preceding comma)
        pieces = re.split(r",?\s+and\s+", s)
        result: list[str] = []

        for piece in pieces:
            piece = piece.strip().rstrip(",").strip()
            if not piece:
                continue
            commas = piece.count(",")
            if commas <= 1:
                # Either 'Last F' (0 commas) or 'Last, First' (1 comma).
                result.append(piece)
            else:
                # Pairs of 'Last, First, Last, First, ...'
                parts = [p.strip() for p in piece.split(",") if p.strip()]
                for i in range(0, len(parts), 2):
                    if i + 1 < len(parts):
                        result.append(f"{parts[i]}, {parts[i+1]}")
                    else:
                        result.append(parts[i])

        return result
    else:
        # No ' and ': could be Pattern 1 (comma-separated singles) or Pattern 2 without final ' and '
        parts = [p.strip() for p in s.split(",") if p.strip()]

        if len(parts) == 1:
            # Single author, e.g. "Schroeder, A.D."
            return parts

        # Check if this is Pattern 1: every part matches "Surname Initial(s)" like "Lancaster V" or "Shipp S"
        # Pattern 1 parts have exactly 2 tokens (surname and initial), no commas
        looks_like_pattern1 = all(
            len(p.split()) == 2 and len(p.split()[1]) <= 2
            for p in parts
        )

        if looks_like_pattern1:
            # Pattern 1: all parts are "Surname Initial", return as-is
            return parts
        else:
            # Pattern 2/3 without ' and ': pair consecutive parts as (Last, First)
            result: list[str] = []
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    result.append(f"{parts[i]}, {parts[i+1]}")
                else:
                    result.append(parts[i])
            return result
