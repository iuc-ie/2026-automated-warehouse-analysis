# -*- coding: utf-8 -*-
"""
BİLEŞEN 9: MTBF/MTTR Güvenilirlik Modellemesi + FMEA
Manuel Forkliftli Depo vs Four-Way Otomatik Depo
Raftürk Vaka Çalışması

Metodoloji:
  - MTBF/MTTR: MIL-HDBK-217F (ABD Savunma Bakanlığı güvenilirlik el kitabı)
  - Kullanılabilirlik: A = MTBF / (MTBF + MTTR)  (IEC 61703)
  - FMEA: IEC 60812 — Arıza modu ve etkileri analizi
  - Sistem güvenilirliği: Seri/paralel konfigürasyon modelleri

Veri kaynakları:
  - Forklift MTBF: endüstri ortalamaları (Toyota, Linde teknik dokümanları)
  - Four-Way shuttle: Mao ve diğ. (2023) + üretici katalogları
  - ⚠️ RAFTÜRK'TEN GÜNCELLENECEK: Gerçek arıza kayıtları

Spyder IDE: F5 ile çalıştır
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings('ignore')

print("╔═══════════════════════════════════════════════════════════╗")
print("║  BİLEŞEN 9: MTBF/MTTR Güvenilirlik Modellemesi + FMEA  ║")
print("║  Raftürk — Manuel vs Four-Way Depo                       ║")
print("╚═══════════════════════════════════════════════════════════╝")

# =============================================================================
# 1. MTBF / MTTR PARAMETRELERİ (Literatür + Endüstri Ortalamaları)
# =============================================================================
# ⚠️ RAFTÜRK'TEN GÜNCELLENECEK — şu an literatür/endüstri değerleri

# --- MANUEL SİSTEM BİLEŞENLERİ ---
manuel_bilesenleri = {
    'Forklift Motor/Şanzıman':  {'adet': 3, 'mtbf_h': 2000, 'mttr_h': 6.0,
        'kaynak': 'Toyota teknik servis ortalaması'},
    'Forklift Hidrolik Sistem':  {'adet': 3, 'mtbf_h': 3000, 'mttr_h': 4.0,
        'kaynak': 'Linde servis verileri'},
    'Forklift Lastik/Fren':      {'adet': 3, 'mtbf_h': 4000, 'mttr_h': 2.0,
        'kaynak': 'Endüstri ortalaması'},
    'Forklift Elektrik/Akü':     {'adet': 3, 'mtbf_h': 2500, 'mttr_h': 3.0,
        'kaynak': 'Endüstri ortalaması'},
    'Raf Sistemi (Mekanik)':     {'adet': 1, 'mtbf_h': 50000, 'mttr_h': 8.0,
        'kaynak': 'Çelik raf üretici garantisi'},
}

# --- FOUR-WAY SİSTEM BİLEŞENLERİ ---
fourway_bilesenleri = {
    'Shuttle Araç (MAXLINK)':    {'adet': 6, 'mtbf_h': 8000, 'mttr_h': 2.0,
        'kaynak': 'Mao ve diğ. (2023) + üretici kataloğu'},
    'Asansör Mekanizması':       {'adet': 4, 'mtbf_h': 10000, 'mttr_h': 3.0,
        'kaynak': 'AS/RS endüstri ortalaması'},
    'WMS/WCS Yazılım':           {'adet': 1, 'mtbf_h': 5000, 'mttr_h': 1.0,
        'kaynak': 'Yazılım güvenilirlik literatürü'},
    'Konveyör/Transfer Hattı':   {'adet': 1, 'mtbf_h': 15000, 'mttr_h': 2.5,
        'kaynak': 'Endüstri ortalaması'},
    'Sensör/RFID Sistemi':       {'adet': 1, 'mtbf_h': 20000, 'mttr_h': 1.5,
        'kaynak': 'Endüstri ortalaması'},
    'Raf Sistemi (Otomatik)':    {'adet': 1, 'mtbf_h': 60000, 'mttr_h': 6.0,
        'kaynak': 'Çelik raf üretici garantisi'},
    'Enerji/Batarya Sistemi':    {'adet': 6, 'mtbf_h': 6000, 'mttr_h': 1.0,
        'kaynak': 'Li-ion batarya ömür verileri'},
}

YILLIK_CALISMA = 312 * 16  # gün × saat/gün = 4992 saat/yıl

# =============================================================================
# 2. SİSTEM MTBF HESABI (Seri Model — En Zayıf Halka)
# =============================================================================
def sistem_mtbf_seri(bilesenleri):
    """
    Seri sistem: 1/MTBF_sistem = Σ(adet_i / MTBF_i)
    Herhangi bir bileşen arızalanırsa sistem durur.
    """
    toplam_ariza_orani = 0
    detaylar = []
    for isim, v in bilesenleri.items():
        lambda_i = v['adet'] / v['mtbf_h']  # arıza oranı (1/saat)
        toplam_ariza_orani += lambda_i
        detaylar.append({
            'isim': isim,
            'adet': v['adet'],
            'mtbf_h': v['mtbf_h'],
            'mttr_h': v['mttr_h'],
            'lambda': lambda_i,
            'yillik_ariza': lambda_i * YILLIK_CALISMA,
            'kaynak': v['kaynak']
        })
    
    mtbf_sistem = 1 / toplam_ariza_orani if toplam_ariza_orani > 0 else float('inf')
    return mtbf_sistem, toplam_ariza_orani, detaylar

mn_mtbf, mn_lambda, mn_det = sistem_mtbf_seri(manuel_bilesenleri)
fw_mtbf, fw_lambda, fw_det = sistem_mtbf_seri(fourway_bilesenleri)

# =============================================================================
# 3. SİSTEM MTTR HESABI (Ağırlıklı Ortalama)
# =============================================================================
def sistem_mttr(detaylar, toplam_lambda):
    """MTTR_sistem = Σ(lambda_i × MTTR_i) / Σ(lambda_i)"""
    pay = sum(d['lambda'] * d['mttr_h'] for d in detaylar)
    return pay / toplam_lambda if toplam_lambda > 0 else 0

mn_mttr = sistem_mttr(mn_det, mn_lambda)
fw_mttr = sistem_mttr(fw_det, fw_lambda)

# =============================================================================
# 4. KULLANILABİLİRLİK (Availability)
# =============================================================================
# A = MTBF / (MTBF + MTTR)  — Steady-state availability (IEC 61703)
mn_avail = mn_mtbf / (mn_mtbf + mn_mttr)
fw_avail = fw_mtbf / (fw_mtbf + fw_mttr)

# Yıllık duruş saati
mn_durus = (1 - mn_avail) * YILLIK_CALISMA
fw_durus = (1 - fw_avail) * YILLIK_CALISMA

# Yıllık arıza sayısı
mn_ariza_yil = mn_lambda * YILLIK_CALISMA
fw_ariza_yil = fw_lambda * YILLIK_CALISMA

print(f"\n{'─'*60}")
print("  SİSTEM GÜVENİLİRLİK METRİKLERİ")
print(f"{'─'*60}")
print(f"  {'Metrik':<32} {'Manuel':>12} {'Four-Way':>12}")
print(f"  {'─'*56}")
print(f"  {'MTBF (saat)':<32} {mn_mtbf:>12.1f} {fw_mtbf:>12.1f}")
print(f"  {'MTBF (gün)':<32} {mn_mtbf/16:>12.1f} {fw_mtbf/16:>12.1f}")
print(f"  {'MTTR (saat)':<32} {mn_mttr:>12.2f} {fw_mttr:>12.2f}")
print(f"  {'Arıza oranı λ (1/saat)':<32} {mn_lambda:>12.6f} {fw_lambda:>12.6f}")
print(f"  {'Kullanılabilirlik A (%)':<32} {mn_avail*100:>11.3f}% {fw_avail*100:>11.3f}%")
print(f"  {'Yıllık arıza sayısı':<32} {mn_ariza_yil:>12.1f} {fw_ariza_yil:>12.1f}")
print(f"  {'Yıllık duruş (saat)':<32} {mn_durus:>12.1f} {fw_durus:>12.1f}")
print(f"  {'Yıllık çalışma (saat)':<32} {YILLIK_CALISMA:>12} {YILLIK_CALISMA:>12}")

# =============================================================================
# 5. BİLEŞEN BAZLI DETAY
# =============================================================================
def detay_yazdir(isim, detaylar):
    print(f"\n  {isim} — Bileşen Bazlı Arıza Analizi:")
    print(f"  {'Bileşen':<28} {'Adet':>5} {'MTBF':>7} {'MTTR':>6} {'λ':>10} {'Yıl/Arıza':>10}")
    for d in sorted(detaylar, key=lambda x: -x['yillik_ariza']):
        print(f"  {d['isim']:<28} {d['adet']:>5} {d['mtbf_h']:>6}h {d['mttr_h']:>5.1f}h "
              f"{d['lambda']:>10.6f} {d['yillik_ariza']:>10.2f}")

detay_yazdir("MANUEL SİSTEM", mn_det)
detay_yazdir("FOUR-WAY SİSTEM", fw_det)

# =============================================================================
# 6. FMEA — ARIZA MODU VE ETKİLERİ ANALİZİ (IEC 60812)
# =============================================================================
# RPN = Şiddet × Olasılık × Tespit zorluğu (1-10 ölçeği)

print(f"\n{'═'*60}")
print("  FMEA — ARIZA MODU VE ETKİLERİ ANALİZİ (IEC 60812)")
print(f"{'═'*60}")

fmea_manuel = [
    # [Bileşen, Arıza Modu, Etki, Şiddet, Olasılık, Tespit, RPN]
    ['Forklift Motor',    'Motor arızası',         'Tam duruş',           8, 5, 4, None],
    ['Forklift Motor',    'Performans düşüşü',     'Yavaşlama',           4, 6, 6, None],
    ['Hidrolik Sistem',   'Sızıntı',               'Kaldırma kapasitesi↓', 7, 4, 5, None],
    ['Hidrolik Sistem',   'Pompa arızası',          'Tam duruş',           9, 3, 3, None],
    ['Lastik/Fren',       'Lastik patlaması',       'Güvenlik riski',      9, 3, 7, None],
    ['Lastik/Fren',       'Fren aşınması',          'Güvenlik riski',      8, 4, 5, None],
    ['Elektrik/Akü',      'Akü deşarjı',            'Vardiya kaybı',       6, 6, 3, None],
    ['Elektrik/Akü',      'Kablo/kontak arızası',   'Aralıklı duruş',     5, 4, 6, None],
    ['Raf Sistemi',       'Deformasyon',             'Güvenlik + kapasite', 8, 2, 4, None],
    ['Operatör',          'İnsan hatası',            'Ürün hasarı/kaza',    7, 7, 8, None],
]

fmea_fourway = [
    ['Shuttle Araç',      'Motor arızası',          'Shuttle devre dışı',  6, 3, 3, None],
    ['Shuttle Araç',      'Sensör hatası',          'Yanlış konum',        5, 4, 2, None],
    ['Shuttle Araç',      'Tekerlek aşınması',      'Hız düşüşü',         3, 5, 4, None],
    ['Asansör',           'Mekanik arıza',          'Kat erişimi kayıp',   7, 3, 3, None],
    ['Asansör',           'Encoder hatası',         'Konumlama hatası',    5, 3, 2, None],
    ['WMS/WCS',           'Yazılım çökmesi',        'Tam sistem duruşu',   9, 2, 2, None],
    ['WMS/WCS',           'İletişim hatası',        'Shuttle gecikme',     4, 4, 3, None],
    ['Konveyör',          'Bant kayması',           'Transfer gecikmesi',  4, 3, 4, None],
    ['Sensör/RFID',       'Okuma hatası',           'Envanter tutarsızlık', 5, 3, 3, None],
    ['Batarya',           'Erken deşarj',           'Shuttle duruşu',      5, 4, 3, None],
]

def fmea_hesapla(tablo):
    for satir in tablo:
        satir[6] = satir[3] * satir[4] * satir[5]  # RPN = S × O × D
    return sorted(tablo, key=lambda x: -x[6])

fmea_manuel = fmea_hesapla(fmea_manuel)
fmea_fourway = fmea_hesapla(fmea_fourway)

def fmea_yazdir(isim, tablo):
    print(f"\n  {isim}:")
    print(f"  {'Bileşen':<18} {'Arıza Modu':<22} {'S':>3} {'O':>3} {'D':>3} {'RPN':>5} {'Risk'}")
    print(f"  {'─'*68}")
    for r in tablo:
        risk = 'KRİTİK' if r[6]>=200 else ('YÜKSEK' if r[6]>=125 else ('ORTA' if r[6]>=50 else 'DÜŞÜK'))
        print(f"  {r[0]:<18} {r[1]:<22} {r[3]:>3} {r[4]:>3} {r[5]:>3} {r[6]:>5}  {risk}")

fmea_yazdir("MANUEL SİSTEM FMEA", fmea_manuel)
fmea_yazdir("FOUR-WAY SİSTEM FMEA", fmea_fourway)

# RPN istatistikleri
mn_rpn = [r[6] for r in fmea_manuel]
fw_rpn = [r[6] for r in fmea_fourway]
print(f"\n  RPN Özet:")
print(f"  {'Metrik':<24} {'Manuel':>10} {'Four-Way':>10}")
print(f"  {'Ortalama RPN':<24} {np.mean(mn_rpn):>10.1f} {np.mean(fw_rpn):>10.1f}")
print(f"  {'Maksimum RPN':<24} {max(mn_rpn):>10} {max(fw_rpn):>10}")
print(f"  {'RPN ≥ 200 (Kritik)':<24} {sum(1 for r in mn_rpn if r>=200):>10} {sum(1 for r in fw_rpn if r>=200):>10}")
print(f"  {'RPN ≥ 125 (Yüksek+)':<24} {sum(1 for r in mn_rpn if r>=125):>10} {sum(1 for r in fw_rpn if r>=125):>10}")

# =============================================================================
# 7. GÜVENİLİRLİK FONKSİYONU R(t) = e^(-λt)
# =============================================================================
t_saat = np.linspace(0, YILLIK_CALISMA, 500)
mn_Rt = np.exp(-mn_lambda * t_saat)
fw_Rt = np.exp(-fw_lambda * t_saat)

# =============================================================================
# 8. GRAFİKLER (5 panel)
# =============================================================================
C_FW='#00D4A8'; C_MN='#FF6B6B'; C_GOLD='#FFD700'
C_TEXT='#E8E8E8'; C_GRID='#2A2A3E'; C_BG='#0D1117'; C_PANEL='#161B22'

fig = plt.figure(figsize=(18, 22))
fig.patch.set_facecolor(C_BG)
fig.suptitle('Bileşen 9: MTBF/MTTR Güvenilirlik Modellemesi + FMEA\n'
             'Manuel Forkliftli Depo vs Four-Way Otomatik Depo — Raftürk',
             fontsize=15, fontweight='bold', color=C_TEXT, y=0.98)

# ─ Panel 1: Güvenilirlik fonksiyonu R(t) ──────────────────────────────────
ax1 = fig.add_subplot(3, 2, 1); ax1.set_facecolor(C_PANEL)
ax1.plot(t_saat/16, mn_Rt*100, '-', color=C_MN, lw=2.5, label=f'Manuel (MTBF={mn_mtbf:.0f}h)')
ax1.plot(t_saat/16, fw_Rt*100, '-', color=C_FW, lw=2.5, label=f'Four-Way (MTBF={fw_mtbf:.0f}h)')
ax1.axhline(36.8, color='#888', ls=':', alpha=0.5, lw=1)
ax1.text(YILLIK_CALISMA/16*0.95, 39, 'R(MTBF)=36.8%', ha='right', color='#888', fontsize=8)
ax1.set_xlabel('Çalışma Süresi (iş günü)', color=C_TEXT)
ax1.set_ylabel('Güvenilirlik R(t) %', color=C_TEXT)
ax1.set_title('Güvenilirlik Fonksiyonu R(t) = e^(-λt)\n(MIL-HDBK-217F)', 
              color=C_TEXT, fontsize=11, fontweight='bold', pad=12)
ax1.set_xlim(0, YILLIK_CALISMA/16); ax1.set_ylim(0, 105)
ax1.tick_params(colors=C_TEXT)
for s in ax1.spines.values(): s.set_edgecolor(C_GRID)
ax1.legend(fontsize=9, facecolor=C_PANEL, edgecolor=C_GRID, labelcolor=C_TEXT)
ax1.grid(alpha=0.15, color='white')

# ─ Panel 2: Kullanılabilirlik karşılaştırması ─────────────────────────────
ax2 = fig.add_subplot(3, 2, 2); ax2.set_facecolor(C_PANEL)
metrikler = ['Kullanılabilirlik\n(%)', 'MTBF\n(gün)', 'MTTR\n(saat)', 'Yıllık Arıza\n(adet)', 'Yıllık Duruş\n(saat)']
mn_vals = [mn_avail*100, mn_mtbf/16, mn_mttr, mn_ariza_yil, mn_durus]
fw_vals = [fw_avail*100, fw_mtbf/16, fw_mttr, fw_ariza_yil, fw_durus]
# Normalize for radar (0-1, her zaman büyük=iyi yönünde)
def norm_guv(mn_v, fw_v, buyuk_iyi=True):
    mx = max(mn_v, fw_v); mn = min(mn_v, fw_v)
    if mx == mn: return 0.5, 0.5
    r_mn = (mn_v - mn)/(mx - mn) if buyuk_iyi else (mx - mn_v)/(mx - mn)
    r_fw = (fw_v - mn)/(mx - mn) if buyuk_iyi else (mx - fw_v)/(mx - mn)
    return r_mn, r_fw

buyuk_iyi_flags = [True, True, False, False, False]  # Avail+MTBF büyük iyi, MTTR+arıza+duruş küçük iyi
mn_norm = []; fw_norm = []
for i in range(len(metrikler)):
    r1, r2 = norm_guv(mn_vals[i], fw_vals[i], buyuk_iyi_flags[i])
    mn_norm.append(r1); fw_norm.append(r2)

x_pos = np.arange(len(metrikler))
w = 0.35
b1 = ax2.bar(x_pos - w/2, mn_norm, w, color=C_MN, label='Manuel', edgecolor='none')
b2 = ax2.bar(x_pos + w/2, fw_norm, w, color=C_FW, label='Four-Way', edgecolor='none')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(metrikler, color=C_TEXT, fontsize=8)
ax2.set_ylabel('Normalize Skor (büyük=iyi)', color=C_TEXT, fontsize=9)
ax2.set_title('Güvenilirlik Metrikleri Karşılaştırması\n(Normalize 0–1)', 
              color=C_TEXT, fontsize=11, fontweight='bold', pad=12)
ax2.tick_params(colors=C_TEXT); ax2.set_ylim(0, 1.15)
for s in ax2.spines.values(): s.set_edgecolor(C_GRID)
ax2.legend(fontsize=9, facecolor=C_PANEL, edgecolor=C_GRID, labelcolor=C_TEXT)
ax2.grid(axis='y', alpha=0.15, color='white')

# ─ Panel 3: FMEA RPN karşılaştırması (yatay bar) ─────────────────────────
ax3 = fig.add_subplot(3, 2, 3); ax3.set_facecolor(C_PANEL)
mn_fmea_isim = [f"{r[0]}: {r[1]}" for r in fmea_manuel[:7]]
mn_fmea_rpn = [r[6] for r in fmea_manuel[:7]]
colors3 = ['#EF5350' if v>=200 else '#FF9800' if v>=125 else '#FFC107' if v>=50 else '#4CAF50' for v in mn_fmea_rpn]
bars3 = ax3.barh(mn_fmea_isim[::-1], mn_fmea_rpn[::-1], color=colors3[::-1], edgecolor='none', height=0.6)
for bar, val in zip(bars3, mn_fmea_rpn[::-1]):
    ax3.text(val+5, bar.get_y()+bar.get_height()/2, str(val),
             va='center', color=C_TEXT, fontsize=9, fontweight='bold')
ax3.axvline(200, color='#EF5350', ls='--', alpha=0.7, lw=1.5, label='Kritik (200)')
ax3.axvline(125, color='#FF9800', ls='--', alpha=0.5, lw=1, label='Yüksek (125)')
ax3.set_xlabel('RPN (Şiddet × Olasılık × Tespit)', color=C_TEXT, fontsize=9)
ax3.set_title('Manuel Sistem FMEA — RPN Sıralaması\n(IEC 60812)', 
              color=C_TEXT, fontsize=11, fontweight='bold', pad=12)
ax3.tick_params(colors=C_TEXT, labelsize=8)
for s in ax3.spines.values(): s.set_edgecolor(C_GRID)
ax3.legend(fontsize=8, facecolor=C_PANEL, edgecolor=C_GRID, labelcolor=C_TEXT, loc='lower right')
ax3.grid(axis='x', alpha=0.15, color='white')

# ─ Panel 4: FMEA RPN — Four-Way ──────────────────────────────────────────
ax4 = fig.add_subplot(3, 2, 4); ax4.set_facecolor(C_PANEL)
fw_fmea_isim = [f"{r[0]}: {r[1]}" for r in fmea_fourway[:7]]
fw_fmea_rpn = [r[6] for r in fmea_fourway[:7]]
colors4 = ['#EF5350' if v>=200 else '#FF9800' if v>=125 else '#FFC107' if v>=50 else '#4CAF50' for v in fw_fmea_rpn]
bars4 = ax4.barh(fw_fmea_isim[::-1], fw_fmea_rpn[::-1], color=colors4[::-1], edgecolor='none', height=0.6)
for bar, val in zip(bars4, fw_fmea_rpn[::-1]):
    ax4.text(val+3, bar.get_y()+bar.get_height()/2, str(val),
             va='center', color=C_TEXT, fontsize=9, fontweight='bold')
ax4.axvline(200, color='#EF5350', ls='--', alpha=0.7, lw=1.5, label='Kritik (200)')
ax4.axvline(125, color='#FF9800', ls='--', alpha=0.5, lw=1, label='Yüksek (125)')
ax4.set_xlabel('RPN (Şiddet × Olasılık × Tespit)', color=C_TEXT, fontsize=9)
ax4.set_title('Four-Way Sistem FMEA — RPN Sıralaması\n(IEC 60812)', 
              color=C_TEXT, fontsize=11, fontweight='bold', pad=12)
ax4.tick_params(colors=C_TEXT, labelsize=8)
for s in ax4.spines.values(): s.set_edgecolor(C_GRID)
ax4.legend(fontsize=8, facecolor=C_PANEL, edgecolor=C_GRID, labelcolor=C_TEXT, loc='lower right')
ax4.grid(axis='x', alpha=0.15, color='white')

# ─ Panel 5: Bileşen bazlı yıllık arıza katkısı (pasta grafik yan yana) ──
ax5a = fig.add_subplot(3, 2, 5); ax5a.set_facecolor(C_PANEL)
mn_isim = [d['isim'].split('(')[0].strip() for d in mn_det]
mn_yar = [d['yillik_ariza'] for d in mn_det]
renk5 = ['#EF5350','#FF9800','#FFC107','#42A5F5','#66BB6A']
wedges, texts, autotexts = ax5a.pie(mn_yar, labels=mn_isim, autopct='%1.1f%%',
    colors=renk5, textprops={'color':C_TEXT,'fontsize':8},
    pctdistance=0.75, startangle=90)
for t in autotexts: t.set_fontsize(8); t.set_color('white'); t.set_fontweight('bold')
ax5a.set_title(f'Manuel — Yıllık Arıza Dağılımı\n(Toplam: {mn_ariza_yil:.1f} arıza/yıl)',
               color=C_TEXT, fontsize=11, fontweight='bold', pad=12)

ax5b = fig.add_subplot(3, 2, 6); ax5b.set_facecolor(C_PANEL)
fw_isim = [d['isim'].split('(')[0].strip() for d in fw_det]
fw_yar = [d['yillik_ariza'] for d in fw_det]
renk6 = ['#26A69A','#42A5F5','#AB47BC','#FFA726','#78909C','#66BB6A','#EF5350']
wedges2, texts2, autotexts2 = ax5b.pie(fw_yar, labels=fw_isim, autopct='%1.1f%%',
    colors=renk6, textprops={'color':C_TEXT,'fontsize':7},
    pctdistance=0.75, startangle=90)
for t in autotexts2: t.set_fontsize(7); t.set_color('white'); t.set_fontweight('bold')
ax5b.set_title(f'Four-Way — Yıllık Arıza Dağılımı\n(Toplam: {fw_ariza_yil:.1f} arıza/yıl)',
               color=C_TEXT, fontsize=11, fontweight='bold', pad=12)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('bilesen9_guvenilirlik.png', dpi=200, bbox_inches='tight', facecolor=C_BG)
print("\n✓ Grafik kaydedildi: bilesen9_guvenilirlik.png")

# =============================================================================
# 9. ÖZET
# =============================================================================
print(f"\n{'═'*60}")
print("  ÖZET BULGULAR")
print(f"{'═'*60}")
print(f"  Four-Way MTBF {fw_mtbf:.0f}h vs Manuel {mn_mtbf:.0f}h")
print(f"    → Four-Way {fw_mtbf/mn_mtbf:.1f}x daha uzun arızasız çalışma")
print(f"  Four-Way MTTR {fw_mttr:.1f}h vs Manuel {mn_mttr:.1f}h")
print(f"    → Four-Way {mn_mttr/fw_mttr:.1f}x daha hızlı onarım")
print(f"  Kullanılabilirlik: FW {fw_avail*100:.3f}% vs MN {mn_avail*100:.3f}%")
print(f"    → Fark: {(fw_avail-mn_avail)*YILLIK_CALISMA:.1f} saat/yıl ek çalışma")
print(f"  FMEA: Manuel {sum(1 for r in mn_rpn if r>=200)} kritik arıza modu")
print(f"         Manuel ortalama RPN={np.mean(mn_rpn):.0f} vs FW={np.mean(fw_rpn):.0f}")
print(f"  İnsan hatası (operatör): Manuel'de RPN={fmea_manuel[0][6]}")
print(f"    → Four-Way'de bu risk kategorisi mevcut değil")
