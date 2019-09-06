# Bill generation

This script generates a bill from a template

## Install

- It requires python 3.6+

```
pip install -r requirements.txt
```

- It requires wkhtmltopdf installed on your os

https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf

```
sudo apt-get install wkhtmltopdf
```

## Usage

All the files are generated in the "bills" directory. Their names match the pattern "LASTNAME_Firtname_Facture.pdf"

```
python generate_bill.py --help                                                                                                                                                                                 ven. 06 sept. 2019 16:49:45 CEST
Usage: generate_bill.py [OPTIONS]

Options:
  --firstname TEXT  FirstName for bill (ex: John)
  --lastname TEXT   LastName for bill (ex: Woo)
  --amount FLOAT    Amount of the bill in € (ex: 120.0)
  --email TEXT      Email to send the mail
  --csv_file PATH   CSV File : lastname, firstname, amount
  --sendmail        Send the bill by mail
  --help            Show this message and exit.
```

### Single bill
This command generates a 100€ bill for a John Woo and sends it by email

```
python generate_bill.py --firstname="John" --lastname="woo" --amount="100" --email="jwoo@gmail.com" --sendmail
```

### From a csv
You can generate several bills at the same time using a csv file (each line contains data for a single bill).
Format your comma separated csv file so as to have three (or four) columns : "woo";"John";100.0;"jwoo@gmail.com"

```
python generate_bill.py --csv_file=pathto/mycsvfile.csv --sendmail
```
