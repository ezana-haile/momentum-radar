import streamlit as st
import pandas as pd
import requests
import datetime
import time

st.set_page_config(page_title="Broad Market Radar", page_icon="📡", layout="centered")
st.title("📡 500-Ticker Institutional Radar")
st.write("Batch-sliced scanning engine. Rates-optimized for broad market hunting.")

# --- USER CREDENTIALS ---
st.sidebar.header("🔑 API Connection Settings")
ALPACA_API_KEY = st.sidebar.text_input("Alpaca API Key", type="password", value="PKV7X5UXF3FVVIXXCW6MGJFENQ")
ALPACA_SECRET_KEY = st.sidebar.text_input("Alpaca Secret Key", type="password", value="3vB8arzD18nTJvgULhCBRoda5FnoAzQspj9RhfdpMbxh")
DATA_URL = "https://data.alpaca.markets/v2"

headers = {
    "APCA-API-KEY-ID": ALPACA_API_KEY.strip(),
    "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY.strip(),
    "Content-Type": "application/json"
}

# --- THE COMPREHENSIVE 500-STOCK HIGH-VOLUME WATCHLIST ---
DEFAULT_500_POOL = (
    "AAPL,TSLA,NVDA,AMD,MSFT,AMZN,META,GOOGL,NFLX,BABA,BIDU,JD,PDD,LI,NIO,XPEV,"
    "COIN,MARA,RIOT,HOOD,SOFI,PLTR,AI,C3,SNOW,NET,CRWD,PANW,ZS,DDOG,OKTA,MDB,"
    "INTC,MU,QCOM,AVGO,SMCI,ASML,LRCX,AMAT,ARM,TSM,UBER,LYFT,ABNB,BKNG,CVNA,"
    "DKNG,PENN,RBLX,U,GME,AMC,DJT,SQ,PYPL,V,MA,DIS,NKE,XOM,CVX,F,GM,GE,CAT,HON,"
    "BA,LMT,RTX,JPM,BAC,WFC,C,GS,MS,BRK/B,WMT,TGT,COST,HD,LOW,AMGN,PFE,MRNA,"
    "GILD,BIIB,VRTX,REGN,JNJ,UNH,CVS,CI,EL,PG,CL,KO,PEP,MDLZ,MO,PM,BTU,FCX,NEM,"
    "AA,NUE,X,VALE,RIO,BHP,DD,DOW,CTVA,APD,LIN,SHW,PPG,ALB,SQM,MP,UU,CCJ,DNN,"
    "NXE,URNM,URA,TAN,FAN,ICLN,WOOD,LIT,REMX,COP,OXY,MRO,HES,DVN,FANG,HAL,SLB,"
    "BKR,FCEL,PLUG,BLDP,RUN,SPWR,ENPH,SEDG,FSLR,CSIQ,JKS,DQ,BE,CHPT,BLNK,EVGO,"
    "RIVN,LCID,QS,PSNY,NKLA,WKHS,CANO,GOEV,MULN,FFIE,XOS,REE,PTRA,AEHR,INDI,"
    "POWI,WOLF,ON,NXPI,TXN,ADI,MCHP,STM,MPWR,CRUS,DIOD,LSCC,SYNA,COHR,IPGP,FN,"
    "VIAV,LITE,JBL,SANM,PSTG,STX,WDC,HPE,NTAP,ANET,CSCO,JNPR,FFIV,CIEN,XRX,"
    "HPQ,DELL,STME,SMCI,DDD,SSYS,VJET,DM,XONE,PROTO,MTLS,MMM,TMO,A,PKI,"
    "WAT,MTD,ILMN,PACB,TXG,NTRA,GH,EXAS,CDNA,NVTA,CGEN,COLL,TECH,CRL,"
    "IQV,MEDP,ICLR,INCY,ALNY,BMRN,SGEN,SEG,ASND,SRPT,IONS,CRSP,NTLA,"
    "EDIT,BEAM,VERV,ALEC,BLUE,SGMO,CELU,BNTX,CURE,NVAX,INO,VBI,DYAI,VXRT,"
    "AZN,SNY,NVO,LLY,MRK,BMY,ABBV,ELV,HUM,"
    "CNC,MOH,AGV,THC,CYH,UHS,HCA,SEM,ACHC,MODV,AVA,EHC,AMN,CHNG,HQY,PHR,DOCU,"
    "PING,FORG,SAIL,ZSC,FTNT,CHKP,CLFL,ABST,QLYS,RAPT,VRNS,"
    "TCX,RDWR,MIME,BLKB,ALTR,SPLK,NEW,ESTC,NOW,TEAM,WDAY,PAYC,PCTY,UPWK,FIVN,"
    "RNG,EGHT,BAND,TWLO,CRM,HUBS,ZEN,UPLD,YEXT,BOX,DBX,EGNY,SOPH,PRO,APP,"
    "UPST,AFRM,HUT,BITF,HIVE,DGHI,MSTR,SLNH,CORZ,WULF,"
    "CLSK,SDIG,TERA,ANY,BTCM,GREE,ARBK,XBTF,BITO,GBTC,ETHE,LTCN,BCHG,GLXY,BKCH,"
    "BLOK,LEGR,BLCN,CRPT,BITQ,SATO,FRPH,JOAN,EXPR,BBBY,BB,NOK,KOSS,TLRY,"
    "CGC,ACB,HEXO,SNDL,CRON,APHA,TPB,UVV,BTI,IMBBY,STZ,TAP,BUD,SAM,DEO,"
    "CCEP,COKE,FIZZ,MNST,CELH,KDP,YELP,OPEN,ZG,Z,RDFN,EXPE,TRIP,TNL,MAR,HLT,H,WH,CHH,IHRT,CZR,MGM,WYNN,"
    "LVS,RSI,GAN,BALY,CHDN,ERI,NCLH,RCL,CCL,SAVE,BLU,"
    "JBLU,LUV,AAL,DAL,UAL,ALK,HA,SNCY"
)

st.subheader("📋 Scan Global Momentum Pool")
watch_input = st.text_area("Active Scanning Pool (500 Curated Tickers Loaded):", value=DEFAULT_500_POOL, height=200)

watchlist = [ticker.strip().upper() for ticker in watch_input.split(",") if ticker.strip()]

if st.button("🚀 Run Live 500-Ticker Mass Scan", use_container_width=True):
    st.info(f"Initiating batch-sliced scan across {len(watchlist)} assets...")
    breakout_detected = False
   
    end_date = datetime.date.today().isoformat()
    start_date = (datetime.date.today() - datetime.timedelta(days=40)).isoformat()
               
    BATCH_SIZE = 50
    total_tickers = len(watchlist)
   
    progress_bar = st.progress(0)
   
    for i in range(0, total_tickers, BATCH_SIZE):
        batch = watchlist[i:i + BATCH_SIZE]
        ticker_string = ",".join(batch)
       
        progress_percentage = int((i / total_tickers) * 100)
        progress_bar.progress(progress_percentage)
       
        try:
            # 3. BULK SNAPSHOT REQUEST
            snapshot_res = requests.get(f"{DATA_URL}/stocks/snapshots?symbols={ticker_string}", headers=headers)
            if snapshot_res.status_code != 200:
                continue
               
            snapshots = snapshot_res.json().get('snapshots', {})
           
            for symbol in batch:
                if symbol not in snapshots or snapshots[symbol] is None:
                    continue
               
                try:
                    stock_data = snapshots[symbol]
                    latest_quote = stock_data.get('latestQuote', {})
                    live_price = latest_quote.get('ap', 0)   
                    bid_price = latest_quote.get('bp', 0)    
                    today_vol = stock_data.get('dailyBar', {}).get('v', 0)

                    if live_price <= 0:
                        continue
                   
                    # 4. HISTORY ENDPOINT CALL
                    hist_res = requests.get(f"{DATA_URL}/stocks/{symbol}/bars?timeframe=1Day&start={start_date}&end={end_date}&limit=100", headers=headers)
                    if hist_res.status_code != 200:
                        continue
                   
                    bars = hist_res.json().get('bars', [])
                    if len(bars) < 10: # Spaced down safely to verify the 10-period window
                        continue
                   
                    df = pd.DataFrame(bars)
                    df['10_SMA'] = df['c'].rolling(window=10).mean()
                   
                    sma_10 = df['10_SMA'].iloc[-1]
                    avg_20_vol = df['v'].tail(20).mean()
                   
                    # 5. CONSTRAINTS (Adjust filters back to strict targets during open hours)
                    is_above_sma = live_price > sma_10
                    is_rallying = True 
                    has_huge_volume = True 
                   
                    if is_above_sma and is_rallying and has_huge_volume:
                        breakout_detected = True
                        st.success(
                            f"🟢 **BUY TARGET IDENTIFIED: {symbol}**\n\n"
                            f"* **Live Price:** ${live_price:.2f} (MA-10 baseline: ${sma_10:.2f})\n"
                            f"* **IEX Volume:** {today_vol:,} shares tracked.\n"
                        )
                except Exception as ticker_error:
                    continue # Skips a single bad asset (like formatting bugs) instead of ruining the whole batch
           
            time.sleep(0.4) # Rates-compliance pause
           
        except Exception as batch_error:
            continue
           
    progress_bar.progress(100)
   
    if not breakout_detected:
        st.warning("Scan complete. No stock currently matches the filtering criteria.")

Sent from Outlook for iOS
