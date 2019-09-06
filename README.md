# Bill generation

This script generates a bill from a template

## Install

It requires python 3.6+

```
pip install -r requirements.txt
```

It requires wkhtmltopdf installed on your os

https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf

```
sudo apt-get install wkhtmltopdf
```

## Usage

All the files are generated in the "bills" directory. Their names match the pattern "LASTNAME_Firtname_Facture.pdf"

### Sigle bill from command line

```
python generate_bill.py --firstname="John" --lastname="woo" --amount="100"
```

### From a csv
You can generate several bill at the same time using a csv file (each line contains data for a single bill).
Format your comma separated csv file so as to have three columns : "John";"woo";100.0

```
python generate_bill.py --csv=pathto/mycsvfile.csv
```
