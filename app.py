import requests
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
# Canlı ortamda (production) tüm kaynaklara erişimi kapatmak için origins parametresini kullanın
# Örnek: CORS(app, origins=["https://example.com"])
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
        # Geliştirme ortamı için verify=False kullanılıyor. Canlı sunucuda (production) kaldırılması şiddetle önerilir.
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

    base_url_1 = "https://hanedansystem.alwaysdata.net/hanesiz"
    base_url_2 = "https://api.hexnox.pro/sowixapi"
    
    base_url = base_url_1 if api == "1" else base_url_2

    # --- Sorgu URL'lerini yönetmek için sözlük (dictionary) kullanımı ---
    # Kodun bakımı ve yeni sorgu eklenmesi çok daha kolay hale gelir.
    sorgu_urls = {
        "1": f"{base_url}/sulale.php?tc={tc}",
        "2": f"{base_url}/tc.php?tc={tc}" if api == "1" else f"{base_url}/tcpro.php?tc={tc}",
        "3": f"{base_url}/adres.php?tc={tc}",
        "4": f"{base_url}/adsoyad.php?ad={ad}&soyad={soyad}&il={il}" if api == "1" else f"{base_url}/adsoyadilce.php?ad={ad}&soyad={soyad}&il={il}",
        "5": f"{base_url}/aile.php?tc={tc}",
        "6": f"{base_url}/gsmtc.php?gsm={gsm}" if api == "1" else f"{base_url}/gsmdetay.php?gsm={gsm}",
        "7": f"{base_url}/tcgsm.php?tc={tc}",
        "8": f"{base_url}/diploma/diploma.php?tc={tc}",
        "9": f"{base_url}/ayak.php?tc={tc}",
        "10": f"{base_url}/boy.php?tc={tc}",
        "11": f"{base_url}/burc.php?tc={tc}",
        "12": f"{base_url}/cm.php?tc={tc}",
        "13": f"{base_url}/cocuk.php?tc={tc}",
        "14": f"{base_url}/anne.php?tc={tc}",
        "15": f"{base_url}/ehlt.php?tc={tc}",
        "16": f"{base_url}/imei.php?imei={imei}",
        "17": f"{base_url}/operator.php?gsm={gsm}",
        "18": f"{base_url}/telegram_sorgu.php?username={username}",
        "19": f"{base_url}/hikaye.php?tc={tc}",
        "20": "https://hexnox.pro/sowix/vesika.php?tc={tc}",
        "21": f"{base_url}/hane.php?tc={tc}",
        "22": f"{base_url}/muhallev.php?tc={tc}",
        "23": "https://hexnox.pro/sowixfree/lgs/lgs.php?tc={tc}",
        "24": "https://hexnox.pro/sowixfree/plaka.php?plaka={plaka}",
        "25": "https://www.instagram.com/by_.r4t/posts/?l=1",
        "26": "https://hexnox.pro/sowixfree/sertifika.php?tc={tc}",
        "27": "https://hexnox.pro/sowixfree/üni.php?tc={tc}",
        "28": "https://hexnox.pro/sowixfree/aracparca.php?plaka={plaka}",
        "29": "https://hexnox.pro/sowixfree/şehit.php?Ad={ad}&Soyad={soyad}",
        "30": "https://hexnox.pro/sowixfree/interpol.php?ad={ad}&soyad={soyad}",
        "31": "https://hexnox.pro/sowixfree/personel.php?tc={tc}",
        "32": "https://hexnox.pro/sowixfree/internet.php?tc={tc}",
        "33": "https://hexnox.pro/sowixfree/nvi.php?tc={tc}",
        "34": "https://hexnox.pro/sowixfree/nezcane.php?il={il}&ilce={ilce}",
        "35": "https://hexnox.pro/sowixfree/basvuru/basvuru.php?tc={tc}",
        "36": "https://hexnox.pro/sowixfree/police/police.php?tc={tc}",
        "37": f"{base_url}/tapu.php?tc={tc}",
        "38": f"{base_url}/okulno.php?tc={tc}",
        "39": f"{base_url}/isyeriyetkili.php?tc={tc}",
        "40": f"{base_url}/isyeri.php?tc={tc}"
    }

    url = sorgu_urls.get(sorgu_tipi)

    # --- İstediğiniz özel filtreleme kuralı (sorgu tipi 4) ---
    if sorgu_tipi == "4":
        tam_isim = f"{ad.lower()} {soyad.lower()}"
        if tam_isim in ["bayram çetin", "idris çetin", "tuba çetin"] and il.lower() == "erzurum":
            return jsonify(success=False, message="Veri bulunamadı.")
            
        url = sorgu_urls["4"]
    
    # --- Kombine sorgu için özel durum (sorgu tipi 41) ---
    elif sorgu_tipi == "41":
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

    # Eğer sorgu tipi sözlükte bulunmuyorsa hata döndür
    if not url:
        return jsonify(success=False, message="Geçersiz sorgu tipi"), 400

    # Diğer tüm sorgular için ortak işlev
    return sorgu_isteği_yap(url, headers)

if __name__ == "__main__":
    # Canlı sunucuda (production) debug=True ayarı KAPATILMALIDIR.
    # Güvenlik açığı yaratır!
    app.run(host="0.0.0.0", port=5000, debug=False)
