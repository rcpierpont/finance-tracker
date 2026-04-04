


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

