import os
import string
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import discord

ChromeOptions = Options()
ChromeOptions.add_argument("--log-level=3")
Version = "2.2"
Url = "https://store.steampowered.com/join"
SteamIcon = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/240px-Steam_icon_logo.svg.png"
BotUrl = "https://github.com/lilkajt/Steam-Account-Generator"
DomainInput = ""
BotPath = Path(__file__).resolve().parent


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

# FILE FUNCTIONS
def ExportCSV(email, username, password):
    data = {"Email": email, "Username": username, "Password": password}
    df = pd.DataFrame(data, index=[0])
    file_path = BotPath / "CreatedAccounts.csv"

    if not file_path.exists():
        df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, mode="a", index=False, header=False)

def AccountsFromCSV():
    file_name = input("\tWhat is the file name(without extension): ")
    file_path = BotPath / f"{file_name}.csv"
    if not file_path.exists():
        print(f"\tFile '{file_path.name}' not found in {BotPath}.")
        return [], [], []

    file = pd.read_csv(file_path)
    emails = file["Email"].tolist()
    usernames = file["Username"].tolist()
    passwords = file["Password"].tolist()
    return emails, usernames, passwords

def ExampleFile(fileName):
    data = {"Email":"Testemail@domain.com", "Username":"test1", "Password":"testpassword"}
    df = pd.DataFrame(data, index=[0])
    file_path = BotPath / f"{fileName}.csv"

    if not file_path.exists():
        df.to_csv(file_path, index=False)

def WebhookURL():
    webhook_path = BotPath / "webhook.txt"
    if not webhook_path.exists():
        return ""

    with webhook_path.open("r", encoding="utf-8") as webhook_file:
        return webhook_file.readline().strip()

# NOTIFICATIONS
def Notification(notiType):
    if notiType == "email":
        prompt = "Check email to confirm and press Enter to continue."
    elif notiType == "captcha":
        prompt = "Solve the captcha in the browser and press Enter to continue."
    else:
        prompt = "Complete the required action and press Enter to continue."

    input(f"\n\t{prompt}\n\t")

# BROWSER HELPERS
def type_with_delay(element, value):
    for char in value:
        element.send_keys(char)
        time.sleep(np.random.uniform(0, 0.1))


def prompt_for_count(message):
    while True:
        try:
            value = int(input(message))
        except ValueError:
            print("\tPlease enter a valid number.")
            continue

        if value <= 0:
            print("\tPlease enter a number greater than zero.")
            continue

        return value

# RANDOM STRINGS
def RndString(length):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def RndPassword(length):
    return RndString(length)

def RndDomainEmail(domain):
    username = RndString(8)
    return f"{username}@{domain}"

# DATA INPUTS
def GenerateOption(option):
    if option == "domain":
        email, username, password = Domain()
        GenAccount(email, username, password)
    elif option == "newAccount":
        email, username, password = OneAccount()
        GenAccount(email, username, password)
    else:
        emails, usernames, passwords = AccountsFromCSV()
        if not emails:
            return

        for i in range(len(emails)):
            print(f"\tGenerating account nr {i+1}")
            GenAccount(emails[i], usernames[i], passwords[i])

def OneAccount():
    email = input("\tEnter your email: ")
    username = email.split("@")[0]
    password = RndPassword(14)
    return email, username, password

def Domain():
    global DomainInput
    if DomainInput == "":
        DomainInput = input("\tEnter your domain: ")
        email = RndDomainEmail(DomainInput)
    else:
        email = RndDomainEmail(DomainInput)
    username = email.split("@")[0]
    password = RndPassword(14)
    return email, username, password

# WEBHOOK
def WebhookSend(email, username, password, profLink):
    webhookUrl = WebhookURL()
    if webhookUrl == "INSTEAD OF THIS LINE PUT YOUR DISCORD WEBHOOK TO GET NOTIFICATIONS!" or webhookUrl == "":
        print("\tInvalid webhook, change in webhook.txt.\n\tContinue...")
    else:
        try:
            webhook = discord.SyncWebhook.from_url(webhookUrl)
            webhook.send(embed=DiscordEmbed(email, username, password, profLink))
        except discord.errors.DiscordException as discord_error:
            print(f"\tFailed to send webhook notification: {discord_error}")

def DiscordEmbed(email, username, password, profLink):
    embed = discord.Embed(
        title="New Steam Account",
        color=0x669900
    )
    embed.set_author(name="SAG - Steam Account Generator", url=BotUrl)
    embed.add_field(name="Username", value=f"{username}")
    embed.add_field(name="Password", value=f"||{password}||")
    embed.add_field(name="Email", value=f"{email}",inline=False)
    embed.add_field(name="Profile link", value=f"{profLink}",inline=False)
    embed.set_footer(text="Account generated using SAG bot by Lilkajt", icon_url=SteamIcon)
    return embed

# MESSAGE
def MenuMessage():
    print("")
    print("--------------------------------------------------")
    print(f"| WELCOME TO STEAM-ACCOUNT-GENERATOR Version {Version} |")
    print("--------------------------------------------------")
    print("")
    messageList = [[1, "create accounts from file"], [2, "create new account each time"], [3, "create accounts using your domain"], [4, "Create example file"], [5, "HELP"], [6, "Contact info"]]
    column = ["Options", "Description"]
    df = pd.DataFrame(messageList, columns=column)
    print(df.to_string(index=False))

def Help():
    print("\n\tHELP")
    print("\tOption domain supports custom user domains")

def Contact():
    print("\n\tContact information")
    print("\tdiscord: lilkajt#6121")

# GENERATOR
def GenAccount(email, username, password):
    time.sleep(np.random.uniform(0, 0.1))
    driver = webdriver.Chrome(options=ChromeOptions)
    driver.get(Url)
    time.sleep(6)
    email_field = driver.find_element(By.XPATH, '//*[@id="email"]')
    email_field.click()
    type_with_delay(email_field, email)
    time.sleep(0.5)
    reenter_email_field = driver.find_element(By.XPATH, '//*[@id="reenter_email"]')
    reenter_email_field.click()
    type_with_delay(reenter_email_field, email)
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//*[@id="i_agree_check"]').click()
    Notification("captcha")
    print("\n\tCaptcha confirmed!")
    driver.find_element(By.XPATH, '//*[@id="createAccountButton"]').click()
    Notification("email")
    print("\n\tEmail confirmed!")
    # SameEmail(driver)
    time.sleep(2)
    account_name_field = driver.find_element(By.XPATH, '//*[@id="accountname"]')
    account_name_field.click()
    type_with_delay(account_name_field, username)
    time.sleep(0.5)
    password_field = driver.find_element(By.XPATH, '//*[@id="password"]')
    password_field.click()
    type_with_delay(password_field, password)
    time.sleep(0.5)
    reenter_password_field = driver.find_element(By.XPATH, '//*[@id="reenter_password"]')
    reenter_password_field.click()
    type_with_delay(reenter_password_field, password)
    # username = NameCheck(driver, username)
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="createAccountButton"]').click()
    time.sleep(6)
    profLink = ExtractLink(driver)
    print("\tAccount successfully created")
    ExportCSV(email, username, password)
    WebhookSend(email, username, password, profLink)
    driver.quit()

# Not working
def SameEmail(driver,option=True):
    element = f"return document.querySelectorAll(\"button\")[2].textContent"
    element = driver.execute_script(element)
    if element == "Continue" and option == True:
        driver.execute_script("EmailConfirmedVerified( 0 );")
    else:
        print("\tWaiting for input...")
        input()

# Not working
def NameCheck(driver, username):
    element = "return document.querySelectorAll(\".password_tag.warning\")[0].textContent"
    element = driver.execute_script(element)
    # print(f"name check script run element {element}")
    if element == "Not Available":
        time.sleep(1)
        newUsername = driver.execute_script("return document.querySelector(\"#suggested_name_1\").text")
        # newUsername = driver.find_element(By.XPATH, '//*[@id="suggested_name_1"]').text
        driver.find_element(By.ID, "suggested_name_1").click()
        print(f"\tName taken. Changing name.\n\tNew name {newUsername}")
        Notification("account name")
        return newUsername
    return username

def ExtractLink(driver):
    profLink = f"return document.querySelector(\"a\").getAttribute(\"href\")"
    profLink = driver.execute_script(profLink)
    return profLink

def ProgramMenu():
    while True:
        clear_console()
        MenuMessage()
        choice = input("Input number you choose: ")

        match choice:
            case "1":
                clear_console()
                print("\tYou choose creating accounts from CSV file")
                GenerateOption("file_accounts")
            case "2":
                clear_console()
                print("\tYou choose creating new accounts each time")
                count = prompt_for_count("\tHow many accounts would you like to generate? ")
                for i in range(count):
                    print(f"\tGenerating account nr {i+1}")
                    GenerateOption("newAccount")
            case "3":
                clear_console()
                print("\tYou choose creating accounts using your domain\t")
                count = prompt_for_count("\tHow many accounts would you like to generate? ")
                for i in range(count):
                    print(f"\tGenerating account nr {i+1}")
                    GenerateOption("domain")
            case "4":
                clear_console()
                print("\tCreating example file")
                ExampleFile(input("\tWhat file name do you want: "))
                print("\tDone! Check current folder")
                time.sleep(3)
            case "5":
                clear_console()
                Help()
                time.sleep(5)
            case "6":
                clear_console()
                Contact()
                time.sleep(5)
            case _:
                print(f"Incorrect input! {choice}")
                print("Restarting!")
                time.sleep(5)


def main():
    try:
        ProgramMenu()
        time.sleep(1)
    except Exception as err:
        print(err)
        print("Press Enter to close the program...")
        input()


if __name__ == "__main__":
    main()