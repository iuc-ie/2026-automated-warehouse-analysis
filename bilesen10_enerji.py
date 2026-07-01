# -*- coding: utf-8 -*-
"""
BİLEŞEN 10: Enerji Tüketim Profili Karşılaştırması
Manuel Forkliftli Depo vs Four-Way Otomatik Depo
Raftürk Vaka Çalışması

Metodoloji:
  - Bileşen bazlı enerji modelleme (bottom-up approach)
  - Endüstri referansları: Duffield & Humphreys (2020), IEA (2023)
  - Forklift enerji: EPTA (European Power Tools Association) + Toyota specs
  - Shuttle enerji: Mao ve diğ. (2023) + üretici katalog verileri

⚠️ RAFTÜRK'TEN GÜNCELLENECEK: Gerçek enerji faturaları, tarife bilgileri

Spyder IDE: F5 ile çalıştır
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings('ignore')

print("╔═══════════════════════════════════════════════════════════╗")
print("║  BİLEŞEN 10: Enerji Tüketim Profili Karşılaştırması     ║")
print("║  Raftürk — Manuel vs Four-Way Depo                       ║")
print("╚═══════════════════════════════════════════════════════════╝")

# =============================================================================
# 1. GENEL PARAMETRELER
# =============================================================================
YILLIK_GUN = 312          # iş günü/yıl
GUNLUK_SAAT = 16          # saat/gün (2 vardiya)
YILLIK_SAAT = YILLIK_GUN * GUNLUK_SAAT  # 4992 saat

# ⚠️ RAFTÜRK'TEN GÜNCELLENECEK
ELEKTRIK_BIRIM_FIYAT = 0.10  # USD/kWh (Türkiye sanayi tarifesi ortalaması, 2024)
# Kaynak: EPDK sanayi tarifesi → ~3.5 TL/kWh ≈ 0.10 USD/kWh

# =============================================================================
# 2. MANUEL SİSTEM ENERJİ BİLEŞENLERİ
# =============================================================================
# Endüstri standardı: Depo forkliftleri %80+ elektrikli (akülü)
# Kaynak: Industrial Truck Association (ITA) 2023 raporu

# ⚠️ RAFTÜRK'TEN GÜNCELLENECEK — şu an endüstri ortalamaları
manuel_enerji = {
    'Elektrikli Forklift (şarj)': {
        'adet': 3,
        'birim_kw': 7.5,         # kW (48V akü, 15 kWh kapasiteli forklift şarjı)
        'kullanim_orani': 0.65,  # %65 aktif kullanım (boşta, mola, bekleme hariç)
        'kaynak': 'Toyota 8FBMT25 teknik şartname; ITA (2023)'
    },
    'Depo Aydınlatma': {
        'adet': 1,
        'birim_kw': 12.0,        # kW (60.940×54.710 mm² tesis, LED armatür)
        'kullanim_orani': 1.0,   # Çalışma süresince sürekli açık
        'kaynak': 'ASHRAE 90.1 depo aydınlatma standardı'
    },
    'Depo HVAC/Havalandırma': {
        'adet': 1,
        'birim_kw': 8.0,         # kW (havalandırma fanları, ısıtıcı değil)
        'kullanim_orani': 0.70,  # Sezonluk değişkenlik
        'kaynak': 'ASHRAE depo havalandırma kılavuzu'
    },
    'Ofis/IT Ekipmanları': {
        'adet': 1,
        'birim_kw': 2.0,         # kW (bilgisayar, yazıcı, aydınlatma)
        'kullanim_orani': 0.80,
        'kaynak': 'Endüstri ortalaması'
    },
}

# =============================================================================
# 3. FOUR-WAY SİSTEM ENERJİ BİLEŞENLERİ
# =============================================================================
fourway_enerji = {
    'Shuttle Araçları (MAXLINK)': {
        'adet': 6,
        'birim_kw': 1.2,         # kW (Li-ion, yüklü çalışma ortalaması)
        'kullanim_orani': 0.75,  # %75 aktif hareket (şarj istasyonu dönüşü dahil)
        'kaynak': 'Mao ve diğ. (2023); üretici MAXLINK kataloğu'
    },
    'Asansör Mekanizmaları': {
        'adet': 4,
        'birim_kw': 5.5,         # kW (kaldırma motoru, fren sistemi)
        'kullanim_orani': 0.50,  # %50 — sürekli çalışmaz, çevrim bazlı
        'kaynak': 'AS/RS asansör endüstri ortalaması'
    },
    'Konveyör/Transfer Hattı': {
        'adet': 1,
        'birim_kw': 3.0,         # kW
        'kullanim_orani': 0.60,
        'kaynak': 'Endüstri ortalaması'
    },
    'WCS/WMS Sunucu + Kontrol': {
        'adet': 1,
        'birim_kw': 2.5,         # kW (sunucu + switch + UPS)
        'kullanim_orani': 1.0,   # 24/7 çalışır
        'kaynak': 'Veri merkezi enerji kılavuzu'
    },
    'Sensör/RFID/Ağ Altyapısı': {
        'adet': 1,
        'birim_kw': 0.8,         # kW
        'kullanim_orani': 1.0,
        'kaynak': 'Endüstri ortalaması'
    },
    'Depo Aydınlatma (Azaltılmış)': {
        'adet': 1,
        'birim_kw': 6.0,         # kW — otomatik depoda insan trafiği az, aydınlatma %50 azaltılabilir
        'kullanim_orani': 0.80,  # Hareket sensörlü, sadece bakım alanlarında tam
        'kaynak': 'ASHRAE 90.1; Low ve diğ. (2024)'
    },
    'HVAC/Havalandırma': {
        'adet': 1,
        'birim_kw': 8.0,
        'kullanim_orani': 0.70,
        'kaynak': 'ASHRAE depo havalandırma kılavuzu'
    },
    'Ofis/IT Ekipmanları': {
        'adet': 1,
        'birim_kw': 2.5,         # Manuel'den biraz fazla (WMS operatör terminali)
        'kullanim_orani': 0.80,
        'kaynak': 'Endüstri ortalaması'
    },
}

# =============================================================================
# 4. BİLEŞEN BAZLI HESAPLAMA
# =============================================================================
def hesapla_enerji(bilesenleri):
    detaylar = []
    for isim, v in bilesenleri.items():
        gucluk = v['adet'] * v['birim_kw'] * v['kullanim_orani']  # kW efektif
        gunluk = gucluk * GUNLUK_SAAT                              # kWh/gün
        yillik = gucluk * YILLIK_SAAT                               # kWh/yıl
        maliyet = yillik * ELEKTRIK_BIRIM_FIYAT                     # USD/yıl
        detaylar.append({
            'isim': isim, 'adet': v['adet'], 'birim_kw': v['birim_kw'],
            'kullanim': v['kullanim_orani'], 'efektif_kw': gucluk,
            'gunluk_kwh': gunluk, 'yillik_kwh': yillik,
            'yillik_usd': maliyet, 'kaynak': v['kaynak']
        })
    toplam_kw = sum(d['efektif_kw'] for d in detaylar)
    toplam_yillik = sum(d['yillik_kwh'] for d in detaylar)
    toplam_maliyet = sum(d['yillik_usd'] for d in detaylar)
    return detaylar, toplam_kw, toplam_yillik, toplam_maliyet

mn_det, mn_kw, mn_yillik, mn_maliyet = hesapla_enerji(manuel_enerji)
fw_det, fw_kw, fw_yillik, fw_maliyet = hesapla_enerji(fourway_enerji)

# =============================================================================
# 5. KONSOL ÇIKTISI
# =============================================================================
def yazdir_detay(isim, detaylar, toplam_kw, toplam_yillik, toplam_maliyet):
    print(f"\n{'─'*70}")
    print(f"  {isim}")
    print(f"{'─'*70}")
    print(f"  {'Bileşen':<32} {'Adet':>4} {'kW':>5} {'Kull%':>5} {'Ef.kW':>6} {'kWh/yıl':>10} {'USD/yıl':>9}")
    print(f"  {'─'*68}")
    for d in sorted(detaylar, key=lambda x: -x['yillik_kwh']):
        print(f"  {d['isim']:<32} {d['adet']:>4} {d['birim_kw']:>5.1f} {d['kullanim']*100:>4.0f}% "
              f"{d['efektif_kw']:>6.2f} {d['yillik_kwh']:>10,.0f} {d['yillik_usd']:>9,.0f}")
    print(f"  {'─'*68}")
    print(f"  {'TOPLAM':<32} {'':>4} {'':>5} {'':>5} {toplam_kw:>6.2f} {toplam_yillik:>10,.0f} {toplam_maliyet:>9,.0f}")

yazdir_detay("MANUEL SİSTEM ENERJİ PROFİLİ", mn_det, mn_kw, mn_yillik, mn_maliyet)
yazdir_detay("FOUR-WAY SİSTEM ENERJİ PROFİLİ", fw_det, fw_kw, fw_yillik, fw_maliyet)

# Karşılaştırma özet
print(f"\n{'═'*60}")
print("  ENERJİ KARŞILAŞTIRMA ÖZETİ")
print(f"{'═'*60}")
print(f"  {'Metrik':<34} {'Manuel':>12} {'Four-Way':>12}")
print(f"  {'─'*58}")
print(f"  {'Efektif güç (kW)':<34} {mn_kw:>12.2f} {fw_kw:>12.2f}")
print(f"  {'Günlük tüketim (kWh/gün)':<34} {mn_kw*GUNLUK_SAAT:>12,.0f} {fw_kw*GUNLUK_SAAT:>12,.0f}")
print(f"  {'Yıllık tüketim (kWh/yıl)':<34} {mn_yillik:>12,.0f} {fw_yillik:>12,.0f}")
print(f"  {'Yıllık maliyet (USD/yıl)':<34} {mn_maliyet:>12,.0f} {fw_maliyet:>12,.0f}")
fark_kwh = fw_yillik - mn_yillik
fark_usd = fw_maliyet - mn_maliyet
print(f"  {'Fark (kWh/yıl)':<34} {fark_kwh:>+12,.0f} {'':>12}")
print(f"  {'Fark (USD/yıl)':<34} {fark_usd:>+12,.0f} {'':>12}")
print(f"  {'Birim enerji maliyeti (USD/kWh)':<34} {ELEKTRIK_BIRIM_FIYAT:>12.3f} {'':>12}")

# Throughput başına enerji verimliliği
mn_throughput_yil = 60 * YILLIK_SAAT    # palet/yıl
fw_throughput_yil = 120 * YILLIK_SAAT
mn_kwh_palet = mn_yillik / mn_throughput_yil
fw_kwh_palet = fw_yillik / fw_throughput_yil
print(f"\n  ENERJİ VERİMLİLİĞİ (palet başına):")
print(f"  {'Yıllık throughput (palet)':<34} {mn_throughput_yil:>12,} {fw_throughput_yil:>12,}")
print(f"  {'kWh/palet':<34} {mn_kwh_palet:>12.4f} {fw_kwh_palet:>12.4f}")
print(f"  {'USD/palet (enerji)':<34} {mn_kwh_palet*ELEKTRIK_BIRIM_FIYAT:>12.4f} {fw_kwh_palet*ELEKTRIK_BIRIM_FIYAT:>12.4f}")
print(f"  {'Verimlilik farkı':<34} {'':>12} {mn_kwh_palet/fw_kwh_palet:>11.1f}x")

# =============================================================================
# 6. AYLIK TREND MODELİ
# =============================================================================
# Mevsimsel faktörler (HVAC bağımlı — yaz/kış daha yüksek)
aylar = ['Oca','Şub','Mar','Nis','May','Haz','Tem','Ağu','Eyl','Eki','Kas','Ara']
# Mevsimsel çarpanlar (HVAC yükü: kış ısıtma + yaz soğutma etkisi)
mevsim = np.array([1.08, 1.05, 0.98, 0.92, 0.90, 0.95, 1.02, 1.05, 0.95, 0.92, 0.98, 1.10])
gun_ay = np.array([26, 24, 27, 26, 26, 26, 26, 22, 26, 27, 26, 25])  # iş günü/ay

mn_aylik = (mn_kw * GUNLUK_SAAT * gun_ay * mevsim)   # kWh/ay
fw_aylik = (fw_kw * GUNLUK_SAAT * gun_ay * mevsim)

print(f"\n{'─'*60}")
print("  AYLIK ENERJİ TÜKETİM TAHMİNİ (kWh)")
print(f"{'─'*60}")
print(f"  {'Ay':<8} {'İş Günü':>8} {'Mevsim':>8} {'Manuel':>10} {'Four-Way':>10}")
for i in range(12):
    print(f"  {aylar[i]:<8} {gun_ay[i]:>8} {mevsim[i]:>8.2f} {mn_aylik[i]:>10,.0f} {fw_aylik[i]:>10,.0f}")
print(f"  {'TOPLAM':<8} {gun_ay.sum():>8} {'':>8} {mn_aylik.sum():>10,.0f} {fw_aylik.sum():>10,.0f}")

# =============================================================================
# 7. GRAFİKLER (4 panel)
# =============================================================================
C_FW='#00D4A8'; C_MN='#FF6B6B'; C_GOLD='#FFD700'
C_TEXT='#E8E8E8'; C_GRID='#2A2A3E'; C_BG='#0D1117'; C_PANEL='#161B22'

fig = plt.figure(figsize=(18, 16))
fig.patch.set_facecolor(C_BG)
fig.suptitle('Bileşen 10: Enerji Tüketim Profili Karşılaştırması\n'
             'Manuel Forkliftli Depo vs Four-Way Otomatik Depo — Raftürk',
             fontsize=15, fontweight='bold', color=C_TEXT, y=0.98)

# ─ Panel 1: Bileşen bazlı enerji dağılımı (yatay bar, yan yana) ──────────
ax1 = fig.add_subplot(2, 2, 1); ax1.set_facecolor(C_PANEL)
# Ortak kategoriler
kategoriler = ['Forklift/Shuttle', 'Asansör', 'Konveyör', 'Aydınlatma', 'HVAC', 'IT/WCS', 'Sensör/RFID']
mn_kat = [
    sum(d['yillik_kwh'] for d in mn_det if 'Forklift' in d['isim']),
    0,  # Manuel'de asansör yok
    0,  # Manuel'de konveyör yok
    sum(d['yillik_kwh'] for d in mn_det if 'Aydınlatma' in d['isim']),
    sum(d['yillik_kwh'] for d in mn_det if 'HVAC' in d['isim']),
    sum(d['yillik_kwh'] for d in mn_det if 'Ofis' in d['isim']),
    0   # Manuel'de sensör yok
]
fw_kat = [
    sum(d['yillik_kwh'] for d in fw_det if 'Shuttle' in d['isim']),
    sum(d['yillik_kwh'] for d in fw_det if 'Asansör' in d['isim']),
    sum(d['yillik_kwh'] for d in fw_det if 'Konveyör' in d['isim']),
    sum(d['yillik_kwh'] for d in fw_det if 'Aydınlatma' in d['isim']),
    sum(d['yillik_kwh'] for d in fw_det if 'HVAC' in d['isim']),
    sum(d['yillik_kwh'] for d in fw_det if 'Ofis' in d['isim'] or 'WCS' in d['isim']),
    sum(d['yillik_kwh'] for d in fw_det if 'Sensör' in d['isim']),
]
y_pos = np.arange(len(kategoriler))
w = 0.35
ax1.barh(y_pos - w/2, np.array(mn_kat)/1000, w, color=C_MN, label='Manuel', edgecolor='none')
ax1.barh(y_pos + w/2, np.array(fw_kat)/1000, w, color=C_FW, label='Four-Way', edgecolor='none')
ax1.set_yticks(y_pos); ax1.set_yticklabels(kategoriler, color=C_TEXT, fontsize=9)
ax1.set_xlabel('Yıllık Enerji Tüketimi (MWh/yıl)', color=C_TEXT)
ax1.set_title('Bileşen Bazlı Enerji Dağılımı\n(Yıllık, MWh)', color=C_TEXT, fontsize=11, fontweight='bold', pad=12)
ax1.tick_params(colors=C_TEXT)
for s in ax1.spines.values(): s.set_edgecolor(C_GRID)
ax1.legend(fontsize=9, facecolor=C_PANEL, edgecolor=C_GRID, labelcolor=C_TEXT)
ax1.grid(axis='x', alpha=0.15, color='white')

# ─ Panel 2: Yıllık toplam karşılaştırma (bar + maliyet) ──────────────────
ax2 = fig.add_subplot(2, 2, 2); ax2.set_facecolor(C_PANEL)
x2 = np.arange(3)
labels2 = ['Toplam\n(MWh/yıl)', 'Maliyet\n(USD/yıl)', 'kWh/palet\n(×1000)']
mn_v2 = [mn_yillik/1000, mn_maliyet, mn_kwh_palet*1000]
fw_v2 = [fw_yillik/1000, fw_maliyet, fw_kwh_palet*1000]
w2 = 0.32
b2a = ax2.bar(x2-w2/2, mn_v2, w2, color=C_MN, label='Manuel', edgecolor='none')
b2b = ax2.bar(x2+w2/2, fw_v2, w2, color=C_FW, label='Four-Way', edgecolor='none')
for bars in [b2a, b2b]:
    for bar in bars:
        h = bar.get_height()
        ax2.text(bar.get_x()+bar.get_width()/2, h+max(mn_v2)*0.02, f'{h:,.0f}',
                 ha='center', color=C_TEXT, fontsize=9, fontweight='bold')
ax2.set_xticks(x2); ax2.set_xticklabels(labels2, color=C_TEXT, fontsize=9)
ax2.set_title('Yıllık Enerji ve Maliyet Özeti', color=C_TEXT, fontsize=11, fontweight='bold', pad=12)
ax2.tick_params(colors=C_TEXT)
for s in ax2.spines.values(): s.set_edgecolor(C_GRID)
ax2.legend(fontsize=9, facecolor=C_PANEL, edgecolor=C_GRID, labelcolor=C_TEXT)
ax2.grid(axis='y', alpha=0.15, color='white')

# ─ Panel 3: Aylık trend eğrisi ───────────────────────────────────────────
ax3 = fig.add_subplot(2, 2, 3); ax3.set_facecolor(C_PANEL)
x3 = np.arange(12)
ax3.plot(x3, mn_aylik/1000, 'o-', color=C_MN, lw=2.5, ms=7, label='Manuel')
ax3.plot(x3, fw_aylik/1000, 's-', color=C_FW, lw=2.5, ms=7, label='Four-Way')
ax3.fill_between(x3, mn_aylik/1000, fw_aylik/1000, alpha=0.15,
                 color=C_FW if fw_yillik > mn_yillik else C_MN)
ax3.set_xticks(x3); ax3.set_xticklabels(aylar, color=C_TEXT, fontsize=9)
ax3.set_ylabel('Aylık Tüketim (MWh)', color=C_TEXT)
ax3.set_title('Aylık Enerji Tüketim Trendi\n(Mevsimsel HVAC etkisi dahil)', color=C_TEXT, fontsize=11, fontweight='bold', pad=12)
ax3.tick_params(colors=C_TEXT)
for s in ax3.spines.values(): s.set_edgecolor(C_GRID)
ax3.legend(fontsize=9, facecolor=C_PANEL, edgecolor=C_GRID, labelcolor=C_TEXT)
ax3.grid(alpha=0.15, color='white')

# ─ Panel 4: Enerji verimliliği (palet başına kWh) ─────────────────────────
ax4 = fig.add_subplot(2, 2, 4); ax4.set_facecolor(C_PANEL)
# Stacked bar: bileşen bazlı palet başına kWh
kat_isim = ['Taşıma\n(Forklift/Shuttle)', 'Kaldırma\n(Asansör)', 'Altyapı\n(Aydınlatma+HVAC+IT)']
mn_palet_kat = [
    mn_kat[0]/mn_throughput_yil,  # Forklift
    0,                             # Asansör yok
    sum(mn_kat[3:])/mn_throughput_yil  # Altyapı
]
fw_palet_kat = [
    fw_kat[0]/fw_throughput_yil,
    (fw_kat[1]+fw_kat[2])/fw_throughput_yil,
    sum(fw_kat[3:])/fw_throughput_yil
]
x4 = np.arange(2)
renk4 = ['#42A5F5', '#FFA726', '#AB47BC']
bottom_mn = 0; bottom_fw = 0
for i, (k, r) in enumerate(zip(kat_isim, renk4)):
    vals = [mn_palet_kat[i], fw_palet_kat[i]]
    ax4.bar(0, mn_palet_kat[i], 0.45, bottom=bottom_mn, color=r, label=k if True else '', edgecolor='none')
    ax4.bar(1, fw_palet_kat[i], 0.45, bottom=bottom_fw, color=r, edgecolor='none')
    bottom_mn += mn_palet_kat[i]; bottom_fw += fw_palet_kat[i]

# Toplam etiket
ax4.text(0, bottom_mn+0.001, f'{mn_kwh_palet:.4f}\nkWh/palet', ha='center',
         color=C_MN, fontsize=10, fontweight='bold')
ax4.text(1, bottom_fw+0.001, f'{fw_kwh_palet:.4f}\nkWh/palet', ha='center',
         color=C_FW, fontsize=10, fontweight='bold')
ax4.text(0.5, max(bottom_mn, bottom_fw)*0.5, f'{mn_kwh_palet/fw_kwh_palet:.1f}x\ndaha verimli',
         ha='center', va='center', color=C_GOLD, fontsize=12, fontweight='bold',
         bbox=dict(boxstyle='round', facecolor=C_PANEL, edgecolor=C_GOLD, alpha=0.8))
ax4.set_xticks([0,1]); ax4.set_xticklabels(['Manuel', 'Four-Way'], color=C_TEXT, fontsize=12)
ax4.set_ylabel('kWh / palet', color=C_TEXT)
ax4.set_title('Enerji Verimliliği: Palet Başına Tüketim\n(Düşük = Daha Verimli)', color=C_TEXT, fontsize=11, fontweight='bold', pad=12)
ax4.tick_params(colors=C_TEXT)
for s in ax4.spines.values(): s.set_edgecolor(C_GRID)
ax4.legend(fontsize=8, facecolor=C_PANEL, edgecolor=C_GRID, labelcolor=C_TEXT, loc='upper right')
ax4.grid(axis='y', alpha=0.15, color='white')

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('bilesen10_enerji.png', dpi=200, bbox_inches='tight', facecolor=C_BG)
print("\n✓ Grafik kaydedildi: bilesen10_enerji.png")
