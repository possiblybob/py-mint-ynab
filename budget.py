''' Converts CSV files from Mint to YNAB format for budgeting '''
import csv
import sys

YNAB_COLUMNS = [
	'Date',
	'Payee',
	'Category',
	'Memo',
	'Outflow',
	'Inflow',
]
MINT_COLUMNS = [
	'date',
	'description',
	'original_description',
	'amount',
	'transaction_type',
	'category',
	'account',
	'label',
	'notes',
]
CATEGORY_MAPPINGS = {
	'Amusement': 'Entertainment: General',
	'Auto Insurance': 'Auto: Insurance',
	'Baby Supplies': 'Kids: Baby Supplies',
	'Babysitter & Daycare': 'Kids: Daycare',
	'Business Travel': 'Business: Travel',
	'Charlotte': 'Shopping: Charlotte',
	'Chris': 'Shopping: Chris',
	'Church Tithe': 'Gifts: Church Tithe',
	'Clothing': 'Shopping: Clothing',
	'Dana': 'Shopping: Dana',
	'Dentist': 'Health: Doctor',
	'Doctor': 'Health: Doctor',
	'Gas & Fuel': 'Auto: Gas / Fuel',
	'Gift': 'Gifts: Presents',
	'Groceries': 'Food: Groceries',
	'Gym': 'Health: Gym',
	'Home Decor': 'Home: Decor',
	'Home Improvement': 'Home: Home Improvement',
	'Home Services': 'Home: Maintenance',
	'Home Supplies': 'Home: Home Supplies',
	'Interest Income': 'Income: Available next month',
	'Internet/Cable': 'Bills: Internet',
	'Missions': 'Gifts: Missions',
	'Mobile Phone': 'Bills: Mobile Phone',
	'Mortgage & Rent': 'Home: Mortgage',
	'Movies & DVDs': 'Entertainment: Videos',
	'Paycheck': 'Income: Available next month',
	'Personal Care': 'Personal Care: General',
	'Pet Food & Supplies': 'Pets: Food / Supplies',
	'Pet Grooming': 'Pets: Food / Supplies',
	'Pharmacy': 'Health: Pharmacy',
	'Random Giving': 'Gifts: Random',
	'Restaurants': 'Food: Restaurants',
	'Service & Parts': 'Auto: Service / Parts',
	'Travel': 'Savings Goals: Vacation',
	'Utilities': 'Bills: Utilities',
	'Vacation': 'Savings Goals: Vacation'
}
EXCLUDED_CATEGORIES = [
	'Credit Card Payment',
	'Exclude from Mint',
]

def get_ynab_category(mint_category):
	''' Gets the mapped YNAB category for the Mint category '''
	try:
		category = CATEGORY_MAPPINGS[mint_category]
	except (ValueError, IndexError, KeyError):
		category = ''
	return category

def convert_row(row):
	''' Converts an individual row '''
	record = {
		'Date': row['date'],
		'Payee': row['description'],
		'Category': get_ynab_category(row['category']),
		'Memo': row['category'],
	}
	
	# determine inflow/outflow
	if row['transaction_type'].lower() == 'debit':
		record['Outflow'] = row['amount']
	else:
		record['Inflow'] = row['amount']

	return record
	
def convert(file_name):
	''' Converts from one CSV format to another '''
	# load Mint CSV
	input_file = None
	ynab_records = []
	with open(file_name, 'r', newline='') as csv_file:
		try:
			input_file = csv.DictReader(csv_file, fieldnames=MINT_COLUMNS)
			skipped_header = False
			# convert Mint transactions
			for row in input_file:
				if skipped_header and row['category'] not in EXCLUDED_CATEGORIES:
					ynab_records.append(convert_row(row))
				else:
					skipped_header = True
		except ValueError:
			pass

	# write out YNAB transactions
	with open('ynab.csv', 'w', newline='') as ynab_file:
		csvwriter = csv.DictWriter(ynab_file, delimiter=',', fieldnames=YNAB_COLUMNS)
		csvwriter.writerow(dict((fn, fn) for fn in YNAB_COLUMNS))
		for record in ynab_records:
			 csvwriter.writerow(record)

if __name__ == "__main__":
	convert(sys.argv[1])