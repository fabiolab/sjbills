from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from pathlib import Path
from loguru import logger
import unicodedata
import jinja2
import click
import pendulum
import pdfkit
import os
import csv

from conf import settings

TEMPLATE_DIR = "templates"
TEMPLATE_FILE = "bill.html"
BILLS_DIR = "bills"

SEASON = "2022/2023"
MAIL_SUBJECT = f"Facture {SEASON}"


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
    "--adherent_firstname",
    help="FirstName of the adherent (if different from bill)",
    required=False,
    type=click.STRING,
)
@click.option(
    "--adherent_lastname",
    help="LastName of the adherent (if different from bill)",
    required=False,
    type=click.STRING,
)
@click.option(
    "--amount",
    help="Amount of the bill in € (ex: 120.0)",
    required=False,
    type=click.FLOAT,
)
@click.option(
    "--email", help="Email to send the mail", required=False, type=click.STRING
)
@click.option(
    "--csv_file",
    help="CSV File : lastname, firstname, amount",
    required=False,
    type=click.Path(exists=True),
)
@click.option("--sendmail", help="Send the bill by mail", is_flag=True)
def generate_bill(
    firstname: str,
    lastname: str,
    adherent_firstname: str,
    adherent_lastname: str,
    amount: float,
    csv_file: str,
    sendmail: bool,
    email: str,
):
    password = None
    if sendmail:
        password = click.prompt("Please enter the smtp password", hide_input=True)
    if csv_file:
        generate_bill_from_csv(csv_file, sendmail, password)
    elif firstname and lastname and amount:
        pdf_file = generate_single_bill(
            firstname, lastname, amount, adherent_firstname, adherent_lastname
        )
        if sendmail:
            send_mail(firstname, email, pdf_file, password)
    else:
        click.echo(
            f"Required arguments are missing. Please run the commande again with the --help option"
        )


def generate_single_bill(
    bill_firstname: str,
    bill_lastname: str,
    amount: float,
    adherent_firstname: str = None,
    adherent_lastname: str = None,
) -> str:

    if not adherent_firstname:
        adherent_firstname = bill_firstname
        adherent_lastname = bill_lastname

    template_loader = jinja2.FileSystemLoader(searchpath=f"./{TEMPLATE_DIR}")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(TEMPLATE_FILE)

    now = pendulum.now("Europe/Paris")

    generated_html = template.render(
        name=f"{bill_firstname.capitalize()} {bill_lastname.upper()}",
        amount=amount,
        adherent=f"{adherent_firstname.capitalize()} {adherent_lastname.upper()}",
        season=SEASON,
        dt=now.format("DD/MM/YYYY"),
    )

    source_html_file = strip_accent(
        f"{TEMPLATE_DIR}/{adherent_lastname.upper()}_{adherent_firstname.capitalize()}_Facture.html"
    )

    target_pdf_file = strip_accent(
        f"{BILLS_DIR}/{adherent_lastname.upper()}_{adherent_firstname.capitalize()}_Facture.pdf"
    )

    logger.info(f"Generate {source_html_file} from {TEMPLATE_DIR}/{TEMPLATE_FILE}")
    html_file = open(source_html_file, "w")
    html_file.write(generated_html)
    html_file.close()

    logger.info(f"Generate {target_pdf_file} from {source_html_file}")
    pdfkit.from_file(source_html_file, target_pdf_file)

    logger.info(f"Remove {source_html_file}")
    os.unlink(source_html_file)

    return target_pdf_file


def generate_bill_from_csv(csv_file: str, sendmail: bool, passwd: str):
    with open(csv_file, "r") as thefile:
        csv_reader = csv.reader(thefile, delimiter=";")
        for row in csv_reader:
            try:
                bill_firstname = row[1].strip()
                bill_lastname = row[0].strip()
                amount = row[2].strip()
                adherent_lastname = row[3].strip()
                adherent_firstname = row[4].strip()
            except IndexError:
                logger.error(
                    f"A field is missing in the current row {row}. The line is ignored."
                )
            else:
                pdf = generate_single_bill(
                    bill_firstname,
                    bill_lastname,
                    float(amount),
                    adherent_firstname,
                    adherent_lastname,
                )
                if sendmail:
                    try:
                        send_mail(bill_firstname, row[5], pdf, passwd)
                    except IndexError:
                        logger.error(
                            f"No email specified in the row {row}. Email not sent."
                        )


def send_mail(name: str, email: str, pdf_filepath: str, smtp_password: str):
    body = f"""
    <p>
        Bonjour {name.capitalize()},
    </p>
    <p>
        Veuillez trouver ci-joint la facture correspondant à votre adhésion au club du <b>SJB pour la saison {SEASON}</b>.
    </p>
    <p>Cordialement,
        <br/>Fabrice pour le SJB
    </p>
    """

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message.attach(MIMEText(body, "html"))
    message["From"] = settings.mail_sender
    message["To"] = email
    message["Subject"] = settings.mail_subject
    message["cc"] = settings.mail_cc
    message["reply-to"] = settings.mail_sender

    # Open PDF file in binary mode
    with open(pdf_filepath, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    filename = Path(pdf_filepath).name
    logger.info(f"Add {filename} as an attachment")
    # Add header as key/value pair to attachment part
    part.add_header("Content-Disposition", f"attachment; filename= {filename}")

    # Add attachment to message and convert message to string
    message.attach(part)

    text = message.as_string()

    # Log in to server using secure context and send email
    with SMTP_SSL(settings.mail_smtp_host, settings.mail_smtp_port) as server:
        server.login(settings.mail_smtp_login, smtp_password)
        server.sendmail(settings.mail_sender, [email, settings.mail_cc], text)
        logger.info(f"Successfully sent email to {email}")


def strip_accent(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


if __name__ == "__main__":
    generate_bill()
