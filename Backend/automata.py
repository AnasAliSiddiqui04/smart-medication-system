# automata.py - DFA LOGIC (No changes needed)
VALID_SYMBOLS = {"M", "E", "T", "X"}

def validate_pattern(pattern: str) -> bool:
    """DFA-based validation"""
    if not pattern:
        return False

    for char in pattern.upper():
        if char not in VALID_SYMBOLS:
            return False
    return True

def pattern_meaning(pattern: str):
    meaning = []
    for char in pattern.upper():
        if char == "M":
            meaning.append("Morning")
        elif char == "E":
            meaning.append("Evening")
        elif char == "T":
            meaning.append("Twice Daily")
        elif char == "X":
            meaning.append("Skip")
    return meaning