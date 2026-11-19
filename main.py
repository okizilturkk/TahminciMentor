import threading
import analiz_motoru
from kivy.app import App
from kivy.clock import mainthread
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView


class IddaaAnalizApp(App):

  def build(self):
    self.ana_duzen = BoxLayout(orientation="vertical", padding=10, spacing=8)
    self.ana_duzen.bind(pos=self.saha_ciz, size=self.saha_ciz)

    # 1. Üst Kontrol Butonu
    self.btn_yenile = Button(
        text="Günlük Tüm Maçları Çek (Süper Lig Dahil)",
        size_hint_y=None,
        height=52,
        background_normal="",
        background_color=(0.12, 0.58, 0.30, 0.95),
        font_size="16sp",
        bold=True,
    )
    self.btn_yenile.bind(on_press=self.verileri_baslat)
    self.ana_duzen.add_widget(self.btn_yenile)

    # 2. Orta Alan: Belirgin Kaydırma Çubuklu 2 Sütunlu Maç Listesi
    self.scroll = ScrollView(
        size_hint=(1, 0.55),
        bar_width=10,
        bar_color=(0.2, 0.95, 0.45, 0.95),
        bar_inactive_color=(0.2, 0.85, 0.4, 0.70),
        scroll_type=list(("bars", "content")),
    )
    self.mac_listesi_alani = GridLayout(
        cols=2, size_hint_y=None, spacing=6, padding=(2, 2, 16, 2)
    )
    self.mac_listesi_alani.bind(
        minimum_height=self.mac_listesi_alani.setter("height")
    )
    self.scroll.add_widget(self.mac_listesi_alani)
    self.ana_duzen.add_widget(self.scroll)

    # 3. Alt Alan: Altın Çerçeveli Afilli AI Yorum Kartı
    self.alt_kart = BoxLayout(size_hint=(1, 0.37), padding=2)
    self.alt_kart.bind(pos=self.kart_ciz, size=self.kart_ciz)

    self.yorum_scroll = ScrollView(
        bar_width=8,
        bar_color=(1, 0.8, 0.2, 0.95),
        bar_inactive_color=(1, 0.8, 0.2, 0.60),
        scroll_type=list(("bars", "content")),
    )
    self.sonuc_ekrani = Label(
        text="AI maç yorumu ve analiz için yukarıdan bir maça dokunun...",
        size_hint_y=None,
        halign="left",
        valign="top",
        markup=True,
        font_size="14sp",
        padding=(10, 10),
    )
    self.sonuc_ekrani.bind(
        width=self.etiket_genislik_ayarla,
        texture_size=self.etiket_yukseklik_ayarla,
    )
    self.yorum_scroll.add_widget(self.sonuc_ekrani)
    self.alt_kart.add_widget(self.yorum_scroll)
    self.ana_duzen.add_widget(self.alt_kart)

    return self.ana_duzen

  def saha_ciz(self, instance, value):
    instance.canvas.before.clear()
    with instance.canvas.before:
      Color(0.05, 0.14, 0.08, 1)
      Rectangle(pos=instance.pos, size=instance.size)

      Color(0.07, 0.18, 0.10, 1)
      serit_yukseklik = instance.height / 8
      for i in range(0, 8, 2):
        Rectangle(
            pos=(instance.x, instance.y + i * serit_yukseklik),
            size=(instance.width, serit_yukseklik),
        )

      Color(1, 1, 1, 0.15)
      cx, cy = instance.center_x, instance.center_y
      w, h = instance.width, instance.height

      Line(
          rectangle=(instance.x + 15, instance.y + 15, w - 30, h - 30),
          width=1.5,
      )
      Line(points=(instance.x + 15, cy, instance.right - 15, cy), width=1.5)
      Line(circle=(cx, cy, min(w, h) * 0.16), width=1.5)
      Line(
          rectangle=(
              cx - w * 0.25,
              instance.top - 15 - h * 0.14,
              w * 0.5,
              h * 0.14,
          ),
          width=1.5,
      )
      Line(
          rectangle=(cx - w * 0.25, instance.y + 15, w * 0.5, h * 0.14),
          width=1.5,
      )

  def kart_ciz(self, instance, value):
    instance.canvas.before.clear()
    with instance.canvas.before:
      Color(0.03, 0.06, 0.04, 0.88)
      Rectangle(pos=instance.pos, size=instance.size)
      # Altın sarısı ince çerçeve çizgisi
      Color(0.95, 0.78, 0.20, 0.45)
      Line(
          rectangle=(instance.x, instance.y, instance.width, instance.height),
          width=1.2,
      )

  def etiket_genislik_ayarla(self, instance, genislik):
    instance.text_size = (genislik, None)

  def etiket_yukseklik_ayarla(self, instance, boyut):
    _, yukseklik = boyut
    instance.height = yukseklik

  def verileri_baslat(self, instance):
    self.btn_yenile.text = "Tüm Bülten Çekiliyor..."
    self.btn_yenile.disabled = True
    self.mac_listesi_alani.clear_widgets()
    threading.Thread(target=self.veri_thread, daemon=True).start()

  def veri_thread(self):
    maclar, hata = analiz_motoru.gunluk_maclari_getir()
    self.butonlari_olustur(maclar, hata)

  @mainthread
  def butonlari_olustur(self, maclar, hata_mesaji):
    self.btn_yenile.text = f"Bülteni Yenile ({len(maclar)} Maç)"
    self.btn_yenile.disabled = False

    if not maclar:
      self.sonuc_ekrani.text = (
          f"[color=ff4444]{hata_mesaji or 'Bugün için maç bulunamadı.'}[/color]"
      )
      return

    for mac in maclar:
      renk = (
          (0.14, 0.45, 0.25, 0.90)
          if "Turkey" in mac["lig"]
          else (0.09, 0.16, 0.12, 0.88)
      )
      btn = Button(
          text=f"{mac['kisa_baslik']}\n[size=11sp][color=cccccc]{mac['lig']}[/color][/size]",
          markup=True,
          halign="center",
          valign="middle",
          size_hint_y=None,
          height=62,
          background_normal="",
          background_color=renk,
          font_size="12sp",
      )
      btn.bind(size=btn.setter("text_size"))
      btn.bind(on_press=lambda instance, m=mac: self.analizi_baslat(m))
      self.mac_listesi_alani.add_widget(btn)

  def analizi_baslat(self, mac):
    self.sonuc_ekrani.text = (
        f"[b]{mac['baslik']}[/b]\nYapay zeka istatistikleri okuyor ve maç"
        " yorumu hazırlıyor..."
    )
    threading.Thread(
        target=self.tahmin_thread, args=(mac,), daemon=True
    ).start()

  def tahmin_thread(self, mac):
    sonuclar = analiz_motoru.mac_tahmini_getir(mac)
    self.ekrani_guncelle(mac, *sonuclar)

  @mainthread
  def ekrani_guncelle(
      self,
      mac,
      p1,
      p0,
      p2,
      tavsiye,
      ev_form,
      dep_form,
      gol_tahmini,
      ai_yorum,
  ):
    self.sonuc_ekrani.text = (
        f"[b][color=33ccff]{mac['baslik']}[/color][/b]\n"
        f"Son Form -> Ev: [b]{ev_form}[/b]  |  Dep: [b]{dep_form}[/b]  |  Gol"
        f" Çizgisi: {gol_tahmini}\n"
        f"Olasılıklar -> Ev: [b]{p1}[/b]  |  Beraberlik: [b]{p0}[/b]  |  Dep:"
        f" [b]{p2}[/b]\n"
        f"Sistem Tahmini: [b][color=00ff66]{tavsiye}[/color][/b]\n"
        "--------------------------------------------------\n"
        f"[b][color=ffcc00]AI Maç Yorumu:[/color][/b] {ai_yorum}"
    )


if __name__ == "__main__":
  IddaaAnalizApp().run()
