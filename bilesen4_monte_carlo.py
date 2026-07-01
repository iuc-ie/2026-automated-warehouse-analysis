# -*- coding: utf-8 -*-
"""
BİLEŞEN 4: Monte Carlo Risk Simülasyonu
v4 finansal değerleriyle: 1.789.128 USD ek yatırım, 580.859 USD/yıl tasarruf

Akademik temel:
- Glasserman (2004): Monte Carlo Methods in Financial Engineering
- Vose (2008): Risk Analysis - A Quantitative Guide
- Hubbard (2014): How to Measure Anything

10.000 iterasyon, 10 yıl analiz süresi, %15 iskonto

Spyder/Anaconda'da çalıştırmak için: F5 (Run)
"""
import numpy as np
import matplotlib.pyplot as plt
import json

np.random.seed(42)

# ============================================================
# 1. PARAMETRELER (v4 ile birebir tutarlı)
# ============================================================
N_ITER = 10000
N_YIL = 10
ISKONTO_ORAN = 0.15

# Yatırım: triangular(min, mode, max) — v4 baseline
FW_YATIRIM_MIN, FW_YATIRIM_MODE, FW_YATIRIM_MAX = 1_800_000, 2_000_000, 2_300_000
MN_YATIRIM_MIN, MN_YATIRIM_MODE, MN_YATIRIM_MAX = 195_000, 210_872, 230_000

# Yıllık tasarruf kalemleri (USD/yıl)
ISGUCU_MIN, ISGUCU_MODE, ISGUCU_MAX = 100_000, 118_078, 140_000
THROUGHPUT_GELIR_MIN, THROUGHPUT_GELIR_MODE, THROUGHPUT_GELIR_MAX = 280_000, 374_400, 480_000
HASAR_MIN, HASAR_MODE, HASAR_MAX = 25_000, 38_500, 60_000
KAZA_MIN, KAZA_MODE, KAZA_MAX = 10_000, 25_000, 45_000
EK_OPS_MIN, EK_OPS_MODE, EK_OPS_MAX = 15_000, 24_881, 40_000
ENERJI_TASARRUF_MIN, ENERJI_TASARRUF_MODE, ENERJI_TASARRUF_MAX = -10_000, 5_000, 25_000
BAKIM_FARKI_MIN, BAKIM_FARKI_MODE, BAKIM_FARKI_MAX = -25_000, -10_000, 10_000

ENFLASYON_MIN, ENFLASYON_MODE, ENFLASYON_MAX = 0.20, 0.25, 0.35

# ============================================================
# 2. MONTE CARLO SİMÜLASYONU
# ============================================================
print(f"Monte Carlo: {N_ITER:,} iterasyon, {N_YIL} yıl, %{ISKONTO_ORAN*100:.0f} iskonto")

# Triangular örnekler
fw_yatirim = np.random.triangular(FW_YATIRIM_MIN, FW_YATIRIM_MODE, FW_YATIRIM_MAX, N_ITER)
mn_yatirim = np.random.triangular(MN_YATIRIM_MIN, MN_YATIRIM_MODE, MN_YATIRIM_MAX, N_ITER)
ek_yatirim = fw_yatirim - mn_yatirim

isgucu = np.random.triangular(ISGUCU_MIN, ISGUCU_MODE, ISGUCU_MAX, N_ITER)
throughput_gelir = np.random.triangular(THROUGHPUT_GELIR_MIN, THROUGHPUT_GELIR_MODE, THROUGHPUT_GELIR_MAX, N_ITER)
hasar = np.random.triangular(HASAR_MIN, HASAR_MODE, HASAR_MAX, N_ITER)
kaza = np.random.triangular(KAZA_MIN, KAZA_MODE, KAZA_MAX, N_ITER)
ek_ops = np.random.triangular(EK_OPS_MIN, EK_OPS_MODE, EK_OPS_MAX, N_ITER)
enerji = np.random.triangular(ENERJI_TASARRUF_MIN, ENERJI_TASARRUF_MODE, ENERJI_TASARRUF_MAX, N_ITER)
bakim = np.random.triangular(BAKIM_FARKI_MIN, BAKIM_FARKI_MODE, BAKIM_FARKI_MAX, N_ITER)
enflasyon = np.random.triangular(ENFLASYON_MIN, ENFLASYON_MODE, ENFLASYON_MAX, N_ITER)

yillik_tasarruf_yil1 = isgucu + throughput_gelir + hasar + kaza + ek_ops + enerji + bakim
print(f"Yıllık tasarruf (yıl 1) ortalaması: {yillik_tasarruf_yil1.mean():,.0f} USD")

# 10 yıllık NPV
npv = np.zeros(N_ITER)
discounted_savings = np.zeros((N_ITER, N_YIL))
cumulative_undiscounted = np.zeros((N_ITER, N_YIL))

for yil in range(1, N_YIL + 1):
    yillik = yillik_tasarruf_yil1 * (1 + enflasyon * 0.7) ** (yil - 1)
    discount = (1 + ISKONTO_ORAN) ** yil
    discounted = yillik / discount
    discounted_savings[:, yil-1] = discounted
    npv += discounted
    if yil == 1:
        cumulative_undiscounted[:, 0] = yillik
    else:
        cumulative_undiscounted[:, yil-1] = cumulative_undiscounted[:, yil-2] + yillik

npv = npv - ek_yatirim

# Basit payback
payback_simple = np.zeros(N_ITER)
for i in range(N_ITER):
    cum = cumulative_undiscounted[i]
    yatirim = ek_yatirim[i]
    if cum[-1] < yatirim:
        payback_simple[i] = N_YIL + 1
    else:
        for y in range(N_YIL):
            if cum[y] >= yatirim:
                if y == 0:
                    payback_simple[i] = yatirim / cum[0]
                else:
                    payback_simple[i] = y + (yatirim - cum[y-1]) / (cum[y] - cum[y-1])
                break

# İskontolu payback
payback_disc = np.zeros(N_ITER)
cum_disc = np.cumsum(discounted_savings, axis=1)
for i in range(N_ITER):
    yatirim = ek_yatirim[i]
    if cum_disc[i, -1] < yatirim:
        payback_disc[i] = N_YIL + 1
    else:
        for y in range(N_YIL):
            if cum_disc[i, y] >= yatirim:
                if y == 0:
                    payback_disc[i] = yatirim / cum_disc[i, 0]
                else:
                    payback_disc[i] = y + (yatirim - cum_disc[i, y-1]) / (cum_disc[i, y] - cum_disc[i, y-1])
                break

# ============================================================
# 3. İSTATİSTİKLER
# ============================================================
print(f"\n=== NPV (10 yıl, USD) ===")
print(f"  Ortalama:    {npv.mean():>14,.0f}")
print(f"  Medyan:      {np.median(npv):>14,.0f}")
print(f"  P5:          {np.percentile(npv, 5):>14,.0f}")
print(f"  P95:         {np.percentile(npv, 95):>14,.0f}")
print(f"  P(NPV>0):    %{(npv > 0).mean()*100:.1f}")

print(f"\n=== Basit Payback (yıl) ===")
print(f"  Medyan:      {np.median(payback_simple):>6.2f}")
print(f"  P95:         {np.percentile(payback_simple, 95):>6.2f}")
print(f"  P(<5 yıl):   %{(payback_simple < 5).mean()*100:.1f}")

print(f"\n=== İskontolu Payback (yıl) ===")
print(f"  Medyan:      {np.median(payback_disc):>6.2f}")

# ============================================================
# 4. GRAFİKLER (özet)
# ============================================================
C_FW = '#1D9E75'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle('Şekil 4.1 — Monte Carlo NPV ve Payback Dağılımları',
             fontsize=13, fontweight='bold', y=0.99)

ax = axes[0]
ax.hist(npv/1e6, bins=50, color=C_FW, alpha=0.7, edgecolor='white')
ax.axvline(np.median(npv)/1e6, color='black', linestyle='--', linewidth=2)
ax.axvline(0, color='red', linestyle='-', linewidth=1.5, alpha=0.6)
ax.set_xlabel('NPV (milyon USD)')
ax.set_ylabel('Frekans')
ax.set_title(f'NPV — P(NPV>0) = %{(npv > 0).mean()*100:.1f}')
ax.grid(axis='y', alpha=0.3)

ax = axes[1]
ax.hist(payback_simple, bins=40, color=C_FW, alpha=0.7, edgecolor='white')
ax.axvline(np.median(payback_simple), color='black', linestyle='--', linewidth=2)
ax.axvline(5, color='red', linestyle=':', linewidth=1.5, alpha=0.6, label='5 yıl eşiği')
ax.set_xlabel('Payback (yıl)')
ax.set_ylabel('Frekans')
ax.set_title(f'Payback medyan: {np.median(payback_simple):.2f} yıl')
ax.legend()
ax.grid(axis='y', alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('sekil_4_1_ozet.png', dpi=200, bbox_inches='tight')
plt.show()

print("\n✓ Bileşen 4 tamamlandı")
