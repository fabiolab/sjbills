from pydantic import BaseSettings


class Settings(BaseSettings):
    mail_sender: str = "SJB <secretariat@sjb35.com>"
    mail_cc: str = "secretariat@sjb35.com"
    mail_smtp_host: str = "smtp-zose.yulpa.io"
    mail_smtp_port: str = 465
    mail_smtp_login: str = "fabio@fabiolab.fr"


settings = Settings()
