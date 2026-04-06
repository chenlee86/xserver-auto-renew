import json
import os

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
    driver.find_element(By.ID, "user_password").send_keys(env.password, Keys.ENTER)

    while driver.current_url != "https://secure.xserver.ne.jp/xapanel/xvps/index":
        driver.implicitly_wait(10)

    cookies = driver.get_cookies()
    with open("cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=4)

    driver.quit()
