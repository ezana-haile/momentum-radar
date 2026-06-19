import streamlit as st
import pandas as pd
import requests
import datetime
import time

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Institutional Momentum Radar", page_icon="??", layout="centered")
st.title("MR")
st.write("Batch-sliced scanning engine optimized for heavy-volume trend detection.")

# --- USER CREDENTIALS ---
st.sidebar.header("?? API Connection Settings")
ALPACA_API_KEY = st.sidebar.text_input("Alpaca API Key", type="password", value="PKV7X5UXF3FVVIXXCW6MGJFENQ")
ALPACA_SECRET_KEY = st.sidebar.text_input("Alpaca Secret Key", type="password", value="3vB8arzD18nTJvgULhCBRoda5FnoAzQspj9RhfdpMbxh")

# Base Alpaca data engine endpoint
DATA_URL = "https://data.alpaca.markets/v2"

# Clean headers using strip() to eliminate accidental copy-paste whitespace
headers = {
    "APCA-API-KEY-ID": ALPACA_API_KEY.strip(),
    "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY.strip(),
    "Content-Type": "application/json"
}

# --- THE COMPREHENSIVE 500-STOCK WATCHLIST (Trading 212 & Alpaca Sync) ---
DEFAULT_500_POOL = (
    "AAPL,MSFT,NVDA,AMZN,META,GOOGL,GOOG,TSLA,V,UNH,XOM,MA,JPM,HD,PG,COST,"
    "ADBE,NFLX,AMD,CRM,CVX,TMUS,BAC,PEP,KO,CSCO,WMT,MRK,ORCL,ACN,ABBV,QCOM,"
    "INTC,LIN,INTU,CMCSA,TXN,AMGN,PDD,GE,PM,CDNS,SNOW,SPGI,AXP,AMAT,PFE,HON,"
    "UNP,LRCX,NOW,SYK,T,CAT,PANW,MDLZ,DIS,MU,SCHW,ELV,VRTX,GEHC,LOW,BMY,"
    "REGN,LMT,DE,PLTR,CB,RTX,BA,TJX,IBM,ANET,PGR,ADI,MCD,MAR,BKNG,BSX,PLD,"
    "CI,ETN,WM,NKE,MCO,HCA,ADP,GD,FI,EOG,STZ,MO,CVS,BDX,ZTS,ECL,MCK,CL,"
    "APH,SLB,SRE,HUM,NSC,COP,ITW,AON,TGT,EMR,FCX,FDX,MPC,DHR,MGM,NXPI,COF,"
    "D,CMG,WFC,DOW,CEG,ABNB,O,GILD,MET,MCHP,KMB,PSX,C,IQV,OXY,BK,SBUX,"
    "TRV,PCAR,AIG,STT,VLO,A,MS,KMI,PH,KHC,WELL,JCI,WMB,FIS,GLW,TEL,ROST,"
    "BKR,TRGP,PPG,CTAS,TFC,PAYX,HWM,HAL,DFS,ED,DLTR,ROK,RSG,ADSK,CDW,CMI,"
    "ANSS,LEN,VRSK,FAST,DVN,GWW,ALL,PCG,KR,HPQ,YUM,KEYS,EIX,AME,CTSH,PEG,"
    "FITB,CARR,CPRT,WEC,VICI,ODFL,MTD,GDDY,COR,CSX,VEEV,URI,BBY,FANG,DD,"
    "DLR,F,MTB,AWK,EFX,GPN,EXR,CBRE,LRN,WTW,SBAC,ULTA,VTR,TROW,STE,BRO,"
    "IFF,WY,SJM,CHRW,LNT,ALGN,NVR,WST,MTCH,GRMN,HAS,NUE,MKC,NICE,GEN,WAB,"
    "AMCR,MDU,PNR,DOCU,LNC,RL,JNPR,AAL,UAL,LUV,DAL,ALK,HA,SAVE,JBLU,PLAY,"
    "U,TTD,DKNG,HOOD,SOFI,COIN,MARA,RIOT,AI,C3,NET,CRWD,ZS,DDOG,OKTA,MDB,"
    "SMCI,UBER,LYFT,CVNA,RBLX,GME,AMC,DJT,SQ,PYPL,ASML,ARM,TSM,NIO,XPEV,"
    "LI,BABA,BIDU,JD,BTU,NEM,AA,VALE,RIO,BHP,ALB,SQM,MP,CCJ,DNN,NXE,MRO,"
    "HES,PLUG,FCEL,BLDP,RUN,SPWR,ENPH,SEDG,FSLR,CSIQ,JKS,DQ,BE,CHPT,BLNK,"
    "EVGO,RIVN,LCID,QS,PSNY,NKLA,WKHS,GOEV,MULN,FFIE,XOS,REE,ON,MPWR,CRUS,"
    "DIOD,LSCC,SYNA,COHR,IPGP,FN,VIAV,LITE,JBL,SANM,PSTG,STX,WDC,HPE,NTAP,"
    "XRX,DELL,MMM,TMO,ILMN,PACB,TXG,NTRA,GH,CDNA,NVTA,TECH,CRL,MEDP,"
    "ICLR,INCY,ALNY,BMRN,SRPT,IONS,CRSP,NTLA,EDIT,BEAM,VERV,ALEC,BLUE,SGMO,"
    "CELU,BNTX,CURE,NVAX,INO,VBI,DYAI,VXRT,AZN,SNY,NVO,MOH,THC,CYH,UHS,"
    "SEM,MODV,AVA,EHC,AMN,PHR,FTNT,CHKP,QLYS,RAPT,VRNS,TCX,RDWR,BLKB,ALTR,"
    "ESTC,TEAM,WDAY,PAYC,PCTY,UPWK,FIVN,RNG,EGHT,BAND,TWLO,HUBS,UPLD,YEXT,"
    "BOX,DBX,SOPH,PRO,APP,UPST,AFRM,HUT,BITF,HIVE,MSTR,CLSK,SDIG,TERA,ANY,"
    "BTCM,GREE,ARBK,TLRY,CGC,ACB,SNDL,CRON,TPB,UVV,BTI,STZ,TAP,BUD,SAM,"
    "DEO,CCEP,COKE,FIZZ,MNST,CELH,KDP,YELP,OPEN,ZG,Z,RDFN,EXPE,TRIP,TNL,"
    "HLT,H,WH,CHH,IHRT,CZR,WYNN,LVS,RSI,GAN,BALY,CHDN"
)

st.subheader("Scan Configuration Loop")
watch_input = st.text_area("Active Ticker Pool:", value=DEFAULT_500_POOL, height=200)

# Parse inputs into a robust list format
watchlist = [ticker.strip().upper() for ticker in watch_input.split(",") if ticker.strip()]

if st.button("Run Live 500-Ticker Mass Scan", use_container_width=True):
    st.info(f"Initiating institutional scan across {len(watchlist)} targets...")
    breakout_detected = False
   
    # 1. DATE BOUNDARIES FOR HISTORICAL ANALYSIS
    # Look back 400 calendar days to guarantee we easily cover 200 trading days
    end_date = datetime.date.today().isoformat()
    start_date = (datetime.date.today() - datetime.timedelta(days=400)).isoformat()
               
    # 2. BATCH SLICER ENGINE
    BATCH_SIZE = 50
    total_tickers = len(watchlist)
    progress_bar = st.progress(0)
   
    for i in range(0, total_tickers, BATCH_SIZE):
        batch = watchlist[i:i + BATCH_SIZE]
        ticker_string = ",".join(batch)
       
        # UI Progress Update
        progress_percentage = int((i / total_tickers) * 100)
        progress_bar.progress(progress_percentage)
       
        # 3. HIGH-SPEED SINGLE-SYMBOL LOOP ENGINE (Failsafe Individual Checks)
        for symbol in batch:
            try:
                # --- SNAPSHOT STAGE (Adding &feed=iex) ---
                snapshot_url = f"{DATA_URL}/stocks/{symbol}/snapshot?feed=iex"
                snapshot_res = requests.get(snapshot_url, headers=headers)
                if snapshot_res.status_code != 200:
                    continue
                   
                stock_data = snapshot_res.json()
                latest_quote = stock_data.get('latestQuote', {})
                live_price = latest_quote.get('ap', 0)     # Current Ask Price
                bid_price = latest_quote.get('bp', 0)      # Current Bid Price
                today_vol = stock_data.get('dailyBar', {}).get('v', 0)

                # Pull the actual last recorded executed trade price, not an empty bid/ask quote order
                # latest_trade = stock_data.get('latestTrade', {})
                # live_price = latest_trade.get('p', 0)      # 'p' is the actual last traded print price
                
                # # Fallback to daily bar close if no live trade print exists yet
                # if live_price <= 0:
                #     live_price = stock_data.get('dailyBar', {}).get('c', 0)
                
                # today_vol = stock_data.get('dailyBar', {}).get('v', 0)

                # Guardrail against dead tickers or zero volume anomalies
                if live_price <= 0 or bid_price <= 0:
                    continue
               
                # --- HISTORICAL BARS STAGE (Forcing &feed=iex to override subscription bounds) ---
                hist_url = f"{DATA_URL}/stocks/{symbol}/bars?timeframe=1Day&start={start_date}&end={end_date}&limit=1000&feed=iex"
                hist_res = requests.get(hist_url, headers=headers)
                if hist_res.status_code != 200:
                    continue
               
                bars = hist_res.json().get('bars', [])
                if len(bars) < 200:
                    continue # Skip newly listed assets lacking a complete 200-day average trendline
               
                # --- MATHEMATICAL CALCULATIONS ---
                df = pd.DataFrame(bars)
                df['200_SMA'] = df['c'].rolling(window=200).mean()
               
                sma_200 = df['200_SMA'].iloc[-1]
                avg_20_vol = df['v'].tail(20).mean()
               
                # --- STRATEGIC MOMENTUM CRITERIA ---
                is_above_200_sma = live_price > sma_200
                is_rallying = live_price >= (bid_price * 0.999)
                #has_huge_volume = True # Always passes or compare to daily opening price
               
                # --- DISCOVERY LOGIC ---
                if is_above_200_sma and is_rallying and has_huge_volume:
                    breakout_detected = True
                    volume_ratio = today_vol / avg_20_vol
                    
                    st.success(
                        f"**INSTITUTIONAL BREAKOUT IDENTIFIED: {symbol}**\n\n"
                        f"* **Live Price:** ${live_price:.2f} (Above 200-SMA of ${sma_200:.2f})\n"
                        f"* **Volume Surge:** {volume_ratio:.2f}x average daily institutional baseline.\n"
                        f"Action: Review setup on Trading 212.*"
                    )
            except Exception as single_ticker_error:
                continue # Isolates faults so one bad symbol doesn't stall the loop
       
        # Rate-limit safety bumper
        time.sleep(0.4)
           
    progress_bar.progress(100)
   
    if not breakout_detected:
        st.warning("Scan complete. No stock currently matches the filtering criteria.")
