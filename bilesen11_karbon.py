# -*- coding: utf-8 -*-
"""
BİLEŞEN 11: Karbon Ayak İzi Analizi
Manuel Forkliftli Depo vs Four-Way Otomatik Depo
Raftürk Vaka Çalışması

Metodoloji: GHG Protocol Corporate Standard (WRI/WBCSD, 2004)
Kapsam: Scope 2 — elektrik kaynaklı dolaylı emisyonlar
Sınırlılık: Scope 1 (yakıt) ve Scope 3 (tedarik zinciri) dahil değildir.

Akademik referanslar:
- WRI/WBCSD (2004). GHG Protocol Corporate Accounting and Reporting Standard.
- IEA (2023). CO2 Emissions from Fuel Combustion. OECD/IEA, Paris.
- IPCC (2021). AR6 Climate Change — The Physical Science Basis.
- Dekker, R. vd. (2012). Operations Research for Green Logistics. EJOR, 219(3).
- Bouchery, Y. vd. (2012). Including sustainability criteria into inventory models.
  EJOR, 222(2), 229-240.

Veri kaynakları notu:
  - Enerji tüketim değerleri (kWh/yıl): Bileşen 10 bottom-up tahmininden alınmıştır.
    Bu değerler Raftürk'ten gerçek enerji faturası alınmadığı için tahminidir.
    (NOT: Gerçek fatura verisi ile güncellenmelidir — parametre bloğu işaretlidir.)
  - Türkiye elektrik emisyon faktörü: IEA (2023) doğrudan veri.
  - AB ETS karbon fiyatı: 2024 yıl ortalaması — piyasa verisi.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# 1. PARAMETRELER
# =============================================================================

# ── B10'dan alınan enerji tüketimi (TAHMİN — Bileşen 10 bottom-up modeli) ──
# ⚠️ NOT: Bu değerler Bileşen 10'daki bottom-up enerji modelinden türetilmiştir.
#    Raftürk'ten gerçek enerji faturası temin edildiğinde güncellenmelidir.
MN_KWH_YIL   = 168_854   # kWh/yıl — Manuel depo (B10 tahmini)
FW_KWH_YIL   = 169_229   # kWh/yıl — Four-Way depo (B10 tahmini)
# ─── NOT: Toplam kWh farkı küçük görünse de palet başına verimlilik (kWh/palet)
#     farkı önemlidir: Manuel 0.564, FW 0.283 kWh/palet (2× fark, B10'dan)

MN_KWH_PALET = 0.5637    # kWh/palet — Manuel (B10 tahmini)
FW_KWH_PALET = 0.2825    # kWh/palet — FW (B10 tahmini)

# ── Yıllık palet hacimleri ──
YILLIK_GUN         = 312
MN_KAPASITE_SAAT   = 60    # palet/saat
FW_KAPASITE_SAAT   = 120   # palet/saat
GUNLUK_SAAT        = 16    # saat/gün (2 vardiya)
MN_PALET_YIL       = MN_KAPASITE_SAAT * GUNLUK_SAAT * YILLIK_GUN  # 299,520
FW_PALET_YIL       = FW_KAPASITE_SAAT * GUNLUK_SAAT * YILLIK_GUN  # 599,040

# ── Emisyon faktörü — Türkiye elektrik şebekesi (GERÇEK VERİ) ──
# Kaynak: IEA (2023) Electricity CO2 Emissions Intensity — Turkey: 0.443 kgCO2/kWh
# (2022 yılı verisi; 2023 güncellemesi tahmini bekleniyor)
EF_TURKEY = 0.443         # kgCO2eq/kWh — IEA (2023)

# ── AB ETS karbon fiyatı (GERÇEK VERİ — piyasa referansı) ──
# 2024 yıl ortalaması ~65 EUR/tCO2 (EEX/ICE Endex spot fiyatları)
KARBON_FIYAT_EUR   = 65.0  # EUR/tCO2
EUR_USD            = 1.08   # EUR/USD (2024 ort.)
KARBON_FIYAT_USD   = KARBON_FIYAT_EUR * EUR_USD  # ~70.2 USD/tCO2

# ── Analiz ufku ──
N_YIL = 10

# =============================================================================
# 2. EMİSYON HESAPLARI
# =============================================================================

# Toplam yıllık emisyon (Scope 2, pazar bazlı)
MN_CO2_YIL = MN_KWH_YIL * EF_TURKEY / 1000   # tCO2eq/yıl
FW_CO2_YIL = FW_KWH_YIL * EF_TURKEY / 1000   # tCO2eq/yıl

# Palet başına emisyon (fonksiyonel birim — akademik karşılaştırma için kritik)
MN_CO2_PALET = MN_KWH_PALET * EF_TURKEY       # kgCO2eq/palet
FW_CO2_PALET = FW_KWH_PALET * EF_TURKEY       # kgCO2eq/palet

# Emisyon yoğunluğu farkı — eşit hacim üzerinden (299,520 palet = Manuel max)
# FW 299,520 paleti ne kadar CO2 ile işler?
FW_CO2_ESIT_HACIM = MN_PALET_YIL * FW_CO2_PALET / 1000   # tCO2eq/yıl
MN_CO2_ESIT_HACIM = MN_PALET_YIL * MN_CO2_PALET / 1000   # tCO2eq/yıl

# FW'nin kapasite avantajından kaynaklı ek emisyon (fazla 299,520 palet)
FW_EK_PALET  = FW_PALET_YIL - MN_PALET_YIL
FW_EK_CO2    = FW_EK_PALET * FW_CO2_PALET / 1000  # tCO2eq/yıl

# Net emisyon tasarrufu (eşit hacim bazında)
EMISYON_TASARRUF_YIL = MN_CO2_ESIT_HACIM - FW_CO2_ESIT_HACIM  # tCO2eq/yıl
KARBON_TASARRUF_USD  = EMISYON_TASARRUF_YIL * KARBON_FIYAT_USD  # USD/yıl

# 10 yıllık kümülatif
MN_CO2_10YIL    = MN_CO2_ESIT_HACIM * N_YIL
FW_CO2_10YIL    = FW_CO2_ESIT_HACIM * N_YIL
KUMUL_TASARRUF  = EMISYON_TASARRUF_YIL * N_YIL

print("╔══════════════════════════════════════════════════════════════╗")
print("║  BİLEŞEN 11: KARBON AYAK İZİ ANALİZİ                       ║")
print("║  GHG Protocol Scope 2 — Elektrik Kaynaklı Emisyonlar        ║")
print("╚══════════════════════════════════════════════════════════════╝")
print(f"\n  ⚠️  Veri notu: Enerji değerleri B10 tahminidir (gerçek fatura bekleniyor)")
print(f"  ✓   Emisyon faktörü: IEA (2023) Türkiye — {EF_TURKEY} kgCO2/kWh (gerçek)")
print(f"  ✓   Karbon fiyatı: AB ETS 2024 ort. — {KARBON_FIYAT_EUR:.0f} EUR/tCO2 (gerçek)")

print(f"\n{'─'*62}")
print(f"  {'Metrik':<40} {'Manuel':>10} {'Four-Way':>10}")
print(f"{'─'*62}")
print(f"  {'Yıllık enerji tüketimi (kWh/yıl)':<40} {MN_KWH_YIL:>10,.0f} {FW_KWH_YIL:>10,.0f}")
print(f"  {'Yıllık kapasite (palet/yıl)':<40} {MN_PALET_YIL:>10,.0f} {FW_PALET_YIL:>10,.0f}")
print(f"  {'kWh/palet':<40} {MN_KWH_PALET:>10.4f} {FW_KWH_PALET:>10.4f}")
print(f"  {'kgCO2eq/palet':<40} {MN_CO2_PALET:>10.4f} {FW_CO2_PALET:>10.4f}")
print(f"  {'Yıllık CO2 (eşit hacim bazında, tCO2)':<40} {MN_CO2_ESIT_HACIM:>10.1f} {FW_CO2_ESIT_HACIM:>10.1f}")
print(f"  {'10 yıl kümülatif CO2 (tCO2)':<40} {MN_CO2_10YIL:>10.1f} {FW_CO2_10YIL:>10.1f}")
print(f"{'─'*62}")
print(f"  {'Emisyon tasarrufu (eşit hacim, yıllık)':<40} {EMISYON_TASARRUF_YIL:>+10.1f} tCO2/yıl")
print(f"  {'10 yıl kümülatif tasarruf':<40} {KUMUL_TASARRUF:>+10.1f} tCO2")
print(f"  {'Karbon maliyeti tasarrufu (yıllık)':<40} {KARBON_TASARRUF_USD:>+10,.0f} USD/yıl")
print(f"  {'kgCO2/palet azalması (%)':<40} {(1-FW_CO2_PALET/MN_CO2_PALET)*100:>+10.1f} %")

# =============================================================================
# 3. GRAFİKLER
# =============================================================================

fig = plt.figure(figsize=(16, 12))
gs  = GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.35)
ax1 = fig.add_subplot(gs[0, :2])
ax2 = fig.add_subplot(gs[0, 2])
ax3 = fig.add_subplot(gs[1, :2])
ax4 = fig.add_subplot(gs[1, 2])

fig.suptitle(
    'Bileşen 11: Karbon Ayak İzi Analizi — Manuel vs Four-Way Depo\n'
    'GHG Protocol Scope 2 | IEA (2023) Türkiye Emisyon Faktörü: 0.443 kgCO₂/kWh',
    fontsize=12, fontweight='bold', y=1.01
)

C_MN = '#E24B4A'
C_FW = '#1D9E75'
C_NOTA = '#F5A623'

# ── Graf 1: kgCO2/palet karşılaştırması (fonksiyonel birim) ────────────────
kategoriler = ['Manuel\nForklift', 'Four-Way\nOtomatik']
co2_palet   = [MN_CO2_PALET, FW_CO2_PALET]
bars1 = ax1.bar(kategoriler, co2_palet, color=[C_MN, C_FW], alpha=0.85,
                edgecolor='white', width=0.45)

for bar, v in zip(bars1, co2_palet):
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.003,
             f'{v:.3f} kg\nCO₂eq/palet',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

# Azalma oku
pct_azalma = (1 - FW_CO2_PALET/MN_CO2_PALET)*100
ax1.annotate('',
    xy=(1, FW_CO2_PALET),
    xytext=(0, MN_CO2_PALET),
    arrowprops=dict(arrowstyle='->', color='#333', lw=1.5,
                    connectionstyle='arc3,rad=-0.2'))
ax1.text(0.5, (MN_CO2_PALET+FW_CO2_PALET)/2,
         f'−{pct_azalma:.0f}%\nazalma',
         ha='center', va='center', fontsize=10, fontweight='bold', color='#333',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFDE7', alpha=0.9))

ax1.set_ylabel('Emisyon Yoğunluğu (kgCO₂eq/palet)', fontsize=10)
ax1.set_title('Fonksiyonel Birim Karşılaştırması\n(kgCO₂eq / işlenen palet)',
              fontsize=11, fontweight='bold')
ax1.grid(axis='y', alpha=0.25)
ax1.set_ylim(0, MN_CO2_PALET * 1.3)

# Veri kaynağı notu
ax1.text(0.02, 0.95,
         '⚠ Enerji: B10 tahmini\n✓ Emisyon faktörü: IEA (2023)',
         transform=ax1.transAxes, fontsize=8, va='top',
         bbox=dict(boxstyle='round', facecolor='#FFF8E1', alpha=0.85))

# ── Graf 2: Yıllık CO2 bileşen dağılımı ──────────────────────────────────────
# Manuel bileşenler (B10'dan)
mn_oran = {'Forklift\nşarjı': 0.74, 'Aydınlatma': 0.13, 'HVAC': 0.09, 'Diğer': 0.04}
fw_oran = {'Shuttle+\nAsansör': 0.71, 'Aydınlatma': 0.11, 'HVAC': 0.09, 'WCS/\nSensör': 0.09}

x   = np.arange(2)
w   = 0.35
renkler_bilesen = ['#4E9AF1', '#F5A623', '#1D9E75', '#9B59B6']

mn_vals = [MN_CO2_ESIT_HACIM * v for v in mn_oran.values()]
fw_vals = [FW_CO2_ESIT_HACIM * v for v in fw_oran.values()]

bottom_mn = 0
bottom_fw = 0
for i, (renk, (mk, mv), (fk, fv)) in enumerate(zip(renkler_bilesen,
                                                     mn_oran.items(),
                                                     fw_oran.items())):
    b1 = ax2.bar(0, mv, 0.5, bottom=bottom_mn, color=renk, alpha=0.85,
                 edgecolor='white', label=mk)
    b2 = ax2.bar(1, fv, 0.5, bottom=bottom_fw, color=renk, alpha=0.85,
                 edgecolor='white')
    if mv > 0.8:
        ax2.text(0, bottom_mn + mv/2, f'{mv:.1f}t', ha='center',
                 va='center', fontsize=8, color='white', fontweight='bold')
    if fv > 0.8:
        ax2.text(1, bottom_fw + fv/2, f'{fv:.1f}t', ha='center',
                 va='center', fontsize=8, color='white', fontweight='bold')
    bottom_mn += mv
    bottom_fw += fv

ax2.set_xticks([0, 1])
ax2.set_xticklabels(['Manuel', 'Four-Way'], fontsize=10)
ax2.set_ylabel('tCO₂eq/yıl', fontsize=9)
ax2.set_title('Emisyon Bileşen Dağılımı\n(eşit 299K palet/yıl bazında)',
              fontsize=11, fontweight='bold')
ax2.grid(axis='y', alpha=0.25)
ax2.legend(fontsize=7, loc='upper right', ncol=2)

# ── Graf 3: 10 yıllık kümülatif CO2 ─────────────────────────────────────────
yillar  = np.arange(1, N_YIL+1)
mn_kum  = MN_CO2_ESIT_HACIM * yillar
fw_kum  = FW_CO2_ESIT_HACIM * yillar
tasarruf_kum = mn_kum - fw_kum

ax3.fill_between(yillar, mn_kum, fw_kum, alpha=0.15, color=C_FW,
                 label=f'Kümülatif tasarruf ({KUMUL_TASARRUF:.0f} tCO₂)')
ax3.plot(yillar, mn_kum, color=C_MN, lw=2.5, marker='o', ms=5,
         markeredgecolor='white', markeredgewidth=1, label='Manuel kümülatif')
ax3.plot(yillar, fw_kum, color=C_FW, lw=2.5, marker='o', ms=5,
         markeredgecolor='white', markeredgewidth=1, label='Four-Way kümülatif')

# 10. yıl etiketleri
ax3.annotate(f'{mn_kum[-1]:.0f} tCO₂',
             xy=(N_YIL, mn_kum[-1]),
             xytext=(N_YIL-1.2, mn_kum[-1]+8),
             fontsize=9, color=C_MN, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=C_MN, lw=1))
ax3.annotate(f'{fw_kum[-1]:.0f} tCO₂',
             xy=(N_YIL, fw_kum[-1]),
             xytext=(N_YIL-1.2, fw_kum[-1]-12),
             fontsize=9, color=C_FW, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=C_FW, lw=1))

ax3.set_xlabel('Yıl', fontsize=10)
ax3.set_ylabel('Kümülatif CO₂ Emisyonu (tCO₂eq)', fontsize=10)
ax3.set_title(f'10 Yıllık Kümülatif Emisyon\n(eşit 299K palet/yıl bazı — tasarruf: {KUMUL_TASARRUF:.0f} tCO₂)',
              fontsize=11, fontweight='bold')
ax3.legend(fontsize=9)
ax3.grid(alpha=0.2)
ax3.set_xlim(1, N_YIL)

# ── Graf 4: Karbon fiyatı duyarlılık analizi ──────────────────────────────────
fiyatlar = np.linspace(20, 150, 100)   # EUR/tCO2
tasarruf_eur = EMISYON_TASARRUF_YIL * fiyatlar  # EUR/yıl

ax4.plot(fiyatlar, tasarruf_eur, color='#4E9AF1', lw=2.5)
ax4.fill_between(fiyatlar, 0, tasarruf_eur, alpha=0.15, color='#4E9AF1')

# Mevcut fiyat işareti
ax4.axvline(KARBON_FIYAT_EUR, color=C_NOTA, lw=1.8, ls='--', alpha=0.8)
ax4.axhline(KARBON_TASARRUF_USD/EUR_USD, color=C_NOTA, lw=1.2, ls=':', alpha=0.6)
ax4.plot(KARBON_FIYAT_EUR, KARBON_TASARRUF_USD/EUR_USD, 'o',
         color=C_NOTA, ms=10, zorder=6, markeredgecolor='white', markeredgewidth=1.5)
ax4.annotate(f'Mevcut:\n{KARBON_FIYAT_EUR:.0f} EUR/t\n{KARBON_TASARRUF_USD/EUR_USD:,.0f} EUR/yıl',
             xy=(KARBON_FIYAT_EUR, KARBON_TASARRUF_USD/EUR_USD),
             xytext=(KARBON_FIYAT_EUR+15, KARBON_TASARRUF_USD/EUR_USD+50),
             fontsize=8.5, color=C_NOTA, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=C_NOTA, lw=1))

ax4.set_xlabel('AB ETS Karbon Fiyatı (EUR/tCO₂)', fontsize=10)
ax4.set_ylabel('Yıllık Karbon Maliyet Tasarrufu (EUR/yıl)', fontsize=10)
ax4.set_title('Karbon Fiyatı Duyarlılık Analizi\n(emisyon tasarrufunun parasal değeri)',
              fontsize=11, fontweight='bold')
ax4.grid(alpha=0.2)
ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))

plt.savefig('/home/claude/bilesen11_karbon.png', dpi=200, bbox_inches='tight')
plt.close()
print("\nGrafik kaydedildi: bilesen11_karbon.png")

# =============================================================================
# 4. ÖZET ÇIKTI
# =============================================================================
print(f"\n{'═'*62}")
print("  ÖZET BULGULAR")
print(f"{'═'*62}")
print(f"  Fonksiyonel birim bazında (kgCO2/palet):")
print(f"    Manuel : {MN_CO2_PALET:.4f} kgCO2eq/palet")
print(f"    FW     : {FW_CO2_PALET:.4f} kgCO2eq/palet")
print(f"    Azalma : %{pct_azalma:.1f} ({MN_CO2_PALET-FW_CO2_PALET:.4f} kgCO2/palet)")
print(f"\n  Eşit hacim (299,520 palet/yıl) bazında:")
print(f"    Manuel : {MN_CO2_ESIT_HACIM:.1f} tCO2eq/yıl")
print(f"    FW     : {FW_CO2_ESIT_HACIM:.1f} tCO2eq/yıl")
print(f"    Tasarruf: {EMISYON_TASARRUF_YIL:.1f} tCO2eq/yıl")
print(f"\n  10 yıl kümülatif tasarruf: {KUMUL_TASARRUF:.1f} tCO2eq")
print(f"  Karbon maliyet tasarrufu : {KARBON_TASARRUF_USD:,.0f} USD/yıl")
print(f"  ({KARBON_TASARRUF_USD/EUR_USD:,.0f} EUR/yıl @ {KARBON_FIYAT_EUR:.0f} EUR/tCO2)")

# Sonuçları döndür (Word için)
sonuclar = {
    'mn_co2_palet': MN_CO2_PALET,
    'fw_co2_palet': FW_CO2_PALET,
    'pct_azalma': pct_azalma,
    'mn_co2_yil': MN_CO2_ESIT_HACIM,
    'fw_co2_yil': FW_CO2_ESIT_HACIM,
    'tasarruf_yil': EMISYON_TASARRUF_YIL,
    'kumul_10yil': KUMUL_TASARRUF,
    'karbon_tasarruf_usd': KARBON_TASARRUF_USD,
    'ef_turkey': EF_TURKEY,
    'karbon_fiyat_eur': KARBON_FIYAT_EUR,
}
