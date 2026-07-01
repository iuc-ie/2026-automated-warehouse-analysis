# -*- coding: utf-8 -*-
"""
BİLEŞEN 6: Break-Even (Başabaş) Analizi
v4 değerleriyle birebir tutarlı

Akademik temel:
- Horngren, Datar & Rajan (2015): Cost Accounting (15th ed.)
- Park (2019): Fundamentals of Engineering Economics
- Brent (1973): Algorithms for Minimization without Derivatives

Hesaplanan break-even noktaları:
1. Yıllık Tasarruf alt sınırı
2. FW Yıllık Hacim alt sınırı
3. Saatlik Throughput alt sınırı
4. FW Yatırım Maliyeti üst sınırı
+ Margin of Safety (MoS) hesabı

Spyder/Anaconda'da çalıştırmak için: F5 (Run)
"""
import numpy as np
import matplotlib.pyplot as plt
import json
from scipy.optimize import brentq

# ============================================================
# 1. PARAMETRELER (v4 — Bileşen 4-5 ile birebir)
# ============================================================
N_YIL = 10
ISKONTO = 0.15
ENFLASYON = 0.25
GUN_YIL = 312
PALET_GELIR = 5  # USD/palet

# Yatırım
FW_YATIRIM = 2_000_000
MN_YATIRIM = 210_872
EK_YATIRIM = FW_YATIRIM - MN_YATIRIM

# Yıllık tasarruf bileşenleri
ISGUCU = 118_078
THROUGHPUT_GELIR = 374_400
HASAR = 38_500
KAZA = 25_000
EK_OPS = 24_881
ENERJI = 5_000
BAKIM = -10_000

YILLIK_TASARRUF = ISGUCU + THROUGHPUT_GELIR + HASAR + KAZA + EK_OPS + ENERJI + BAKIM
SABIT_TASARRUF = ISGUCU + HASAR + KAZA + EK_OPS + ENERJI + BAKIM

# Throughput
BASELINE_THROUGHPUT_HOUR = 120
GUN_SAAT_FW = 24
GUN_SAAT_MN = 22

fw_yillik_baseline = BASELINE_THROUGHPUT_HOUR * GUN_SAAT_FW * GUN_YIL
mn_yillik_baseline = BASELINE_THROUGHPUT_HOUR * GUN_SAAT_MN * GUN_YIL

print(f"Baseline yıllık tasarruf: {YILLIK_TASARRUF:,.0f} USD/yıl")
print(f"Baseline ek yatırım:      {EK_YATIRIM:,.0f} USD")

# ============================================================
# 2. NPV HESAP FONKSİYONU
# ============================================================
def npv_hesap(yillik_tasarruf, ek_yatirim=EK_YATIRIM, n_yil=N_YIL,
              iskonto=ISKONTO, enflasyon=ENFLASYON):
    npv = 0
    for yil in range(1, n_yil + 1):
        yillik = yillik_tasarruf * (1 + enflasyon * 0.7) ** (yil - 1)
        discounted = yillik / ((1 + iskonto) ** yil)
        npv += discounted
    npv -= ek_yatirim
    return npv

baseline_npv = npv_hesap(YILLIK_TASARRUF)
print(f"Baseline NPV (10 yıl): {baseline_npv:,.0f} USD")

# ============================================================
# 3. PAYBACK SÜRELERİ
# ============================================================
cumulative = 0
payback_simple = None
for yil in range(1, 21):
    yillik = YILLIK_TASARRUF * (1 + ENFLASYON * 0.7) ** (yil - 1)
    cumulative_prev = cumulative
    cumulative += yillik
    if cumulative >= EK_YATIRIM and payback_simple is None:
        payback_simple = (yil - 1) + (EK_YATIRIM - cumulative_prev) / yillik
        break

cumulative_disc = 0
payback_disc = None
for yil in range(1, 21):
    yillik = YILLIK_TASARRUF * (1 + ENFLASYON * 0.7) ** (yil - 1)
    discounted = yillik / ((1 + ISKONTO) ** yil)
    cumulative_prev = cumulative_disc
    cumulative_disc += discounted
    if cumulative_disc >= EK_YATIRIM and payback_disc is None:
        payback_disc = (yil - 1) + (EK_YATIRIM - cumulative_prev) / discounted
        break

print(f"\nPayback:  Basit {payback_simple:.2f} yıl  |  İskontolu {payback_disc:.2f} yıl")

# ============================================================
# 4. BREAK-EVEN HESAPLARI
# ============================================================
# 4.1 Yıllık tasarruf alt sınırı (Brent's method)
be_tasarruf = brentq(lambda t: npv_hesap(t), 1, 2_000_000)
mos_tasarruf = (YILLIK_TASARRUF - be_tasarruf) / YILLIK_TASARRUF * 100

# 4.2 FW yıllık hacim alt sınırı
ek_hacim_be = (be_tasarruf - SABIT_TASARRUF) / PALET_GELIR
fw_hacim_be = mn_yillik_baseline + ek_hacim_be
mos_hacim = (fw_yillik_baseline - fw_hacim_be) / fw_yillik_baseline * 100

# 4.3 Saatlik throughput
saatlik_be = fw_hacim_be / (GUN_SAAT_FW * GUN_YIL)
mos_saatlik = (BASELINE_THROUGHPUT_HOUR - saatlik_be) / BASELINE_THROUGHPUT_HOUR * 100

# 4.4 FW yatırım üst sınırı
discount_factor_total = sum(
    (1 + ENFLASYON * 0.7) ** (yil - 1) / (1 + ISKONTO) ** yil
    for yil in range(1, N_YIL + 1)
)
max_ek_yatirim = YILLIK_TASARRUF * discount_factor_total
max_fw_yatirim = max_ek_yatirim + MN_YATIRIM
mos_yatirim = (max_fw_yatirim - FW_YATIRIM) / FW_YATIRIM * 100

print(f"\n=== BREAK-EVEN SONUÇLARI ===")
print(f"  Yıllık Tasarruf BE:    {be_tasarruf:>12,.0f} USD  (MoS %{mos_tasarruf:.0f})")
print(f"  FW Yıllık Hacim BE:    {fw_hacim_be:>12,.0f} palet (MoS %{mos_hacim:.0f})")
print(f"  Saatlik Throughput BE: {saatlik_be:>12.1f} p/h    (MoS %{mos_saatlik:.0f})")
print(f"  Max FW Yatırım:        {max_fw_yatirim:>12,.0f} USD  (MoS %{mos_yatirim:.0f})")

# ============================================================
# 5. KÜMÜLATIF NAKİT AKIŞI ÖZET GRAFİĞİ
# ============================================================
yillar = list(range(0, N_YIL + 1))
cum_undisc = [0]
cum_disc = [0]
for yil in range(1, N_YIL + 1):
    yillik = YILLIK_TASARRUF * (1 + ENFLASYON * 0.7) ** (yil - 1)
    discounted = yillik / ((1 + ISKONTO) ** yil)
    cum_undisc.append(cum_undisc[-1] + yillik)
    cum_disc.append(cum_disc[-1] + discounted)

net_undisc = [c - EK_YATIRIM for c in cum_undisc]
net_disc = [c - EK_YATIRIM for c in cum_disc]

C_FW = '#1D9E75'
C_BE = '#E24B4A'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle('Şekil 6 — Kümülatif Nakit Akışı ve Break-Even Noktaları',
             fontsize=13, fontweight='bold', y=0.99)

ax = axes[0]
ax.plot(yillar, [v/1e6 for v in net_undisc], color=C_FW, linewidth=2.5, marker='o')
ax.axhline(0, color='red', linestyle='-', alpha=0.6)
ax.axvline(payback_simple, color=C_FW, linestyle=':', linewidth=1.5)
ax.set_xlabel('Yıl')
ax.set_ylabel('Kümülatif Net Pozisyon (M USD)')
ax.set_title(f'İskontosuz — Basit Payback {payback_simple:.2f} yıl')
ax.grid(True, alpha=0.3)

ax = axes[1]
ax.plot(yillar, [v/1e6 for v in net_disc], color='#FF9800', linewidth=2.5, marker='s')
ax.axhline(0, color='red', linestyle='-', alpha=0.6)
ax.axvline(payback_disc, color='#FF9800', linestyle=':', linewidth=1.5)
ax.set_xlabel('Yıl')
ax.set_ylabel('Kümülatif NPV (M USD)')
ax.set_title(f'İskontolu — Iskontolu Payback {payback_disc:.2f} yıl')
ax.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('break_even.png', dpi=200, bbox_inches='tight')
plt.show()

print(f"\n✓ Break-even analizi tamamlandı")
