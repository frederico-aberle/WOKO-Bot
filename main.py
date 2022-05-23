
############################# Edit this: ######################################

link = 'https://www.woko.ch/de/zimmer-in-zuerich'

address = 'Altstetterstrasse'

username = '########'
password = '########'

sender = 'nethz@student.ethz.ch'

subject_msg_for_me = 'Yo, neues WG Zimmer isch frei gworde!'
body_msg_for_me = 'Neues WG Zimmer freigeworden'

subject_msg_for_receiver = 'Anfrage betreffend Nachmieter Zimmer in Zürich'
body_msg_for_receiver = 'Hey ,\n\ndeinAnliegen\n\nFreue mich auf ein Kennenlerngespräch ^^ Erreichen kann' \
                        'st du mich unter der Nummer +41 22 333 4444.\n\nViele Grüße\ndeinName'

legi = "Legi.pdf"
immatrikulationsbestaetigung = "Immatrikulationsbestaetigung.pdf"

###############################################################################

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import smtplib
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def main():
    driver = webdriver.Chrome()
    driver.get(link)

    # wait until ads are loaded
    WebDriverWait(driver, timeout=10).until(lambda d: d.find_elements(by=By.XPATH, value='//*[@id="GruppeID_98"]/div[2]/div/div'))

    # get all ads
    divs = driver.find_elements(by=By.XPATH, value='//*[@id="GruppeID_98"]/div[2]/div/div')

    # iterate through the ads
    for div in divs:
        # check if address matches the address of the ad
        if address in div.find_elements(by=By.TAG_NAME, value='td')[-1].get_attribute("textContent"):
            print(div.find_element(by=By.TAG_NAME, value='h3').get_attribute("textContent"))

            send_me_an_email()
            send_receiver_an_email(driver, div)

    # wait till next hour
    time.sleep(3600)

    # close all tabs and windows
    driver.quit()


def send_me_an_email():
    # create smtp server and start smtp server
    server = smtplib.SMTP('mail.ethz.ch', 587)
    server.starttls()

    # create e-mail
    msg_for_me = EmailMessage()
    msg_for_me['subject'] = subject_msg_for_me
    msg_for_me.set_content(body_msg_for_me)

    # log into your e-mail
    server.login(username, password)

    # send e-mail
    server.sendmail(sender,
                    sender,
                    msg_for_me.as_string()
                    )


def attach_file(filename):
    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    return part


def send_receiver_an_email(driver, div):
    # open link to the ad
    a = div.find_element(by=By.TAG_NAME, value='a')
    driver.execute_script("arguments[0].click();", a)

    # get e-mail address
    a = driver.find_element(by=By.XPATH, value='/html/body/main/div/div/div[3]/table[2]/tbody/tr[3]/td[2]/a')
    receiver = a.get_attribute("textContent")

    # get receiver's name
    elem = driver.find_element(by=By.XPATH, value='/html/body/main/div/div/div[3]/table[2]/tbody/tr[1]/td[2]')
    name = elem.get_attribute("textContent").split()[0]

    # create smtp server and start smtp server
    server = smtplib.SMTP('mail.ethz.ch', 587)
    server.starttls()

    # create e-mail
    msg_for_receiver = MIMEMultipart()
    msg_for_receiver['subject'] = subject_msg_for_receiver
    msg_for_receiver.attach(MIMEText(body_msg_for_receiver[:4] + name + body_msg_for_receiver[4:], "plain"))

    # Add attachments to e-mail
    part_one = attach_file(legi)
    part_two = attach_file(immatrikulationsbestaetigung)
    msg_for_receiver.attach(part_one)
    msg_for_receiver.attach(part_two)

    # log into your e-mail
    server.login(username, password)

    # send e-mail
    server.sendmail(sender,
                    sender,
                    msg_for_receiver.as_string()
                    )

    driver.back()

# repeat for 24 hours a day and 30 days a month
for i in range(30 * 24):
    main()
