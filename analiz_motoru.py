from datetime import datetime
import random
import requests

API_KEY = "b64354cd9aa5a941c0bb0d88805e533b"


def gunluk_maclari_getir():
  cekilen_maclar = []
  hata_mesaji = ""

  try:
    bugun = datetime.now().strftime("%Y-%m-%d")
    url = "https://" + "v3.football." + "api-sports.io" + "/fixtures"
    headers = {"x-apisports-key": API_KEY}
    params = {"date": bugun, "timezone": "Europe/Istanbul"}

    res = requests.get(url, headers=headers, params=params, timeout=15)
    if res.status_code == 200:
      veri = res.json()
      if veri.get("errors"):
        hata_mesaji = f"API Uyarısı: {veri.get('errors')}"
      else:
        turkiye_maclari, diger_maclar = [], []
        for f in veri.get("response", []):
          fix = f.get("fixture", {})
          lg = f.get("league", {})
          tm = f.get("teams", {})

          tarih_tam = fix.get("date", "")
          saat = tarih_tam[11:16] if len(tarih_tam) >= 16 else "--:--"
          ulke = lg.get("country", "")
          ev = tm.get("home", {}).get("name", "Ev")
          dep = tm.get("away", {}).get("name", "Dep")

          mac_obj = {
              "id": fix.get("id"),
              "baslik": f"({saat}) {ev} - {dep}",
              "kisa_baslik": f"({saat}) {ev}\nvs {dep}",
              "ev": ev,
              "dep": dep,
              "lig": f"{ulke} - {lg.get('name', 'Lig')}",
          }
          if ulke == "Turkey":
            turkiye_maclari.append(mac_obj)
          else:
            diger_maclar.append(mac_obj)

        cekilen_maclar = turkiye_maclari + diger_maclar
    else:
      hata_mesaji = f"Sunucu Hatası ({res.status_code})"
  except Exception as e:
    hata_mesaji = f"Bağlantı Hatası: {str(e)}"

  return cekilen_maclar, hata_mesaji


def turkce_cevir(metin):
  if not metin:
    return "Standart Analiz"
  sozluk = {
      "Double chance :": "Çifte Şans:",
      "Winner :": "Maç Sonucu:",
      "Combo Double chance :": "Kombo Çifte Şans:",
      "Combo Winner :": "Kombo Maç Sonucu:",
      "Home or Draw": "1X (Ev veya Beraberlik)",
      "Draw or Away": "X2 (Beraberlik veya Dep)",
      "Home or Away": "12 (Ev veya Dep)",
      "draw or ": "Beraberlik veya ",
      " or draw": " veya Beraberlik",
      "Home": "MS 1 (Ev Sahibi)",
      "Away": "MS 2 (Deplasman)",
      "Draw": "MS 0 (Beraberlik)",
      "No predictions available": "Yeterli veri yok",
      "goals": "gol",
      "and": "ve",
      "over": "Üst",
      "under": "Alt",
  }
  for ing, tr in sozluk.items():
    metin = metin.replace(ing, tr)
  return metin


def akilli_mentor_yorumu(
    mac, p1_str, p0_str, p2_str, ev_form, dep_form, comp, gol_tahmini, h2h_list
):
  try:
    y1 = int(str(p1_str).replace("%", "").strip() or 33)
    y0 = int(str(p0_str).replace("%", "").strip() or 33)
    y2 = int(str(p2_str).replace("%", "").strip() or 33)
  except Exception:
    y1, y0, y2 = 33, 33, 33

  girisler = [
      f"Bak kanka, {mac['ev']} - {mac['dep']} maçının verilerini masaya"
      " yatırdığımızda tablo çok net konuşuyor.",
      "Bu karşılaşma tam bir taktik savaşına gebe; gel birlikte rakamların"
      " satır aralarını okuyalım.",
      f"İstatistik motorunu kurcaladım, {mac['ev']} ile {mac['dep']}"
      " arasındaki güç dengesinde dikkat çekici detaylar var.",
  ]
  parcalar = [random.choice(girisler)]

  # 1. Maçın Senaryosu ve Güç Dengesi
  if y1 >= 55:
    parcalar.append(
        f"{mac['ev']} hem taraftar desteğini hem de kağıt üzerindeki kalite"
        f" farkını arkasına almış durumda (%{y1}). Maça baskılı başlayıp erken"
        " skor bulmaları şaşırtmaz."
    )
  elif y2 >= 55:
    parcalar.append(
        f"Deplasman olmasına rağmen {mac['dep']} bu maçın ağır favorisi (%{y2})."
        " Geçiş oyununu çok iyi oynuyorlar ve hata affetmeyeceklerdir."
    )
  elif y0 >= 40 and abs(y1 - y2) <= 10:
    parcalar.append(
        "İki takım da birbirini tartarak oynayacaktır; ne ev sahibi tam"
        " üstünlük kurabiliyor ne de deplasman kolay teslim oluyor. Maçın"
        f" berabere bitme ihtimali (%{y0}) masada çok güçlü duruyor."
    )
  else:
    onde = mac["ev"] if y1 > y2 else mac["dep"]
    geride = mac["dep"] if y1 > y2 else mac["ev"]
    parcalar.append(
        f"Kağıt üzerinde {onde} bir adım önde görünse de {geride} kolay pes"
        " edecek bir ekip değil; tek farklı veya son dakikalarda çözülecek"
        " gergin bir 90 dakika bizi bekliyor."
    )

  # 2. Form ve Psikolojik Durum Analizi
  if ev_form and ev_form != "-":
    w_ev = ev_form.count("W")
    l_ev = ev_form.count("L")
    if w_ev >= 4:
      parcalar.append(
          f"Özellikle {mac['ev']} son 5 maçta {w_ev} galibiyetle adeta"
          " özgüven patlaması yaşıyor."
      )
    elif l_ev >= 3:
      parcalar.append(
          f"Öte yandan {mac['ev']} cephesinde işler yolunda gitmiyor; son"
          f" haftalardaki {l_ev} mağlubiyet takım üzerinde ciddi baskı"
          " yaratmış."
      )

  if dep_form and dep_form != "-":
    w_dep = dep_form.count("W")
    l_dep = dep_form.count("L")
    if w_dep >= 3:
      parcalar.append(
          f"{mac['dep']} ise son maçlardaki istikrarlı çizgisiyle dış sahada"
          " bile kolay lokma olmadığını kanıtladı."
      )
    elif l_dep >= 3:
      parcalar.append(
          f"{mac['dep']} deplasman karnesi alarm veriyor, savunma arkasına"
          " atılan toplarda çok kolay pozisyon veriyorlar."
      )

  # 3. Kafa Kafaya (H2H) Geçmiş Analizi
  if h2h_list and len(h2h_list) >= 2:
    parcalar.append(
        "Aralarındaki geçmiş rekabete baktığımızda da birbirlerini iyi tanıyan"
        " iki ekip görüyoruz."
    )

  # 4. Mentor Kupon Tavsiyesi
  att_h = int(str(comp.get("att", {}).get("home", "50%")).replace("%", "") or 50)
  att_a = int(str(comp.get("att", {}).get("away", "50%")).replace("%", "") or 50)

  if (att_h + att_a) >= 120 or "+" in str(gol_tahmini):
    parcalar.append(
        "Mentor Tavsiyesi: İki takımın da hücum iştahı açık; taraf bahsi"
        " yerine gollere yönelmek (1.5 Üst / 2.5 Üst) çok daha akıllıca bir"
        " hamle olur."
    )
  elif y1 >= 55 or y2 >= 55:
    favori = mac["ev"] if y1 > y2 else mac["dep"]
    parcalar.append(
        f"Mentor Tavsiyesi: Macera aramaya gerek yok, {favori} galibiyeti"
        " kuponlarda sağlam bir liman gibi duruyor."
    )
  else:
    parcalar.append(
        "Mentor Tavsiyesi: Bu tarz dengeli maçlarda doğrudan taraf seçmek"
        " risklidir; çifte şans ile kendini sağlama almanı öneririm."
    )

  return " ".join(parcalar)


def mac_tahmini_getir(mac):
  p1, p0, p2 = "33%", "33%", "33%"
  tavsiye, ev_form, dep_form, gol_tahmini, ai_yorum = (
      "Veri bekleniyor",
      "-",
      "-",
      "-",
      "",
  )

  try:
    url = "https://" + "v3.football." + "api-sports.io" + "/predictions"
    headers = {"x-apisports-key": API_KEY}
    res = requests.get(
        url, headers=headers, params={"fixture": mac["id"]}, timeout=12
    )

    if res.status_code == 200:
      resp_list = res.json().get("response", [])
      if resp_list:
        data = next(iter(resp_list))
        pred = data.get("predictions", {})
        percent = pred.get("percent", {})

        p1 = percent.get("home", "33%")
        p0 = percent.get("draw", "33%")
        p2 = percent.get("away", "33%")
        tavsiye = turkce_cevir(pred.get("advice", "Analiz Tamamlandı"))
        gol_tahmini = pred.get("under_over") or "Standart"

        teams = data.get("teams", {})
        ef = teams.get("home", {}).get("league", {}).get("form", "-") or "-"
        df = teams.get("away", {}).get("league", {}).get("form", "-") or "-"
        ev_form = ef[-5:] if len(ef) > 5 else ef
        dep_form = df[-5:] if len(df) > 5 else df

        ai_yorum = akilli_mentor_yorumu(
            mac,
            p1,
            p0,
            p2,
            ev_form,
            dep_form,
            data.get("comparison", {}),
            gol_tahmini,
            data.get("h2h", []),
        )
    else:
      tavsiye = f"API Hatası ({res.status_code})"
  except Exception as e:
    tavsiye = f"Hata: {str(e)}"

  return p1, p0, p2, tavsiye, ev_form, dep_form, gol_tahmini, ai_yorum
