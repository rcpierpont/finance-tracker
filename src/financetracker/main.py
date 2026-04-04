import click
from financetracker.sheetsapi import FinanceSheet
from financetracker.core import get_sum,select_by_category
from financetracker.files import load_config
from datetime import datetime as dt
import calendar
import re

iso_date = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
sheet_name = 'test'

# TODO: make app flow more like go pokedex:
#   - sheet loaded on start and written to json
#   - calculations are done by pulling data from json
#   - when session ends, any net new rows are appended to sheet using api
# TODO: add command to save common expenses as shortcuts, for example "ft save subway --desc subway --amount 3.00 --category transportation"
# TODO: add command to add new rows from saved shortcuts, for example "ft sc subway 2" would execute "ft add subway 3.00 transportation <current-date>" twice
# TODO: add command balance, which calculates a total and subtracts from monthly income


@click.group()
def cli():
    pass

@cli.command()
@click.argument('month')
@click.option('-c', '--category', 'cat')
def total(month, cat = None):
    gs = FinanceSheet(sheet_name)
    total = 0
    selected = []
    for row in gs.get_data():
        row_cat = row['Category']
        
        month_int = int(str(row['Date']).split('-')[1])
        month_name = calendar.month_name[month_int].lower()
        month_abbr = calendar.month_abbr[month_int].lower()
        
        if month.lower() in [month_name, month_abbr] and row_cat.lower() == cat.lower(): 
            selected.append(row)
    
    total = get_sum(selected)
    out_str = ''
    if cat is not None:
        out_str = f"total for {month} in category {cat}: {total}"
    else:
        out_str = f"total for {month}: {total}"
    click.echo(out_str)


@cli.command()
@click.argument('desc')
@click.argument('amount')
@click.argument('cat')
@click.option('--now/--not-now', default=True)
def add(desc, amount, cat, now):
    gs = FinanceSheet(sheet_name)
    """
    desc = input('Enter description: ')
    amount = input('Enter amount: ')
    cat = input('Enter category: ')
    date = input('Enter date: ')
    """
    if now:
        date = dt.now().date().strftime("%Y-%m-%d")
    else:
        while True:
            date = input('Enter date: ')
            if re.fullmatch(iso_date, date):
                break
            print('Date format invalid, please re-enter using YYYY-mm-dd.')


    gs.add_row([desc, amount, cat, date])

def main():
    cli()

if __name__ == '__main__':
    main()