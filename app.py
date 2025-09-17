import requests
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
CORS(app)

# Gelen veriyi temizleyen ve istenmeyen ifadeleri kaldıran fonksiyon
def filtrele_veri(metin):
    if not isinstance(metin, str):
        return ""

    istenmeyen_ifadeler = ["GEÇERSİZ", "HATA", "BULUNAMADI", "NOT FOUND", "ERROR", "hata"]
    
    satirlar = metin.strip().splitlines()
    temiz_satirlar = []
    
    for s in satirlar:
        s = s.strip()
        # Satır boşsa veya istenmeyen bir ifade içeriyorsa atla
        if not s or any(ifade in s.upper() for ifade in istenmeyen_ifadeler):
            continue
        # ID, Telegram gibi özel anahtar kelimeleri içeren satırları filtrele
        if "id:" in s.lower() or "telegram" in s.lower() or "kullaniciadi:" in s.lower() or "link:" in s.lower():
            continue
        # Gereksiz boşlukları ve karakterleri temizle
        s = s.replace(":", ": ").replace("  ", " ").strip()
        temiz_satirlar.append(s)

    return "\n".join(temiz_satirlar)

# API isteklerini yöneten ve hata yakalayan merkezi fonksiyon
def sorgu_isteği_yap(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=90, verify=False)
        
        # HTTP hatalarını yakala (örn. 404, 500)
        response.raise_for_status() 

        # Gelen veriyi filtrele
        filtrelenmis = filtrele_veri(response.text)
        
        if filtrelenmis:
            return jsonify(success=True, result=filtrelenmis)
        else:
            return jsonify(success=False, message="Veri bulunamadı veya geçersiz. Lütfen girdiğiniz bilgileri kontrol edin.")
    
    except requests.exceptions.HTTPError as http_err:
        return jsonify(success=False, message=f"API hatası: {http_err.response.status_code} - API sunucusuyla bağlantı kurulamıyor. Lütfen daha sonra tekrar deneyin."), http_err.response.status_code
    except requests.exceptions.RequestException as req_err:
        return jsonify(success=False, message=f"İstek hatası: API ile iletişim kurulamadı. Sunucu adresi yanlış olabilir."), 500

@app.route("/")
def anasayfa():
    return send_from_directory(".", "anasayfa.html")

@app.route("/admin")
def admin():
    return send_from_directory(".", "admin.html")

@app.route("/api/sorgu", methods=["POST"])
def sorgu():
    data = request.json
    api = data.get("api")
    sorgu_tipi = data.get("sorgu")
    headers = data.get("headers", {})

    tc = data.get("tc", "")
    gsm = data.get("gsm", "")
    ad = data.get("ad", "")
    soyad = data.get("soyad", "")
    il = data.get("il", "")
    imei = data.get("imei", "")
    username = data.get("username", "")
    plaka = data.get("plaka", "")
    ilce = data.get("ilce", "")

    url = ""
    base_url = "https://hanedansystem.alwaysdata.net/hanesiz" if api == "1" else "https://api.hexnox.pro/sowixapi"

    if sorgu_tipi == "1":
        url = f"{base_url}/sulale.php?tc={tc}"
    elif sorgu_tipi == "2":
        url = f"{base_url}/tc.php?tc={tc}" if api == "1" else f"{base_url}/tcpro.php?tc={tc}"
    elif sorgu_tipi == "3":
        url = f"{base_url}/adres.php?tc={tc}"
    elif sorgu_tipi == "4":
        # Bu kısım, yeni eklenen filtreleme kuralıdır
        tam_isim = f"{ad.lower()} {soyad.lower()}"
        if tam_isim in ["bayram çetin", "idris çetin", "tuba çetin"] and il.lower() == "erzurum":
            return jsonify(success=False, message="Veri bulunamadı.")
            
        url = f"{base_url}/adsoyad.php?ad={ad}&soyad={soyad}&il={il}" if api == "1" else f"{base_url}/adsoyadilce.php?ad={ad}&soyad={soyad}&il={il}"
    elif sorgu_tipi == "5":
        url = f"{base_url}/aile.php?tc={tc}"
    elif sorgu_tipi == "6":
        url = f"{base_url}/gsmtc.php?gsm={gsm}" if api == "1" else f"{base_url}/gsmdetay.php?gsm={gsm}"
    elif sorgu_tipi == "7":
        url = f"{base_url}/tcgsm.php?tc={tc}"
    elif sorgu_tipi == "8":
        url = f"{base_url}/diploma/diploma.php?tc={tc}"
    elif sorgu_tipi == "9":
        url = f"{base_url}/ayak.php?tc={tc}"
    elif sorgu_tipi == "10":
        url = f"{base_url}/boy.php?tc={tc}"
    elif sorgu_tipi == "11":
        url = f"{base_url}/burc.php?tc={tc}"
    elif sorgu_tipi == "12":
        url = f"{base_url}/cm.php?tc={tc}"
    elif sorgu_tipi == "13":
        url = f"{base_url}/cocuk.php?tc={tc}"
    elif sorgu_tipi == "14":
        url = f"{base_url}/anne.php?tc={tc}"
    elif sorgu_tipi == "15":
        url = f"{base_url}/ehlt.php?tc={tc}"
    elif sorgu_tipi == "16":
        url = f"{base_url}/imei.php?imei={imei}"
    elif sorgu_tipi == "17":
        url = f"{base_url}/operator.php?gsm={gsm}"
    elif sorgu_tipi == "18":
        url = f"{base_url}/telegram_sorgu.php?username={username}"
    elif sorgu_tipi == "19":
        url = f"{base_url}/hikaye.php?tc={tc}"
    elif sorgu_tipi == "20":
        url = f"https://hexnox.pro/sowix/vesika.php?tc={tc}"
    elif sorgu_tipi == "21":
        url = f"{base_url}/hane.php?tc={tc}"
    elif sorgu_tipi == "22":
        url = f"{base_url}/muhallev.php?tc={tc}"
    elif sorgu_tipi == "23":
        url = f"https://hexnox.pro/sowixfree/lgs/lgs.php?tc={tc}"
    elif sorgu_tipi == "24":
        url = f"https://hexnox.pro/sowixfree/plaka.php?plaka={plaka}"
    elif sorgu_tipi == "25":
        url = "https://www.instagram.com/by_.r4t/posts/?l=1"
    elif sorgu_tipi == "26":
        url = f"https://hexnox.pro/sowixfree/sertifika.php?tc={tc}"
    elif sorgu_tipi == "27":
        url = f"https://hexnox.pro/sowixfree/üni.php?tc={tc}"
    elif sorgu_tipi == "28":
        url = f"https://hexnox.pro/sowixfree/aracparca.php?plaka={plaka}"
    elif sorgu_tipi == "29":
        url = f"https://hexnox.pro/sowixfree/şehit.php?Ad={ad}&Soyad={soyad}"
    elif sorgu_tipi == "30":
        url = f"https://hexnox.pro/sowixfree/interpol.php?ad={ad}&soyad={soyad}"
    elif sorgu_tipi == "31":
        url = f"https://hexnox.pro/sowixfree/personel.php?tc={tc}"
    elif sorgu_tipi == "32":
        url = f"https://hexnox.pro/sowixfree/internet.php?tc={tc}"
    elif sorgu_tipi == "33":
        url = f"https://hexnox.pro/sowixfree/nvi.php?tc={tc}"
    elif sorgu_tipi == "34":
        url = f"https://hexnox.pro/sowixfree/nezcane.php?il={il}&ilce={ilce}"
    elif sorgu_tipi == "35":
        url = f"https://hexnox.pro/sowixfree/basvuru/basvuru.php?tc={tc}"
    elif sorgu_tipi == "36":
        url = f"https://hexnox.pro/sowixfree/police/police.php?tc={tc}"
    elif sorgu_tipi == "37":
        url = f"{base_url}/tapu.php?tc={tc}"
    elif sorgu_tipi == "38":
        url = f"{base_url}/okulno.php?tc={tc}"
    elif sorgu_tipi == "39":
        url = f"{base_url}/isyeriyetkili.php?tc={tc}"
    elif sorgu_tipi == "40":
        url = f"{base_url}/isyeri.php?tc={tc}"
    elif sorgu_tipi == "41":
        # Kombine sorgu için özel durum
        results = {}
        sorgular = [
            ("sulale", f"{base_url}/sulale.php?tc={tc}"),
            ("tc", f"{base_url}/tc.php?tc={tc}" if api == "1" else f"{base_url}/tcpro.php?tc={tc}"),
            ("adres", f"{base_url}/adres.php?tc={tc}"),
            ("aile", f"{base_url}/aile.php?tc={tc}")
        ]

        for ad, sorgu_url in sorgular:
            response = requests.get(sorgu_url, headers=headers, timeout=90, verify=False)
            if response.status_code == 200:
                results[ad] = filtrele_veri(response.text)
            else:
                results[ad] = f"Hata: {response.status_code} - {response.reason}"
        
        return jsonify(success=True, results=results)
    else:
        return jsonify(success=False, message="Geçersiz sorgu tipi"), 400

    # Diğer tüm sorgular için ortak işlev
    return sorgu_isteği_yap(url, headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
