import json
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .settings import LoginSettings

if __name__ == "__main__":
    env = LoginSettings()

    options = Options()
    if os.environ.get("HEADLESS", "").lower() in ("1", "true", "yes"):
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    driver.get("https://secure.xserver.ne.jp/xapanel/login/xvps/")
    driver.find_element(By.ID, "memberid").send_keys(env.username)
    driver.find_element(By.ID, "user_password").send_keys(env.password)
    driver.find_element(By.NAME, "action_user_login").click()

    timeout = 30
    start_time = time.time()
    while "login" in driver.current_url:
        time.sleep(1)
        if time.time() - start_time > timeout:
            print(f"Login timeout or failed. Current URL: {driver.current_url}")
            print("Page Text Preview:")
            try:
                print(driver.find_element(By.TAG_NAME, "body").text)
            except Exception as e:
                print(f"Could not get body text: {e}")
            driver.quit()
            exit(1)
    
    print(f"Login finished, current URL: {driver.current_url}")

    cookies = driver.get_cookies()
    with open("cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=4)

    driver.quit()
