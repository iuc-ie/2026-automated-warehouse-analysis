# -*- coding: utf-8 -*-
"""
BİLEŞEN 2: Senaryo Analizi (Düşük / Orta / Yüksek Talep)
Bottleneck Analysis (Goldratt 1984) + Capacity Utilization
v4 Excel verileriyle uyumlu

Spyder/Anaconda'da çalıştırmak için: F5 (Run)
Çıktılar: 4 PNG grafik + senaryo_sonuclar.json
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import FancyBboxPatch
import json

# ============================================================
# 1. SİSTEM PARAMETRELERİ (v4)
# ============================================================
# Manuel forklift sistemi
MN_FORKLIFT = 3                  # baz senaryo
MN_HIZ_YUKLU = 8 / 3.6           # 8 km/saat → 2.22 m/s
MN_HIZ_BOS = 12 / 3.6            # 12 km/saat → 3.33 m/s
MN_KALDIRMA = 15                 # sn
MN_INDIRME = 12                  # sn
MN_EK = 10                       # sn (manevra/arama)
MN_ORT_MESAFE = 40.9             # m (köşegen/2)
MN_VERIMLILIK = 0.85             # mola, yorgunluk

# Four-Way sistemi
FW_SHUTTLE = 6
FW_ASANSOR = 4
FW_HIZ_YUKLU = 1.25              # m/s
FW_HIZ_BOS = 2.0                 # m/s
FW_KALDIRMA = 1.5                # sn
FW_ORT_MESAFE = 18.25            # m (raf genişliği/2)
FW_KAT_DEGISIM_ORAN = 0.70       # %70 işlemde kat değişimi
FW_ASANSOR_CEVRIM = 45           # sn
FW_VERIMLILIK = 0.95             # otomatik sistem yüksek verim

# Operasyonel
GUN_SAAT_FW = 24                 # 7/24
GUN_SAAT_MN = 22                 # 3 vardiya - mola
YIL_GUN = 312
PALET_GELIR = 5                  # USD/palet

# ============================================================
# 2. ÇEVRİM SÜRELERİ
# ============================================================
# Manuel
mn_cevrim_sn = (MN_ORT_MESAFE / MN_HIZ_YUKLU + MN_KALDIRMA + 
                MN_ORT_MESAFE / MN_HIZ_BOS + MN_INDIRME + MN_EK)
mn_cevrim_eff_sn = mn_cevrim_sn / MN_VERIMLILIK
mn_kapasite_3 = (3600 / mn_cevrim_eff_sn) * 3
mn_kapasite_5 = (3600 / mn_cevrim_eff_sn) * 5

# Four-Way
fw_shuttle_cevrim = (FW_ORT_MESAFE / FW_HIZ_YUKLU + FW_KALDIRMA*2 + FW_ORT_MESAFE / FW_HIZ_BOS)
fw_asansor_cevrim_eff = FW_ASANSOR_CEVRIM * FW_KAT_DEGISIM_ORAN
fw_total_cevrim = fw_shuttle_cevrim + fw_asansor_cevrim_eff

fw_shuttle_capacity = 6 * 3600 / fw_shuttle_cevrim * FW_VERIMLILIK
fw_elevator_capacity = 4 * 3600 / FW_ASANSOR_CEVRIM * FW_VERIMLILIK
fw_elevator_practical_cap = fw_elevator_capacity / FW_KAT_DEGISIM_ORAN
fw_kapasite = min(fw_shuttle_capacity, fw_elevator_practical_cap)
fw_bottleneck = "Shuttle" if fw_shuttle_capacity < fw_elevator_practical_cap else "Asansör"

print(f"Manuel forklift çevrim: {mn_cevrim_eff_sn:.1f} sn")
print(f"Manuel kapasite (3 forklift): {mn_kapasite_3:.0f} p/h")
print(f"Manuel kapasite (5 forklift): {mn_kapasite_5:.0f} p/h")
print(f"\nFW shuttle çevrim: {fw_shuttle_cevrim:.1f} sn")
print(f"FW shuttle kapasitesi: {fw_shuttle_capacity:.0f} p/h")
print(f"FW asansör efektif kapasitesi: {fw_elevator_practical_cap:.0f} p/h")
print(f"FW SİSTEM KAPASİTESİ: {fw_kapasite:.0f} p/h ({fw_bottleneck})")

# ============================================================
# 3. SENARYOLAR
# ============================================================
senaryolar = {
    'Düşük Talep':  {'demand': 60,  'aciklama': 'Düşük sezon (Raftürk hedefinin %50)'},
    'Orta Talep':   {'demand': 120, 'aciklama': 'Baseline (Raftürk hedefi)'},
    'Yüksek Talep': {'demand': 180, 'aciklama': 'Pik dönem (Raftürk hedefinin %150)'},
}

sonuclar = {}
print(f"\n{'Senaryo':<15} {'Talep':>8} {'Manuel(3)':>11} {'Manuel(5)':>11} {'FW':>9}")
print("-"*60)
for s_name, s_data in senaryolar.items():
    demand = s_data['demand']
    
    mn3_cap = mn_kapasite_3
    mn5_cap = mn_kapasite_5
    
    sonuclar[s_name] = {
        'demand': demand,
        'aciklama': s_data['aciklama'],
        'mn_3': {
            'cap': mn3_cap,
            'achieved': min(mn3_cap, demand),
            'karsilama_pct': min(mn3_cap, demand) / demand * 100,
            'yillik_supply': min(mn3_cap, demand) * GUN_SAAT_MN * YIL_GUN,
            'yillik_demand': demand * GUN_SAAT_MN * YIL_GUN,
            'kacirilan': max(0, demand * GUN_SAAT_MN * YIL_GUN - min(mn3_cap, demand) * GUN_SAAT_MN * YIL_GUN),
        },
        'mn_5': {
            'cap': mn5_cap,
            'achieved': min(mn5_cap, demand),
            'karsilama_pct': min(mn5_cap, demand) / demand * 100,
            'yillik_supply': min(mn5_cap, demand) * GUN_SAAT_MN * YIL_GUN,
            'yillik_demand': demand * GUN_SAAT_MN * YIL_GUN,
            'kacirilan': max(0, demand * GUN_SAAT_MN * YIL_GUN - min(mn5_cap, demand) * GUN_SAAT_MN * YIL_GUN),
        },
        'fw': {
            'cap': fw_kapasite,
            'achieved': min(fw_kapasite, demand),
            'karsilama_pct': min(fw_kapasite, demand) / demand * 100,
            'yillik_supply': min(fw_kapasite, demand) * GUN_SAAT_FW * YIL_GUN,
            'yillik_demand': demand * GUN_SAAT_FW * YIL_GUN,
            'kacirilan': max(0, demand * GUN_SAAT_FW * YIL_GUN - min(fw_kapasite, demand) * GUN_SAAT_FW * YIL_GUN),
        },
    }
    
    print(f"{s_name:<15} {demand:>5} p/h {min(mn3_cap, demand):>10.0f} {min(mn5_cap, demand):>10.0f} {min(fw_kapasite, demand):>8.0f}")

sonuclar['_meta'] = {
    'mn_cevrim_sn': mn_cevrim_eff_sn,
    'mn_kapasite_3': mn_kapasite_3,
    'mn_kapasite_5': mn_kapasite_5,
    'fw_shuttle_cevrim': fw_shuttle_cevrim,
    'fw_total_cevrim': fw_total_cevrim,
    'fw_kapasite': fw_kapasite,
    'fw_bottleneck': fw_bottleneck,
    'fw_shuttle_capacity': fw_shuttle_capacity,
    'fw_elevator_capacity': fw_elevator_capacity,
    'fw_elevator_practical': fw_elevator_practical_cap,
    'palet_gelir': PALET_GELIR,
}

with open('senaryo_sonuclar.json', 'w', encoding='utf-8') as f:
    json.dump(sonuclar, f, indent=2, ensure_ascii=False)

# ============================================================
# 4. GRAFİKLER (özet)
# ============================================================
C_FW = '#1D9E75'
C_MN3 = '#E24B4A'
C_MN5 = '#F4A582'
C_DEMAND = '#525252'

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})

# --- Şekil 2.1 ---
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle('Şekil 2.1 — Senaryo Bazlı Saatlik Kapasite Karşılaştırması',
             fontsize=13, fontweight='bold', y=0.99)

sn_list = list(senaryolar.keys())
talepler = [sonuclar[sn]['demand'] for sn in sn_list]
mn3_caps = [sonuclar[sn]['mn_3']['cap'] for sn in sn_list]
mn5_caps = [sonuclar[sn]['mn_5']['cap'] for sn in sn_list]
fw_caps = [sonuclar[sn]['fw']['cap'] for sn in sn_list]

ax = axes[0]
x = np.arange(len(sn_list))
w = 0.20
ax.bar(x - 1.5*w, talepler, w, label='Talep', color=C_DEMAND, alpha=0.75)
ax.bar(x - 0.5*w, mn3_caps, w, label='Manuel (3)', color=C_MN3)
ax.bar(x + 0.5*w, mn5_caps, w, label='Manuel (5)', color=C_MN5)
ax.bar(x + 1.5*w, fw_caps, w, label='Four-Way', color=C_FW)
ax.set_xticks(x); ax.set_xticklabels(sn_list)
ax.set_ylabel('palet / saat')
ax.set_title('Sistem Kapasitesi vs Talep')
ax.legend(loc='upper left', fontsize=9)
ax.grid(axis='y', alpha=0.3)

ax = axes[1]
karsilama = {
    'Manuel (3)': [sonuclar[sn]['mn_3']['karsilama_pct'] for sn in sn_list],
    'Manuel (5)': [sonuclar[sn]['mn_5']['karsilama_pct'] for sn in sn_list],
    'Four-Way': [sonuclar[sn]['fw']['karsilama_pct'] for sn in sn_list],
}
for i, (label, vals) in enumerate(karsilama.items()):
    ax.bar(x + (i-1)*0.27, vals, 0.25, label=label,
           color=[C_MN3, C_MN5, C_FW][i])
ax.axhline(y=100, color='#1D9E75', linestyle='--', alpha=0.6)
ax.set_xticks(x); ax.set_xticklabels(sn_list)
ax.set_ylabel('Karşılama Oranı (%)')
ax.set_title('Talep Karşılama Oranı')
ax.legend(loc='lower left', fontsize=9)
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(0, 118)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('sekil_2_1_senaryo_kapasite.png', dpi=200, bbox_inches='tight')
plt.show()

print("\n✓ Bileşen 2 hesapları ve grafikleri tamamlandı")
print("  Tam grafik seti için: bilesen2_full.py kullan")
