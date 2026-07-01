# -*- coding: utf-8 -*-
"""
BİLEŞEN 12: Markov Zinciri Sistem Durum Analizi
Manuel Forkliftli Depo vs Four-Way Otomatik Depo
Raftürk Vaka Çalışması

Metodoloji: Sürekli Zamanlı Markov Zinciri (Continuous-Time Markov Chain — CTMC)
Üç durum modeli: S0=Çalışma, S1=Arıza, S2=Planlı Bakım

Akademik referanslar:
  - Trivedi, K.S. & Bobbio, A. (2017). Reliability and Availability Engineering.
    Cambridge University Press. [Ch.9: CTMC Availability Models]
  - Ye, Y. vd. (2019). Modeling for reliability optimization of system design
    and maintenance based on Markov chain theory. Computers & Chemical Engineering.
  - Alaswad, S. & Xiang, Y. (2017). A review on condition-based maintenance
    optimization models for stochastically deteriorating system.
    European Journal of Operational Research, 258(3), 849-864.
  - IEC 61703 (2016). Mathematical expressions for reliability, availability,
    maintainability and maintenance support terms.

Veri kaynakları notu:
  - MTBF / MTTR değerleri: Bileşen 9 güvenilirlik modelinden alınmıştır.
    B9 parametreleri MIL-HDBK-217F ve endüstri kataloglarına dayalı TAHMİNDİR.
    Raftürk'ten gerçek saha verisi alındığında güncellenmelidir.
  - Planlı bakım periyodu: Endüstri standardı (forklift: 500h, FW: 1000h)
    — TAHMİN, üretici dokümantasyonu ile doğrulanmalıdır.

CTMC Sınırlılığı (Karmakar & Gopinath, 2015):
  Markov özelliği exponansiyel dağılım varsayımı gerektirir.
  Gerçek arıza süreleri Weibull dağılımı izleyebilir — bu model
  yaklaşık bir alt sınır tahmini sunar.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from scipy.linalg import null_space
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# 1. PARAMETRELER — B9'DAN ALINAN DEĞERLER
# =============================================================================

# ── B9 sistem seviyesi MTBF/MTTR (TAHMİN — MIL-HDBK-217F bazlı) ─────────────
# ⚠️ Bu değerler B9 bottom-up güvenilirlik modelinden türetilmiştir.
MN_MTBF = 223.7   # saat — Manuel sistem (B9 tahmini)
MN_MTTR = 4.09    # saat — Manuel sistem (B9 tahmini)
FW_MTBF = 402.7   # saat — Four-Way sistemi (B9 tahmini)
FW_MTTR = 1.71    # saat — Four-Way sistemi (B9 tahmini)

# ── Planlı bakım parametreleri (TAHMİN — endüstri standardı) ─────────────────
# Manuel: forklift planlı bakım her 500 saatte bir, ~4 saat sürer
# FW: shuttle planlı bakım her 1000 saatte bir, ~2 saat sürer
# Kaynak: Toyota forklift bakım kılavuzu, Swisslog AS/RS bakım protokolü
MN_BAKIM_PERIYOT = 500    # saat   — ⚠ tahmin
MN_BAKIM_SURE    = 4.0    # saat   — ⚠ tahmin
FW_BAKIM_PERIYOT = 1000   # saat   — ⚠ tahmin
FW_BAKIM_SURE    = 2.0    # saat   — ⚠ tahmin

# ── Geçiş oranları (CTMC, Trivedi & Bobbio 2017) ─────────────────────────────
# λ = arıza oranı (S0→S1): 1/MTBF  [1/saat]
# μ = onarım oranı (S1→S0): 1/MTTR  [1/saat]
# α = planlı bakım oranı (S0→S2): 1/bakım_periyot  [1/saat]
# β = bakım tamamlama oranı (S2→S0): 1/bakım_sure  [1/saat]

def gecis_oranlari(mtbf, mttr, bakim_p, bakim_s):
    lam  = 1 / mtbf       # arıza oranı
    mu   = 1 / mttr       # onarım oranı
    alfa = 1 / bakim_p    # planlı bakıma geçiş oranı
    beta = 1 / bakim_s    # bakımdan çıkış oranı
    return lam, mu, alfa, beta

MN_LAM, MN_MU, MN_ALFA, MN_BETA = gecis_oranlari(MN_MTBF, MN_MTTR, MN_BAKIM_PERIYOT, MN_BAKIM_SURE)
FW_LAM, FW_MU, FW_ALFA, FW_BETA = gecis_oranlari(FW_MTBF, FW_MTTR, FW_BAKIM_PERIYOT, FW_BAKIM_SURE)

# =============================================================================
# 2. CTMC MODELİ — Q MATRİSİ VE KARARLI DURUM
# =============================================================================
# Durumlar: S0=Çalışma, S1=Arıza (planlanmamış), S2=Planlı Bakım
# Q matrisi (oran matrisi):
#       S0          S1      S2
# S0 [-(λ+α)       λ       α  ]
# S1 [  μ        -μ        0  ]
# S2 [  β          0      -β  ]

def Q_matrisi(lam, mu, alfa, beta):
    return np.array([
        [-(lam + alfa),  lam,    alfa],
        [ mu,           -mu,    0   ],
        [ beta,          0,    -beta]
    ])

def kararli_durum(Q):
    """
    π·Q = 0 ve Σπ = 1 koşulunu çöz.
    Yöntem: null_space(Q^T) → normalize et.
    Trivedi & Bobbio (2017), Ch.9, Denklem 9.14
    """
    ns = null_space(Q.T)
    pi = np.abs(ns[:, 0])
    pi = pi / pi.sum()
    return pi

MN_Q  = Q_matrisi(MN_LAM, MN_MU, MN_ALFA, MN_BETA)
FW_Q  = Q_matrisi(FW_LAM, FW_MU, FW_ALFA, FW_BETA)
MN_PI = kararli_durum(MN_Q)
FW_PI = kararli_durum(FW_Q)

# Kullanılabilirlik = P(S0=Çalışma)
MN_A = MN_PI[0]
FW_A = FW_PI[0]

# MTBF bazlı kullanılabilirlik (IEC 61703) — doğrulama için
MN_A_IEC = MN_MTBF / (MN_MTBF + MN_MTTR)
FW_A_IEC = FW_MTBF / (FW_MTBF + FW_MTTR)

# =============================================================================
# 3. GEÇİCİ ANALİZ — Zaman İçinde Durum Olasılıkları
# =============================================================================
from scipy.linalg import expm

def gecici_analiz(Q, t_max=2000, n=500):
    """π(t) = π(0) · exp(Qt) — Trivedi & Bobbio (2017), Denklem 9.8"""
    t_arr = np.linspace(0, t_max, n)
    pi0   = np.array([1.0, 0.0, 0.0])   # başlangıç: tamamen çalışır
    sonuc = np.zeros((n, 3))
    for i, t in enumerate(t_arr):
        sonuc[i] = pi0 @ expm(Q * t)
    return t_arr, sonuc

MN_T, MN_TRAN = gecici_analiz(MN_Q)
FW_T, FW_TRAN = gecici_analiz(FW_Q)

# =============================================================================
# 4. OPERASYONEL ETKİ HESAPLARI
# =============================================================================
YILLIK_SAAT = 312 * 16   # 4992 saat/yıl

# Yıllık beklenen kesinti süreleri
MN_PLANSIZ_KESINTI = (1 - MN_A_IEC) * YILLIK_SAAT * (MN_LAM/(MN_LAM+MN_ALFA))
FW_PLANSIZ_KESINTI = (1 - FW_A_IEC) * YILLIK_SAAT * (FW_LAM/(FW_LAM+FW_ALFA))
MN_PLANLI_BAKIM    = (MN_ALFA / (MN_LAM + MN_ALFA)) * (1 - MN_A_IEC) * YILLIK_SAAT
FW_PLANLI_BAKIM    = (FW_ALFA / (FW_LAM + FW_ALFA)) * (1 - FW_A_IEC) * YILLIK_SAAT

# Kullanılabilirlik farkından kaynaklanan ek verimli saat
EKSTRA_VERIMLI_SAAT = (FW_A - MN_A) * YILLIK_SAAT
# Ekstra palet (120 p/s × ekstra saat)
EKSTRA_PALET = EKSTRA_VERIMLI_SAAT * 120

# =============================================================================
# 5. YAZDIR
# =============================================================================
print("╔══════════════════════════════════════════════════════════════╗")
print("║  BİLEŞEN 12: MARKOV ZİNCİRİ SİSTEM DURUM ANALİZİ           ║")
print("║  CTMC — 3 Durum: Çalışma / Arıza / Planlı Bakım            ║")
print("╚══════════════════════════════════════════════════════════════╝")
print(f"\n  ⚠ MTBF/MTTR: B9 tahmini (MIL-HDBK-217F bazlı)")
print(f"  ⚠ Planlı bakım periyodu: Endüstri standardı tahmini")
print(f"  ⚠ CTMC sınırlılığı: Exponansiyel dağılım varsayımı (Weibull daha gerçekçi)")

print(f"\n{'─'*64}")
print(f"  {'Parametre':<38} {'Manuel':>11} {'Four-Way':>11}")
print(f"{'─'*64}")
print(f"  {'MTBF (saat)':<38} {MN_MTBF:>11.1f} {FW_MTBF:>11.1f}")
print(f"  {'MTTR (saat)':<38} {MN_MTTR:>11.2f} {FW_MTTR:>11.2f}")
print(f"  {'Planlı bakım periyodu (saat)':<38} {MN_BAKIM_PERIYOT:>11.0f} {FW_BAKIM_PERIYOT:>11.0f}")
print(f"  {'λ — arıza oranı (1/saat)':<38} {MN_LAM:>11.6f} {FW_LAM:>11.6f}")
print(f"  {'μ — onarım oranı (1/saat)':<38} {MN_MU:>11.6f} {FW_MU:>11.6f}")
print(f"  {'α — planlı bakım oranı (1/saat)':<38} {MN_ALFA:>11.6f} {FW_ALFA:>11.6f}")

print(f"\n  Q MATRİSİ — MANUEL:")
for row in MN_Q:
    print(f"    {row}")
print(f"\n  Q MATRİSİ — FOUR-WAY:")
for row in FW_Q:
    print(f"    {row}")

print(f"\n{'─'*64}")
print(f"  KARARLI DURUM OLASILIKLARI π (Trivedi & Bobbio 2017)")
print(f"{'─'*64}")
print(f"  {'Durum':<38} {'Manuel':>11} {'Four-Way':>11}")
print(f"{'─'*64}")
print(f"  {'π₀ — Çalışma (Kullanılabilirlik)':<38} {MN_PI[0]:>11.4f} {FW_PI[0]:>11.4f}")
print(f"  {'π₁ — Arıza (planlanmamış)':<38} {MN_PI[1]:>11.4f} {FW_PI[1]:>11.4f}")
print(f"  {'π₂ — Planlı Bakım':<38} {MN_PI[2]:>11.4f} {FW_PI[2]:>11.4f}")
print(f"  {'Toplam':<38} {sum(MN_PI):>11.4f} {sum(FW_PI):>11.4f}")
print(f"\n  IEC 61703 doğrulama A=MTBF/(MTBF+MTTR):")
print(f"  Manuel : {MN_A_IEC:.4f}  |  Four-Way : {FW_A_IEC:.4f}")
print(f"\n{'─'*64}")
print(f"  OPERASYONEL ETKİ ({YILLIK_SAAT:,} saat/yıl)")
print(f"{'─'*64}")
print(f"  {'Kullanılabilirlik farkı':<38} {FW_A-MN_A:>+11.4f}")
print(f"  {'Ekstra verimli saat/yıl':<38} {EKSTRA_VERIMLI_SAAT:>+11.1f} saat")
print(f"  {'Ekstra palet/yıl (120 p/s)':<38} {EKSTRA_PALET:>+11.0f} palet")

# =============================================================================
# 6. GRAFİKLER
# =============================================================================
fig = plt.figure(figsize=(16, 12))
gs  = GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.35)
ax1 = fig.add_subplot(gs[0, :2])
ax2 = fig.add_subplot(gs[0, 2])
ax3 = fig.add_subplot(gs[1, :2])
ax4 = fig.add_subplot(gs[1, 2])

fig.suptitle(
    'Bileşen 12: Markov Zinciri Sistem Durum Analizi\n'
    'CTMC — 3 Durum Modeli (Çalışma / Arıza / Planlı Bakım)  |  '
    'Trivedi & Bobbio (2017)',
    fontsize=12, fontweight='bold', y=1.01
)

C_MN='#E24B4A'; C_FW='#1D9E75'; C_BAK='#F5A623'; C_ARZ='#4E9AF1'

# ── Graf 1: Geçici analiz — P(Çalışma) zaman içinde ─────────────────────────
ax1.plot(MN_T, MN_TRAN[:,0], color=C_MN, lw=2.5, label='Manuel — P(Çalışma)')
ax1.plot(FW_T, FW_TRAN[:,0], color=C_FW, lw=2.5, label='Four-Way — P(Çalışma)')
ax1.plot(MN_T, MN_TRAN[:,1], color=C_MN, lw=1.5, ls='--', alpha=0.6, label='Manuel — P(Arıza)')
ax1.plot(FW_T, FW_TRAN[:,1], color=C_FW, lw=1.5, ls='--', alpha=0.6, label='Four-Way — P(Arıza)')

# Kararlı durum çizgileri
ax1.axhline(MN_PI[0], color=C_MN, lw=1, ls=':', alpha=0.7)
ax1.axhline(FW_PI[0], color=C_FW, lw=1, ls=':', alpha=0.7)
ax1.text(1850, MN_PI[0]+0.003, f'MN π₀={MN_PI[0]:.4f}', fontsize=8, color=C_MN, fontweight='bold')
ax1.text(1850, FW_PI[0]-0.007, f'FW π₀={FW_PI[0]:.4f}', fontsize=8, color=C_FW, fontweight='bold')

ax1.set_xlabel('Zaman (saat)', fontsize=10)
ax1.set_ylabel('Durum Olasılığı π(t)', fontsize=10)
ax1.set_title('Geçici Durum Analizi — π(t) = π(0)·exp(Qt)\n(Başlangıç: sistem tamamen çalışır)',
              fontsize=11, fontweight='bold')
ax1.legend(fontsize=9, loc='center right')
ax1.grid(alpha=0.2)
ax1.set_xlim(0, 2000)
ax1.set_ylim(0, 1.05)
ax1.text(0.02, 0.05, '⚠ MTBF/MTTR: B9 tahmini\n⚠ Exp. dağılım varsayımı',
         transform=ax1.transAxes, fontsize=8,
         bbox=dict(boxstyle='round', facecolor='#FFF8E1', alpha=0.85))

# ── Graf 2: Kararlı durum pasta ──────────────────────────────────────────────
durumlar = ['Çalışma\n(π₀)', 'Arıza\n(π₁)', 'Bakım\n(π₂)']
renkler  = [C_FW, C_ARZ, C_BAK]

x = np.arange(3); w = 0.35
bars_mn = ax2.bar(x - w/2, MN_PI*100, w, color=[C_MN]*3, alpha=0.85,
                  edgecolor='white', label='Manuel')
bars_fw = ax2.bar(x + w/2, FW_PI*100, w, color=renkler, alpha=0.85,
                  edgecolor='white', label='Four-Way')

for bar, v in zip(bars_mn, MN_PI*100):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
             f'{v:.2f}%', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=C_MN)
for bar, v in zip(bars_fw, FW_PI*100):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
             f'{v:.2f}%', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#0F6E56')

ax2.set_xticks(x)
ax2.set_xticklabels(durumlar, fontsize=9)
ax2.set_ylabel('Kararlı Durum Olasılığı (%)', fontsize=9)
ax2.set_title('Kararlı Durum Dağılımı\nπ·Q=0, Σπ=1',
              fontsize=11, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(axis='y', alpha=0.2)
ax2.set_ylim(0, 105)

# ── Graf 3: Q matrisi ısı haritası (iki sistem) ──────────────────────────────
durum_etiketleri = ['S₀\nÇalışma', 'S₁\nArıza', 'S₂\nBakım']

im = ax3.imshow(np.abs(MN_Q), cmap='Reds', aspect='auto', alpha=0.8)
for i in range(3):
    for j in range(3):
        val = MN_Q[i,j]
        renk = 'white' if abs(val) > np.abs(MN_Q).max()*0.5 else 'black'
        ok = '→' if val > 0 else ('↓' if i==j else '')
        ax3.text(j, i, f'{val:.5f}\n{ok}',
                 ha='center', va='center', fontsize=9, color=renk, fontweight='bold')
ax3.set_xticks(range(3)); ax3.set_yticks(range(3))
ax3.set_xticklabels(durum_etiketleri, fontsize=9)
ax3.set_yticklabels(durum_etiketleri, fontsize=9)
ax3.set_title('Q Matrisi (Oran Matrisi) — Manuel\n'
              'q_ij: i durumundan j\'ye geçiş oranı (1/saat)',
              fontsize=11, fontweight='bold')
plt.colorbar(im, ax=ax3, label='|q_ij| (1/saat)')

# ── Graf 4: Kullanılabilirlik karşılaştırma ve operasyonel etki ──────────────
kategoriler = ['Kullanılabilirlik\n(π₀, %)', 'Arızada\nGeçen Süre\n(saat/yıl)',
               'Ekstra Verimli\nSaat/Yıl (FW)']

mn_vals = [MN_A*100, MN_PI[1]*YILLIK_SAAT, 0]
fw_vals = [FW_A*100, FW_PI[1]*YILLIK_SAAT, EKSTRA_VERIMLI_SAAT]

x4 = np.arange(3); w4 = 0.35
b_mn = ax4.bar(x4[:2] - w4/2, mn_vals[:2], w4, color=C_MN, alpha=0.85,
               edgecolor='white', label='Manuel')
b_fw = ax4.bar(x4[:2] + w4/2, fw_vals[:2], w4, color=C_FW, alpha=0.85,
               edgecolor='white', label='Four-Way')
b_ek = ax4.bar(x4[2], fw_vals[2], w4, color='#4E9AF1', alpha=0.85,
               edgecolor='white', label='FW Kazanım')

for bar, v in [(b_mn[0],mn_vals[0]),(b_fw[0],fw_vals[0])]:
    ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.2,
             f'{v:.2f}%', ha='center', va='bottom', fontsize=8.5, fontweight='bold')
for bar, v in [(b_mn[1],mn_vals[1]),(b_fw[1],fw_vals[1]),(b_ek[0],fw_vals[2])]:
    ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
             f'{v:.0f}h', ha='center', va='bottom', fontsize=8.5, fontweight='bold')

ax4.set_xticks(x4)
ax4.set_xticklabels(kategoriler, fontsize=8.5)
ax4.set_title('Kullanılabilirlik & Operasyonel Etki\n'
              f'(Yıllık {YILLIK_SAAT:,} saat bazında)',
              fontsize=11, fontweight='bold')
ax4.legend(fontsize=9); ax4.grid(axis='y', alpha=0.2)

plt.savefig('/home/claude/bilesen12_markov.png', dpi=200, bbox_inches='tight')
plt.close()
print("\nGrafik kaydedildi: bilesen12_markov.png")
