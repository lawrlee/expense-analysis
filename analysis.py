import argparse
import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

from data import get_data


def factorplot_category_spending_per_month(df, pdf):
    gb = df.groupby([df.Year, df.Month, df.Category], as_index=False)
    gb_sum = gb.Debit.sum()
    fill_rows = []
    for y in gb_sum['Year'].unique():
        for m in gb_sum[gb_sum['Year'] == y]['Month'].unique():
            for c in gb_sum['Category'].unique():
                if gb_sum.loc[(gb_sum.Year == y) & (gb_sum.Month == m) & (gb_sum.Category == c)].empty:
                    fill_rows.append({'Year': y, 'Month': m, 'Category': c, 'Debit': 0})

    gb_sum = gb_sum.append(pd.DataFrame(fill_rows))

    g = sns.FacetGrid(gb_sum, col="Month", row="Year", size=4)
    g = g.map(plt.bar, "Category", "Debit")
    g.set_xticklabels(rotation=90)
    plt.tight_layout()
    pdf.savefig()
    plt.close()

def categories_per_month(df, pdf):
    all_category_sum = df.groupby([df.Year, df.Month, df.Category])['Debit'].sum()
    for year in all_category_sum.index.levels[0]:
        sums_by_year = all_category_sum.loc[year]
        for month in sums_by_year.index.levels[0]:
            sums_by_year_month = sums_by_year.loc[month]
            sorted_sums = sums_by_year_month.sort_values()
            print(sorted_sums)
            if not sorted_sums.empty:
                plt.figure(figsize=(11, 8.5))
                g = sns.barplot(x=sorted_sums.index, y=sorted_sums)
                g.set_xticklabels(g.get_xticklabels(), rotation=90)
                plt.title('{}/{}'.format(str(month), str(year)))
                plt.tight_layout()
                pdf.attach_note('Costs for {}/{}'.format(str(month), str(year)))
                pdf.savefig()
                plt.close()


def sanitize_df(df):
    category_mappings = {
        'amazon': 'Amazon',
        'safeway': 'Grocery',
        'gobble': 'Gobble',
        'target': 'Target',
        'trupanion': 'Pet Insurance',
        'alpha & omega': 'Wine Club',
        'comcast': 'Cable/Internet',
        'playstation': 'Cable/Internet',
        'in n out': 'Fast Food',
        'in-n-out': 'Fast Food',
        'mcdonald': 'Fast Food',
        'avenues': 'Vet',
        'wholefds': 'Grocery',
        'trader joe': 'Grocery',
        'costco': 'Costco',
        'geico': 'Car Insurance',
        'netflix': 'Cable/Internet',
        'chargepoint': 'Gas',
        'mta ips': 'Parking',
        'parking': 'Parking',
        'fastrak': 'Transportation',
        'lyft': 'Transportation',
        'itunes': 'Subscription',
        'SFMTA CIT': 'Parking Ticket',
        'whistle': 'Kingston',
        'kukje': 'Grocery',
        'lucky': 'Grocery',
        'autopay': 'Payment',
        'payment': 'Payment'
    }

    for cat_string, cat in category_mappings.items():
        df.loc[df.Description.str.contains(cat_string, case=False), 'Category'] = cat

    df.replace('', np.nan, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = [x.year for x in df['Date']]
    df['Month'] = [x.month for x in df['Date']]
    df['Debit'] = pd.to_numeric(df['Debit'])
    df['Credit'] = pd.to_numeric(df['Credit'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--google-sheet-id', help='Google Sheet ID')
    parser.add_argument('-o', '--output_pdf', help='Output PDF path')
    args = parser.parse_args()

    spreadsheet_data = get_data()
    df = pd.DataFrame(spreadsheet_data[1:], columns=spreadsheet_data[0])
    sanitize_df(df) # mutate in place

    with PdfPages(args.output_pdf) as pdf:
        categories_per_month(df, pdf)