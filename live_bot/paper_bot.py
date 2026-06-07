"""
Paper-trading bot — multi-edge book (deployed). Tracks in parallel, NO REAL MONEY:
  TREND  - Donchian 55/20 + 200-MA + BTC-master regime, long-only, ATR stop/sizing.
  FLUSH  - liquidation-flush reversion: buy a coin after a >8% 4h dump that stabilises
           (knife filter), size by flush magnitude (<=3x), exit on +5% bounce or 4 bars.
  BLEND  - 70% trend + 30% flush (derived) = the validated book (OOS Sharpe ~1.05, lower DD).
Each = its own paper account on the 20-coin Binance basket, 4H. Public REST (no key).
State per strategy in state_*.json; equity in equity_*.csv; web/data.json for the dashboard.
"""
import sys, os, json, time, csv
from datetime import datetime, timezone
from pathlib import Path
import requests, numpy as np, pandas as pd

HERE = Path(__file__).parent
COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","LINKUSDT",
         "LTCUSDT","DOGEUSDT","MATICUSDT","DOTUSDT","ATOMUSDT","NEARUSDT","FILUSDT","UNIUSDT",
         "ETCUSDT","XLMUSDT","ALGOUSDT","ICPUSDT"]
INTERVAL="4h"; START_EQUITY=10000.0; COST=0.001+0.0005
# trend
ENTRY,EXIT,MA_LEN,ADX_MIN,ATR_LEN,ATR_STOP,RISK_PCT = 55,20,200,25,14,2.5,5.0
# flush
FL_THR,FL_CONFIRM,FL_TARGET,FL_MAXBARS,FL_MAXSIZE = -0.08,-0.02,0.05,4,3.0
BASE="https://api.binance.com/api/v3/klines"
STRATS=["trend","flush"]; BLEND_W={"trend":0.7,"flush":0.3}

TG_TOKEN=os.environ.get("TG_TOKEN",""); TG_CHAT=os.environ.get("TG_CHAT","")
def tg(m):
    if TG_TOKEN and TG_CHAT:
        try: requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",data={"chat_id":TG_CHAT,"text":m},timeout=10)
        except Exception: pass
def now(): return datetime.now(timezone.utc).isoformat()
def state_path(st): return HERE/f"state_{st}.json"
def eqlog_path(st): return HERE/f"equity_{st}.csv"
TRADELOG=HERE/"trades.csv"

def fetch(sym,limit=400):
    r=requests.get(BASE,params={"symbol":sym,"interval":INTERVAL,"limit":limit},timeout=20); r.raise_for_status()
    df=pd.DataFrame(r.json(),columns=["t","o","h","l","c","v","ct","q","n","tb","tq","ig"])
    for x in ["o","h","l","c"]: df[x]=df[x].astype(float)
    return df
def rma(s,n): return s.ewm(alpha=1/n,adjust=False).mean()
def indicators(df):
    h,l,c=df.h,df.l,df.c; pc=c.shift()
    tr=pd.concat([h-l,(h-pc).abs(),(l-pc).abs()],axis=1).max(axis=1); atr=rma(tr,ATR_LEN)
    up=h.diff(); dn=-l.diff(); plus=np.where((up>dn)&(up>0),up,0.0); minus=np.where((dn>up)&(dn>0),dn,0.0)
    ax=rma(tr,14); pdi=100*rma(pd.Series(plus,index=df.index),14)/ax.replace(0,np.nan); mdi=100*rma(pd.Series(minus,index=df.index),14)/ax.replace(0,np.nan)
    adx=rma((100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan)).fillna(0),14)
    return atr,adx,c.rolling(MA_LEN).mean(),h.rolling(ENTRY).max(),l.rolling(EXIT).min()

def load_state(st):
    p=state_path(st)
    if p.exists(): return json.loads(p.read_text())
    sub=START_EQUITY/len(COINS)
    return {"coins":{c:{"cash":sub,"units":0.0,"entry":0.0,"stop":0.0,"peak":0.0,"held":0,"size":0.0} for c in COINS}}
def log_trade(row):
    new=not TRADELOG.exists()
    with open(TRADELOG,"a",newline="") as f:
        w=csv.writer(f)
        if new: w.writerow(["time","strat","coin","action","price","units","reason","pnl"])
        w.writerow(row)
def append_eq(st,total):
    p=eqlog_path(st); new=not p.exists()
    with open(p,"a",newline="") as f:
        w=csv.writer(f)
        if new: w.writerow(["time","equity"])
        w.writerow([now(),round(total,2)])

def series_of(stname):
    p=eqlog_path(stname); out=[]
    if p.exists():
        with open(p) as f:
            next(f,None)
            for ln in f:
                a=ln.strip().split(",")
                if len(a)==2: out.append([a[0][:16],round(float(a[1]),2)])
    return out
def closed_pnls(stname):
    out=[]
    if TRADELOG.exists():
        with open(TRADELOG) as f:
            for row in csv.DictReader(f):
                if row.get("strat")==stname and row.get("action")=="SELL" and row.get("pnl"):
                    try: out.append(float(row["pnl"]))
                    except ValueError: pass
    return out
def stat_block(stname, series, total):
    eqv=[s[1] for s in series]
    mdd=0.0
    if len(eqv)>1:
        peak=eqv[0]
        for v in eqv: peak=max(peak,v); mdd=min(mdd,v/peak-1)
    yrs=max(len(eqv),1)/(365*6)
    cagr=(total/START_EQUITY)**(1/yrs)-1 if yrs>0 and total>0 else 0.0
    pls=closed_pnls(stname); wins=[x for x in pls if x>0]; los=[x for x in pls if x<=0]
    wr=len(wins)/len(pls)*100 if pls else 0.0
    pf=sum(wins)/abs(sum(los)) if los and sum(los)!=0 else (0.0 if not wins else 999.0)
    return dict(equity=round(total,2),pnl_pct=round((total/START_EQUITY-1)*100,2),
                cagr=round(cagr*100,1),maxdd=round(mdd*100,1),wr=round(wr,1),pf=round(pf,2),
                trades=len(pls),series=series)

def write_webdata(states, totals):
    levels=[]
    for st in STRATS:
        levels.append({"lev":st, **stat_block(st, series_of(st), totals[st])})
    # derived blend from per-cycle returns of trend & flush
    def rets(stname):
        s=series_of(stname); return [s[i][1]/s[i-1][1]-1 if s[i-1][1] else 0 for i in range(1,len(s))], [r[0] for r in s]
    tr,tt=rets("trend"); fr,_=rets("flush")
    blend_series=[]; eqb=START_EQUITY; times=[x[0] for x in series_of("trend")]
    if tr and fr and len(tr)==len(fr):
        blend_series.append([times[0] if times else now()[:16], round(eqb,2)])
        for i in range(len(tr)):
            eqb*= (1+BLEND_W["trend"]*tr[i]+BLEND_W["flush"]*fr[i])
            blend_series.append([times[i+1] if i+1<len(times) else now()[:16], round(eqb,2)])
    levels.append({"lev":"blend 70/30", **stat_block("blend", blend_series, eqb)})
    s3=states["flush"]
    positions=[{"coin":c,"units":round(cs["units"],6),"entry":cs["entry"],"stop":round(cs.get("stop",0),6)}
               for c,cs in states["trend"]["coins"].items() if cs["units"]>0]
    positions+=[{"coin":c+" (flush)","units":round(cs["units"],6),"entry":cs["entry"],"stop":"+5% / 4bar"}
                for c,cs in s3["coins"].items() if cs["units"]>0]
    data={"updated":now()[:16],"start":START_EQUITY,"n_coins":len(COINS),"levels":levels,"positions":positions}
    web=HERE.parent/"web"; web.mkdir(exist_ok=True); (web/"data.json").write_text(json.dumps(data),encoding="utf-8")

def cycle():
    states={st:load_state(st) for st in STRATS}
    totals={st:0.0 for st in STRATS}; actions=[]
    # BTC master regime for trend
    try:
        bdf=fetch("BTCUSDT"); _,_,bma,_,_=indicators(bdf); bi=len(bdf)-2; btc_ok=bool(bdf.c.iloc[bi]>bma.iloc[bi])
    except Exception: btc_ok=True
    for c in COINS:
        try: df=fetch(c)
        except Exception as e:
            print(f"{c}: fetch fail {e}")
            for st in STRATS: totals[st]+=states[st]["coins"][c]["cash"]
            continue
        atr,adx,ma,donHi,donLo=indicators(df); i=len(df)-2
        price,low,high,a=df.c.iloc[i],df.l.iloc[i],df.h.iloc[i],atr.iloc[i]
        r_prev=df.c.iloc[i-1]/df.c.iloc[i-2]-1 if i>=2 else 0.0
        r_now=df.c.iloc[i]/df.c.iloc[i-1]-1 if i>=1 else 0.0
        # ---- TREND ----
        cs=states["trend"]["coins"][c]
        if cs["units"]>0:
            cs["peak"]=max(cs["peak"],high)
            if price<donLo.iloc[i-1] or low<cs["stop"]:
                pnl=cs["units"]*price*(1-COST)-cs["units"]*cs["entry"]*(1+COST); cs["cash"]+=cs["units"]*price*(1-COST)
                log_trade([now(),"trend",c,"SELL",round(price,6),round(cs["units"],6),"exit",round(pnl,2)]); actions.append(f"trend {c} EXIT")
                cs.update(units=0.0,entry=0.0,stop=0.0,peak=0.0)
        elif price>donHi.iloc[i-1] and adx.iloc[i]>ADX_MIN and price>ma.iloc[i] and btc_ok and a>0:
            sd=a*ATR_STOP; u=(cs["cash"]*RISK_PCT/100)/sd; u=min(u,cs["cash"]*0.95/price)
            if u>0:
                cs["cash"]-=u*price*(1+COST); cs.update(units=u,entry=price,stop=price-sd,peak=high)
                log_trade([now(),"trend",c,"BUY",round(price,6),round(u,6),"breakout",""]); actions.append(f"trend {c} BUY")
        totals["trend"]+=cs["cash"]+cs["units"]*price
        # ---- FLUSH ----
        fs=states["flush"]["coins"][c]
        if fs["units"]>0:
            if high/fs["entry"]-1>=FL_TARGET or fs["held"]>=FL_MAXBARS:
                pnl=fs["units"]*price*(1-COST)-fs["units"]*fs["entry"]*(1+COST); fs["cash"]+=fs["units"]*price*(1-COST)
                log_trade([now(),"flush",c,"SELL",round(price,6),round(fs["units"],6),"bounce/timeout",round(pnl,2)]); actions.append(f"flush {c} EXIT")
                fs.update(units=0.0,entry=0.0,held=0,size=0.0)
            else: fs["held"]+=1
        elif r_prev<FL_THR and r_now>FL_CONFIRM:
            size=min(FL_MAXSIZE,abs(r_prev)/0.10)
            u=size*fs["cash"]*0.95/price
            if u>0:
                fs["cash"]-=u*price*(1+COST); fs.update(units=u,entry=price,held=1,size=size)
                log_trade([now(),"flush",c,"BUY",round(price,6),round(u,6),f"flush {r_prev*100:.0f}%",""]); actions.append(f"flush {c} BUY")
        totals["flush"]+=fs["cash"]+fs["units"]*price
    for st in STRATS:
        states[st]["last_run"]=now(); states[st]["equity"]=round(totals[st],2)
        state_path(st).write_text(json.dumps(states[st],indent=2)); append_eq(st,totals[st])
    write_webdata(states,totals)
    summ=" | ".join(f"{st} ${totals[st]:,.0f}" for st in STRATS)+(f" | {', '.join(actions)}" if actions else " | no trades")
    tg("PaperBot "+summ); print(f"{now()}  {summ}")

if __name__=="__main__":
    if "--loop" in sys.argv:
        while True:
            try: cycle()
            except Exception as e: print("cycle error:",e)
            time.sleep(4*3600)
    else: cycle()
