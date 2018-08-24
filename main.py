import configparser
import logging
import logging.handlers
import smtplib

project_name = "ReMailer"
smtp_provider = {"gmail.com": "smtp.gmail.com", "yahoo.com": "smtp.mail.yahoo.com"}


# https://automatetheboringstuff.com/chapter16/


def read_login():
    config = configparser.ConfigParser()
    config.read(".\login.ini")

    mail = config.get("LOGIN", "email")
    password = config.get("LOGIN", "password")

    return mail, password


def create_config():
    """" create base config to fill in """
    config = configparser.ConfigParser()
    config.add_section("LOGIN")
    config.set("LOGIN", "email", "")
    config.set("LOGIN", "password", "")

    with open(".\login.ini", "w") as ini:
        config.write(ini)


def init_logger():
    """" prepare logging to file & stream """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # minimum level

    # complete log in file
    fh = logging.handlers.RotatingFileHandler(f"{project_name}.log", maxBytes=1 * 1024 * 1024, backupCount=4)  # 1MB
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)

    # logging >=info to stdout
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

    return logger


def connect_smtp(logger, mail):
    """ start the connection """

    host = mail.split("@")[1]
    try:
        smtp_domain = smtp_provider[host]
    except KeyError:
        logger.error(f"SMTP-Provider {host} is unknown, exiting")
        # TODO try smtp.XX before giving up
        exit(2)

    logger.info(f"Connecting to {smtp_domain}")
    smtp_obj = smtplib.SMTP(smtp_domain, port=587)

    response = smtp_obj.ehlo()  # "hello server"
    logging.debug(response)
    if response[0] != 250:  # 250: success
        logger.error(f"no connection possible, exiting")
        exit(3)

    logger.info(f"Encrypting with TLS")
    response = smtp_obj.starttls()  # start encryption (if possible)
    logging.debug(response)

    # TODO login
    # TODO use special gmail key if needed


def main():

    logger = init_logger()
    logger.info(f"\n\n--- Welcome to {project_name} ---\n")

    logger.debug("Starting up")
    try:
        mail, password = read_login()
    except configparser.NoSectionError:
        logger.error("No file found, creating")
        create_config()
        logger.error("Created file, fill out and restart")
        exit(1)

    logger.info(f"Found mail address <{mail}> with password <{password}>")  # TODO obfuscate PW

    connect_smtp(logger, mail)




if __name__ == "__main__":
    main()
