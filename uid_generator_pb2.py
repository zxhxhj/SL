import threading
import time
import requests
import logging
import binascii
import json
import urllib3
import random
import warnings
import os
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from cryptography.hazmat.primitives.ciphers import Cipher as Cp, algorithms as Al, modes as Md
from cryptography.hazmat.backends import default_backend as Bk
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.protobuf.timestamp_pb2 import Timestamp

# استدعاء بروتوباف تسجيل الدخول من ملفات البوت
try:
    import xMaSrY_Pb2 as pb
except ImportError:
    try:
        import xMaSrY_Pb2_2 as pb
    except ImportError:
        pb = None

warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ================== ثوابت وإعدادات OB55 الرسمية ==================
OB_VERSION = "OB55"
CLIENT_VERSION = "1.132.3"
MAJOR_HOST = "loginbp.ppmainecoonghj.com"
CLIENT_HOST = "clientbp.ppmainecoonghj.com"
GA_SV = "1789534056"

K = b"Yg&tc%DEuh6%Zc^8"
IV = b"6oyZDr22E3ychjM%"

def padB(d):
    n = 16 - (len(d) % 16)
    return d + bytes([n] * n)

def enc(b):
    c = Cp(Al.AES(K), Md.CBC(IV), backend=Bk())
    e = c.encryptor()
    return e.update(padB(b)) + e.finalize()

def decode_varint(data, pos):
    result = 0
    shift = 0
    while True:
        if pos >= len(data):
            return None, pos
        byte = data[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        shift += 7
        if not (byte & 0x80):
            break
    return result, pos

def pbD(data):
    """تحليل protobuf مع تخطي الإزاحات تلقائياً"""
    best_out = {}
    for offset in range(min(150, len(data))):
        i = offset
        out = {}
        try:
            while i < len(data):
                key, i = decode_varint(data, i)
                if key is None:
                    break
                fn, wt = key >> 3, key & 0x7
                if wt == 0:
                    v, i = decode_varint(data, i)
                    out[str(fn)] = {"t": "int", "v": v}
                elif wt == 2:
                    ln, i = decode_varint(data, i)
                    if ln is None:
                        break
                    v = data[i:i+ln]
                    i += ln
                    try:
                        out[str(fn)] = {"t": "str", "v": v.decode()}
                    except Exception:
                        out[str(fn)] = {"t": "hex", "v": v.hex()}
                elif wt == 1:
                    out[str(fn)] = {"t": "64b", "v": data[i:i+8].hex()}
                    i += 8
                elif wt == 5:
                    out[str(fn)] = {"t": "32b", "v": data[i:i+4].hex()}
                    i += 4
                else:
                    break
            if "8" in out and out["8"]["t"] == "str" and len(out["8"]["v"]) > 20:
                return out
            if len(out) > len(best_out):
                best_out = out
        except Exception:
            continue
    return best_out

def ua():
    return "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"

def gTok(u, p, max_retries=3):
    """استخراج access_token و open_id من خوادم جارينا"""
    urls = [
        "https://100067.connect.garena.com/oauth/guest/token/grant",
        "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    ]
    last_exc = None
    for attempt in range(max_retries):
        for target_url in urls:
            try:
                r = requests.post(
                    target_url,
                    headers={
                        "Host": target_url.split("https://")[1].split("/")[0],
                        "User-Agent": ua(),
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "close"
                    },
                    data={
                        "uid": str(u),
                        "password": str(p),
                        "response_type": "token",
                        "client_type": "2",
                        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
                        "client_id": "100067"
                    },
                    verify=False,
                    timeout=15
                )
                if r.status_code == 429:
                    wait = random.uniform(4, 10) * (attempt + 1)
                    logger.warning(f"⚠️ حظر مؤقت (429) للحساب {str(u)[:6]}... انتظار {wait:.1f} ثانية")
                    time.sleep(wait)
                    continue
                if r.status_code != 200:
                    continue
                d = r.json()
                if "access_token" in d and "open_id" in d:
                    return d["access_token"], d["open_id"]
            except Exception as e:
                last_exc = e
                time.sleep(1)
    raise last_exc if last_exc else Exception("فشل الحصول على توكن جارينا")

def build_major_payload(access_token, open_id):
    """بناء بايلود الدخول الحي المتوافق 100% مع OB55"""
    if pb and hasattr(pb, 'MajorLogin'):
        ml = pb.MajorLogin()
    else:
        import MajoRLoGinrEq_pb2
        ml = MajoRLoGinrEq_pb2.MajorLogin()

    ml.event_time = str(datetime.now())[:-7]
    ml.game_name = "free fire"
    ml.platform_id = 2
    ml.client_version = CLIENT_VERSION
    ml.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    ml.system_hardware = "Handheld"
    ml.telecom_operator = "Verizon"
    ml.network_type = "WIFI"
    ml.screen_width = 1920
    ml.screen_height = 1080
    ml.screen_dpi = "280"
    ml.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    ml.memory = 3003
    ml.gpu_renderer = "Adreno (TM) 640"
    ml.gpu_version = "OpenGL ES 3.1 v1.46"
    ml.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    ml.client_ip = "223.191.51.89"
    ml.language = "en"
    ml.open_id = str(open_id)

    try: ml.open_id_type = "4"
    except Exception: ml.open_id_type = 4

    ml.device_type = "Handheld"
    ml.memory_available.version = 55
    ml.memory_available.hidden_value = 81
    ml.access_token = str(access_token)
    ml.platform_sdk_id = 1
    ml.network_operator_a = "Verizon"
    ml.network_type_a = "WIFI"
    ml.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    ml.external_storage_total = 36235
    ml.external_storage_available = 31335
    ml.internal_storage_total = 2519
    ml.internal_storage_available = 703
    ml.game_disk_storage_available = 25010
    ml.game_disk_storage_total = 26628
    ml.external_sdcard_avail_storage = 32992
    ml.external_sdcard_total_storage = 36235
    ml.login_by = 3
    ml.library_path = "/data/app/com.dts.freefireth/lib/arm64"
    ml.reg_avatar = 1
    ml.library_token = "1f74b435e72dfb267bce75a21d10074a|/data/app/com.dts.freefireth/base.apk"
    ml.channel_type = 3
    ml.cpu_type = 2
    ml.cpu_architecture = "64"
    ml.client_version_code = "2019121040"
    ml.graphics_api = "OpenGLES2"
    ml.supported_astc_bitset = 16383

    try: ml.login_open_id_type = 4
    except Exception: ml.login_open_id_type = "4"

    ml.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    ml.loading_time = 13564
    ml.release_channel = "android"
    ml.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    ml.android_engine_init_flag = 110009
    ml.if_push = 1
    ml.is_vpn = 1

    try: ml.origin_platform_type = "4"
    except Exception: ml.origin_platform_type = 4
    try: ml.primary_platform_type = "4"
    except Exception: ml.primary_platform_type = 4

    return enc(ml.SerializeToString())

def gJwt(u, p, max_retries=3):
    """استخراج JWT token بنظام OB55"""
    for attempt in range(max_retries):
        try:
            logger.info(f"🔄 جاري استخراج توكن الحساب {str(u)[:6]}... (محاولة {attempt+1})")
            at, oid = gTok(u, p)
            pay = build_major_payload(at, oid)
            r = requests.post(
                f"https://{MAJOR_HOST}/MajorLogin",
                headers={
                    "Expect": "100-continue",
                    "X-Unity-Version": "2018.4.12f1",
                    "X-GA": "v1 1",
                    "ReleaseVersion": OB_VERSION,
                    "X-Ga-Sv": GA_SV,
                    "Authorization": "Bearer ",
                    "Host": MAJOR_HOST,
                    "User-Agent": ua(),
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept-Encoding": "gzip"
                },
                data=pay,
                verify=False,
                timeout=20
            )
            if r.status_code != 200:
                raise Exception(f"MajorLogin HTTP {r.status_code}")
            
            d = pbD(r.content)
            tok = d.get("8", {}).get("v", "")
            if not tok:
                raise Exception("فشل العثور على حقل التوكن بالرد")
            
            logger.info(f"✅ تم الحصول على التوكن للحساب {str(u)[:6]}...")
            return tok.strip()
        except Exception as e:
            logger.error(f"❌ خطأ الحساب {str(u)[:6]}...: {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(3, 8))
            else:
                return None

def encrypt_api(plain_text):
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(bytes.fromhex(plain_text), AES.block_size))
    return cipher_text.hex()

def Encrypt_ID(number):
    number = int(number)
    encoded_bytes = []
    while True:
        byte = number & 0x7F
        number >>= 7
        if number:
            byte |= 0x80
        encoded_bytes.append(byte)
        if not number:
            break
    return bytes(encoded_bytes).hex()

def load_accounts(file_path="accs.txt"):
    accounts = []
    if not os.path.exists(file_path):
        logger.error(f"❌ ملف {file_path} غير موجود!")
        return accounts
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        # دعم صيغة JSON
        if content.startswith("{") and content.endswith("}"):
            try:
                data = json.loads(content)
                for u, p in data.items():
                    accounts.append((str(u).strip(), str(p).strip()))
                return accounts
            except Exception:
                pass
        
        # دعم أسطر UID:PASS
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                parts = line.split(":", 1)
                u, p = parts[0].strip(), parts[1].strip()
                if u and p:
                    accounts.append((u, p))
    except Exception as e:
        logger.error(f"❌ خطأ في قراءة ملف الحسابات: {e}")
    return accounts

l9bi7e_ToK = load_accounts()

JWT_ToKeNs = {}
SpAm_RunNiNg = {}
spam_threads = {}

def MaSrY_UpdateJwt():
    """تحديث دوري ذكي لتوكنات الحسابات"""
    logger.info("🔄 بدء فحص وتحديث التوكنات في الخلفية...")
    while True:
        success_count = 0
        current_accs = load_accounts()
        for uId, PaSs in current_accs:
            try:
                token = gJwt(uId, PaSs)
                if token:
                    JWT_ToKeNs[uId] = token
                    success_count += 1
                time.sleep(random.uniform(1.5, 3.5))
            except Exception as e:
                logger.error(f"خطأ الحساب {str(uId)[:6]}: {e}")
                time.sleep(2)
        
        logger.info(f"📊 اكتملت دورة التحديث: {success_count}/{len(current_accs)} توكنات جاهزة للعمل.")
        time.sleep(random.uniform(180, 360))

def MaSrY_SendFriend(target_uid, token, account_uid):
    """إرسال طلب الصداقة بالبروتوكول الرسمي OB55"""
    try:
        enc_target = Encrypt_ID(target_uid)
        payload = f"08a7c4839f1e10{enc_target}1801"
        enc_payload = encrypt_api(payload)

        headers = {
            "Authorization": f"Bearer {token}",
            "X-Unity-Version": "2018.4.12f1",
            "X-GA": "v1 1",
            "ReleaseVersion": OB_VERSION,
            "X-Ga-Sv": GA_SV,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": ua(),
            "Host": CLIENT_HOST
        }

        response = requests.post(
            f"https://{CLIENT_HOST}/RequestAddingFriend",
            headers=headers,
            data=bytes.fromhex(enc_payload),
            timeout=10,
            verify=False
        )

        if response.status_code == 200:
            return response
        return None
    except Exception:
        return None

def MaSrY_InfiniteSpam(target_uid, session_id, accounts_list=None):
    """إرسال سبام طلبات صداقة مستمر"""
    success = 0
    failed = 0
    accounts = accounts_list if accounts_list else load_accounts()
    SpAm_RunNiNg[session_id] = True
    
    logger.info(f"🚀 بدء إرسال طلبات الصداقة للهدف: {target_uid}")
    
    while SpAm_RunNiNg.get(session_id):
        for uid, _ in accounts:
            if not SpAm_RunNiNg.get(session_id):
                break
            token = JWT_ToKeNs.get(uid)
            if not token:
                continue
            
            response = MaSrY_SendFriend(target_uid, token, uid)
            if response is None:
                failed += 1
            else:
                success += 1
            
            if (success + failed) % 15 == 0:
                update_spam_status(session_id, target_uid, success, failed)
            
            time.sleep(0.12)
    
    logger.info(f"🏁 انتهى السبام للهدف {target_uid}: نجاح {success} | فشل {failed}")
    return {"success": success, "failed": failed}

def update_spam_status(session_id, target_uid, success, failed):
    spam_threads[session_id] = {
        "target_uid": target_uid,
        "success": success,
        "failed": failed,
        "running": SpAm_RunNiNg.get(session_id, False),
        "updated_at": datetime.now().isoformat()
    }

# ================== الـ API Endpoints ==================
@app.route('/spm', methods=['GET'])
def start_spam():
    try:
        target_uid = request.args.get('uid')
        if not target_uid or not str(target_uid).isdigit():
            return jsonify({"status": "error", "message": "الاستخدام الصحيح: /spm?uid=الآيدي"}), 400
        
        session_id = f"{target_uid}_{int(time.time())}"
        
        for sid, info in spam_threads.items():
            if info.get('target_uid') == target_uid and info.get('running'):
                return jsonify({
                    "status": "error",
                    "message": f"يوجد طلب نشط بالفعل للآيدي {target_uid}",
                    "session_id": sid
                }), 409
        
        thread = threading.Thread(
            target=MaSrY_InfiniteSpam,
            args=(target_uid, session_id, None),
            daemon=True
        )
        thread.start()
        
        spam_threads[session_id] = {
            "target_uid": target_uid,
            "success": 0,
            "failed": 0,
            "running": True,
            "started_at": datetime.now().isoformat()
        }
        
        return jsonify({
            "status": "success",
            "message": f"✅ بدأ إرسال الطلبات بنجاح على {target_uid}",
            "session_id": session_id,
            "active_tokens": len(JWT_ToKeNs)
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/stp', methods=['GET'])
def stop_spam():
    try:
        target_uid = request.args.get('uid')
        if not target_uid:
            return jsonify({"status": "error", "message": "الاستخدام الصحيح: /stp?uid=الآيدي"}), 400
        
        stopped_sessions = []
        for sid, info in spam_threads.items():
            if info.get('target_uid') == target_uid and SpAm_RunNiNg.get(sid):
                SpAm_RunNiNg[sid] = False
                stopped_sessions.append(sid)
        
        if stopped_sessions:
            return jsonify({
                "status": "success",
                "message": f"🛑 تم إيقاف {len(stopped_sessions)} جلسة بنجاح",
                "sessions": stopped_sessions
            }), 200
        
        return jsonify({"status": "error", "message": "❌ لا توجد جلسة نشطة لهذا الآيدي"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    try:
        target_uid = request.args.get('uid')
        if target_uid:
            sessions = [{"session_id": sid, **info} for sid, info in spam_threads.items() 
                       if info.get('target_uid') == target_uid]
            return jsonify({"status": "success", "data": sessions}), 200
        
        active = {sid: info for sid, info in spam_threads.items() if info.get('running')}
        return jsonify({
            "status": "success",
            "active_sessions_count": len(active),
            "active_tokens": len(JWT_ToKeNs),
            "total_accounts": len(load_accounts()),
            "data": active
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/tokens', methods=['GET'])
def show_tokens():
    accs = load_accounts()
    return jsonify({
        "total_accounts": len(accs),
        "active_tokens": len(JWT_ToKeNs),
        "status": "جاري التحديث..." if len(JWT_ToKeNs) == 0 else f"{len(JWT_ToKeNs)} توكن نشط"
    }), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "FreeFire Spam API (OB55 Ultra)",
        "status": "running",
        "commands": {
            "start": "/spm?uid=123456789",
            "stop": "/stp?uid=123456789", 
            "status": "/status?uid=123456789",
            "tokens": "/tokens"
        }
    }), 200

if __name__ == "__main__":
    threading.Thread(target=MaSrY_UpdateJwt, daemon=True).start()
    time.sleep(1)
    port = int(os.environ.get("PORT", 10913))
    print("=" * 55)
    print(f"✅ FreeFire Spam API (OB55) is Running on port {port}!")
    print("=" * 55)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
