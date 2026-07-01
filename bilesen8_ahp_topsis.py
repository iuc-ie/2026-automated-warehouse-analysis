# -*- coding: utf-8 -*-
"""
BİLEŞEN 8: AHP + TOPSIS Çok Kriterli Karar Modeli
Manuel Forkliftli Depo vs Four-Way Otomatik Depo
Raftürk Vaka Çalışması

Metodoloji:
  AHP: Saaty (1980)  |  TOPSIS: Hwang & Yoon (1981)
  Finansal kriter MALİYET YÖNLÜ (10-yıl toplam USD, küçük=iyi)
  → Manuel maliyet avantajı vs Four-Way operasyonel üstünlük = gerçek trade-off

Spyder IDE: F5 ile çalıştır
"""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings('ignore')

KRITER = ['Finansal', 'Operasyonel', 'İSG', 'Alan', 'İşgücü']
ALT    = ['Manuel', 'Four-Way']
FAYDA  = [False, True, True, True, True]
nc = len(KRITER)

print("╔═══════════════════════════════════════════════════════════╗")
print("║  BİLEŞEN 8: AHP + TOPSIS Çok Kriterli Karar Modeli      ║")
print("║  Raftürk — Manuel vs Four-Way Depo                       ║")
print("╚═══════════════════════════════════════════════════════════╝")

# ── AHP ────────────────────────────────────────────────────────────────────
A = np.array([[1,1/2,1/3,1/4,1/3],[2,1,1/2,1/3,1/2],[3,2,1,1/2,1/2],
              [4,3,2,1,1],[3,2,2,1,1]], dtype=float).T
w = (A / A.sum(0)).mean(1)
Aw = A @ w; lmax = (Aw/w).mean(); CI=(lmax-nc)/(nc-1); RI=1.12; CR=CI/RI

print(f"\n  AHP Ağırlıkları:")
for k,v in zip(KRITER,w): print(f"    {k:<14} w={v:.4f}")
print(f"  CR = {CR:.4f} {'✓ Tutarlı' if CR<0.10 else '✗ Tutarsız'}")

# ── KARAR MATRİSİ ──────────────────────────────────────────────────────────
X = np.array([[1711, 60, 4, 55, 3],     # Manuel
              [4200, 120, 9, 85, 9]],    # Four-Way
             dtype=float)

print(f"\n  Karar Matrisi:")
print(f"  {'Kriter':<14} {'Manuel':>8} {'Four-Way':>10} {'Tür':>10}")
birim=['k$','p/s','/10','%','/10']; tur=['Maliyet↓','Fayda↑','Fayda↑','Fayda↑','Fayda↑']
for i,(k,b,t) in enumerate(zip(KRITER,birim,tur)):
    print(f"  {k:<14} {X[0,i]:>6.0f} {b:<4} {X[1,i]:>6.0f} {b:<4} {t:>10}")

# ── TOPSIS ──────────────────────────────────────────────────────────────────
def topsis(X, w, fayda):
    R = X / np.sqrt((X**2).sum(0))
    V = R * w
    Ap = np.array([V[:,j].min() if not fayda[j] else V[:,j].max() for j in range(X.shape[1])])
    An = np.array([V[:,j].max() if not fayda[j] else V[:,j].min() for j in range(X.shape[1])])
    Dp = np.sqrt(((V-Ap)**2).sum(1))
    Dn = np.sqrt(((V-An)**2).sum(1))
    Ci = Dn/(Dp+Dn)
    return V, Ap, An, Dp, Dn, Ci

V, Ap, An, Dp, Dn, Ci = topsis(X, w, FAYDA)

print(f"\n  TOPSIS Sonuçları:")
print(f"  {'Alt.':<12} {'D⁺':>8} {'D⁻':>8} {'Ci':>8} {'Sıra':>6}")
sira = np.argsort(Ci)[::-1]
for i,a in enumerate(ALT):
    s = np.where(sira==i)[0][0]+1
    print(f"  {a:<12} {Dp[i]:.4f}   {Dn[i]:.4f}   {Ci[i]:.4f}   #{s}")
print(f"\n  V matrisi:")
print(f"  {'':>12}"+"".join(f"{k:>11}" for k in KRITER))
for i,a in enumerate(ALT):
    print(f"  {a:<12}"+"".join(f"{V[i,j]:>11.4f}" for j in range(nc)))
print(f"  {'A⁺':<12}"+"".join(f"{Ap[j]:>11.4f}" for j in range(nc)))
print(f"  {'A⁻':<12}"+"".join(f"{An[j]:>11.4f}" for j in range(nc)))

kaz = ALT[np.argmax(Ci)]
print(f"\n  ► Kazanan: {kaz} (Ci={max(Ci):.4f})")

# ── DUYARLILIK: Finansal ağırlık sweep ──────────────────────────────────────
fin_range = np.linspace(0.10, 0.55, 50)
ci_mn_arr, ci_fw_arr = [], []
for fw in fin_range:
    kalan = 1.0 - fw
    oranlar = w[1:] / w[1:].sum()
    ww = np.array([fw] + list(kalan * oranlar))
    _,_,_,_,_,ci = topsis(X, ww, FAYDA)
    ci_mn_arr.append(ci[0]); ci_fw_arr.append(ci[1])
ci_mn_arr = np.array(ci_mn_arr); ci_fw_arr = np.array(ci_fw_arr)
cross_idx = np.argmin(np.abs(ci_mn_arr - ci_fw_arr))
cross_w = fin_range[cross_idx]
print(f"\n  Duyarlılık: Crossover noktası = w_fin ≈ {cross_w:.3f}")
print(f"  w_fin < {cross_w:.2f} → Four-Way kazanır | w_fin > {cross_w:.2f} → Manuel kazanır")

# ── GRAFİKLER (5 panel: 2+2+1) ─────────────────────────────────────────────
C_FW='#00D4A8'; C_MN='#FF6B6B'; C_GOLD='#FFD700'
C_TEXT='#E8E8E8'; C_GRID='#2A2A3E'; C_BG='#0D1117'; C_PANEL='#161B22'

fig = plt.figure(figsize=(18, 20))
fig.patch.set_facecolor(C_BG)
fig.suptitle('Bileşen 8: AHP + TOPSIS Çok Kriterli Karar Analizi\n'
             'Manuel Forkliftli Depo vs Four-Way Otomatik Depo — Raftürk',
             fontsize=15, fontweight='bold', color=C_TEXT, y=0.98)

# ─ Panel 1: AHP Ağırlıkları ───────────────────────────────────────────────
ax1 = fig.add_subplot(3, 2, 1); ax1.set_facecolor(C_PANEL)
renk = ['#4FC3F7','#81C784','#FFB74D','#CE93D8','#F06292']
b1 = ax1.barh(KRITER[::-1], w[::-1], color=renk[::-1], height=0.55, edgecolor='none')
for bar,val in zip(b1,w[::-1]):
    ax1.text(val+0.008, bar.get_y()+bar.get_height()/2, f'w={val:.3f}',
             va='center', color=C_TEXT, fontsize=11, fontweight='bold')
ax1.axvline(0.2, color='#888', ls='--', alpha=0.5, label='Eşit (0.200)')
ax1.set_xlabel('Ağırlık', color=C_TEXT); ax1.set_xlim(0, max(w)*1.35)
ax1.set_title(f'AHP Kriter Ağırlıkları\nCR={CR:.4f} < 0.10 ✓ Tutarlı (Saaty, 1980)',
              color=C_TEXT, fontsize=11, fontweight='bold', pad=12)
ax1.tick_params(colors=C_TEXT)
for s in ax1.spines.values(): s.set_edgecolor(C_GRID)
ax1.legend(fontsize=8, facecolor=C_PANEL, edgecolor=C_GRID, labelcolor=C_TEXT)
ax1.grid(axis='x', alpha=0.15, color='white')

# ─ Panel 2: TOPSIS Skor ──────────────────────────────────────────────────
ax2 = fig.add_subplot(3, 2, 2); ax2.set_facecolor(C_PANEL)
b2 = ax2.bar([0,1], Ci, color=[C_MN,C_FW], width=0.45, edgecolor='none', zorder=3)
for bar,val in zip(b2,Ci):
    ax2.text(bar.get_x()+bar.get_width()/2, val+0.015, f'Ci={val:.4f}',
             ha='center', color=C_TEXT, fontsize=13, fontweight='bold')
ax2.axhline(0.5, color=C_GOLD, ls='--', alpha=0.7, lw=1.5, label='Eşik (0.50)')
ax2.set_xticks([0,1]); ax2.set_xticklabels(ALT, color=C_TEXT, fontsize=12)
ax2.set_ylabel('Ci Skoru', color=C_TEXT); ax2.set_ylim(0,0.85)
ax2.set_title('TOPSIS Yakınlık Skoru\n(Ci→1.0 = İdeal Çözüme Yakın)',
              color=C_TEXT, fontsize=11, fontweight='bold', pad=12)
ax2.tick_params(colors=C_TEXT)
for s in ax2.spines.values(): s.set_edgecolor(C_GRID)
ax2.legend(fontsize=9, facecolor=C_PANEL, edgecolor=C_GRID, labelcolor=C_TEXT)
ax2.grid(axis='y', alpha=0.15, color='white', zorder=0)
# Trade-off notu
ax2.text(0.5, 0.95, f'Manuel: maliyet avantajı (w_fin=0.40)\n'
         f'ΔCi = {abs(Ci[1]-Ci[0]):.4f}', ha='center', va='top',
         transform=ax2.transAxes, fontsize=9, color=C_GOLD,
         bbox=dict(boxstyle='round', facecolor=C_PANEL, edgecolor=C_GOLD, alpha=0.8))

# ─ Panel 3: Radar ─────────────────────────────────────────────────────────
ax3 = fig.add_subplot(3, 2, 3, projection='polar'); ax3.set_facecolor(C_PANEL)
def n01(v,j):
    col=X[:,j]; mn,mx=col.min(),col.max()
    if mx==mn: return 0.5
    r=(v-mn)/(mx-mn); return r if FAYDA[j] else 1-r
rmn=[n01(X[0,j],j) for j in range(nc)]
rfw=[n01(X[1,j],j) for j in range(nc)]
ang=np.linspace(0,2*np.pi,nc,endpoint=False).tolist(); ang+=ang[:1]
rmn+=rmn[:1]; rfw+=rfw[:1]
ax3.plot(ang,rmn,'o-',color=C_MN,lw=2.5,ms=7,label='Manuel',zorder=3)
ax3.fill(ang,rmn,color=C_MN,alpha=0.2)
ax3.plot(ang,rfw,'s-',color=C_FW,lw=2.5,ms=7,label='Four-Way',zorder=3)
ax3.fill(ang,rfw,color=C_FW,alpha=0.2)
ax3.set_xticks(ang[:-1])
ax3.set_xticklabels(KRITER, color=C_TEXT, fontsize=9, fontweight='bold')
ax3.set_yticks([0.25,0.50,0.75,1.0])
ax3.set_yticklabels(['','0.50','','1.00'], color='#777', fontsize=7)
ax3.set_ylim(0,1.05); ax3.grid(color=C_GRID, alpha=0.5)
ax3.spines['polar'].set_color(C_GRID)
ax3.set_title('Radar: Normalize Performans\n(Manuel: Finansal üstün | FW: 4 kriter üstün)',
              color=C_TEXT, fontsize=11, fontweight='bold', pad=20)
ax3.legend(loc='upper right', bbox_to_anchor=(1.35,1.12),
           facecolor=C_PANEL, edgecolor=C_GRID, labelcolor=C_TEXT, fontsize=9)

# ─ Panel 4: D+/D- ─────────────────────────────────────────────────────────
ax4 = fig.add_subplot(3, 2, 4); ax4.set_facecolor(C_PANEL)
ww=0.32
bdp=ax4.bar(np.arange(2)-ww/2, Dp, ww, label='D⁺ (İdeal Uzaklık)',
            color=['#EF9A9A','#EF9A9A'], edgecolor='none', zorder=3)
bdn=ax4.bar(np.arange(2)+ww/2, Dn, ww, label='D⁻ (Neg. İdeal Uzaklık)',
            color=[C_MN,C_FW], edgecolor='none', zorder=3)
for bar in list(bdp)+list(bdn):
    h=bar.get_height()
    ax4.text(bar.get_x()+bar.get_width()/2, h+0.003, f'{h:.4f}',
             ha='center', color=C_TEXT, fontsize=9, fontweight='bold')
ax4.set_xticks([0,1]); ax4.set_xticklabels(ALT, color=C_TEXT, fontsize=12)
ax4.set_ylabel('Mesafe', color=C_TEXT)
ax4.set_title('TOPSIS Mesafe Analizi\n(İyi: D⁺ küçük, D⁻ büyük)',
              color=C_TEXT, fontsize=11, fontweight='bold', pad=12)
ax4.tick_params(colors=C_TEXT)
for s in ax4.spines.values(): s.set_edgecolor(C_GRID)
ax4.legend(fontsize=8, facecolor=C_PANEL, edgecolor=C_GRID, labelcolor=C_TEXT, loc='upper center')
ax4.grid(axis='y', alpha=0.15, color='white', zorder=0)

# ─ Panel 5: Duyarlılık Eğrisi (tam genişlik) ──────────────────────────────
ax5 = fig.add_subplot(3, 1, 3); ax5.set_facecolor(C_PANEL)
ax5.plot(fin_range*100, ci_mn_arr, '-', color=C_MN, lw=2.5, label='Manuel Ci')
ax5.plot(fin_range*100, ci_fw_arr, '-', color=C_FW, lw=2.5, label='Four-Way Ci')
ax5.axvline(cross_w*100, color=C_GOLD, ls='--', lw=2,
            label=f'Crossover: w_fin = {cross_w:.1%}')
ax5.axhline(0.5, color='#555', ls=':', alpha=0.5)
ax5.fill_betweenx([0,1], 10, cross_w*100, alpha=0.08, color=C_FW)
ax5.fill_betweenx([0,1], cross_w*100, 55, alpha=0.08, color=C_MN)
ax5.text(cross_w*100-8, 0.72, 'FOUR-WAY\nBÖLGESİ', color=C_FW,
         fontsize=11, fontweight='bold', ha='center')
ax5.text(cross_w*100+8, 0.72, 'MANUEL\nBÖLGESİ', color=C_MN,
         fontsize=11, fontweight='bold', ha='center')
ax5.scatter([cross_w*100], [ci_mn_arr[cross_idx]], s=120, color=C_GOLD,
            zorder=5, edgecolors='white', linewidths=2)
ax5.set_xlabel('Finansal Kriter Ağırlığı (%)', color=C_TEXT, fontsize=11)
ax5.set_ylabel('TOPSIS Ci Skoru', color=C_TEXT, fontsize=11)
ax5.set_title(f'Duyarlılık Analizi: Finansal Ağırlık vs TOPSIS Sonucu\n'
              f'Crossover ≈ w_fin = {cross_w:.1%} — Bu noktanın altında Four-Way optimal',
              color=C_TEXT, fontsize=12, fontweight='bold', pad=12)
ax5.set_xlim(10, 55); ax5.set_ylim(0.15, 0.85)
ax5.tick_params(colors=C_TEXT)
for s in ax5.spines.values(): s.set_edgecolor(C_GRID)
ax5.legend(fontsize=10, facecolor=C_PANEL, edgecolor=C_GRID, labelcolor=C_TEXT, loc='upper left')
ax5.grid(alpha=0.15, color='white')
# Mevcut ağırlık notu
ax5.annotate(f'Mevcut: w_fin={w[0]:.1%}', xy=(w[0]*100, Ci[0]),
             xytext=(w[0]*100+5, Ci[0]+0.08),
             arrowprops=dict(arrowstyle='->', color=C_TEXT, lw=1.5),
             fontsize=9, color=C_TEXT, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor=C_PANEL, edgecolor=C_TEXT, alpha=0.8))

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig('bilesen8_ahp_topsis.png', dpi=200, bbox_inches='tight', facecolor=C_BG)
print("\n✓ Grafik kaydedildi: bilesen8_ahp_topsis.png")
