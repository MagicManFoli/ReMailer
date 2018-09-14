"""" handlers to be used for incoming messages """

import logging
from smtplib import SMTP
from typing import Set

import pyzmail


class Handlers:
    """
    This class contains handlers for all possible domains.
    It won't initialise clients or fetch messages, this should be done externally (separation of concerns)
    """

    def __init__(self, sender: SMTP, this_mail: str, logger: logging.Logger):
        """

        :param sender: initialised smtp_client
        :param this_mail: mail_address to use as sender
        :param logger: global logging object
        """

        self._logger: logging.Logger = logger
        self._this: str = this_mail
        self._sender: SMTP = sender

        # TODO invert list? 1 tag : n handlers OR 1 handler : n tags
        self._mail_handlers = {"mailrobot@mail.xing.com": self._format_xing}

    def handle(self, source: str, mail_raw: bytes):
        """
        Call to let mail be handled

        :param source: address of source
        :param mail_raw: mail body
        """

        self._mail_handlers[source](mail_raw)

    def _format_xing(self, mail_raw: bytes):
        """" call with RFC 822 Mail body """

        self._logger.info("decoding XING message")

        mail = pyzmail.PyzMessage.factory(mail_raw)

        mail_TO = mail.get_address("to")  # mail adress only
        mail_FROM = mail.get_address("from")
        mail_SUBJECT = mail.get_subject()
        # X-Forward To?

        # this is the magic bit, XING shows message in text_part but hides it in (visible) html_part
        payload = mail.text_part.get_payload().decode(mail.text_part.charset)
        self._logger.info(f"From: {mail_FROM}, mail_TO: {mail_TO}, Subject: {mail_SUBJECT}, Size: {len(payload)}")

        self._logger.debug("Adding signature")
        payload += "\n-[Decoded using ReMailer from Modisch Fabrications]-"

        # TODO Collapse whitespace and reformat

        # compare against address, not name
        if mail_TO[1] == self._this:
            target = mail_FROM
        else:
            target = mail_TO

        source = self._this

        subject = "[Decoded] " + mail_SUBJECT

        self._logger.info(f"Formatting done, sending back to {target}")
        self._sender.sendmail(source, target, f"Subject: {subject}\n{payload}".encode())
        self._logger.info("Sent successfully")

    def _format_no_ip(self, mail_raw: bytes):
        """" extracts key to press """
        # TODO fill with life

    @property
    def sources(self) -> Set:
        """

        :return: list of
        """
        return set(self._mail_handlers.keys())

# end
