# -*- coding: utf-8 -*-
"""
BİLEŞEN 5 - Tornado Analizi Hesaplaması
v4 değerleriyle birebir tutarlı

İki yaklaşım:
1. OAT (One-at-a-Time): her parametre ±%20 değişim, NPV etkisi
2. Spearman rank correlation: MC verilerinden istatistiksel sensitivity
"""
import numpy as np
import json
from scipy import stats

np.random.seed(42)

# ============================================================
# 1. BASELINE PARAMETRELER (v4 — Bileşen 4 ile birebir)
# ============================================================
N_YIL = 10
ISKONTO = 0.15

baseline = {
    'isgucu':           118_078,
    'throughput_gelir': 374_400,
    'hasar':             38_500,
    'kaza':              25_000,
    'ek_ops':            24_881,
    'enerji':             5_000,
    'bakim':            -10_000,
    'fw_yatirim':     2_000_000,
    'mn_yatirim':       210_872,
    'enflasyon':           0.25,
}

def npv_hesap(params, iskonto=ISKONTO):
    """Tek bir parametre seti için NPV hesabı."""
    yillik_yil1 = (params['isgucu'] + params['throughput_gelir'] + params['hasar']
                   + params['kaza'] + params['ek_ops'] + params['enerji'] + params['bakim'])
    ek_yatirim = params['fw_yatirim'] - params['mn_yatirim']
    
    npv = 0
    for yil in range(1, N_YIL + 1):
        yillik = yillik_yil1 * (1 + params['enflasyon'] * 0.7) ** (yil - 1)
        discounted = yillik / ((1 + iskonto) ** yil)
        npv += discounted
    npv -= ek_yatirim
    return npv

baseline_npv = npv_hesap(baseline)
print(f"Baseline NPV: {baseline_npv:,.0f} USD")

# ============================================================
# 2. OAT ANALİZİ (±%20)
# ============================================================
print("\n=== OAT Sensitivity (±%20) ===")

sensitivity_params = [
    ('throughput_gelir', 'Throughput Gelir Avantajı'),
    ('fw_yatirim',       'FW Yatırım Maliyeti'),
    ('isgucu',           'İşgücü Tasarrufu'),
    ('enflasyon',        'Yıllık Enflasyon'),
    ('hasar',            'Hasar Tasarrufu'),
    ('kaza',             'Kaza Tasarrufu'),
    ('ek_ops',           'Ek Operasyonel Tasarruf'),
    ('bakim',            'Bakım Maliyeti Farkı'),
    ('enerji',           'Enerji Tasarrufu'),
    ('mn_yatirim',       'Manuel Yatırım'),
]

oat_results = []
for key, label in sensitivity_params:
    p_low = baseline.copy()
    p_low[key] = baseline[key] * 0.80
    npv_low = npv_hesap(p_low)
    
    p_high = baseline.copy()
    p_high[key] = baseline[key] * 1.20
    npv_high = npv_hesap(p_high)
    
    delta_low = npv_low - baseline_npv
    delta_high = npv_high - baseline_npv
    abs_swing = abs(delta_high - delta_low)
    
    oat_results.append({
        'param': key,
        'label': label,
        'baseline': baseline[key],
        'low_value': baseline[key] * 0.80,
        'high_value': baseline[key] * 1.20,
        'npv_low': npv_low,
        'npv_high': npv_high,
        'delta_low': delta_low,
        'delta_high': delta_high,
        'abs_swing': abs_swing,
    })

# İskonto oranı için ayrı hesap (yüzde puan değişimi: %12 - %18)
iskonto_low = npv_hesap(baseline, iskonto=0.12)   # daha düşük iskonto = daha yüksek NPV
iskonto_high = npv_hesap(baseline, iskonto=0.18)  # daha yüksek iskonto = daha düşük NPV
oat_results.append({
    'param': 'iskonto',
    'label': 'İskonto Oranı (%15±3)',
    'baseline': 0.15,
    'low_value': 0.12,
    'high_value': 0.18,
    'npv_low': iskonto_low,
    'npv_high': iskonto_high,
    'delta_low': iskonto_low - baseline_npv,   # %12 → NPV artar (pozitif)
    'delta_high': iskonto_high - baseline_npv,  # %18 → NPV azalır (negatif)
    'abs_swing': abs((iskonto_low - baseline_npv) - (iskonto_high - baseline_npv)),
})

oat_results.sort(key=lambda x: x['abs_swing'], reverse=True)

print(f"\n{'Parametre':<30} {'-değişim':>15} {'+değişim':>15} {'Toplam swing':>15}")
print("-" * 80)
for r in oat_results:
    print(f"{r['label']:<30} {r['delta_low']:>15,.0f} {r['delta_high']:>15,.0f} {r['abs_swing']:>15,.0f}")

# ============================================================
# 3. SPEARMAN KORELASYON
# ============================================================
print("\n=== Spearman Rank Correlation ===")

with open('mc_sonuclar.json') as f:
    mc = json.load(f)

npv_arr = np.array(mc['npv'])
inputs = mc['inputs']

mc_param_map = {
    'isgucu': 'İşgücü Tasarrufu',
    'throughput_gelir': 'Throughput Gelir Avantajı',
    'hasar': 'Hasar Tasarrufu',
    'kaza': 'Kaza Tasarrufu',
    'ek_ops': 'Ek Operasyonel Tasarruf',
    'enerji': 'Enerji Tasarrufu',
    'bakim': 'Bakım Maliyeti Farkı',
    'fw_yatirim': 'FW Yatırım Maliyeti',
    'enflasyon': 'Yıllık Enflasyon',
}

correlation_results = []
for key, label in mc_param_map.items():
    arr = np.array(inputs[key])
    rho, pval = stats.spearmanr(arr, npv_arr)
    correlation_results.append({
        'param': key,
        'label': label,
        'rho': float(rho),
        'pval': float(pval),
        'abs_rho': abs(float(rho)),
    })

correlation_results.sort(key=lambda x: x['abs_rho'], reverse=True)

print(f"\n{'Parametre':<30} {'Spearman ρ':>12} {'|ρ|':>10}")
print("-" * 55)
for r in correlation_results:
    print(f"{r['label']:<30} {r['rho']:>+12.4f} {r['abs_rho']:>10.4f}")

# ============================================================
# 4. KAYDET (mevcut dosyayı tamamen üzerine yaz)
# ============================================================
import os
if os.path.exists('tornado_sonuclar.json'):
    os.remove('tornado_sonuclar.json')

sonuclar = {
    'baseline_npv': float(baseline_npv),
    'baseline': {k: float(v) for k, v in baseline.items()},
    'oat': oat_results,
    'correlation': correlation_results,
    'parametreler': {
        'n_yil': N_YIL,
        'iskonto': ISKONTO,
        'oat_pct': 0.20,
    }
}

def to_serializable(obj):
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, list):
        return [to_serializable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    return obj

with open('tornado_sonuclar.json', 'w', encoding='utf-8') as f:
    json.dump(to_serializable(sonuclar), f, indent=2, ensure_ascii=False)

print(f"\n✓ tornado_sonuclar.json kaydedildi")
print(f"  En büyük 3 etken: {[r['label'] for r in oat_results[:3]]}")
