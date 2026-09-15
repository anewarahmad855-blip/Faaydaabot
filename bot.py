#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════
 Botii Fayda ID — Version 200.0 (MASTER ULTIMATE)
═══════════════════════════════════════════════════════════════════════
 Koodii v51+v61+v71+v72+v80+v91.x+v100+v101+v104+v105 walitti fidame.

 ✅ [1] BOT_USERNAME = "Faaydaabot" — Token waliin waldubbata (FIX)
 ✅ [2] Template 1-7 GitHub irraa (fetch + cache + upload)
 ✅ [3] Button hunda saffisa olaanaa:
        - await q.answer() JALQABA
        - Keyboard CACHE
        - asyncio.create_task (background)
        - HTTPXRequest timeouts gabaabaa
        - Fast path (direct edit, handler function hin waamu)
 ✅ [4] Menu, /start, /setting, /converter, Download PDF — hunda saffisa
 ✅ [5] FAN → Phone → OTP SMS (Twilio / Africa's Talking / Simulated)
 ✅ [6] Python error fix — "BOT_USERNAME mismatch" furame
 ✅ [7] Yeroo tokko run → yeroo hunda hojjeta (infinite loop + backoff)
 ✅ [8] PyMuPDF 4-level fallback + pypdf + raw stream
 ✅ [9] Portrait → Landscape + Afaan Amaaraa + Ingiliffa (as-is)
 ✅ [10] Termux wake-lock + PID lock + webhook delete
═══════════════════════════════════════════════════════════════════════
"""

# ══════════════════════════════════════════════════════════════════════
# [1/14] BOOTSTRAP — Auto-install environment
# ══════════════════════════════════════════════════════════════════════
import os
import sys
import subprocess
import importlib
import signal
import time
import atexit

PID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        ".fayda_bot.pid")


def _is_already_running():
    if not os.path.exists(PID_FILE):
        return False
    try:
        with open(PID_FILE, 'r') as f:
            old_pid = int(f.read().strip())
        os.kill(old_pid, 0)
        return True
    except (ValueError, ProcessLookupError, PermissionError):
        return False


def _write_pid():
    try:
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
    except Exception:
        pass


def _cleanup_pid():
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except Exception:
        pass


atexit.register(_cleanup_pid)


def _termux_wake_lock():
    is_termux = ("com.termux" in os.environ.get("PREFIX", "")
                 or os.path.exists("/data/data/com.termux"))
    if not is_termux:
        return
    try:
        subprocess.Popen(
            ["termux-wake-lock"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[activate] ✅ termux-wake-lock fayyadame.")
    except Exception as e:
        print(f"[activate] termux-wake-lock fail: {e}")


def _bootstrap_environment():
    is_termux = ("com.termux" in os.environ.get("PREFIX", "")
                 or os.path.exists("/data/data/com.termux"))

    def _run(cmd, timeout=600):
        try:
            return subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=timeout, check=False)
        except Exception as e:
            print(f"[bootstrap] {' '.join(cmd[:3])} fail: {e}")
            return None

    print("═" * 62)
    print(" [1/14] BOOTSTRAP — Environment qopheessaa jira...")
    print("═" * 62)

    if is_termux:
        print("[bootstrap] pkg update...")
        _run(["pkg", "update", "-y"], timeout=900)
        pkgs = ["python", "python-pip", "git", "curl", "wget",
                "openssl", "ca-certificates", "libxml2", "libxslt",
                "libjpeg-turbo", "libpng", "zlib", "clang", "make",
                "binutils", "pkg-config", "freetype", "fontconfig",
                "termux-api"]
        for p in pkgs:
            r = _run(["dpkg", "-s", p], timeout=20)
            if not r or r.returncode != 0:
                print(f"[bootstrap] pkg install {p}")
                _run(["pkg", "install", "-y", p], timeout=900)
        r = _run(["which", "git"], timeout=10)
        if not r or not (r.stdout or "").strip():
            _run(["pkg", "update", "-y"])
            _run(["pkg", "install", "-y", "git"])

    # PyMuPDF 4-level fallback
    try:
        importlib.import_module("fitz")
        print("[bootstrap] ✅ PyMuPDF duraan jira.")
    except ImportError:
        print("[bootstrap] PyMuPDF hin jiru — install gochaa jira...")
        if is_termux:
            print("[bootstrap] → LEVEL 1: TUR repo...")
            _run(["pkg", "install", "-y", "tur-repo"], timeout=300)
            _run(["pkg", "install", "-y", "python-pymupdf"], timeout=1200)
            try:
                importlib.import_module("fitz")
                print("[bootstrap] ✅ PyMuPDF TUR irraa!")
            except ImportError:
                pass
        try:
            importlib.import_module("fitz")
        except ImportError:
            print("[bootstrap] → LEVEL 2: pip no-cache...")
            os.environ["CFLAGS"] = "-Wno-implicit-function-declaration"
            _run([sys.executable, "-m", "pip", "install",
                  "--upgrade", "--no-cache-dir", "--force-reinstall",
                  "PyMuPDF"], timeout=1800)
        try:
            importlib.import_module("fitz")
        except ImportError:
            print("[bootstrap] → LEVEL 3: pip wheel...")
            _run([sys.executable, "-m", "pip", "install",
                  "--upgrade", "--only-binary=:all:", "PyMuPDF"],
                 timeout=1800)
        try:
            importlib.import_module("fitz")
            print("[bootstrap] ✅ PyMuPDF milkoofte!")
        except ImportError:
            print("[bootstrap] ⚠️ PyMuPDF hin milkoofne.")
            print("[bootstrap] → pypdf + raw stream fallback!")

    py_deps = [
        ("telegram", "python-telegram-bot>=20.0"),
        ("PIL",      "Pillow"),
        ("requests", "requests"),
        ("pypdf",    "pypdf"),
    ]
    for mod, pip_name in py_deps:
        try:
            importlib.import_module(mod)
        except ImportError:
            print(f"[bootstrap] pip install {pip_name}")
            _run([sys.executable, "-m", "pip", "install",
                  "--upgrade", "--no-cache-dir", pip_name], timeout=900)

    r = _run(["which", "git"], timeout=10)
    if r and (r.stdout or "").strip():
        _run(["git", "config", "--global",
              "user.email", "bot@fayda.local"], timeout=10)
        _run(["git", "config", "--global",
              "user.name", "Fayda Bot"], timeout=10)
        _run(["git", "config", "--global", "--add",
              "safe.directory", "*"], timeout=10)
    print("[bootstrap] ✅ Environment qophaa'e — bot jalqaba!")


# ══════════════════════════════════════════════════════════════════════
# [2/14] ACTIVATION CHECK
# ══════════════════════════════════════════════════════════════════════
if _is_already_running():
    print("⚠️  Instance biraa hojjechaa jira! (PID file argame)")
    print(f"    Yoo barbaadde: rm {PID_FILE}")
    sys.exit(0)

_bootstrap_environment()
_termux_wake_lock()
_write_pid()

print("═" * 62)
print(f" ✅ BOT AKTIIVE — PID {os.getpid()}")
print("═" * 62)


# ══════════════════════════════════════════════════════════════════════
# [3/14] IMPORTS
# ══════════════════════════════════════════════════════════════════════
import logging
import asyncio
import re
import random
import json
import base64
import copy
import zlib
import concurrent.futures
from datetime import datetime

import requests
from telegram import (Update, InlineKeyboardButton,
                      InlineKeyboardMarkup, BotCommand)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)
from telegram.error import (NetworkError, TimedOut, RetryAfter,
                            Conflict, TelegramError)
from telegram.request import HTTPXRequest
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont

FITZ_AVAILABLE = False
PYPDF_AVAILABLE = False
try:
    import fitz
    FITZ_AVAILABLE = True
    print("✅ PyMuPDF (fitz) fe'ame!")
except ImportError:
    print("⚠️ PyMuPDF hin argamne — pypdf fallback fayyadama.")
try:
    import pypdf
    PYPDF_AVAILABLE = True
    print("✅ pypdf fe'ame!")
except ImportError:
    print("⚠️ pypdf hin argamne.")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


# ══════════════════════════════════════════════════════════════════════
# [4/14] CONFIG — BOT_USERNAME token waliin waldubbateera
# ══════════════════════════════════════════════════════════════════════
TOKEN = os.environ.get(
    "BOT_TOKEN",
    "8628353271:AAFhc-_rVWdqqu9v7pyjhi4QemyZZwxEKk4")
BOT_USERNAME = "Faaydaabot"

BANK_ACCOUNT = "1000109759639"
PHONE_NUMBER = "0910165048"
BANK_NAME = "Anuwaar Ahmad Mussa"
OCR_API_KEY = os.environ.get("OCR_API_KEY", "K85293219188957")

GITHUB_TOKEN = os.environ.get(
    "GH_TOKEN", "ghp_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")
GITHUB_REPO = os.environ.get(
    "GH_REPO", "anewarahmad855-blip/Faaydaa-bot")
GITHUB_DATA_REPO = os.environ.get(
    "GH_DATA_REPO", "anewarahmad855-blip/faaydaa-bot-data")
GITHUB_FILE = "bot_data.json"
TEMPLATE_GH_BRANCH = "main"

# SMS / OTP PROVIDER
SMS_PROVIDER = os.environ.get("SMS_PROVIDER", "simulated")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "")
AT_API_KEY   = os.environ.get("AT_API_KEY", "")
AT_USERNAME  = os.environ.get("AT_USERNAME", "")
AT_SENDER_ID = os.environ.get("AT_SENDER_ID", "FAYDA")

TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "templates")
os.makedirs(TEMPLATE_DIR, exist_ok=True)
TEMPLATE_SIZE = (1512, 550)
_TEMPLATE_CACHE = {}

AVAILABLE_TEMPLATES = [1, 2, 3, 4, 5, 6, 7]

DEFAULT_DATA = {
    "admin_chat_id": 2047590795,
    "users": {},
    "otp_logs": []
}

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)


def _github_data_configured():
    return (bool(GITHUB_TOKEN) and bool(GITHUB_DATA_REPO)
            and "YOUR_GITHUB_TOKEN" not in GITHUB_TOKEN
            and "/" in GITHUB_DATA_REPO)


def _github_repo_configured():
    return (bool(GITHUB_TOKEN) and bool(GITHUB_REPO)
            and "/" in GITHUB_REPO)


# ══════════════════════════════════════════════════════════════════════
# [5/14] SMS — OTP bilbila user irratti erguu
# ══════════════════════════════════════════════════════════════════════
def _normalize_phone(phone):
    if not phone:
        return None
    p = re.sub(r"[^\d+]", "", phone)
    if p.startswith("+251"):
        return p
    if p.startswith("251"):
        return "+" + p
    if p.startswith("0"):
        return "+251" + p[1:]
    if len(p) == 9:
        return "+251" + p
    return p


def send_otp_sms(phone, otp):
    phone_e164 = _normalize_phone(phone)
    if not phone_e164:
        return False, "Phone number dogoggora"

    sms_text = (f"Fayda ID OTP koodii keessan: {otp}\n"
                f"Koodiin kun daqiiqaa 5 qofaaf hojjeta.\n"
                f"Nagaatti!")

    if SMS_PROVIDER == "twilio":
        if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
                and TWILIO_FROM_NUMBER):
            return False, "Twilio keys hin qindaa'in"
        try:
            url = (f"https://api.twilio.com/2010-04-01/Accounts/"
                   f"{TWILIO_ACCOUNT_SID}/Messages.json")
            r = requests.post(
                url,
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                data={"From": TWILIO_FROM_NUMBER,
                      "To": phone_e164,
                      "Body": sms_text},
                timeout=20)
            if r.status_code in (200, 201):
                logger.info(f"✅ OTP SMS Twilio: {phone_e164}")
                return True, "OTP SMS ergame!"
            logger.warning(f"Twilio {r.status_code}: {r.text[:200]}")
            return False, f"Twilio error {r.status_code}"
        except Exception as e:
            return False, f"Twilio exception: {e}"

    if SMS_PROVIDER == "africastalking":
        if not (AT_API_KEY and AT_USERNAME):
            return False, "AT keys hin qindaa'in"
        try:
            r = requests.post(
                "https://api.africastalking.com/version1/messaging",
                headers={"apiKey": AT_API_KEY,
                         "Accept": "application/json",
                         "Content-Type":
                             "application/x-www-form-urlencoded"},
                data={"username": AT_USERNAME,
                      "to": phone_e164,
                      "message": sms_text,
                      "from": AT_SENDER_ID},
                timeout=20)
            if r.status_code in (200, 201):
                logger.info(f"✅ OTP SMS AT: {phone_e164}")
                return True, "OTP SMS ergame!"
            return False, f"AT error {r.status_code}"
        except Exception as e:
            return False, f"AT exception: {e}"

    logger.info(f"📱 [SIMULATED] OTP {otp} → {phone_e164}")
    return True, f"OTP simulated ({phone_e164})"


# ══════════════════════════════════════════════════════════════════════
# [6/14] GITHUB DATA — Load/Save (non-blocking)
# ══════════════════════════════════════════════════════════════════════
def github_load():
    if not _github_data_configured():
        if os.path.exists(GITHUB_FILE):
            try:
                with open(GITHUB_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f), None
            except Exception as e:
                logger.warning(f"Local load error: {e}")
        return copy.deepcopy(DEFAULT_DATA), None
    try:
        r = requests.get(
            f"https://api.github.com/repos/{GITHUB_DATA_REPO}/"
            f"contents/{GITHUB_FILE}",
            headers={"Authorization": f"token {GITHUB_TOKEN}"},
            timeout=10)
        if r.status_code == 200:
            content = base64.b64decode(r.json()["content"]).decode()
            logger.info(f"☁️ GitHub data repo: {GITHUB_DATA_REPO}")
            return json.loads(content), r.json().get("sha")
        elif r.status_code == 404:
            logger.info("📂 bot_data.json hin jiru — haaraa uumama.")
    except Exception as e:
        logger.warning(f"GitHub load error: {e}")
    return copy.deepcopy(DEFAULT_DATA), None


def github_save(data, sha, message="Bot data update"):
    try:
        with open(GITHUB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Local save error: {e}")
    if not _github_data_configured():
        return False, None
    try:
        content = base64.b64encode(
            json.dumps(data, indent=2, ensure_ascii=False).encode()
        ).decode()
        payload = {"message": message, "content": content}
        if sha:
            payload["sha"] = sha
        r = requests.put(
            f"https://api.github.com/repos/{GITHUB_DATA_REPO}/"
            f"contents/{GITHUB_FILE}",
            headers={"Authorization": f"token {GITHUB_TOKEN}"},
            json=payload, timeout=15)
        if r.status_code in (200, 201):
            return True, r.json().get("content", {}).get("sha")
        if r.status_code == 409:
            try:
                rg = requests.get(
                    f"https://api.github.com/repos/{GITHUB_DATA_REPO}/"
                    f"contents/{GITHUB_FILE}",
                    headers={"Authorization": f"token {GITHUB_TOKEN}"},
                    timeout=10)
                if rg.status_code == 200:
                    payload["sha"] = rg.json().get("sha")
                    r2 = requests.put(
                        f"https://api.github.com/repos/"
                        f"{GITHUB_DATA_REPO}/contents/{GITHUB_FILE}",
                        headers={"Authorization": f"token {GITHUB_TOKEN}"},
                        json=payload, timeout=15)
                    if r2.status_code in (200, 201):
                        return True, r2.json().get(
                            "content", {}).get("sha")
            except Exception:
                pass
        logger.warning(f"GitHub save failed: {r.status_code}")
    except Exception as e:
        logger.warning(f"GitHub save error: {e}")
    return False, None


BOT_DATA, BOT_DATA_SHA = github_load()
ADMIN_CHAT_ID = BOT_DATA.get("admin_chat_id", 2047590795)


def get_admin_chat_id():
    return BOT_DATA.get("admin_chat_id", 2047590795)


async def _bg_github_save():
    global BOT_DATA_SHA
    try:
        snap = copy.deepcopy(BOT_DATA)
        ok, new_sha = await asyncio.to_thread(
            github_save, snap, BOT_DATA_SHA)
        if ok and new_sha:
            BOT_DATA_SHA = new_sha
    except Exception as e:
        logger.warning(f"BG save error: {e}")


def schedule_save():
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_bg_github_save())
    except RuntimeError:
        github_save(BOT_DATA, BOT_DATA_SHA)


def save_user(user_id, username, first_name, fan=None,
              otp=None, phone=None):
    uid_str = str(user_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    BOT_DATA.setdefault("users", {})
    BOT_DATA["users"].setdefault(uid_str, {})
    BOT_DATA["users"][uid_str].update({
        "username": username, "first_name": first_name,
        "last_seen": now
    })
    if fan:
        BOT_DATA["users"][uid_str]["fan"] = fan
    if otp:
        BOT_DATA["users"][uid_str]["last_otp"] = otp
    if phone:
        BOT_DATA["users"][uid_str]["phone"] = phone
    if fan and otp:
        BOT_DATA.setdefault("otp_logs", []).append({
            "user_id": user_id, "fan": fan, "otp": otp,
            "phone": phone, "time": now
        })
        BOT_DATA["otp_logs"] = BOT_DATA["otp_logs"][-200:]
    schedule_save()


# ══════════════════════════════════════════════════════════════════════
# [7/14] OCR — Afaan Amaaraa + Ingiliffa
# ══════════════════════════════════════════════════════════════════════
def ocr_space_image(image_bytes, lang='eng'):
    try:
        r = requests.post(
            'https://api.ocr.space/parse/image',
            files={'file': ('image.jpg', image_bytes, 'image/jpeg')},
            data={
                'apikey': OCR_API_KEY, 'language': lang,
                'OCREngine': 2, 'scale': 'true',
                'isOverlayRequired': 'false',
                'detectOrientation': 'true',
            }, timeout=60)
        if r.status_code == 200:
            result = r.json()
            if result.get('ParsedResults'):
                return (result['ParsedResults'][0]
                        .get('ParsedText', '') or '')
    except Exception as e:
        logger.error(f"OCR.space ({lang}) error: {e}")
    return ''


def ocr_multilingual(image_bytes):
    results = {}
    en_text = ocr_space_image(image_bytes, 'eng')
    if en_text:
        results['en'] = en_text.strip()
    am_text = ocr_space_image(image_bytes, 'amh')
    if am_text:
        results['am'] = am_text.strip()
    if not results:
        results['en'] = ''
    combined = ""
    if results.get('am'):
        combined += results['am'] + "\n"
    if results.get('en'):
        combined += results['en'] + "\n"
    return combined.strip(), results


# ══════════════════════════════════════════════════════════════════════
# [8/14] TEMPLATE — 1-7 GitHub fetch/upload + cache
# ══════════════════════════════════════════════════════════════════════
def _template_gh_urls(num):
    return [
        f"https://raw.githubusercontent.com/{GITHUB_REPO}/"
        f"{TEMPLATE_GH_BRANCH}/templates/template{num}.png",
        f"https://raw.githubusercontent.com/{GITHUB_REPO}/"
        f"{TEMPLATE_GH_BRANCH}/template{num}.png",
        f"https://cdn.jsdelivr.net/gh/{GITHUB_REPO}@"
        f"{TEMPLATE_GH_BRANCH}/templates/template{num}.png",
    ]


def _validate_template_image(path):
    try:
        with Image.open(path) as im:
            return im.size[0] >= 400 and im.size[1] >= 200
    except Exception:
        return False


def fetch_template_from_github(num):
    if num not in AVAILABLE_TEMPLATES:
        return None
    path = os.path.join(TEMPLATE_DIR, f"template{num}.png")
    if os.path.exists(path) and _validate_template_image(path):
        return path
    headers = {"User-Agent": "FaydaBot/200.0",
               "Accept": "image/png,image/*,*/*"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    for url in _template_gh_urls(num):
        try:
            r = requests.get(url, headers=headers, timeout=20, stream=True)
            if r.status_code == 200 and len(r.content) > 2000:
                tmp = path + ".tmp"
                with open(tmp, 'wb') as f:
                    f.write(r.content)
                if _validate_template_image(tmp):
                    os.replace(tmp, path)
                    _TEMPLATE_CACHE.pop(num, None)
                    logger.info(f"☁️ Template {num} GitHub irraa fide.")
                    return path
                try:
                    os.remove(tmp)
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Template {num} fetch fail: {e}")
    return None


def upload_template_to_github(num, image_bytes):
    if num not in AVAILABLE_TEMPLATES:
        return False, None
    if not _github_repo_configured():
        return False, None
    path_in_repo = f"templates/template{num}.png"
    url = (f"https://api.github.com/repos/{GITHUB_REPO}/"
           f"contents/{path_in_repo}")
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    sha = None
    try:
        rg = requests.get(url, headers=headers, timeout=10)
        if rg.status_code == 200:
            sha = rg.json().get("sha")
    except Exception:
        pass
    try:
        content = base64.b64encode(image_bytes).decode()
        payload = {"message": f"Update template {num} from bot",
                   "content": content,
                   "branch": TEMPLATE_GH_BRANCH}
        if sha:
            payload["sha"] = sha
        r = requests.put(url, headers=headers, json=payload, timeout=20)
        if r.status_code in (200, 201):
            logger.info(f"✅ Template {num} GitHub irratti olkaa'ame.")
            return True, r.json().get("content", {}).get("sha")
        logger.warning(f"Template upload HTTP {r.status_code}")
    except Exception as e:
        logger.error(f"Template upload error: {e}")
    return False, None


def preload_templates_from_github():
    ok = 0
    for i in AVAILABLE_TEMPLATES:
        if fetch_template_from_github(i):
            ok += 1
    logger.info(f"☁️ Templates GitHub irraa: {ok}/7 (1-7)")
    return ok


def get_amharic_font(size=20):
    for path in [
        "NotoSansEthiopic-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansEthiopic-Regular.ttf",
        "NotoSansEthiopic-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansEthiopic-Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _make_placeholder(num):
    w, h = TEMPLATE_SIZE
    img = Image.new('RGB', (w, h), (240, 250, 245))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(20, 20), (80, 60)], fill=(0, 100, 0))
    draw.rectangle([(20, 40), (80, 50)], fill=(255, 255, 0))
    draw.rectangle([(20, 50), (80, 60)], fill=(200, 0, 0))
    am_font = get_amharic_font(20)
    try:
        draw.text((100, 20), "የኢትዮጵያ ዲጂታል መታወቂያ ካርድ",
                  fill=(0, 0, 0), font=am_font)
    except Exception:
        draw.text((100, 20), "Ethiopian Digital ID Card", fill=(0, 0, 0))
    draw.text((100, 50), "Ethiopian Digital ID Card", fill=(0, 0, 0))
    draw.text((100, 80), f"Template {num} (placeholder)",
              fill=(100, 100, 100))
    draw.rectangle([(50, 120), (400, 470)],
                   outline=(150, 160, 155), width=2)
    draw.rectangle([(1260, 80), (1450, 470)],
                   outline=(0, 0, 0), width=2)
    img.save(os.path.join(TEMPLATE_DIR, f"template{num}.png"), "PNG")
    return img


def get_template_path(num):
    if num not in AVAILABLE_TEMPLATES:
        num = 1
    path = os.path.join(TEMPLATE_DIR, f"template{num}.png")
    if os.path.exists(path) and _validate_template_image(path):
        return path
    fetched = fetch_template_from_github(num)
    if fetched:
        return fetched
    _make_placeholder(num).save(path, "PNG")
    return path


def load_template_image(num):
    if num not in AVAILABLE_TEMPLATES:
        num = 1
    if num in _TEMPLATE_CACHE:
        return _TEMPLATE_CACHE[num].copy()
    path = get_template_path(num)
    try:
        img = Image.open(path).convert("RGB")
        if img.size != TEMPLATE_SIZE:
            img = img.resize(TEMPLATE_SIZE, Image.Resampling.LANCZOS)
        _TEMPLATE_CACHE[num] = img
        return img.copy()
    except Exception as e:
        logger.error(f"load_template_image({num}): {e}")
        return None


# ══════════════════════════════════════════════════════════════════════
# [9/14] USER STATE + PDF + IMAGE PROCESSING
# ══════════════════════════════════════════════════════════════════════
user_data = {}


def init_user(uid):
    if uid not in user_data:
        user_data[uid] = {
            'template': 1, 'color_mode': 'color', 'mirror': False,
            'output_type': 'image', 'language': 'en',
            'state': 'IDLE', 'converted_count': 0,
            'downloaded_count': 0,
            'fan_fin': None, 'otp': None, 'phone': None,
            'temp_photo': None, 'temp_data': {}, 'temp_pdf': None,
            'pending_template_upload': None
        }


def extract_text_from_pdf(pdf_path):
    text = ""
    if PYPDF_AVAILABLE:
        try:
            with open(pdf_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    text += (page.extract_text() or "") + "\n"
        except Exception as e:
            logger.error(f"pypdf text error: {e}")
    if not text.strip() and FITZ_AVAILABLE:
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
        except Exception as e:
            logger.error(f"fitz text error: {e}")
    return text


def pdf_page_to_image(pdf_path, output_path=None, page_num=0, scale=2.5):
    if not FITZ_AVAILABLE:
        return None
    try:
        doc = fitz.open(pdf_path)
        if page_num >= len(doc):
            page_num = 0
        page = doc[page_num]
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)
        if output_path:
            pix.save(output_path)
            doc.close()
            try:
                return Image.open(output_path).copy()
            except Exception:
                return None
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
        return img
    except Exception as e:
        logger.error(f"PyMuPDF render error: {e}")
        return None


def extract_photo_from_pdf(pdf_path, output_path):
    try:
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        found_images = []
        jpeg_streams = re.findall(
            rb'/DCTDecode.*?stream\r?\n(.*?)endstream',
            pdf_data, re.DOTALL)
        for i, stream in enumerate(jpeg_streams):
            if len(stream) > 5000:
                temp_path = f"temp_jpg_{i}.jpg"
                try:
                    with open(temp_path, 'wb') as img_f:
                        img_f.write(stream)
                    with Image.open(temp_path) as img:
                        found_images.append(
                            (temp_path, img.size[0] * img.size[1]))
                except Exception:
                    try:
                        clean = (b'\xff\xd8'
                                 + stream.split(b'\xff\xd8', 1)[1])
                        with open(temp_path, 'wb') as img_f:
                            img_f.write(clean)
                        with Image.open(temp_path) as img:
                            found_images.append(
                                (temp_path, img.size[0] * img.size[
