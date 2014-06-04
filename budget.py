''' Converts CSV files from Mint to YNAB format for budgeting '''
import argparse
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

def load_mappings(mappings_file):
	'''Loads Mint->YNAB mappings from external file'''
	with open(mappings_file) as f:
		content = f.readlines()
	mappings = {}
	for line in content:
		key, value = line.split('->')
		key, value = key.strip(), value.strip()
		if key:
			mappings[key] = value
	return mappings

def load_excluded_categories(excludes_file=None):
	'''Loads Mint categories to skip when processing'''
	if excludes_file is None:
		return []
	with open(excludes_file) as f:
		content = f.readlines()
	content = [line.strip() for line in content]
	return content

def load_mint_transactions(transactions_file):
	'''Loads transactions from Mint-formatted CSV file or gives instructions for getting them'''
	transactions = []
	with open(transactions_file, 'r', newline='') as csv_file:
		try:
			input_file = csv.DictReader(csv_file, fieldnames=MINT_COLUMNS)
			# skip header row
			next(input_file)
			transactions = [row for row in input_file]
		except ValueError:
			pass
	return transactions

def find_missing_mappings(transactions, category_mappings, excluded_categories):
	'''makes list of missing category mappings for transactions'''
	missing = set()
	for row in transactions:
		category = row['category']
		if category not in category_mappings.keys() and category not in excluded_categories:
			missing.add(category)
	return missing

def get_ynab_category(mint_category, mappings):
	''' Gets the mapped YNAB category for the Mint category '''
	try:
		category = mappings[mint_category]
	except (ValueError, IndexError, KeyError):
		category = ''
	return category

def convert_row(row, mappings):
	''' Converts an individual row '''
	record = {
		'Date': row['date'],
		'Payee': row['description'],
		'Category': get_ynab_category(row['category'], mappings),
		'Memo': row['category'],
	}
	
	# determine inflow/outflow
	if row['transaction_type'].lower() == 'debit':
		record['Outflow'] = row['amount']
	else:
		record['Inflow'] = row['amount']

	return record
	
def convert(mint_transactions, category_mappings, excluded_categories=None, output_file_name='ynab.csv'):
	''' Converts from one CSV format to another '''
	# load Mint CSV
	input_file = None
	ynab_records = []
	print(excluded_categories)
	for row in mint_transactions:
		try:
			print('%s: %s' % (row['category'], row['category'] in excluded_categories))
			if row['category'] not in excluded_categories:
				# add converted record
				ynab_records.append(convert_row(row, category_mappings))
		except ValueError:
			continue

	# write out YNAB transactions
	with open(output_file_name, 'w', newline='') as ynab_file:
		csvwriter = csv.DictWriter(ynab_file, delimiter=',', fieldnames=YNAB_COLUMNS)
		csvwriter.writerow(dict((fn, fn) for fn in YNAB_COLUMNS))
		for record in ynab_records:
			 csvwriter.writerow(record)

def _get_input_method():
	'''gets input functions for prompting user'''
	try:
		input_method = raw_input
	except NameError:
		input_method = input
	return input_method
			 
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("transactions", help="name of file containing Mint transactions")
	parser.add_argument("mappings", help="name of file containing Mint to YNAB category mappings")
	parser.add_argument("-e", "--excludes", help="name of file containing Mint categories to skip when mappings")
	parser.add_argument("-o", "--out", help="name of file to create containing processed transactions")
	args = parser.parse_args()

	# load Mint transactions
	try:
		transactions = load_mint_transactions(args.transactions)
	except FileNotFoundError:
		transactions = None
	if not transactions:
		print('You will need to download transactions from Mint before')
		print('  they can be converted for importing into YNAB.')
		exit()

	# load Mint->YNAB mappings
	try:
		category_mappings = load_mappings(args.mappings)
	except FileNotFoundError:
		print('You must load a valid Mint -> YNAB category mapping file.')
		exit()
		
	# load categories to skip when processing
	try:
		excluded_categories = load_excluded_categories(args.excludes)
	except FileNotFoundError:
		excluded_categories = []

	missing_mappings = find_missing_mappings(transactions, category_mappings, excluded_categories)
	if missing_mappings:
		print(
			'Please exclude or add mappings for the following %s before continuing:' % 
			('categories' if len(missing_mappings) > 1 else 'category')
		)
		for mapping in missing_mappings:
			print (' - %s' % mapping)
		exit()
		
	# set output file name
	output_file_name = args.out if args.out else 'ynab.csv'
	
	# process transactions
	convert(transactions, category_mappings, excluded_categories, output_file_name)
