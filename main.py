#!python3
"""" read README.md for details """


import configparser
import logging
import logging.handlers
# external
import smtplib
import time
from smtplib import SMTP
from typing import Tuple

from imapclient import IMAPClient

# custom
from Handlers import Handlers

# uses SMTP for sending and IMAP for receiving
# this script should be automated with a crontab or similar

# TODO messages with unknown domain should be answered with usage instructions
# get all mails (old are deleted), sort by "FROM" and if forwarded or not
# use handlers for known domains, answer (forwarded-from) for unknown domains with usage unstructions
# -> prevents multiuse of email adress for other services

project_name = "ReMailer"
smtp_provider = {"gmail.com": "smtp.gmail.com", "yahoo.com": "smtp.mail.yahoo.com"}
imap_provider = {"gmail.com": "imap.gmail.com", "yahoo.com": "imap.mail.yahoo.com"}

# TODO read from arguments or environment
t_restart = 1800
save_mode = False


def read_login() -> Tuple[str, str]:
    """
    read login from file

    :return: mail & password
    """

    config = configparser.ConfigParser()
    config.read("login.ini")

    mail = config.get("LOGIN", "email")
    password = config.get("LOGIN", "password")

    return mail, password


def create_config():
    """
    create base config to fill in
    """

    config = configparser.ConfigParser()
    config.add_section("LOGIN")
    config.set("LOGIN", "email", "")
    config.set("LOGIN", "password", "")

    with open("login.ini", "w") as ini:
        config.write(ini)


def get_logger():
    """
    prepare logging to file & stream. Can be called multiple times .

    :return: logger object
    """

    # singleton, value only present if previously executed
    if "logger" in get_logger.__dict__:
        get_logger.logger.warning("Prevented double initialisation of logger")
        return get_logger.logger

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
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

    get_logger.logger = logger

    return logger


def connect_smtp(logger, mail: str, password: str) -> SMTP:
    """
    prepare the connection to send mails

    :param logger: logging object
    :param mail: string for mail, e.g.
    :param password: string for password (not printed to log)
    :return: connection object
    """

    host = mail.split("@")[1]
    try:
        smtp_domain = smtp_provider[host]
    except KeyError:
        logger.error(f"SMTP-Provider {host} is unknown, exiting")
        # could try smtp.XX before giving up
        exit(2)

    logger.info(f"Connecting to {smtp_domain}")
    smtp_obj = SMTP(smtp_domain, port=587)

    response = smtp_obj.ehlo()  # "hello server"
    logging.debug(response)
    if response[0] != 250:  # 250: success
        logger.error(f"no connection possible, exiting")
        exit(3)

    logger.info(f"Encrypting with TLS")
    response = smtp_obj.starttls()  # start encryption (if possible)
    logging.debug(response)

    logger.info(f"Logging in")  # TODO use special gmail key if needed
    try:
        response = smtp_obj.login(mail, password)
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"Login not accepted. Check if you have \"less secure app access\" "
                      f"turned on: https://myaccount.google.com/lesssecureapps")

        logging.error(e)
        exit(4)

    logger.debug(response)

    logger.info(f"Successful. Ready to send")

    return smtp_obj


def connect_imap(logger, mail: str, password: str) -> IMAPClient:
    """
    prepare the connection to receive mails

    :param logger: logging object
    :param mail: string for mail, e.g.
    :param password: string for password (not printed to log)
    :return: connection object
    """

    host = mail.split("@")[1]
    try:
        imap_domain = imap_provider[host]
    except KeyError:
        logger.error(f"IMAP-Provider {host} is unknown, exiting")
        # TODO try imap.XX before giving up
        exit(2)

    logger.info(f"Connecting to {imap_domain}")
    imap_obj = IMAPClient(imap_domain, ssl=True)

    logger.info(f"Logging in")

    response = imap_obj.login(mail, password)
    logger.debug(response)

    logger.info(f"Successful. Ready to receive")

    return imap_obj


def main():
    """
    start program
    """

    logger = get_logger()

    logger.info(f"\n\n--- Welcome to {project_name} ---\n")

    logger.debug("Starting up")
    try:
        mail_address, password = read_login()
    except configparser.NoSectionError:
        logger.error("No file found, creating")
        create_config()
        logger.error("Created file, fill out and restart")
        exit(1)

    logger.info(f"Found mail address <{mail_address}> with password <{'*' * len(password)}>")
    host = mail_address.split("@")[1]
    if host == "gmail.com":
        logger.info("Congratulations, you have got extended search!")
        extended_search = True
    else:
        logger.warning("No Gmail account, only basic search possible (might miss forwards!)")
        extended_search = False

    logger.info(f"Starting IMAP to receive and SMTP to send")
    imap_client = connect_imap(logger, mail_address, password)
    smtp_client = connect_smtp(logger, mail_address, password)  # get ready to send

    logger.info("Ready! Starting to work on messages")
    # Threading could encapsulate around here acting through a worker queue

    handlers = Handlers(smtp_client, mail_address, logger)

    imap_client.select_folder("INBOX", readonly=save_mode)  # False to delete mail after processing

    # search original FROM (before forwarding) and match to dictionary of handlers
    for domain in handlers.sources:  # search for mail for all handlers
        logger.debug(f"Searching for domain {domain}")

        if extended_search:
            mail_UIDs = imap_client.gmail_search("in: inbox, " + domain)  # better (gmail-only) search
        else:
            mail_UIDs = imap_client.search(['FROM', domain, "UNDELETED"])  # forwards are not detected)

        # UID is identifier
        logger.info(f"Number of mails for {domain}: {len(mail_UIDs)}")
        logger.debug(f" IDS: {mail_UIDs}")

        # call handlers with received matching mail
        for mail_id in mail_UIDs:
            # fetch mail content and unpack list to raw message
            part_to_fetch = "BODY[]"  # ENVELOPE, RFC822, BODY[] possible
            wrapped_mail = imap_client.fetch(mail_id, [part_to_fetch])
            mail = wrapped_mail[mail_id][part_to_fetch.encode()]
            handlers.handle(domain, mail)

        # delete when everything was analysed
        if mail_UIDs:
            if not save_mode:
                logger.info(f"Deleting {len(mail_UIDs)} mails for {domain}")
                imap_client.delete_messages(mail_UIDs)
                imap_client.expunge()
            else:
                logger.info(f"Skipped deleting {len(mail_UIDs)} mails for {domain}")

    logger.info("Cleaning up, closing connections")
    imap_client.logout()
    smtp_client.quit()

    logger.info("Done.")


if __name__ == "__main__":
    # the only reason to stop is an exception
    while True:
        main()
        time.sleep(t_restart)  # better than restarting externally?
