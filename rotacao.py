import pandas as pd, numpy as np
C, A, N = 0.0005, 0.20, 252                                                          # custo, vol-alvo, dias/ano
LOOKBACKS = [126, 189, 252, 315]                                                     # média de parâmetros (não escolho um)
px = pd.concat({a: pd.read_csv(f"dados/{a}.csv", parse_dates=["date"]).set_index("date")["adjustedClose"]
                for a in ["PRIO3","ITUB3","ABEV3"]}, axis=1, sort=True).loc["2008":]  # universo expansível
ret = px.pct_change()
def pesos(L):                                                                        # alocação para UM lookback L
    rank = px.pct_change(L).rank(axis=1)                                             # ranqueia os 3 por momentum
    best = rank.eq(rank.max(axis=1), axis=0).astype(float); best = best.div(best.sum(axis=1), axis=0)
    vol = (best * ret.rolling(20).std() * N**.5).sum(axis=1)                         # vol do ativo escolhido
    return best.mul((A / vol.replace(0, np.nan)).clip(0, 1), axis=0).fillna(0)       # tamanho via vol targeting
w = sum(pesos(L) for L in LOOKBACKS) / len(LOOKBACKS)                                # MÉDIA dos pesos dos 4 lookbacks
r = (w.shift(1) * ret).sum(axis=1) - w.diff().abs().sum(axis=1) * C                  # retorno líquido (shift=sem look-ahead)
eq = (1 + r).cumprod(); m = len(r.dropna()) // 2; sh = lambda x: x.dropna().mean() / x.dropna().std() * N**.5
print(f"Sharpe={sh(r):.2f}  Sortino={r.mean()/r[r<0].std()*N**.5:.2f}  MaxDD={(eq/eq.cummax()-1).min():.0%}  ret={eq.iloc[-1]-1:.0%}")
print(f"walk-fwd: treino={sh(r.dropna().iloc[:m]):.2f}  prova={sh(r.dropna().iloc[m:]):.2f}  desde2021={sh(r.loc['2021':]):.2f}")
