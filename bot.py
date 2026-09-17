import json, os, re
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from html import unescape

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
DEST = "@GoalZone_fotball"
SOURCES = ["ADAK_IR", "TvFutball120", "Footbalfa", "Footballi_Apps"]
STATE_FILE = "state.json"

def get(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8", "ignore")

def send(text):
    body = urlencode({"chat_id": DEST, "text": text}).encode()
    req = Request(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=body)
    with urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

def posts(channel):
    html = get(f"https://t.me/s/{channel}")
    ids = sorted(set(int(x) for x in re.findall(
        r'data-post="' + re.escape(channel) + r'/(\d+)"', html)))
    out = []
    for pid in ids:
        p = html.find(f'data-post="{channel}/{pid}"')
        chunk = html[p:p+12000]
        m = re.search(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', chunk, re.S)
        if not m:
            continue
        text = re.sub(r'<br\s*/?>', "\n", m.group(1))
        text = unescape(re.sub(r'<[^>]+>', '', text)).strip()
        if text:
            out.append((pid, text))
    return out

def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN is not configured by the host.")
        return

    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            state = json.load(f)
    except:
        state = {}

    for ch in SOURCES:
        try:
            ps = posts(ch)
            if ch not in state:
                state[ch] = ps[-1][0] if ps else 0
                continue

            last = int(state[ch])
            for pid, text in ps:
                if pid <= last:
                    continue
                msg = f"{text}\n\n📌 منبع: @{ch}\n『Gøal ZØne』"
                result = send(msg)
                if result.get("ok"):
                    state[ch] = pid
                else:
                    print("SEND_ERROR", ch, result)
                    break
        except Exception as e:
            print("SOURCE_ERROR", ch, repr(e))

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)
    print("SCAN_DONE", state)

if __name__ == "__main__":
    main()
