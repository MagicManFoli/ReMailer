
import pyzmail

logger = None   # set from main


def format_xing(mail_raw, smtp_client):
    """" call with RFC 822 Mail body """

    logger.info("decoding XING message")

    mail = pyzmail.PyzMessage.factory(mail_raw)

    mail_TO = mail.get_address("to")     # mail adress only
    mail_FROM = mail.get_address("from")
    mail_SUBJECT = "[Decoded] " + mail.get_subject("XING for your convenience")

    # this is the magic bit, XING shows message in text_part but hides it in (visible) html_part
    payload = mail.text_part.get_payload().decode(mail.text_part.charset)
    logger.info(f"From: {mail_FROM}, mail_TO: {mail_TO}, Subject: {mail_SUBJECT}, Size: {len(payload)}")

    # TODO Collapse whitespace and reformat

    logger.debug("Adding signature")
    payload += "\n-[Decoded using ReMailer from Modisch Fabrications]-"

    logger.info(f"Formatting done, sending back to {mail_TO}")
    smtp_client.sendmail(mail_FROM, mail_TO, f"Subject: {mail_SUBJECT}\n{payload}".encode())


def format_no_ip():
    """" extracts key to press """
    # TODO do that

