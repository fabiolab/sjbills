import jinja2
import click
import pendulum
import pdfkit
import os
import csv
from loguru import logger

TEMPLATE_DIR = "templates"
TEMPLATE_FILE = "bill.html"
BILLS_DIR = "bills"


@click.command()
@click.option(
    "--firstname",
    help="FirstName for bill (ex: John)",
    required=False,
    type=click.STRING,
)
@click.option(
    "--lastname", help="LastName for bill (ex: Woo)", required=False, type=click.STRING
)
@click.option(
    "--amount",
    help="Amount of the bill in € (ex: 120.0)",
    required=False,
    type=click.FLOAT,
)
@click.option(
    "--csv",
    help="CSV File : firstname, lastname, amount",
    required=False,
    type=click.Path(exists=True),
)
def generate_bill(firstname: str, lastname: str, amount: float, csv: str):
    if csv:
        generate_bill_from_csv(csv)
    elif firstname and lastname and amount:
        generate_single_bill(firstname, lastname, amount)
    else:
        click.echo(
            f"Required arguments are missing. Please run the commande again with the --help option"
        )


def generate_single_bill(firstname: str, lastname: str, amount: float):
    template_loader = jinja2.FileSystemLoader(searchpath=f"./{TEMPLATE_DIR}")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(TEMPLATE_FILE)

    now = pendulum.now("Europe/Paris")

    generated_html = template.render(
        name=f"{firstname.capitalize()} {lastname.upper()}",
        amount=amount,
        dt=now.format("DD/MM/YYYY"),
    )

    source_html_file = (
        f"{TEMPLATE_DIR}/{lastname.upper()}_{firstname.capitalize()}_Facture.html"
    )
    target_pdf_file = (
        f"{BILLS_DIR}/{lastname.upper()}_{firstname.capitalize()}_Facture.pdf"
    )
    logger.info(f"Generate {source_html_file} from {TEMPLATE_DIR}/{TEMPLATE_FILE}")
    html_file = open(source_html_file, "w")
    html_file.write(generated_html)
    html_file.close()

    logger.info(f"Generate {target_pdf_file} from {source_html_file}")
    pdfkit.from_file(source_html_file, target_pdf_file)

    logger.info(f"Remove {source_html_file}")
    os.unlink(source_html_file)


def generate_bill_from_csv(csv_file: str):
    with open(csv_file, "r") as thefile:
        csv_reader = csv.reader(thefile, delimiter=";")
        for row in csv_reader:
            generate_single_bill(row[0], row[1], row[2])


if __name__ == "__main__":
    generate_bill()
