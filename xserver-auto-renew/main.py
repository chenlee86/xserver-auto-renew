import json
import re
from typing import Any

import requests

from .settings import Settings


def get_user_agent():
    res = requests.get(
        "https://raw.githubusercontent.com/fa0311/latest-user-agent/main/header.json"
    )
    headers = res.json()["chrome"]
    headers.update(
        {
            "host": None,
            "connection": None,
            "accept-encoding": None,
            "accept-language": "ja",
        }
    )
    return headers
    
def send_telegram_message(env: Settings, message: str):
    if not env.telegram_bot_token or not env.telegram_chat_id:
        return
    url = f"https://api.telegram.org/bot{env.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": env.telegram_chat_id,
        "text": f"🚀 <b>XServer Auto Renew</b>\n\n{message}",
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")


def set_cookies(cookies: Any, session: requests.Session):
    for cookie in cookies:
        session.cookies.set(
            cookie["name"],
            cookie["value"],
            domain=cookie.get("domain"),
            path=cookie.get("path"),
            secure=cookie.get("secure", False),
        )


if __name__ == "__main__":
    env = Settings()

    session = requests.Session()
    session.headers.update(get_user_agent())
    with open("cookies.json", "r", encoding="utf-8") as f:
        cookies = json.load(f)
    set_cookies(cookies, session)

    res1 = session.get(
        "https://secure.xserver.ne.jp/xapanel/xvps/server/freevps/extend/index",
        params={
            "id_vps": env.id_vps,
        },
    )

    pattern = r'<input type="hidden" name="uniqid" value="(?P<uniqid>[^"]+)" />'
    match = re.search(pattern, res1.text)
    assert match is not None
    uniqid = match.group("uniqid")

    res2 = session.post(
        "https://secure.xserver.ne.jp/xapanel/xvps/server/freevps/extend/do",
        # "https://secure.xserver.ne.jp/xapanel/xvps/server/freevps/extend/conf",
        data={
            "uniqid": uniqid,
            "ethna_csrf": "",
            "id_vps": env.id_vps,
        },
        files={},
    )

    if "利用期限の更新手続きが完了しました。" in res2.text:
        msg = "✅ 您的 VPS 续期成功！(Successfully renewed)"
        print("Done!")
        send_telegram_message(env, msg)
    elif "利用期限の1日前から更新手続きが可能です。" in res2.text:
        msg = "ℹ️ 暂未到续期时间。(Please try again a day before.)"
        print("Failed, please try again a day before.")
        send_telegram_message(env, msg)
    else:
        msg = "❌ 续期失败或出现未知异常，请人工介入检查！(Failed to renew VPS)"
        send_telegram_message(env, msg)
        raise RuntimeError("Failed to renew VPS")
