from smtplib import SMTP

import pyzmail

logger = None   # set from main


def format_xing(mail_raw: bytes, smtp_client: SMTP):
    """" call with RFC 822 Mail body """

    logger.info("decoding XING message")

    mail = pyzmail.PyzMessage.factory(mail_raw)

    mail_TO = mail.get_address("to")     # mail adress only
    mail_FROM = mail.get_address("from")
    mail_SUBJECT = "[Decoded] " + mail.get_subject("XING for your convenience")

    # FIXME X-Forward To?

    # this is the magic bit, XING shows message in text_part but hides it in (visible) html_part
    payload = mail.text_part.get_payload().decode(mail.text_part.charset)
    logger.info(f"From: {mail_FROM}, mail_TO: {mail_TO}, Subject: {mail_SUBJECT}, Size: {len(payload)}")

    # TODO Collapse whitespace and reformat

    logger.debug("Adding signature")
    payload += "\n-[Decoded using ReMailer from Modisch Fabrications]-"

    if mail_TO == this_mail:
        target = mail_FROM
    else:
        target = mail_TO

    source = this_mail

    logger.info(f"Formatting done, sending back to {target}")
    smtp_client.sendmail(source, target, f"Subject: {mail_SUBJECT}\n{payload}".encode())


def format_no_ip():
    """" extracts key to press """
    # TODO do that

