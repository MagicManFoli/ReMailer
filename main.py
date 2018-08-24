import configparser
import logging
import logging.handlers
import smtplib

import Handlers

# uses SMTP for sending and IMAP for receiving
# https://automatetheboringstuff.com/chapter16/

project_name = "ReMailer"
smtp_provider = {"gmail.com": "smtp.gmail.com", "yahoo.com": "smtp.mail.yahoo.com"}
smtp_provider = {"gmail.com": "imap.gmail.com", "yahoo.com": "imap.mail.yahoo.com"}

mail_handlers = {"xing.com": Handlers.format_xing}


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


def connect_smtp(logger, mail, password):
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

    logger.info(f"Logging in")      # TODO use special gmail key if needed
    try:
        response = smtp_obj.login(mail, password)
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"Login not accepted. Check if you have \"less secure app access\" "
                      f"turned on: https://myaccount.google.com/lesssecureapps")

        logging.error(e)
        exit(4)

    logger.info(f"Successful. Ready to send & receive")

    return smtp_obj


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

    logger.info(f"Found mail address <{mail}> with password <{'*' * len(password)}>")
    logger.info(f"Starting IMAP to receive and SMTP to send")

    # TODO connect IMAP to get mails
    #imap_client
    smtp_client = connect_smtp(logger, mail, password)  # get ready to send

    # TODO search original FROM (before forwarding) and match to dictionary of handlers
    # mail_list = imap_client.search( EACH mail_handlers.keys())
    # TODO remove DEBUG
    mail_list = [{"from": "xing.com"}, {"from": "xing.com"}]      # list of mails with matching FROM

    # call handlers with received matching mail
    for mail in mail_list:
        mail_handlers[mail["from"]](mail)

    logger.info("Cleaning up, closing connections")
    #imap_client.quit()
    smtp_client.quit()   # close connection

    logger.info("Done.")

if __name__ == "__main__":
    main()
