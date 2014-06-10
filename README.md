# py-mint-ynab

This project was created to provide a script allowing mapping of transactions
from Mint.com to the format required for import into You Need a Budget (YNAB).

## Instructions for Use

1. Log into Mint.com
2. Assign transactions into your categories
3. Navigate to https://wwws.mint.com/transaction.event?startDate=**06/01/2014**&endDate=**06/30/2014**&exclHidden=T, replacing the start and end date with the date range you want to export.
4. Download all transactions in the date range by clicking the "Export all # link" in the bottom right corner of the page.
5. Save the transactions CSV in the same directory as the budget script.
6. Open You Need a Budget
7. Create list of all categories in your budget.  Format them in "Parent: Child" format.
  - ex. "Auto: Insurance"
8. Create an income category as "Income: Available next month"
9. Create a "mappings.txt" file to create mappings between what you call the categories in Mint and YNAB
10. For each category in your categories and income lists, map the Mint transaction categories to their YNAB equivalents
11. Create an "excludes.txt" file to list Mint categories you do not wish to import into YNAB.
12. Add categories to this list with one category per line.
  - ex. Credit Card Payment
13. Create an excluded category as "Hide from Budgets & Trends" to omit all hidden Mint transactions from YNAB
14. Run the budget script, referencing the transactions, mappings, and exclusions files.

    python budget.py -e excludes.txt transactions.csv mappings.txt

15. If any categories are missing, add them either to the mappings.txt or excludes.txt file as appropriate.
16. Open the converted results in the newly-created ynab.csv file (found in the same directory as the budget script) to look for missing categories.
17. Follow the [How to Import Transactions](http://www.youneedabudget.com/support/article/how-to-import-transactions) instructions provided by YNAB to import your categorized transactions.