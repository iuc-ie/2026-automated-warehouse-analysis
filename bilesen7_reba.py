# -*- coding: utf-8 -*-
"""
BİLEŞEN 7: REBA Ergonomik Risk Skorlaması
Hignett & McAtamney (2000) orijinal metodolojisine BİREBİR uygun

REFERANSLAR (sağlam akademik zemin):
- Hignett, S. & McAtamney, L. (2000). Rapid Entire Body Assessment (REBA).
  Applied Ergonomics, 31(2), 201-205.
- ISO 11228-3:2007 - Ergonomics - Manual handling
- Madani & Dababneh (2016): REBA - A Worker Friendly Tool
- Kee & Karwowski (2007): A comparison of three observational techniques

ÖNEMLİ LİMİTASYON:
- Gerçek saha gözlemi yapılmamış
- Senaryolar literatür+temsili durumlardan türetilmiş
- Tek puanlayıcı (intra-rater) — inter-rater reliability test edilmedi

Spyder/Anaconda'da çalıştırmak için: F5 (Run)
"""
import json

# ============================================================
# 1. REBA SKORLAMA TABLOLARI (Hignett & McAtamney 2000)
# ============================================================

def govde_skoru(aci_derece, donme_yan_egilme=False):
    """0-5° = 1, 0-20° = 2, 20-60° = 3, >60° = 4. +1 dönme/yan eğilme."""
    if aci_derece < 5: skor = 1
    elif aci_derece < 20: skor = 2
    elif aci_derece < 60: skor = 3
    else: skor = 4
    return skor + (1 if donme_yan_egilme else 0)

def boyun_skoru(aci_derece, donme_yan_egilme=False):
    """0-20° = 1, >20° veya ext. = 2. +1 dönme/yan eğilme."""
    skor = 1 if 0 <= aci_derece <= 20 else 2
    return skor + (1 if donme_yan_egilme else 0)

def bacak_skoru(iki_ayak=True, diz_30_60=False, diz_uzeri_60=False):
    """İki ayak destekli = 1, dengesiz = 2. +1 (30-60°) / +2 (>60°)."""
    skor = 1 if iki_ayak else 2
    if diz_uzeri_60: skor += 2
    elif diz_30_60: skor += 1
    return skor

# Tablo A: Gövde × Boyun × Bacak (Hignett & McAtamney 2000, s. 203)
TABLO_A = {
    (1,1,1): 1, (1,1,2): 2, (1,1,3): 3, (1,1,4): 4,
    (1,2,1): 1, (1,2,2): 2, (1,2,3): 3, (1,2,4): 4,
    (1,3,1): 3, (1,3,2): 3, (1,3,3): 5, (1,3,4): 6,
    (2,1,1): 2, (2,1,2): 3, (2,1,3): 4, (2,1,4): 5,
    (2,2,1): 3, (2,2,2): 4, (2,2,3): 5, (2,2,4): 6,
    (2,3,1): 4, (2,3,2): 5, (2,3,3): 6, (2,3,4): 7,
    (3,1,1): 2, (3,1,2): 4, (3,1,3): 5, (3,1,4): 6,
    (3,2,1): 4, (3,2,2): 5, (3,2,3): 6, (3,2,4): 7,
    (3,3,1): 5, (3,3,2): 6, (3,3,3): 7, (3,3,4): 8,
    (4,1,1): 3, (4,1,2): 5, (4,1,3): 6, (4,1,4): 7,
    (4,2,1): 5, (4,2,2): 6, (4,2,3): 7, (4,2,4): 8,
    (4,3,1): 6, (4,3,2): 7, (4,3,3): 8, (4,3,4): 9,
    (5,1,1): 4, (5,1,2): 6, (5,1,3): 7, (5,1,4): 8,
    (5,2,1): 6, (5,2,2): 7, (5,2,3): 8, (5,2,4): 9,
    (5,3,1): 7, (5,3,2): 8, (5,3,3): 9, (5,3,4): 9,
}

def tablo_a(g, b, ba):
    return TABLO_A[(min(max(g,1),5), min(max(b,1),3), min(max(ba,1),4))]

def yuk_skoru(yuk_kg, ani=False):
    """<5 kg = 0, 5-10 = 1, >10 = 2. +1 ani/sarsıntılı."""
    if yuk_kg < 5: skor = 0
    elif yuk_kg <= 10: skor = 1
    else: skor = 2
    return skor + (1 if ani else 0)

def ust_kol_skoru(aci, omuz_kalkik=False, kol_destek_yok=True):
    """-20 +20° = 1, 20-45° = 2, 45-90° = 3, >90° = 4. +1 omuz / -1 destek."""
    if -20 <= aci < 20: skor = 1
    elif 20 <= aci < 45: skor = 2
    elif 45 <= aci < 90: skor = 3
    else: skor = 4
    if omuz_kalkik: skor += 1
    if not kol_destek_yok: skor -= 1
    return max(skor, 1)

def onkol_skoru(aci):
    """60-100° = 1 (optimal), aksi = 2."""
    return 1 if 60 <= aci <= 100 else 2

def bilek_skoru(aci, donme=False):
    """-15 +15° = 1, aksi = 2. +1 dönme."""
    skor = 1 if -15 <= aci <= 15 else 2
    return skor + (1 if donme else 0)

# Tablo B: Üst kol × Önkol × Bilek (Hignett & McAtamney 2000)
TABLO_B = {
    (1,1,1):1,(1,1,2):2,(1,1,3):2,(1,2,1):1,(1,2,2):2,(1,2,3):3,
    (2,1,1):1,(2,1,2):2,(2,1,3):3,(2,2,1):2,(2,2,2):3,(2,2,3):4,
    (3,1,1):3,(3,1,2):4,(3,1,3):5,(3,2,1):4,(3,2,2):5,(3,2,3):5,
    (4,1,1):4,(4,1,2):5,(4,1,3):5,(4,2,1):5,(4,2,2):6,(4,2,3):7,
    (5,1,1):6,(5,1,2):7,(5,1,3):8,(5,2,1):7,(5,2,2):8,(5,2,3):8,
    (6,1,1):7,(6,1,2):8,(6,1,3):8,(6,2,1):8,(6,2,2):9,(6,2,3):9,
}

def tablo_b(uk, ok, bi):
    return TABLO_B[(min(max(uk,1),6), min(max(ok,1),2), min(max(bi,1),3))]

def kavrama_skoru(durum):
    """iyi=0, orta=1, kotu=2, kabul_edilemez=3"""
    return {'iyi':0, 'orta':1, 'kotu':2, 'kabul_edilemez':3}[durum]

# Tablo C (Hignett & McAtamney 2000)
TABLO_C = [
    [1,1,1,2,3,3,4,5,6,7,7,7],
    [1,2,2,3,4,4,5,6,6,7,7,8],
    [2,3,3,3,4,5,6,7,7,8,8,8],
    [3,4,4,4,5,6,7,8,8,9,9,9],
    [4,4,4,5,6,7,8,8,9,9,9,9],
    [6,6,6,7,8,8,9,9,10,10,10,10],
    [7,7,7,8,9,9,9,10,10,11,11,11],
    [8,8,8,9,10,10,10,10,10,11,11,11],
    [9,9,9,10,10,10,11,11,11,12,12,12],
    [10,10,10,11,11,11,11,12,12,12,12,12],
    [11,11,11,11,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12],
]

def tablo_c(skor_a, skor_b):
    return TABLO_C[min(max(skor_a,1),12)-1][min(max(skor_b,1),12)-1]

def aktivite_skoru(statik=False, tekrarli=False, ani=False):
    """+1 her bir koşul: statik >1dk, tekrar >4/dk, ani büyük."""
    return int(statik) + int(tekrarli) + int(ani)

def reba_hesapla(senaryo):
    """Bir senaryo dict'inden tüm REBA hesabını yap."""
    g = govde_skoru(senaryo['govde_aci'], senaryo.get('govde_donme', False))
    b = boyun_skoru(senaryo['boyun_aci'], senaryo.get('boyun_donme', False))
    ba = bacak_skoru(senaryo.get('iki_ayak', True),
                     senaryo.get('diz_30_60', False),
                     senaryo.get('diz_uzeri_60', False))
    a = tablo_a(g, b, ba)
    yuk = yuk_skoru(senaryo['yuk_kg'], senaryo.get('ani_yukleme', False))
    skor_a = a + yuk
    
    uk = ust_kol_skoru(senaryo['ust_kol_aci'],
                       senaryo.get('omuz_kalkik', False),
                       senaryo.get('kol_destek_yok', True))
    ok = onkol_skoru(senaryo['onkol_aci'])
    bi = bilek_skoru(senaryo['bilek_aci'], senaryo.get('bilek_donme', False))
    b_tab = tablo_b(uk, ok, bi)
    kav = kavrama_skoru(senaryo['kavrama'])
    skor_b = b_tab + kav
    
    skor_c = tablo_c(skor_a, skor_b)
    akt = aktivite_skoru(senaryo.get('statik', False),
                         senaryo.get('tekrarli', False),
                         senaryo.get('ani', False))
    final = min(skor_c + akt, 15)
    
    if final == 1: risk = 'İhmal edilebilir'
    elif final <= 3: risk = 'Düşük'
    elif final <= 7: risk = 'Orta'
    elif final <= 10: risk = 'Yüksek'
    else: risk = 'Çok yüksek'
    
    return {'skor_a': skor_a, 'skor_b': skor_b, 'skor_c': skor_c,
            'aktivite': akt, 'reba': final, 'risk': risk}

# ============================================================
# 2. SENARYO TANIMLARI
# ============================================================
SENARYOLAR = {
    'M1': {  # Manuel - Palet Düzeltme/İstifleme
        'govde_aci': 45, 'govde_donme': True,
        'boyun_aci': 25, 'boyun_donme': True,
        'iki_ayak': True, 'diz_30_60': True,
        'yuk_kg': 15, 'ani_yukleme': False,
        'ust_kol_aci': 60, 'omuz_kalkik': False,
        'onkol_aci': 90,
        'bilek_aci': 20, 'bilek_donme': True,
        'kavrama': 'orta',
        'statik': False, 'tekrarli': True, 'ani': False,
    },
    'M2': {  # Manuel - Sıkışmış Palet Kurtarma
        'govde_aci': 70, 'govde_donme': True,
        'boyun_aci': 30, 'boyun_donme': True,
        'iki_ayak': True, 'diz_uzeri_60': True,
        'yuk_kg': 25, 'ani_yukleme': True,
        'ust_kol_aci': 100, 'omuz_kalkik': True,
        'onkol_aci': 50,
        'bilek_aci': 25, 'bilek_donme': True,
        'kavrama': 'kotu',
        'statik': True, 'tekrarli': False, 'ani': True,
    },
    'M3': {  # Manuel - Forklift Sürme (Statik Oturma)
        'govde_aci': 15, 'govde_donme': True,
        'boyun_aci': 30, 'boyun_donme': True,
        'iki_ayak': True, 'diz_30_60': True,
        'yuk_kg': 2, 'ani_yukleme': False,
        'ust_kol_aci': 30, 'omuz_kalkik': False,
        'onkol_aci': 80,
        'bilek_aci': 10, 'bilek_donme': False,
        'kavrama': 'iyi',
        'statik': True, 'tekrarli': True, 'ani': False,
    },
    'F1': {  # Four-Way - WMS Konsol İzleme
        'govde_aci': 5, 'govde_donme': False,
        'boyun_aci': 15, 'boyun_donme': False,
        'iki_ayak': True, 'diz_30_60': True,
        'yuk_kg': 0, 'ani_yukleme': False,
        'ust_kol_aci': 25, 'omuz_kalkik': False, 'kol_destek_yok': False,
        'onkol_aci': 90,
        'bilek_aci': 10, 'bilek_donme': False,
        'kavrama': 'iyi',
        'statik': True, 'tekrarli': False, 'ani': False,
    },
    'F2': {  # Four-Way - Sistem Müdahalesi
        'govde_aci': 10, 'govde_donme': False,
        'boyun_aci': 15, 'boyun_donme': False,
        'iki_ayak': True, 'diz_30_60': False,
        'yuk_kg': 3, 'ani_yukleme': False,
        'ust_kol_aci': 35, 'omuz_kalkik': False,
        'onkol_aci': 70,
        'bilek_aci': 10, 'bilek_donme': False,
        'kavrama': 'iyi',
        'statik': False, 'tekrarli': False, 'ani': False,
    },
    'F3': {  # Four-Way - Periyodik Bakım Kontrolü
        'govde_aci': 35, 'govde_donme': False,
        'boyun_aci': 25, 'boyun_donme': False,
        'iki_ayak': True, 'diz_30_60': True,
        'yuk_kg': 5, 'ani_yukleme': False,
        'ust_kol_aci': 50, 'omuz_kalkik': False,
        'onkol_aci': 75,
        'bilek_aci': 15, 'bilek_donme': False,
        'kavrama': 'iyi',
        'statik': False, 'tekrarli': False, 'ani': False,
    },
}

# ============================================================
# 3. HESAPLAMA VE ÖZET
# ============================================================
print("="*70)
print("BİLEŞEN 7 — REBA Ergonomik Risk Skorlaması")
print("Hignett & McAtamney (2000) orijinal metodolojisi")
print("="*70)

sonuclar = {}
for kod, sen in SENARYOLAR.items():
    sonuclar[kod] = reba_hesapla(sen)

print(f"\n{'Senaryo':<8} {'Skor A':>7} {'Skor B':>7} {'Skor C':>7} {'Akt':>4} {'REBA':>5} {'Risk':<15}")
print("-" * 70)
for kod, r in sonuclar.items():
    print(f"{kod:<8} {r['skor_a']:>7} {r['skor_b']:>7} {r['skor_c']:>7} {r['aktivite']:>4} {r['reba']:>5} {r['risk']:<15}")

manuel_ort = sum(sonuclar[k]['reba'] for k in ['M1','M2','M3']) / 3
fw_ort = sum(sonuclar[k]['reba'] for k in ['F1','F2','F3']) / 3
print(f"\nManuel ortalama REBA:   {manuel_ort:.2f}")
print(f"Four-Way ortalama REBA: {fw_ort:.2f}")
print(f"Risk azalması:          {(manuel_ort-fw_ort):.2f} puan ({(manuel_ort-fw_ort)/manuel_ort*100:.1f}%)")

# Görev süresi ağırlıklı ortalama
agirlikli_m = (sonuclar['M1']['reba']*0.10 +
               sonuclar['M2']['reba']*0.05 +
               sonuclar['M3']['reba']*0.85)
agirlikli_f = (sonuclar['F1']['reba']*0.60 +
               sonuclar['F2']['reba']*0.15 +
               sonuclar['F3']['reba']*0.25)
print(f"\nGörev süresi ağırlıklı:")
print(f"  Manuel: {agirlikli_m:.2f}  |  Four-Way: {agirlikli_f:.2f}")

print(f"\n✓ REBA analizi tamamlandı")
print(f"NOT: Bu analiz literatür+temsili senaryolara dayanır.")
print(f"     Tezde 'gerçek saha gözlemi yapılmamıştır' limitasyonu vurgulanmalıdır.")
