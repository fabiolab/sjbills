# Bill generation

This script generates a bill from a template

## Install

- It requires python 3.10+

```commandline
poetry install
```

- It requires wkhtmltopdf installed on your os

https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf

```commandline
sudo apt-get install wkhtmltopdf
```

## Usage

All the files are generated in the "bills" directory. Their names match the pattern "LASTNAME_Firtname_Facture.pdf"

```commandline
python generate_bill.py --help                                                                                                                                                                                 ven. 06 sept. 2019 16:49:45 CEST
Usage: generate_bill.py [OPTIONS]

Options:
  --firstname TEXT           FirstName for bill (ex: John)
  --lastname TEXT            LastName for bill (ex: Woo)
  --adherent_firstname TEXT  FirstName of the adherent (if different from
                             bill)
  --adherent_lastname TEXT   LastName of the adherent (if different from bill)
  --amount FLOAT             Amount of the bill in € (ex: 120.0)
  --email TEXT               Email to send the mail
  --csv_file PATH            CSV File : lastname, firstname, amount
  --sendmail                 Send the bill by mail
  --help                     Show this message and exit.
```

### Single bill
This command generates a 100€ bill for a John Woo and sends it by email

```commandline
python generate_bill.py --firstname="John" --lastname="woo" --amount="100" --email="jwoo@gmail.com" --sendmail
```

### From a csv
You can generate several bills at the same time using a csv file (each line contains data for a single bill).
Format your comma separated csv file so as to have five (or six) columns : "woo";"John";100.0;"woo";"John";"jwoo@gmail.com"

```commandline
python generate_bill.py --csv_file=pathto/mycsvfile.csv --sendmail
```
