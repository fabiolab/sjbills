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

TEMPLATE_DIR = "templates"
TEMPLATE_FILE = "bill.html"
BILLS_DIR = "bills"

MAIL_SENDER = "SJB <secretariat@sjb35.com>"
MAIL_SUBJECT = "Facture 2019/2020"
MAIL_SMTP_HOST = "smtp.ionos.fr"
MAIL_SMTP_PORT = 465
MAIL_SMTP_LOGIN = "president@sjb35.com"


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
        pdf_file = generate_single_bill(firstname, lastname, amount)
        if sendmail:
            send_mail(firstname, email, pdf_file, password)
    else:
        click.echo(
            f"Required arguments are missing. Please run the commande again with the --help option"
        )


def generate_single_bill(firstname: str, lastname: str, amount: float) -> str:
    template_loader = jinja2.FileSystemLoader(searchpath=f"./{TEMPLATE_DIR}")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(TEMPLATE_FILE)

    now = pendulum.now("Europe/Paris")

    generated_html = template.render(
        name=f"{firstname.capitalize()} {lastname.upper()}",
        amount=amount,
        dt=now.format("DD/MM/YYYY"),
    )

    source_html_file = strip_accent(
        f"{TEMPLATE_DIR}/{lastname.upper()}_{firstname.capitalize()}_Facture.html"
    )

    target_pdf_file = strip_accent(
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

    return target_pdf_file


def generate_bill_from_csv(csv_file: str, sendmail: bool, passwd: str):
    with open(csv_file, "r") as thefile:
        csv_reader = csv.reader(thefile, delimiter=";")
        for row in csv_reader:
            try:
                firstname = row[1].strip()
                lastname = row[0].strip()
                amount = row[2].strip()
            except IndexError:
                logger.error(
                    f"A field is missing in the current row {row}. The line is ignored."
                )
            else:
                pdf = generate_single_bill(firstname, lastname, amount)
                if sendmail:
                    try:
                        send_mail(firstname, row[3], pdf, passwd)
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
        Veuillez trouver ci-joint la facture correspondant à votre adhésion au club du <b>SJB pour la saison 2019/2020</b>.
    </p>
    <p>Cordialement,
        <br/>Fabrice pour le SJB
    </p>
    """

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message.attach(MIMEText(body, "html"))
    message["From"] = MAIL_SENDER
    message["To"] = email
    message["Subject"] = MAIL_SUBJECT
    message["Cc"] = MAIL_SENDER
    message["reply-to"] = MAIL_SENDER

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
    with SMTP_SSL(MAIL_SMTP_HOST, MAIL_SMTP_PORT) as server:
        server.login(MAIL_SMTP_LOGIN, smtp_password)
        server.sendmail(MAIL_SENDER, email, text)
        logger.info(f"Successfully sent email to {email}")


def strip_accent(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


if __name__ == "__main__":
    generate_bill()
