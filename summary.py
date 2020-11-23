from numpy import genfromtxt, empty
from matplotlib.pyplot import show, subplots


def main():
    filename = 'resources/summary.csv'
    data = genfromtxt(filename, dtype=None,
                      skip_header=1, delimiter=',',
                      encoding='UTF8')

    categories = {
        'easy': 'Zbiór łatwy',
        'medium': '',
        'hard': ''
    }
    types = {
        'G_CLEF': 'klucz wiolinowy',
        'F_CLEF': 'klucz basowy',
        'WHOLE': 'cała nuta',
        'HALF': 'półnuta',
        'QUARTER': 'ćwierćnuta',
        'EIGHTH': 'ósemka'
    }

    result = {name: {
        subname: {t: 0 for t in types}
        for subname in ['expected', 'detected',
                        'class', 'tone']
    } for name in categories}

    for row in data:
        category = result[row[0]]
        category['expected'][row[1]] += 1
        category['detected'][row[1]] += 1 if row[3] else 0
        category['class'][row[1]] += 1 if row[4] == row[1] else 0
        category['tone'][row[1]] += 1 if row[5] == row[2] else 0

    col_names = ['detekcja[%]', 'klasyfikacja[%]', 'wysokość[%]']
    rows = ['G_CLEF', 'F_CLEF', 'WHOLE', 'HALF', 'QUARTER', 'EIGHTH']
    summarized = {}

    for category in categories:
        # print(category)
        cat_res = result[category]
        values = empty((len(rows), 3), dtype="<U10")
        for i, obj in enumerate(rows):
            if cat_res['expected'][obj] == 0:
                values[i, :] = '-'
                continue
            values[i, 0] = cat_res['detected'][obj] / cat_res['expected'][obj] * 100
            if cat_res['detected'][obj] == 0:
                values[i, 1:] = '-'
                continue
            values[i, 1] = cat_res['class'][obj] / cat_res['detected'][obj] * 100
            values[i, 2] = cat_res['tone'][obj] / cat_res['detected'][obj] * 100
        summarized[category] = values
        # print(values)

    cat_ord = ['easy', 'medium', 'hard']
    fig, axes = subplots(nrows=len(cat_ord))
    for ax, category in zip(axes, cat_ord):
        ax.axis('off')
        ax.set_title(categories[category])
        ax.table(summarized[category],
                 rowLabels=[types[row] for row in rows],
                 colLabels=col_names, loc='center')
    fig.tight_layout()
    show()

    tex_result = ""
    for category in cat_ord:

        tex_figure = \
            "\\begin{figure}" \
            f"{categories[category]}" \
            "\\centering" \
            "\\end{figure}"


if __name__ == '__main__':
    main()
