def str_to_number(s: str):
    if s.isdigit():
        return int(s)
    try:
        return float(s)
    except ValueError:
        raise
