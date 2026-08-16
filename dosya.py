import sys
import subprocess
import importlib
import time
import os

REQUIRED_PACKAGES = {
    "requests":     "requests",
    "colorama":     "colorama",
    "dns":          "dnspython",
    "whois":        "python-whois",
    "PIL":          "pillow",
    "qrcode":       "qrcode[pil]",
    "phonenumbers": "phonenumbers",
    "faker":        "faker",
    "matplotlib":   "matplotlib",
    "urllib3":      "urllib3",
    "bs4":          "beautifulsoup4",
}

OPTIONAL_PACKAGES = {
    "pyzbar":       "pyzbar",
    "yt_dlp":       "yt-dlp",
    "cryptography": "cryptography",
    "zxcvbn":       "zxcvbn",
}


def _clear():
    os.system("cls" if os.name == "nt" else "clear")


def _install_pkg(package):
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet",
             "--disable-pip-version-check", package],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False


def setup_dependencies():
    _clear()
    print(r"""
██████╗  █████╗ ██████╗  ██████╗      ██████╗ ██████╗ ██████╗ ███████╗
██╔══██╗██╔══██╗██╔══██╗██╔═══██╗    ██╔════╝██╔═══██╗██╔══██╗██╔════╝
██║  ██║███████║██████╔╝██║   ██║    ██║     ██║   ██║██║  ██║█████╗
██║  ██║██╔══██║██╔══██╗██║▄▄ ██║    ██║     ██║   ██║██║  ██║██╔══╝
██████╔╝██║  ██║██║  ██║╚██████╔╝    ╚██████╗╚██████╔╝██████╔╝███████╗
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══▀▀═╝      ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
                        SETUP - @RacistDarwin
""")
    print("  🔍 Modüller kontrol ediliyor...\n")

    all_pkgs = {**REQUIRED_PACKAGES, **OPTIONAL_PACKAGES}
    installed = []
    missing = []

    for module, package in all_pkgs.items():
        try:
            importlib.import_module(module)
            installed.append(package)
        except ImportError:
            missing.append((module, package))

    print(f"  📊 Durum: {len(installed)}/{len(all_pkgs)} yüklü\n")

    if not missing:
        print("  ✅ Tüm modüller hazır! Başlatılıyor...\n")
        time.sleep(1)
        return

    print(f"  ⚠  {len(missing)} eksik modül:\n")
    for _, pkg in missing:
        print(f"     • {pkg}")

    print()
    try:
        ans = input("  Otomatik yüklensin mi? (E/h): ").strip().lower()
    except EOFError:
        ans = "e"
    if ans and ans != "e":
        print("  ⏭ Atlandı.\n")
        time.sleep(1)
        return

    print()
    failed = []
    for i, (mod, pkg) in enumerate(missing, 1):
        bar_len = 30
        pct = i / len(missing)
        filled = int(bar_len * pct)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  [{i}/{len(missing)}] {bar} {int(pct*100)}%  → {pkg}", end="", flush=True)
        if _install_pkg(pkg):
            print("  ✅")
        else:
            print("  ❌")
            failed.append(pkg)

    print()
    if failed:
        print("  ⚠  Yüklenemeyenler:")
        for f in failed:
            print(f"     • {f}   →  pip install {f}")
    else:
        print("  🎉 Tüm modüller başarıyla yüklendi!")
    print()
    time.sleep(1)


if __name__ == "__main__":
    setup_dependencies()


import re
import json
import socket
import hashlib
import ssl
import random
import subprocess as _sub
import threading
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, quote_plus, parse_qs, urlencode

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    sys.exit("requests kütüphanesi yüklenemedi.")

try:
    from colorama import init as _cinit, Fore, Style
    _cinit(autoreset=True)
except ImportError:
    class Fore:
        RED=GREEN=YELLOW=CYAN=MAGENTA=WHITE=BLUE=RESET=""
        LIGHTBLACK_EX=LIGHTGREEN_EX=LIGHTYELLOW_EX=LIGHTRED_EX=""
        LIGHTCYAN_EX=LIGHTMAGENTA_EX=LIGHTWHITE_EX=""
    class Style:
        BRIGHT=RESET_ALL=DIM=""

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except Exception:
    HAS_BS4 = False

try:
    import dns.resolver
    HAS_DNS = True
except Exception:
    HAS_DNS = False

try:
    import whois as whois_lib
    HAS_WHOIS = True
except Exception:
    HAS_WHOIS = False

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    HAS_PIL = True
except Exception:
    HAS_PIL = False

try:
    import qrcode
    HAS_QR = True
except Exception:
    HAS_QR = False

try:
    import phonenumbers
    from phonenumbers import geocoder as _pgeo, carrier as _pcar, timezone as _ptz
    HAS_PHONE = True
except Exception:
    HAS_PHONE = False

try:
    from faker import Faker
    HAS_FAKER = True
except Exception:
    HAS_FAKER = False

try:
    from zxcvbn import zxcvbn
    HAS_ZXCVBN = True
except Exception:
    HAS_ZXCVBN = False


VERSION = "1.1.0"

try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:
    SCRIPT_DIR = Path.cwd()

OUTPUT_DIR = SCRIPT_DIR / "darq_output"
OUTPUT_DIR.mkdir(exist_ok=True)


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]

def _random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


BANNER = rf"""{Fore.CYAN}{Style.BRIGHT}
██████╗  █████╗ ██████╗  ██████╗      ██████╗ ██████╗ ██████╗ ███████╗
██╔══██╗██╔══██╗██╔══██╗██╔═══██╗    ██╔════╝██╔═══██╗██╔══██╗██╔════╝
██║  ██║███████║██████╔╝██║   ██║    ██║     ██║   ██║██║  ██║█████╗
██║  ██║██╔══██║██╔══██╗██║▄▄ ██║    ██║     ██║   ██║██║  ██║██╔══╝
██████╔╝██║  ██║██║  ██║╚██████╔╝    ╚██████╗╚██████╔╝██████╔╝███████╗
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══▀▀═╝      ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
{Fore.YELLOW}
              🔥 ALL-IN-ONE TOOLKIT v{VERSION} 🔥
{Fore.WHITE}                    Owner  : @RacistDarwin
                    Kanal  : https://t.me/DarqCode
                    Output : {OUTPUT_DIR}
{Fore.RED}
       [!] Etik kullanım içindir. Yasal sorumluluk kullanıcıya aittir.
{Style.RESET_ALL}"""


def _banner(text, color=Fore.CYAN):
    print(f"\n{color}{Style.BRIGHT}{'═'*70}")
    print(f"  {text}")
    print(f"{'═'*70}{Style.RESET_ALL}\n")

def _ok(t):    print(f"  {Fore.GREEN}[+] {t}{Style.RESET_ALL}")
def _info(t):  print(f"  {Fore.CYAN}[*] {t}{Style.RESET_ALL}")
def _warn(t):  print(f"  {Fore.YELLOW}[!] {t}{Style.RESET_ALL}")
def _err(t):   print(f"  {Fore.RED}[-] {t}{Style.RESET_ALL}")

def _save(data, filename):
    try:
        safe = re.sub(r"[^\w\-.]", "_", filename)
        p = OUTPUT_DIR / safe
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        _ok(f"Kaydedildi: {p}")
        return p
    except Exception as e:
        _err(f"Kayıt: {e}")
        return None

def _get_session():
    s = requests.Session()
    s.headers.update(_random_headers())
    s.verify = False
    ad = HTTPAdapter(max_retries=Retry(total=2, backoff_factor=0.3), pool_maxsize=50)
    s.mount("http://", ad)
    s.mount("https://", ad)
    return s

def _pause():
    try:
        input(f"\n  {Fore.CYAN}[Enter]{Style.RESET_ALL} devam...")
    except EOFError:
        pass

def _ask(text, default=""):
    try:
        v = input(f"  {Fore.YELLOW}{text}: {Style.RESET_ALL}").strip()
        return v if v else default
    except EOFError:
        return default


def open_output_folder():
    _banner(f"📂 ÇIKTI KLASÖRÜ")
    try:
        if not OUTPUT_DIR.exists():
            OUTPUT_DIR.mkdir(exist_ok=True)
        files = sorted(OUTPUT_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
        if files:
            _info(f"Toplam {len(files)} dosya (son 20):")
            for f in files[:20]:
                size = f.stat().st_size
                if size < 1024: sz = f"{size}B"
                elif size < 1024*1024: sz = f"{size/1024:.1f}KB"
                else: sz = f"{size/1024/1024:.1f}MB"
                print(f"    {Fore.CYAN}•{Style.RESET_ALL} {f.name:<40} {Fore.LIGHTBLACK_EX}({sz}){Style.RESET_ALL}")
        else:
            _warn("Henüz çıktı yok")

        if sys.platform == "win32":
            os.startfile(str(OUTPUT_DIR))
        elif sys.platform == "darwin":
            _sub.Popen(["open", str(OUTPUT_DIR)])
        else:
            _sub.Popen(["xdg-open", str(OUTPUT_DIR)],
                       stdout=_sub.DEVNULL, stderr=_sub.DEVNULL)
        _ok("Klasör açıldı")
    except Exception as e:
        _err(f"Hata: {e}")
    _pause()


class OSINTModule:

    def __init__(self):
        self.session = _get_session()

    def menu(self):
        while True:
            _clear()
            print(BANNER)
            print(f"""
{Fore.RED}{Style.BRIGHT}╔══════════════════════════════════════════════════════╗
║           🔍 OSINT & İSTİHBARAT MODÜLÜ              ║
╠══════════════════════════════════════════════════════╣
║  {Fore.WHITE}[1]{Fore.RED} Email Hunter        (domain → email topla)     ║
║  {Fore.WHITE}[2]{Fore.RED} Phone Lookup        (telefon → operatör)       ║
║  {Fore.WHITE}[3]{Fore.RED} IP Investigator     (IP → konum, port)         ║
║  {Fore.WHITE}[4]{Fore.RED} Domain Recon        (WHOIS, DNS, SSL, tech)    ║
║  {Fore.WHITE}[5]{Fore.RED} Metadata Extractor  (dosyadan gizli bilgi)     ║
║  {Fore.WHITE}[6]{Fore.RED} Breach Checker      (email leak kontrolü)      ║
║  {Fore.WHITE}[7]{Fore.RED} Instagram Scraper   (profil bilgisi)           ║
║  {Fore.WHITE}[8]{Fore.RED} Wayback Machine     (silinmiş sayfalar)        ║
║  {Fore.WHITE}[9]{Fore.RED} Full Recon          (hepsini birden yap)       ║
║                                                      ║
║  {Fore.WHITE}[0]{Fore.RED} Ana menüye dön                                 ║
╚══════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")
            c = _ask("Seçim")
            try:
                if c == "1": self.email_hunter(); _pause()
                elif c == "2": self.phone_lookup(); _pause()
                elif c == "3": self.ip_investigator(); _pause()
                elif c == "4": self.domain_recon(); _pause()
                elif c == "5": self.metadata_extractor(); _pause()
                elif c == "6": self.breach_checker(); _pause()
                elif c == "7": self.instagram_scraper(); _pause()
                elif c == "8": self.wayback_machine(); _pause()
                elif c == "9": self.full_recon(); _pause()
                elif c == "0": break
            except KeyboardInterrupt:
                _warn("İptal"); _pause()
            except Exception as e:
                _err(f"Hata: {e}"); _pause()

    def email_hunter(self, domain=None):
        if not domain:
            domain = _ask("Domain (örn: example.com)")
        if not domain: return []
        _banner(f"📧 EMAIL HUNTER - {domain}")
        emails = set()
        pattern = re.compile(r"[a-zA-Z0-9._+-]+@" + re.escape(domain), re.IGNORECASE)

        _info("Hunter.io alternatifi (public)...")
        try:
            r = self.session.get(f"https://api.hunter.io/v2/domain-search?domain={domain}", timeout=10)
            data = r.json()
            if data.get("data", {}).get("emails"):
                for e in data["data"]["emails"]:
                    emails.add(e["value"].lower())
        except Exception:
            pass

        _info("crt.sh üzerinden...")
        try:
            r = self.session.get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=15)
            for entry in r.json()[:50]:
                nv = entry.get("name_value", "")
                for m in pattern.findall(nv):
                    emails.add(m.lower())
        except Exception:
            pass

        _info("Domain sayfalarını tarıyorum...")
        pages = ["", "/contact", "/about", "/team", "/iletisim", "/hakkimizda",
                 "/contact-us", "/about-us", "/staff", "/kadro", "/support",
                 "/privacy", "/kvkk", "/legal"]
        for page in pages:
            for scheme in ["https", "http"]:
                try:
                    url = f"{scheme}://{domain}{page}"
                    r = self.session.get(url, timeout=6, allow_redirects=True)
                    if r.status_code == 200:
                        for m in pattern.findall(r.text):
                            emails.add(m.lower())
                        if HAS_BS4:
                            soup = BeautifulSoup(r.text, "html.parser")
                            for a in soup.find_all("a", href=True):
                                if "mailto:" in a["href"]:
                                    e = a["href"].replace("mailto:", "").split("?")[0].strip().lower()
                                    if domain in e:
                                        emails.add(e)
                        break
                except Exception:
                    continue

        _info("DuckDuckGo Lite...")
        try:
            r = self.session.get(f"https://lite.duckduckgo.com/lite/?q=%22%40{domain}%22", timeout=10)
            for m in pattern.findall(r.text):
                emails.add(m.lower())
        except Exception:
            pass

        emails = sorted([e for e in emails if not e.startswith(('example@', 'test@', 'user@'))])
        for e in emails: _ok(e)
        if not emails: _warn("Email bulunamadı")
        else: _info(f"Toplam: {len(emails)} email")
        _save({"domain": domain, "emails": emails, "count": len(emails)},
              f"emails_{domain}.json")
        return emails

    def phone_lookup(self, phone=None):
        if not phone:
            phone = _ask("Telefon (+90...)")
        if not phone: return {}
        _banner(f"📱 PHONE LOOKUP - {phone}")
        phone_clean = re.sub(r"[^\d+]", "", phone)
        if not phone_clean.startswith("+"):
            if phone_clean.startswith("0"):
                phone_clean = "+90" + phone_clean[1:]
            else:
                phone_clean = "+" + phone_clean
        result = {"phone": phone, "clean": phone_clean}
        if HAS_PHONE:
            try:
                parsed = phonenumbers.parse(phone_clean, None)
                result["valid"] = phonenumbers.is_valid_number(parsed)
                result["possible"] = phonenumbers.is_possible_number(parsed)
                result["country"] = _pgeo.description_for_number(parsed, "en")
                result["carrier"] = _pcar.name_for_number(parsed, "en")
                result["timezones"] = list(_ptz.time_zones_for_number(parsed))
                result["international"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                result["national"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
                result["e164"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                types = {0:"FIXED_LINE",1:"MOBILE",2:"FIXED_LINE_OR_MOBILE",
                        3:"TOLL_FREE",4:"PREMIUM_RATE",5:"SHARED_COST",
                        6:"VOIP",7:"PERSONAL_NUMBER",8:"PAGER",9:"UAN",
                        10:"UNKNOWN",27:"EMERGENCY"}
                result["type"] = types.get(phonenumbers.number_type(parsed), "UNKNOWN")
            except Exception as e:
                _err(f"{e}")
        else:
            _warn("phonenumbers yok")

        for k, v in result.items(): _info(f"{k:<15}: {v}")
        _save(result, f"phone_{phone_clean}.json")
        return result

    def ip_investigator(self, ip=None):
        if not ip:
            ip = _ask("IP adresi")
        if not ip: return {}
        _banner(f"🌐 IP INVESTIGATOR - {ip}")
        result = {"ip": ip}

        _info("Konum bilgisi (ip-api.com)...")
        try:
            r = self.session.get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=8)
            data = r.json()
            if data.get("status") == "success":
                for k in ["country","regionName","city","zip","lat","lon",
                          "timezone","isp","org","as","reverse","mobile","proxy","hosting"]:
                    if k in data:
                        result[k] = data[k]
                        _info(f"{k:<15}: {data[k]}")
            else:
                _err(data.get("message", "Bilinmeyen hata"))
        except Exception as e:
            _err(f"ip-api: {e}")

        try:
            hostname = socket.gethostbyaddr(ip)[0]
            result["hostname"] = hostname
            _ok(f"hostname: {hostname}")
        except Exception:
            pass

        _info("Port taraması...")
        common = [21,22,23,25,53,80,110,143,443,445,465,587,993,995,
                  1433,1521,2049,2222,3306,3389,5432,5900,6379,8080,8443,27017]
        open_ports = []

        def sc(p):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                if s.connect_ex((ip, p)) == 0:
                    s.close()
                    return p
                s.close()
            except Exception: pass
            return None

        with ThreadPoolExecutor(max_workers=30) as ex:
            futs = [ex.submit(sc, p) for p in common]
            for f in as_completed(futs):
                p = f.result()
                if p:
                    open_ports.append(p)
                    _ok(f"Port {p} AÇIK")
        result["open_ports"] = sorted(open_ports)

        _info("Shodan public info...")
        try:
            r = self.session.get(f"https://internetdb.shodan.io/{ip}", timeout=8)
            if r.status_code == 200:
                sd = r.json()
                if sd.get("ports"):
                    result["shodan_ports"] = sd["ports"]
                    _ok(f"Shodan portlar: {sd['ports']}")
                if sd.get("vulns"):
                    result["vulnerabilities"] = sd["vulns"]
                    _err(f"⚠ Zafiyet: {len(sd['vulns'])} CVE bulundu!")
                    for cve in sd["vulns"][:5]:
                        _err(f"  → {cve}")
                if sd.get("hostnames"):
                    result["hostnames"] = sd["hostnames"]
                if sd.get("tags"):
                    _info(f"Tags: {sd['tags']}")
        except Exception:
            pass

        _save(result, f"ip_{ip.replace('.','_')}.json")
        return result

    def domain_recon(self, domain=None):
        if not domain:
            domain = _ask("Domain")
        if not domain: return {}
        _banner(f"🌍 DOMAIN RECON - {domain}")
        result = {"domain": domain}

        if HAS_WHOIS:
            try:
                _info("WHOIS...")
                w = whois_lib.whois(domain)
                result["whois"] = {
                    "registrar": str(w.registrar) if w.registrar else None,
                    "creation_date": str(w.creation_date) if w.creation_date else None,
                    "expiration_date": str(w.expiration_date) if w.expiration_date else None,
                    "name_servers": list(w.name_servers) if w.name_servers else [],
                    "emails": list(w.emails) if w.emails else [],
                }
                for k, v in result["whois"].items():
                    if v: _info(f"{k:<20}: {str(v)[:80]}")
            except Exception as e:
                _err(f"WHOIS: {e}")

  