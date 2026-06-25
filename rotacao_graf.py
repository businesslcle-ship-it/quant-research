import pandas as pd, numpy as np, matplotlib.pyplot as plt
C, A, N = 0.0005, 0.20, 252
LOOKBACKS = [126, 189, 252, 315]                                                     # média de parâmetros
px = pd.concat({a: pd.read_csv(f"dados/{a}.csv", parse_dates=["date"]).set_index("date")["adjustedClose"]
                for a in ["PRIO3","ITUB3","ABEV3"]}, axis=1, sort=True).loc["2008":]
ret = px.pct_change()
def pesos(L):                                                                        # alocação para UM lookback
    rank = px.pct_change(L).rank(axis=1)
    best = rank.eq(rank.max(axis=1), axis=0).astype(float); best = best.div(best.sum(axis=1), axis=0)
    vol = (best * ret.rolling(20).std() * N**.5).sum(axis=1)
    return best.mul((A / vol.replace(0, np.nan)).clip(0, 1), axis=0).fillna(0)
w = sum(pesos(L) for L in LOOKBACKS) / len(LOOKBACKS)                                 # média dos pesos
r = (w.shift(1) * ret).sum(axis=1) - w.diff().abs().sum(axis=1) * C
eq = (1+r).cumprod(); bh = (1+ret.mean(axis=1)).cumprod(); dd = (eq/eq.cummax()-1)*100
print(f"Sharpe={r.mean()/r.std()*N**.5:.2f}  Sortino={r.mean()/r[r<0].std()*N**.5:.2f}  MaxDD={dd.min():.0f}%  ret={eq.iloc[-1]-1:.0%}")

fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(13, 10), sharex=True, height_ratios=[2, 1, 1])
eq.plot(ax=a1, color="green", label="Rotação"); bh.plot(ax=a1, color="gray", lw=.9, label="Buy&Hold")
a1.set_yscale("log"); a1.legend(loc="upper left"); a1.set_title("Patrimônio acumulado (escala log)"); a1.grid(alpha=.3)
a2.fill_between(dd.index, dd.values, 0, color="red", alpha=.35, label="ESTRATÉGIA")
for asset, cor in [("PRIO3","tab:orange"), ("ITUB3","tab:blue"), ("ABEV3","tab:green")]:
    e = (1 + ret[asset]).cumprod(); a2.plot(e.index, (e/e.cummax()-1)*100, color=cor, lw=.7, alpha=.8, label=asset)
a2.set_title("Drawdown (%): estratégia (vermelho) vs cada ativo"); a2.legend(loc="lower left", ncol=4, fontsize=8); a2.grid(alpha=.3)
w.plot.area(ax=a3, linewidth=0, alpha=.8)
a3.set_title("Alocação — qual ativo e com que tamanho (média de 4 lookbacks)"); a3.legend(loc="upper left"); a3.set_ylim(0, 1)
fig.tight_layout(); fig.savefig("rotacao.png", dpi=130); plt.show()
