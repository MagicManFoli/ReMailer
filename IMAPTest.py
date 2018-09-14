"""" simple test cases for receiving messages """

import unittest

from main import *

domain = "mailrobot@mail.xing.com"


class IMAPTEST(unittest.TestCase):
    def test_loading(self):
        logger = get_logger()
        mail_address, password = read_login()
        imap_client = connect_imap(logger, mail_address, password)
        imap_client.select_folder("INBOX", readonly=save_mode)

        mail_UIDs = imap_client.gmail_search("in: inbox, " + domain)

        part_to_fetch = "BODY[]"
        mail_id = mail_UIDs[0]

        mail = imap_client.fetch(mail_id, [part_to_fetch])[mail_id][part_to_fetch.encode()]
        print("You've got Mail!")
        self.assertGreater(len(mail), 0)  # more like > 1k


# end

if __name__ == '__main__':
    unittest.main()
