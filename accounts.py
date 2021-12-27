import requests
import random
import string
import secrets
import base64
from pathlib import Path
import time

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from verification import get_captcha_key
from phone_verify import verify_phone
from email_verify import verify_email
import environment
from util import upload

names = open('words/names.txt','r').read().splitlines()
nouns = open('words/nouns.txt','r').read().splitlines()
adjectives = open('words/adjectives.txt','r').read().splitlines()
adverbs = open('words/adverbs.txt','r').read().splitlines()
alphabet = []
for c in string.ascii_letters:
    alphabet.append(c)
vowels = ["a", "e", "i", "o", "u", "y"]

def gen_username():
    choice = random.randint(0, 6)
    separator = random.randint(0, 4)
    match choice:
        case 0: # adjective + name
            username = random.choice(adjectives) + " " + random.choice(names).lower()
        case 1: # name + name
            username = random.choice(names).lower() + " " + random.choice(names).lower()
        case 2: # adverb + adjective
            username = random.choice(adverbs).lower() + " " + random.choice(adjectives).lower()
        case 3: # adjective + noun
            match separator:
                case 4: # use parentheses
                    username = "(" + random.choice(adjectives).lower() + ")" + random.choice(nouns).lower()
                case _: # separate with space
                    username = random.choice(adjectives).lower() + " " + random.choice(nouns).lower()
        case 4: # adverb + name
            match separator:
                case 4: # use parentheses
                    username = "(" + random.choice(adverbs).lower() + ")" + random.choice(names).lower()
                case _: # separate with space
                    username = random.choice(adverbs).lower() + " " + random.choice(names).lower()
        case 5: # random ascii
            username = ""
            for i in range(random.randint(3, 6)):
                username += random.choice(alphabet)
        case 6: # noun + noun
            username = random.choice(nouns) + " " + random.choice(nouns)
        case 6: # noun + random vowel
            username = random.choice(nouns) + random.choice(vowels)
    
    return username

def gen_fingerprint(session):
    ENDPOINT = "/experiments"
    return session.get(f"{environment.ENTRY}{ENDPOINT}").json()["fingerprint"]

def set_profile_picture(session, token):
    header = {
        "authorization" : token,
        "content-type": "application/json",
    }
    # get random image from collection of 1815 images
    with open(f"images/{random.randint(1, 1815)}.png", "rb") as image:
        base64_image = base64.b64encode(image.read()).decode("utf-8") 
    data = {
        "avatar" : f"data:image/png;base64,{base64_image}"
    }
    PROFILE_ENDPOINT = "/users/@me"
    resp = session.patch(f"{environment.ENTRY}{PROFILE_ENDPOINT}", json=data, headers=header)

def initiate(session, token):
    headers = {
        "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }
    time.sleep(random.uniform(0,1))
    session.get("https://cdn.discordapp.com/bad-domains/hashes.json", headers=headers)
    USER_ENDPOINT = "/users/@me"
    USERS = "/affinities/users"
    headers["authorization"] = token
    time.sleep(random.uniform(0,1))
    session.get(f"{environment.ENTRY}{USER_ENDPOINT}{USERS}", headers=headers)
    GUILDS = "/affinities/guilds"
    time.sleep(random.uniform(0,1))
    session.get(f"{environment.ENTRY}{USER_ENDPOINT}{GUILDS}", headers=headers)
    SURVEY = "/survey"
    time.sleep(random.uniform(0,1))
    session.get(f"{environment.ENTRY}{USER_ENDPOINT}{SURVEY}", headers=headers)
    session.get("https://status.discord.com/api/v2/scheduled-maintenances/upcoming.json")
    LIBRARY = "/library"
    time.sleep(random.uniform(0,1))
    session.get(f"{environment.ENTRY}{USER_ENDPOINT}{LIBRARY}", headers=headers)
    DETECTABLE = "/applications/detectable"
    time.sleep(random.uniform(0,1))
    session.get(f"{environment.ENTRY}{DETECTABLE}", headers=headers)
    COUNTRY_CODE = "/billing/country-code"
    time.sleep(random.uniform(0,1))
    session.get(f"{environment.ENTRY}{USER_ENDPOINT}{COUNTRY_CODE}", headers=headers)
    SETTINGS = "/settings"
    data = {
        "timezone_offset": 360
    }
    time.sleep(random.uniform(0,1))
    session.patch(f"{environment.ENTRY}{USER_ENDPOINT}{SETTINGS}", json=data, headers=headers)

def create_account():
    session = requests.Session()
    # ==========================================================================
    # Generate date of bith
    month = random.randint(1, 12)
    if month < 10:
        month = "0" + str(month)
    day = random.randint(1,28)
    if day < 10:
        day = "0" + str(day)
    date = f"{random.randint(1970, 2001)}-{month}-{day}"
    # ==========================================================================

    # ==========================================================================
    # Generate username
    username = gen_username()
    # ==========================================================================

    # ==========================================================================
    # Generate fingerprint
    fingerprint = gen_fingerprint(session)
    # ==========================================================================

    # ==========================================================================
    # Generate email using username + catchall
    email_user = username.replace(" ", "_").replace("(", "").replace(")", "_")
    email = f"{email_user}@{environment.CATCHALL}"
    # ==========================================================================

    # ==========================================================================
    # Generate 20 character password
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    # ==========================================================================
    session.post("https://discord.com/", verify=True)
    content_length = len(fingerprint) + len(email) + len(username) + len(password) + len(date)
    REGISTER_ENDPOINT = "/auth/register"
    header = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "content-length": f"{148 + content_length}",
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/register",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "x-fingerprint" : fingerprint,
        "x-super-properties" : Path('x-super-properties.txt').read_text()
    }
    data = {
        "captcha_key": None,
        "consent": True,
        "date_of_birth": date,
        "email": email,
        "fingerprint" : fingerprint,
        "gift_code_sku_id": None,
        "invite": None,
        "password": password,
        "username": username
    }
    time.sleep(1)
    resp = session.post(f"{environment.ENTRY}{REGISTER_ENDPOINT}", json=data, headers=header, verify=True)
    if resp.status_code == 400:
        captcha_key = get_captcha_key("register")
        data["captcha_key"] = captcha_key
        data["content-length"] = f"{146 + content_length + len(captcha_key)}"
        resp = session.post(f"{environment.ENTRY}{REGISTER_ENDPOINT}", json=data, headers=header, verify=True)
    
    token = resp.json()["token"]
    initiate(session, token)
    print(f"Username: {username}\nPassword: {password}\nToken: {token}")
    # verify_phone(token, password)
    # verify_email(token)
    # set_profile_picture(session, token)

    upload(token)

def selenium_test():
    driver = webdriver.Chrome("./chromedriver.exe")
    driver.get("https://discord.com/register")

    username = gen_username()
    email = username.replace(" ", "_").replace("(", "").replace(")", "_")
    email = f"{email}@{environment.CATCHALL}"
    month = random.randint(1,12)
    day = random.randint(1,28)
    year = random.randint(1970, 2001)
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.NAME, "email"))
    ).send_keys(email)
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    month_form = driver.find_element(By.ID, "react-select-2-input")
    month_form.send_keys(month)
    month_form.send_keys(Keys.TAB)
    driver.find_element(By.ID, "react-select-3-input").send_keys(day)
    driver.find_element(By.ID, "react-select-4-input").send_keys(year)
    driver.find_element(By.CLASS_NAME, "button-3k0cO7").click()
    # driver.quit()