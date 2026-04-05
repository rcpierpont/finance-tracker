


def get_sum(rows):
    total = 0
    for row in rows:
        total += row['Amount']
    return total

def select_by_category(rows, category):
    selected = []
    for row in rows:
        if row['Category'].lower() == category.lower():
            selected.append(row)
    return selected


def strip_outside_quotes(text):
    result = []
    in_quotes = False
    for char in text:
        if char == '"':
            in_quotes = not in_quotes
        if not in_quotes and char == " ":
            continue
        result.append(char)
    return "".join(result)