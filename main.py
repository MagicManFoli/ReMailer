import smtplib
import configparser
import logging

project_name = "ReMailer"

def read_login():
    config = configparser.ConfigParser()
    config.read(".\login.ini")

    mail = config.get("LOGIN", "email")
    password = config.get("LOGIN", "password")

    return mail, password

def create_login():
    config = configparser.ConfigParser()
    config.add_section("LOGIN")
    config.set("LOGIN", "email", "")
    config.set("LOGIN", "password", "")

    with open(".\login.ini", "w") as ini:
        config.write(ini)


def init_logger():
    logging.basicConfig(
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        handlers=[
            logging.FileHandler(f"{project_name}.log", ),
            logging.StreamHandler()
        ],
        level=logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # minimum level

    # complete log in file
    fh = logging.FileHandler('spam.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.addHandler(fh)

    # logging >=info to stdout
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.addHandler(ch)

    return logger


def main():

    logger = init_logger()
    logger.info(f"Starting up {__file__}")

    try:
        mail, password = read_login()
    except configparser.NoSectionError:
        print("No file found, creating")
        create_login()
        print("Created file, fill out and restart")
        exit(1)

    print(mail, password)


if __name__ == "__main__":
    main()
