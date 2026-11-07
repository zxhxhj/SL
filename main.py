import requests, os, psutil, sys, jwt, pickle, json, binascii, time, urllib3, base64, re, socket, threading, ssl, pytz, aiohttp, asyncio, signal, random, struct, uuid
from urllib.parse import urlparse
from protobuf_decoder.protobuf_decoder import Parser
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from colorama import Fore, Style, init
from fastapi import FastAPI, HTTPException, Query
import uvicorn

try:
    from cfonts import render, say
except ImportError:
    render = lambda text, **kwargs: text

try:
    import httpx
except ImportError:
    print("[FATAL] httpx not installed. Run: pip install httpx")
    sys.exit(1)

init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==============================================================================
# المسارات المضمونة لبيئة الاستضافة (Railway / Linux Containers)
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGETS_FILE = os.path.join(BASE_DIR, "targets.json")
ACCOUNTS_FILE = os.path.join(BASE_DIR, "accs.txt")

# ==============================================================================
# إعدادات الـ API والمشغلات العامة (OB55 Zero-Ban Core)
# ==============================================================================
app = FastAPI(title="Free Fire Zero-Ban Squad & Room Sniper API", version="OB55-18.0")

class FreeFireBot:
    def __init__(self, uid, password):
        self.uid = str(uid).strip()
        self.password = str(password).strip()
        self.writer = None
        self.key = None
        self.iv = None
        self.region = "ME"
        self.lock = asyncio.Lock()
        self.is_ready = False
        self.in_squad = False
        self.in_room = False
        self.acc_name = "Unknown"
        self.session_start = 0.0
        self.reconnect_count = 0

bot_pool = []
spam_targets = set()
TARGET_STATUS_CACHE = {}
TARGET_ROOM_CACHE = {}
TARGET_LEADER_CACHE = {}

active_target_tasks = {}

# ── إعدادات البروتوكول ──────────────────────────────────────
OB_VERSION          = "OB55"
DEFAULT_CLIENT_VER  = "1.132.9"
CLIENT_VERSION      = "1.132.3"
GA_SV               = "1789535859"
AES_KEY             = b'Yg&tc%DEuh6%Zc^8'
AES_IV              = b'6oyZDr22E3ychjM%'
ME_REGIONS          = ("ME", "MENA", "MIDDLE_EAST")

# ── إعدادات الاستقرار ───────────────────────────────────────
STAGGER_MIN         = 0.15
STAGGER_MAX         = 0.4
LOGIN_RETRY_DELAY   = 1.5
LOGIN_MAX_RETRIES   = 4
GLD_MAX_RETRIES     = 4
TCP_KEEPALIVE_SEC   = 25
TCP_RECONNECT_LIMIT = 5
SESSION_LIFETIME    = 5.5 * 3600

BASE_HEADERS = {
    'User-Agent': 'UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)',
    'Connection': 'close',
    'Accept-Encoding': 'gzip',
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Unity-Version': '2018.4.12f1',
    'X-GA-SV': GA_SV,
    'X-GA': 'v1 1',
    'ReleaseVersion': OB_VERSION,
}

# ==============================================================================
# Raw Protobuf Helpers
# ==============================================================================
def _pb_varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n: b |= 0x80
        out.append(b)
        if not n: break
    return bytes(out)

def _pb_tag(f, wt):       return _pb_varint((f << 3) | wt)
def _pb_str_field(f, v):
    d = v.encode("utf-8") if isinstance(v, str) else bytes(v)
    return _pb_tag(f, 2) + _pb_varint(len(d)) + d
def _pb_int_field(f, v):  return _pb_tag(f, 0) + _pb_varint(int(v))
def _pb_msg_field(f, in_): return _pb_tag(f, 2) + _pb_varint(len(in_)) + in_

def aes_encrypt_sync(payload: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(payload, AES.block_size))

async def aes_encrypt(payload: bytes, key: bytes, iv: bytes) -> bytes:
    return aes_encrypt_sync(payload, key, iv)

# ==============================================================================
# Parsers
# ==============================================================================
def parse_majorlogin_response(data: bytes) -> dict:
    result = {}
    i = 0; n = len(data)
    STRING_FIELDS = {2, 8, 10}
    while i < n:
        try:
            key = 0; shift = 0
            while i < n:
                b = data[i]; i += 1
                key |= (b & 0x7F) << shift
                if not (b & 0x80): break
                shift += 7
                if shift > 64: break
            field_num = key >> 3
            wire_type = key & 7
            if field_num == 0 or field_num > 1000: break

            if wire_type == 0:
                val = 0; shift = 0
                while i < n:
                    b = data[i]; i += 1
                    val |= (b & 0x7F) << shift
                    if not (b & 0x80): break
                    shift += 7
                    if shift > 64: break
                result[field_num] = val
            elif wire_type == 2:
                length = 0; shift = 0
                while i < n:
                    b = data[i]; i += 1
                    length |= (b & 0x7F) << shift
                    if not (b & 0x80): break
                    shift += 7
                    if shift > 32: break
                if length < 0 or i + length > n: break
                val_bytes = data[i:i+length]; i += length
                if field_num in STRING_FIELDS:
                    try: result[field_num] = val_bytes.decode('utf-8')
                    except Exception: result[field_num] = val_bytes
                else:
                    result[field_num] = val_bytes
            elif wire_type == 5:
                if i + 4 > n: break
                result[field_num] = data[i:i+4]; i += 4
            elif wire_type == 1:
                if i + 8 > n: break
                result[field_num] = data[i:i+8]; i += 8
            else:
                break
        except Exception:
            break
    return result

def parse_getlogindata_fields(data: bytes) -> dict:
    result = {}
    i = 0; n = len(data)
    while i < n:
        try:
            key = 0; shift = 0
            while i < n:
                b = data[i]; i += 1
                key |= (b & 0x7F) << shift
                if not (b & 0x80): break
                shift += 7
                if shift > 64: break
            fn = key >> 3; wt = key & 7
            if fn == 0 or fn > 2000: break
            if wt == 0:
                val = 0; shift = 0
                while i < n:
                    b = data[i]; i += 1
                    val |= (b & 0x7F) << shift
                    if not (b & 0x80): break
                    shift += 7
                    if shift > 64: break
                result[fn] = val
            elif wt == 2:
                ln = 0; shift = 0
                while i < n:
                    b = data[i]; i += 1
                    ln |= (b & 0x7F) << shift
                    if not (b & 0x80): break
                    shift += 7
                    if shift > 32: break
                if ln < 0 or i + ln > n: break
                vb = data[i:i+ln]; i += ln
                try: result[fn] = vb.decode('utf-8')
                except Exception: result[fn] = vb
            elif wt == 5:
                if i + 4 > n: break
                result[fn] = data[i:i+4]; i += 4
            elif wt == 1:
                if i + 8 > n: break
                result[fn] = data[i:i+8]; i += 8
            else:
                break
        except Exception:
            break
    return result

# ==============================================================================
# DNS Resolver المضمون
# ==============================================================================
_DNS_CACHE = {}

async def resolve_host_cloudflare(hostname: str) -> str:
    if not hostname: return hostname
    parts = hostname.split('.')
    if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
        return hostname
    now = time.time()
    if hostname in _DNS_CACHE:
        ip, exp = _DNS_CACHE[hostname]
        if now < exp: return ip

    loop = asyncio.get_running_loop()
    try:
        ip_info = await loop.getaddrinfo(hostname, None, family=socket.AF_INET)
        if ip_info:
            ip = ip_info[0][4][0]
            _DNS_CACHE[hostname] = (ip, now + 300.0)
            return ip
    except Exception:
        pass

    return hostname

def new_async_client():
    return httpx.AsyncClient(
        verify=False,
        timeout=httpx.Timeout(15.0, connect=10.0, read=15.0, write=15.0),
        limits=httpx.Limits(max_connections=8, max_keepalive_connections=0, keepalive_expiry=0.1),
        http2=False,
        follow_redirects=False,
    )

# ==============================================================================
# Garena OAuth
# ==============================================================================
async def get_access_token(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    hdrs = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-G998B Build/SP1A.210812.016)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": str(uid),
        "password": str(password),
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    for attempt in range(4):
        try:
            async with new_async_client() as cli:
                r = await cli.post(url, headers=hdrs, data=data)
                if r.status_code == 200:
                    res = r.json()
                    oid = res.get("open_id")
                    at  = res.get("access_token")
                    plat = res.get("platform", 2)
                    if oid and at:
                        return oid, at, plat
                elif r.status_code == 429:
                    await asyncio.sleep(2.0 + attempt * 1.5)
                    continue
        except Exception:
            pass
        await asyncio.sleep(1.0 + attempt * 0.4)
    return None, None, None

def get_device_for_account(account_identifier: str) -> dict:
    return {
        "unique_device_id": f"Google|{str(uuid.uuid4())}",
        "brand": "Samsung",
        "model": "SM-N9860",
        "gpu_renderer": "Adreno (TM) 750",
        "system_software": "Android OS 14 / API-34 (UQ1A.240205.08180011/lyb.20260818.001116)",
        "screen_width": 1600,
        "screen_height": 900,
        "screen_dpi": "240",
        "memory": 5944,
        "processor_details": "x86-64 SSE3 SSE4.1 SSE4.2 AVX | 2865 | 6",
        "client_ip": f"{random.randint(103, 223)}.{random.randint(10, 250)}.{random.randint(10, 250)}.{random.randint(10, 250)}",
    }

async def build_majorlogin_payload(open_id, access_token, platform, client_version, device_info):
    event_time = str(datetime.now())[:-7]
    unique_device_id = device_info.get("unique_device_id", "Google|355a357a-5a46-4487-b7ff-0d0cba22fc86")
    client_ip = device_info.get("client_ip", "105.106.22.27")

    p = bytearray()
    p += _pb_str_field(3, event_time)
    p += _pb_str_field(4, "free fire")
    p += _pb_int_field(5, 1)
    p += _pb_str_field(7, client_version)
    p += _pb_str_field(8, "Android OS 14 / API-34 (UQ1A.240205.08180011/lyb.20260818.001116)")
    p += _pb_str_field(9, "Handheld")
    p += _pb_str_field(10, "Mobilis")
    p += _pb_str_field(11, "WIFI")
    p += _pb_int_field(12, 1600)
    p += _pb_int_field(13, 900)
    p += _pb_str_field(14, "240")
    p += _pb_str_field(15, "x86-64 SSE3 SSE4.1 SSE4.2 AVX | 2865 | 6")
    p += _pb_int_field(16, 5944)
    p += _pb_str_field(17, "Adreno (TM) 750")
    p += _pb_str_field(18, "OpenGL ES 3.1 v1")
    p += _pb_str_field(19, unique_device_id)
    p += _pb_str_field(20, client_ip)
    p += _pb_str_field(21, "ar")
    p += _pb_str_field(22, open_id)
    p += _pb_str_field(23, "4")
    p += _pb_str_field(24, "Handheld")
    p += _pb_str_field(25, "samsung SM-N9860")
    p += _pb_str_field(29, access_token)
    p += _pb_int_field(30, 1)
    p += _pb_str_field(41, "Mobilis")
    p += _pb_str_field(42, "WIFI")
    p += _pb_str_field(57, "7428b253defc164018c604a1ebbfebdf")
    p += _pb_int_field(60, 52691)
    p += _pb_int_field(61, 48409)
    p += _pb_int_field(62, 2519)
    p += _pb_int_field(63, 70)
    p += _pb_int_field(64, 23306)
    p += _pb_int_field(65, 25131)
    p += _pb_int_field(66, 50733)
    p += _pb_int_field(67, 52691)
    p += _pb_int_field(73, 3)
    p += _pb_str_field(74, "/data/app/~~ssQKILR_XTH7OSEi3NCc5A==/com.dts.freefireth-0hF1N7oSc0qbJOZHhueJWQ==/lib/arm64")
    p += _pb_int_field(76, 1)
    p += _pb_str_field(77, "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~ssQKILR_XTH7OSEi3NCc5A==/com.dts.freefireth-0hF1N7oSc0qbJOZHhueJWQ==/base.apk")
    p += _pb_int_field(78, 3)
    p += _pb_int_field(79, 2)
    p += _pb_str_field(81, "64")
    p += _pb_str_field(83, "2019121229")
    p += _pb_int_field(85, 3)
    p += _pb_str_field(86, "OpenGLES2")
    p += _pb_int_field(87, 8191)
    p += _pb_int_field(88, 4)
    p += _pb_str_field(89, "KqsHT6dXfrd81vpmdClMMxZM3UCc59ys5/2cX5FVcMpI3tlWy8d0r8ZWGSBj+06/cGbBzY3JULeYT1rb5tBtz7+GCis6kpkGPjl2SSoYhrjsQOvA")
    p += _pb_int_field(92, 7303)
    p += _pb_str_field(93, "android")
    p += _pb_str_field(94, "KqsHT6dXfrd81vpmdClMMxZM3UCc59ys5/2cX5FVcMpI3tlWy8d0r8ZWGSBj+06/cGbBzY3JULeYT1rb5tBtz7+GCis6kpkGPjl2SSoYhrjsQOvA")
    p += _pb_int_field(95, 111207)
    p += _pb_str_field(96, '{"cur_rate":null,"support_etc2":false}')
    p += _pb_int_field(97, 1)
    p += _pb_int_field(98, 1)
    p += _pb_str_field(99, "4")
    p += _pb_str_field(100, "4")
    p += _pb_msg_field(102, b"")
    p += _pb_int_field(104, 62270)
    p += _pb_int_field(105, 1)
    p += _pb_str_field(106, "https://dl.gmc.freefiremobile.com/live/ABHotUpdates/|https://core-gmc.freefiremobile.com/live/ABHotUpdates/|4a0070ac356973792f002e0b25b96c3b")
    p += _pb_str_field(107, "c8e41b7a93f02d56e1a94c7b8203f5d1")

    return await aes_encrypt(bytes(p), AES_KEY, AES_IV)

class MajorLoginResult:
    def __init__(self, raw_dict, account_id=None, region=None, token=None,
                 url=None, server_time=None, aes_ak=None, iv_i=None):
        self.raw = raw_dict
        self.account_id = account_id
        self.region = region
        self.token = token
        self.url = url
        self.server_time = server_time
        self.aes_ak = aes_ak
        self.iv_i = iv_i

async def send_majorlogin(data, release_version, server_url):
    url = f"{server_url.rstrip('/')}/MajorLogin"
    hdrs = BASE_HEADERS.copy()
    hdrs["ReleaseVersion"] = release_version
    hdrs["Host"] = urlparse(url).netloc

    for attempt in range(3):
        try:
            async with new_async_client() as cli:
                r = await cli.post(url, headers=hdrs, data=data)
                if r.status_code != 200:
                    await asyncio.sleep(0.7 + attempt * 0.4)
                    continue
                content = r.content
                if len(content) < 40:
                    await asyncio.sleep(0.7 + attempt * 0.4)
                    continue

                candidates = [content]
                if len(content) > 64:
                    candidates.append(content[64:])
                for off in (1, 2, 4, 8, 16, 32, 128):
                    if off < len(content) - 40:
                        candidates.append(content[off:])

                for cand in candidates:
                    raw = parse_majorlogin_response(cand)
                    token  = raw.get(8)
                    region = raw.get(2)
                    if not (token and region):
                        continue

                    aes_ak = raw.get(22)
                    iv_i   = raw.get(23)

                    if isinstance(aes_ak, str):
                        try: aes_ak = aes_ak.encode('latin-1')
                        except Exception: aes_ak = None
                    if isinstance(iv_i, str):
                        try: iv_i = iv_i.encode('latin-1')
                        except Exception: iv_i = None

                    if not isinstance(aes_ak, (bytes, bytearray)) or len(aes_ak) not in (16, 24, 32):
                        aes_ak = None
                    if not isinstance(iv_i, (bytes, bytearray)) or len(iv_i) != 16:
                        iv_i = None

                    return MajorLoginResult(
                        raw,
                        account_id=raw.get(1),
                        region=region,
                        token=token,
                        url=raw.get(10),
                        server_time=raw.get(21, 0) or 0,
                        aes_ak=bytes(aes_ak) if aes_ak else None,
                        iv_i=bytes(iv_i) if iv_i else None,
                    )
        except Exception:
            pass
        await asyncio.sleep(0.7 + attempt * 0.4)
    return None

async def send_getlogin(data, base_url, token, release_version):
    url = f"{base_url.rstrip('/')}/GetLoginData"
    hdrs = BASE_HEADERS.copy()
    hdrs["ReleaseVersion"] = release_version
    hdrs["Authorization"] = f"Bearer {token}"
    hdrs["Host"] = "clientbp.ppmainecoonghj.com"

    for attempt in range(GLD_MAX_RETRIES):
        try:
            async with new_async_client() as cli:
                r = await cli.post(url, headers=hdrs, data=data)
                if r.status_code == 200 and len(r.content) > 20:
                    parsed = parse_getlogindata_fields(r.content)
                    if parsed.get(14) or parsed.get(32):
                        return parsed
                await asyncio.sleep(0.5 + attempt * 0.35)
        except Exception:
            await asyncio.sleep(0.5 + attempt * 0.35)
    return None

async def is_me_region(region: str) -> bool:
    return str(region).upper() in ME_REGIONS

async def build_me_online_token(account_uid, token, timestamp, key, iv):
    account_hex = f"{int(account_uid):x}".zfill(16)
    encrypted = (await aes_encrypt(token.encode(), key, iv)).hex()
    timestamp_hex = f"{int(timestamp):x}"
    if len(timestamp_hex) % 2: timestamp_hex = "0" + timestamp_hex
    token_size = f"{len(encrypted) // 2:02x}"
    return f"7a15{account_hex}{timestamp_hex}0000000000000{token_size}{encrypted}"

async def build_me_chat_token(account_uid, jwt_token, timestamp, key, iv):
    account_hex = f"{int(account_uid):x}".zfill(16)
    encrypted = (await aes_encrypt(jwt_token.encode(), key, iv)).hex()
    timestamp_hex = f"{int(timestamp):x}"
    if len(timestamp_hex) % 2: timestamp_hex = "0" + timestamp_hex
    token_size = f"{len(encrypted) // 2:02x}"
    return f"8615{account_hex}{timestamp_hex}00000{token_size}{encrypted}"

async def build_tcp_startup_packet(account_id, token, server_time, key, iv, region="ME", typ='OnLine'):
    if await is_me_region(region):
        if typ == 'OnLine':
            return await build_me_online_token(account_id, token, server_time, key, iv)
        else:
            return await build_me_chat_token(account_id, token, server_time, key, iv)
    uid_hex = f"{int(account_id):016x}"
    timestamp_hex = f"{int(server_time):08x}"
    encoded = token.encode()
    encrypted_packet = (await aes_encrypt(encoded, key, iv)).hex()
    encrypted_packet_length = f"{len(encrypted_packet) // 2:08x}"
    reg = str(region).upper() if region else "ME"
    if typ == 'OnLine':
        prefix = '7119' if reg == 'BD' else ('7114' if reg == 'IND' else '7115')
        return f"{prefix}{uid_hex}{timestamp_hex}00000000{encrypted_packet_length}{encrypted_packet}"
    else:
        prefix = '9219' if reg == 'BD' else ('9214' if reg == 'IND' else '9215')
        return f"{prefix}{uid_hex}{timestamp_hex}{encrypted_packet_length}{encrypted_packet}"

async def send_keep_alive(region="ME") -> bytes:
    try:
        reg = str(region).upper() if region else "ME"
        if reg in ME_REGIONS:
            return bytes.fromhex("0219")
        ka_hex = "0219" if reg == "BD" else ("0214" if reg == "IND" else "0215")
        return bytes.fromhex(ka_hex)
    except Exception:
        return bytes.fromhex("0219")

# ==============================================================================
# إدارة الأهداف
# ==============================================================================
def load_saved_targets():
    global spam_targets
    if os.path.exists(TARGETS_FILE):
        try:
            with open(TARGETS_FILE, "r", encoding="utf-8") as f:
                saved_list = json.load(f)
                spam_targets = set(str(x).strip() for x in saved_list if str(x).strip().isdigit())
                print(f"[+] Loaded {len(spam_targets)} targets from {TARGETS_FILE}")
        except Exception as e:
            print(f"[-] Warning reading {TARGETS_FILE}: {e}")
            spam_targets = set()

def save_targets_to_file():
    try:
        with open(TARGETS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(spam_targets), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[-] Warning saving {TARGETS_FILE}: {e}")

# ==============================================================================
# الحزم والتشفير
# ==============================================================================
def EnC_Vr(N):
    if N < 0: return b''
    H = []
    while True:
        BesTo = N & 0x7F
        N >>= 7
        if N: BesTo |= 0x80
        H.append(BesTo)
        if not N: break
    return bytes(H)

def CrEaTe_VarianT(field_number, value):
    field_header = (field_number << 3) | 0
    return EnC_Vr(field_header) + EnC_Vr(value)

def CrEaTe_LenGTh(field_number, value):
    encoded_value = value.encode('utf-8') if isinstance(value, str) else value
    field_header = (field_number << 3) | 2
    return EnC_Vr(field_header) + EnC_Vr(len(encoded_value)) + encoded_value

async def CrEaTe_ProTo(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            nested_packet = await CrEaTe_ProTo(value)
            packet.extend(CrEaTe_LenGTh(field, nested_packet))
        elif isinstance(value, int):
            packet.extend(CrEaTe_VarianT(field, value))
        elif isinstance(value, str) or isinstance(value, bytes):
            packet.extend(CrEaTe_LenGTh(field, value))
    return packet

async def safe_enc_packet(pk_hex, key, iv):
    K = bytes.fromhex(key) if isinstance(key, str) else key
    V = bytes.fromhex(iv) if isinstance(iv, str) else iv
    cipher = AES.new(K, AES.MODE_CBC, V)
    return cipher.encrypt(pad(bytes.fromhex(pk_hex), AES.block_size)).hex()

async def GeneRaTePk_Async(Pk_hex, opcode_hex, key, iv):
    enc_pkt = await safe_enc_packet(Pk_hex, key, iv)
    header_len = len(enc_pkt) // 2
    header_len_hex = hex(header_len)[2:].upper()
    if len(header_len_hex) == 2: final_packet = opcode_hex + "000000" + header_len_hex + enc_pkt
    elif len(header_len_hex) == 3: final_packet = opcode_hex + "00000" + header_len_hex + enc_pkt
    elif len(header_len_hex) == 4: final_packet = opcode_hex + "0000" + header_len_hex + enc_pkt
    elif len(header_len_hex) == 5: final_packet = opcode_hex + "000" + header_len_hex + enc_pkt
    else: final_packet = opcode_hex + "000000" + header_len_hex + enc_pkt
    return bytes.fromhex(final_packet)

async def Fix_PackEt(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {'wire_type': result.wire_type}
        if result.wire_type in ["varint", "string", "bytes"]:
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = await Fix_PackEt(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

async def DeCode_PackEt(input_text):
    try:
        parsed_results = Parser().parse(input_text)
        parsed_results_dict = await Fix_PackEt(parsed_results)
        return json.dumps(parsed_results_dict)
    except Exception:
        return None

async def get_player_status(packet):
    try:
        json_result = await DeCode_PackEt(packet)
        if not json_result: return "OFFLINE", None, None
        parsed_data = json.loads(json_result)
        data_5 = parsed_data.get("5", {}).get("data", {})
        data_1 = data_5.get("1", {}).get("data", {})
        
        if not data_1: return "OFFLINE", None, None
        status = data_1.get("3", {}).get("data")
        
        room_uid = data_1.get("15", {}).get("data") if "15" in data_1 else None

        leader_uid = None
        if "4" in data_1:
            leader_val = data_1.get("4", {}).get("data")
            if isinstance(leader_val, dict):
                leader_uid = leader_val.get("1", {}).get("data")
            elif isinstance(leader_val, (int, str)):
                leader_uid = leader_val
            
        if status is None: return "OFFLINE", room_uid, leader_uid

        if status == 1: return "SOLO", room_uid, leader_uid
        if status == 2: return "INSQUAD", room_uid, leader_uid
        if status in [3, 5]: return "INGAME", room_uid, leader_uid
        if status == 4: return "IN ROOM", room_uid, leader_uid
        if status in [6, 7]: return "SOCIAL ISLAND", room_uid, leader_uid
        return "NOTFOUND", room_uid, leader_uid
    except Exception:
        return "OFFLINE", None, None

async def createpacketinfo(idddd, key, iv):
    id_val = int(idddd)
    parts = bytearray()
    while id_val > 127:
        parts.append((id_val & 127) | 128)
        id_val >>= 7
    parts.append(id_val)
    payload_len = len(parts)
    field1 = bytearray([0x0A, payload_len]) + parts
    field2 = bytearray([0x10, 0x05])
    message2 = field1 + field2
    msg2_len = len(message2)
    packet = bytearray([0x08, 0x01, 0x12, msg2_len]) + message2
    return await GeneRaTePk_Async(packet.hex().upper(), "0F15", key, iv)

async def CreateNewSquad_Safe(key, iv):
    fields = {
        1: 1,
        2: {
            2: '011d', 3: 1, 4: 3, 5: 'ar',
            8: {1: 'IDC4', 2: 145, 3: 'ME'},
            9: 1,
            10: '01030407090a0b12191a201d2729',
            11: 1, 13: 1,
            14: {
                1: {6: 56}, 2: 731,
                3: '745d59541601024c01015f02020d0905030304570608570d57060d53540402025f5707545301060613050645775945454c18021c051e1a0306491a4760785c53477d735a53486073421b5d5841075642426f5c63610914084e1f005e721f6001467e0c51634263771f5f554642434556660104040f13050445636e74634379505365047256665e405459657766510f615a5250420d11084858416a0d7a470c720065655c5f5a0370584559584a457f43675f460c16024e477a4258430c6050417a45545c47786456597a7a7163545907714109160849667377607d0b4a07657c5c45045f5d784f5b5665096464065875620411050d4d7f7444766661406a6205545d5b5f74507e0b0b535c67580877607d0a1a0148761e795678487f7871465874697177534971666d5a7574677075550d17034503781a675e60787f4d406d7a625d57797d441b47057b026d1a685a0d1102044b0d60040d706067756547767d66777b7f46007346667e43065e5c780813074c5606764057727546596364037054674d590161467f73416209077108',
                4: 'w]ZP', 6: 11, 7: '140b7d71715b751011',
                8: CLIENT_VERSION, 9: 3, 10: 2,
                11: '0362625351363559382b505637416456324b796f566c6364724541566d46795954394b384445494d7a4b646d4b4231562f2b5a727577754a307847426c36712b38683863796b56447967524f4e3676493259347a646974684371364b73464d33724e534a4c4274594f3256565a5465786235484c324c39544a7652514c55374a525663696154544d46776e594e4b4c35353150336c5831475150635668615a77396251674b4d30395a4b6a2f4d675a38656d66757a6e4b356f5a6734367841626a7761363273366235636469637867386a6d4e4944594c383638686e756c3044316a4e445636444a4a69614758456154782b5450696c6f69476f58333638497234563266697a63783934436f5562735039765855683438356a626233356a717a5577504365554c55776374534574456d68426c3957453943524873422b76504a39704863323479517a70446c74644779536f6a6a4f573166433343413733374e617255546d734a70355431686b35635853307134557a6f7a6b75684b6d42423067354f4563634b627a68506c585943712f666a59767531624174504d766437486f4e6e39696e53767679796c6156386e315837636b7978384575626b5868414734565069425961556a75667a2b75675a474164356872324c3156615434613143485745702f6b446142364849434b756f705770706c703151373265463252744f62544957487775305a6753474659514266396f6e48744e7a5035336e72457072366f6c5349455354393839414f494858313471384d4a5763546d514267486d6c3456454c617354426d6f2b36764149525752783664617256692f345147566f4c785944593359477a366e513d3d'
            },
            19: 329, 21: '374f5219', 24: {1: 21}
        }
    }
    proto_data = await CrEaTe_ProTo(fields)
    return await GeneRaTePk_Async(proto_data.hex(), '0515', key, iv)

async def Send_InV(target_uid, key, iv):
    fields = {1: 2, 2: {1: int(target_uid), 2: "ME", 4: 1}}
    proto_data = await CrEaTe_ProTo(fields)
    return await GeneRaTePk_Async(proto_data.hex(), '0515', key, iv)

async def xshadow_SendInv(bot_uid, uid, bot_name, key, iv):
    RANDOM_AVATARS = [902000001, 902000002, 902000005, 902000010, 902000015, 902000022, 902000030, 902000045, 902000088, 902000100]
    random_avatar = random.choice(RANDOM_AVATARS)
    fields = {
        1: 33, 2: {
            1: int(uid), 2: "ME", 3: 1, 4: 1, 6: str(bot_name), 7: 330, 8: 1000, 9: 100,
            10: "DZ", 12: 1, 13: int(uid), 16: 1,
            17: {2: 159, 4: "y[WW", 6: 11, 8: CLIENT_VERSION, 9: 3, 10: 1},
            18: 306, 19: 18, 24: random_avatar,
            26: {}, 27: {1: 11, 2: int(bot_uid), 3: 999}, 28: {},
            31: {1: 1, 2: 32768}, 32: 32768,
            34: {1: int(bot_uid), 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}
        }
    }
    proto_data = await CrEaTe_ProTo(fields)
    return await GeneRaTePk_Async(proto_data.hex(), '0515', key, iv)

async def SPam_Room_Packet(target_uid, room_uid, bot_uid, bot_name, key, iv):
    RANDOM_AVATARS = [902000001, 902000002, 902000005, 902000010, 902000015]
    random_avatar = random.choice(RANDOM_AVATARS)
    fields = {
        1: 78, 2: {
            1: int(room_uid), 2: f"[FF0000]{bot_name}", 4: 330, 5: 6000, 6: 201,
            10: random_avatar, 11: int(target_uid), 12: 1,
            13: {1: 11, 2: int(bot_uid), 3: 9999},
            15: {1: 1, 2: 32768}, 16: 32768,
            18: {1: int(bot_uid), 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}
        }
    }
    proto_data = await CrEaTe_ProTo(fields)
    return await GeneRaTePk_Async(proto_data.hex(), '0E15', key, iv)

async def safe_exit_sq(squad_owner_uid, key, iv):
    fields = {1: 7, 2: {1: int(squad_owner_uid) if str(squad_owner_uid).isdigit() else 0}}
    proto_data = await CrEaTe_ProTo(fields)
    return await GeneRaTePk_Async(proto_data.hex(), '0515', key, iv)

# ==============================================================================
# TcPOnLine
# ==============================================================================
async def TcPOnLine(bot: FreeFireBot, ip, port, auth_packet_hex, reconnect_delay=1.5):
    bot.session_start = time.time()
    bot.reconnect_count = 0

    while True:
        if time.time() - bot.session_start > SESSION_LIFETIME:
            print(f"[↻] Bot {bot.uid} — session expired, refreshing...")
            return

        if bot.reconnect_count >= TCP_RECONNECT_LIMIT:
            print(f"[↻] Bot {bot.uid} — too many reconnects, refreshing login...")
            return

        try:
            resolved_ip = await resolve_host_cloudflare(ip)
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(resolved_ip, int(port)), timeout=10.0
            )
            bot.writer = writer
            bot.is_ready = True
            bot.in_squad = False
            bot.in_room = False
            bot.reconnect_count = 0

            writer.write(bytes.fromhex(auth_packet_hex))
            await writer.drain()
            print(f"[+] Bot {bot.acc_name} ({bot.uid}) Connected — Region: {bot.region}")

            async def reader_loop():
                while True:
                    data2 = await reader.read(9999)
                    if not data2:
                        return
                    hex_data = data2.hex()
                    if "0f00" in hex_data[0:4] or "0e00" in hex_data[0:4]:
                        try:
                            packett = f'08{hex_data.split("08", 1)[1]}'
                            kk = await DeCode_PackEt(packett)
                            if kk:
                                parsed = json.loads(kk)
                                if parsed.get("2", {}).get("data") in [15, 14]:
                                    status_text, room_uid, leader_uid = await get_player_status(packett)
                                    idplayer = parsed.get("5", {}).get("data", {}).get("1", {}).get("data", {}).get("1", {}).get("data")
                                    if idplayer:
                                        idplayer_str = str(idplayer)
                                        TARGET_STATUS_CACHE[idplayer_str] = status_text
                                        if room_uid:
                                            TARGET_ROOM_CACHE[idplayer_str] = str(room_uid)
                                        if leader_uid:
                                            leader_str = str(leader_uid)
                                            TARGET_LEADER_CACHE[idplayer_str] = leader_str
                        except Exception:
                            pass

            async def keepalive_loop():
                ka = await send_keep_alive(bot.region)
                while True:
                    await asyncio.sleep(TCP_KEEPALIVE_SEC)
                    try:
                        if writer.is_closing():
                            return
                        writer.write(ka)
                        await writer.drain()
                    except Exception:
                        return

            r_task = asyncio.create_task(reader_loop())
            k_task = asyncio.create_task(keepalive_loop())

            done, pending = await asyncio.wait(
                [r_task, k_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            for t in pending:
                t.cancel()
            await asyncio.gather(*pending, return_exceptions=True)

        except Exception:
            pass
        finally:
            try:
                if bot.writer:
                    bot.writer.close()
                    await bot.writer.wait_closed()
            except Exception:
                pass
            bot.writer = None
            bot.is_ready = False
            bot.in_squad = False
            bot.in_room = False

        bot.reconnect_count += 1
        print(f"[-] Bot {bot.uid} disconnected — reconnecting ({bot.reconnect_count}/{TCP_RECONNECT_LIMIT})...")
        await asyncio.sleep(reconnect_delay)

# ==============================================================================
# الـ Endpoints
# ==============================================================================
def add_target_core(uid_clean: str):
    spam_targets.add(uid_clean)
    save_targets_to_file()
    TARGET_STATUS_CACHE[uid_clean] = "CHECKING"
    return {"success": True, "status": "success", "message": f"Target {uid_clean} added to list.", "uid": uid_clean}

def stop_target_core(uid_clean: str):
    if uid_clean in spam_targets:
        spam_targets.remove(uid_clean)
        save_targets_to_file()
        TARGET_STATUS_CACHE.pop(uid_clean, None)
        TARGET_ROOM_CACHE.pop(uid_clean, None)
        TARGET_LEADER_CACHE.pop(uid_clean, None)
        return {"success": True, "status": "success", "message": f"Target {uid_clean} removed from list.", "uid": uid_clean}
    return {"success": False, "status": "failed", "message": "Target not found.", "uid": uid_clean}

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Free Fire Squad/Room Sniper",
        "active_bots": sum(1 for b in bot_pool if b.is_ready and b.writer),
        "total_bots": len(bot_pool),
        "total_targets": len(spam_targets)
    }

@app.get("/api/invite")
@app.get("/api/add")
async def add_target_api(uid: str = None, target_uid: str = None):
    chosen_uid = (uid or target_uid or "").strip()
    if not chosen_uid.isdigit():
        return {"success": False, "error": "Invalid UID format. Digits only."}
    return add_target_core(chosen_uid)

@app.get("/api/stop")
@app.get("/api/del")
@app.get("/del")
async def stop_target_api(uid: str = None, target_uid: str = None):
    chosen_uid = (uid or target_uid or "").strip()
    if not chosen_uid.isdigit():
        return {"success": False, "error": "Invalid UID format."}
    return stop_target_core(chosen_uid)

@app.get("/api/targets")
async def view_targets():
    return {
        "success": True,
        "total_targets": len(spam_targets),
        "targets": list(spam_targets),
        "cache": TARGET_STATUS_CACHE,
        "rooms": TARGET_ROOM_CACHE,
        "leaders": TARGET_LEADER_CACHE,
        "active_bots": sum(1 for b in bot_pool if b.is_ready and b.writer)
    }

@app.get("/api/status")
async def view_status_single(uid: str = None, target_uid: str = None):
    chosen_uid = (uid or target_uid or "").strip()
    if chosen_uid in TARGET_STATUS_CACHE:
        return {
            "success": True,
            "uid": chosen_uid,
            "status": TARGET_STATUS_CACHE[chosen_uid],
            "room_uid": TARGET_ROOM_CACHE.get(chosen_uid),
            "leader_uid": TARGET_LEADER_CACHE.get(chosen_uid)
        }
    return {"success": True, "uid": chosen_uid, "status": "UNKNOWN"}

@app.get("/api/clear")
async def clear_all_targets():
    spam_targets.clear()
    TARGET_STATUS_CACHE.clear()
    TARGET_ROOM_CACHE.clear()
    TARGET_LEADER_CACHE.clear()
    save_targets_to_file()
    return {"success": True, "message": "All targets cleared."}

# ==============================================================================
# فحص الحالة في الخلفية
# ==============================================================================
async def check_target(target, bot):
    try:
        if bot.is_ready and bot.writer:
            pkt = await createpacketinfo(target, bot.key, bot.iv)
            async with bot.lock:
                if bot.writer and not bot.writer.is_closing():
                    bot.writer.write(pkt)
                    await bot.writer.drain()
    except Exception:
        pass

async def background_status_updater():
    while True:
        try:
            active_bots = [b for b in bot_pool if b.is_ready and b.writer]
            all_to_check = list(spam_targets)
            if active_bots and all_to_check:
                tasks = []
                for i, target in enumerate(all_to_check):
                    b = active_bots[i % len(active_bots)]
                    tasks.append(check_target(target, b))
                chunk_size = 20
                for i in range(0, len(tasks), chunk_size):
                    await asyncio.gather(*tasks[i:i+chunk_size], return_exceptions=True)
                    await asyncio.sleep(0.08)
        except Exception:
            pass
        await asyncio.sleep(1.5)

# ==============================================================================
# نظام الإرسال
# ==============================================================================
async def target_spam_task(target_uid):
    while target_uid in spam_targets:
        status = TARGET_STATUS_CACHE.get(target_uid, "OFFLINE")

        if status in ["OFFLINE", "NOTFOUND", "UNKNOWN"] or not status:
            await asyncio.sleep(1.0)
            continue

        active_bots = [b for b in bot_pool if b.is_ready and b.writer]
        if not active_bots:
            await asyncio.sleep(1.0)
            continue

        for _ in range(8):
            if target_uid not in spam_targets: break
            status = TARGET_STATUS_CACHE.get(target_uid, "OFFLINE")
            if status in ["OFFLINE", "NOTFOUND", "UNKNOWN"] or not status:
                break

            current_leader = TARGET_LEADER_CACHE.get(target_uid)
            bot = random.choice(active_bots)
            try:
                async with bot.lock:
                    if bot.writer and not bot.writer.is_closing():
                        if status == "IN ROOM":
                            room_uid = TARGET_ROOM_CACHE.get(target_uid)
                            if room_uid:
                                room_pkt = await SPam_Room_Packet(target_uid, room_uid, bot.uid, bot.acc_name, bot.key, bot.iv)
                                bot.writer.write(room_pkt)
                                await bot.writer.drain()
                            else:
                                q_pkt = await createpacketinfo(target_uid, bot.key, bot.iv)
                                bot.writer.write(q_pkt)
                                await bot.writer.drain()
                        else:
                            if not bot.in_squad:
                                create_sq_pkt = await CreateNewSquad_Safe(bot.key, bot.iv)
                                bot.writer.write(create_sq_pkt)
                                await bot.writer.drain()
                                bot.in_squad = True
                                await asyncio.sleep(0.1)

                            inv_pkt = await Send_InV(int(target_uid), bot.key, bot.iv)
                            extra_inv = await xshadow_SendInv(int(bot.uid), int(target_uid), bot.acc_name, bot.key, bot.iv)
                            bot.writer.write(inv_pkt)
                            bot.writer.write(extra_inv)

                            if status == "INSQUAD" and current_leader and str(current_leader) != str(target_uid) and str(current_leader).isdigit():
                                l_inv_pkt = await Send_InV(int(current_leader), bot.key, bot.iv)
                                l_extra_inv = await xshadow_SendInv(int(bot.uid), int(current_leader), bot.acc_name, bot.key, bot.iv)
                                bot.writer.write(l_inv_pkt)
                                bot.writer.write(l_extra_inv)

                            await bot.writer.drain()
                            await asyncio.sleep(0.05)
                            exit_pkt = await safe_exit_sq(bot.uid, bot.key, bot.iv)
                            bot.writer.write(exit_pkt)
                            await bot.writer.drain()
                            bot.in_squad = False
            except Exception:
                bot.in_squad = False

            await asyncio.sleep(random.uniform(0.35, 0.45))

        await asyncio.sleep(1.0)

async def spam_task_manager():
    while True:
        try:
            current_targets = set(spam_targets)
            for target in current_targets:
                if target not in active_target_tasks or active_target_tasks[target].done():
                    active_target_tasks[target] = asyncio.create_task(target_spam_task(target))
            for target in list(active_target_tasks.keys()):
                if target not in current_targets:
                    active_target_tasks[target].cancel()
                    del active_target_tasks[target]
        except Exception:
            pass
        await asyncio.sleep(0.5)

# ==============================================================================
# دورة حياة البوت
# ==============================================================================
async def Bot_Worker_Loop(bot: FreeFireBot):
    while True:
        try:
            open_id, access_token, platform_id = await get_access_token(bot.uid, bot.password)
            if not open_id or not access_token:
                print(f"[-] OAuth failed: {bot.uid}")
                await asyncio.sleep(4 + random.uniform(1, 3))
                continue

            server_url = "https://loginbp.ppmainecoonghj.com"
            release_version = OB_VERSION
            client_version = DEFAULT_CLIENT_VER
            device_info = get_device_for_account(bot.uid)
            major_res = None
            payload = None

            for attempt in range(LOGIN_MAX_RETRIES):
                payload = await build_majorlogin_payload(open_id, access_token, platform_id, client_version, device_info)
                major_res = await send_majorlogin(payload, release_version, server_url)
                if major_res and major_res.token:
                    break
                await asyncio.sleep(LOGIN_RETRY_DELAY + random.uniform(0.2, 0.8))

            if not major_res or not major_res.token:
                print(f"[-] MajorLogin failed: {bot.uid}")
                await asyncio.sleep(5 + random.uniform(1, 3))
                continue

            bot.key = major_res.aes_ak if major_res.aes_ak else AES_KEY
            bot.iv  = major_res.iv_i  if major_res.iv_i  else AES_IV
            bot.region = (major_res.region or "ME").upper()
            TarGeT = major_res.account_id
            ToKen = major_res.token
            timestamp = major_res.server_time or int(time.time())

            gld = await send_getlogin(payload, major_res.url or server_url, major_res.token, release_version)
            if not gld:
                print(f"[-] GetLoginData failed: {bot.uid}")
                await asyncio.sleep(4 + random.uniform(1, 2))
                continue

            functional_addrs = gld.get(14)
            nickname = gld.get(4, f"Bot_{TarGeT}")

            if not functional_addrs:
                print(f"[-] Online Addr missing: {bot.uid}")
                await asyncio.sleep(4)
                continue

            if ':' in str(functional_addrs):
                OnLineiP, OnLineporT = str(functional_addrs).rsplit(':', 1)
            else:
                OnLineiP, OnLineporT = str(functional_addrs), '0'

            bot.acc_name = nickname or f"Bot_{TarGeT}"

            auth_online_hex = await build_tcp_startup_packet(
                int(TarGeT), ToKen, int(timestamp),
                bot.key, bot.iv,
                region=bot.region, typ='OnLine'
            )

            if not auth_online_hex:
                await asyncio.sleep(3)
                continue

            print(f"[+] Bot online: {TarGeT} | {bot.acc_name} | {bot.region}")
            await TcPOnLine(bot, OnLineiP, OnLineporT, auth_online_hex)

        except Exception as e:
            print(f"[-] Exception {bot.uid}: {e}")
            await asyncio.sleep(4 + random.uniform(1, 2))

# ==============================================================================
# تحميل الحسابات مع دعم كل الصيغ
# ==============================================================================
def load_accounts_safely(file_path):
    accounts = {}
    if not os.path.exists(file_path):
        return accounts
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if content.startswith("{") and content.endswith("}"):
            try:
                data = json.loads(content)
                for u, p in data.items():
                    accounts[str(u).strip()] = str(p).strip()
                return accounts
            except Exception:
                pass
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"): continue
            if ":" in line:
                parts = line.split(":", 1)
                u, p = parts[0].strip(), parts[1].strip()
                if u and p: accounts[u] = p
    except Exception as e:
        print(f"[-] Error reading {file_path}: {e}")
    return accounts

# ==============================================================================
# FastAPI Lifespan لتشغيل المهام على السيرفر
# ==============================================================================
@app.on_event("startup")
async def startup_event():
    load_saved_targets()
    accounts_dict = load_accounts_safely(ACCOUNTS_FILE)
    if not accounts_dict:
        print(f"[!] Warning: {ACCOUNTS_FILE} not found or empty at {ACCOUNTS_FILE}")
    else:
        print(f"[+] Loaded {len(accounts_dict)} accounts from {ACCOUNTS_FILE}")
        for uid, pw in accounts_dict.items():
            b = FreeFireBot(uid, pw)
            bot_pool.append(b)
            asyncio.create_task(Bot_Worker_Loop(b))
            await asyncio.sleep(random.uniform(STAGGER_MIN, STAGGER_MAX))

    asyncio.create_task(background_status_updater())
    asyncio.create_task(spam_task_manager())

if __name__ == '__main__':
    port_to_bind = int(os.environ.get("PORT", 8080))
    print(f"[*] Starting server on 0.0.0.0:{port_to_bind}")
    uvicorn.run(app, host="0.0.0.0", port=port_to_bind, log_level="info")
