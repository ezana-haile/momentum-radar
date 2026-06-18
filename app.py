import streamlit as st
import pandas as pd
import requests
import datetime
import time

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Momentum Radar", page_icon="??", layout="centered")
st.title("?? 500-Ticker Breakout Radar")
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

# --- THE COMPREHENSIVE 500-STOCK WATCHLIST ---
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

st.subheader("?? Scan Configuration Loop")
watch_input = st.text_area("Active Ticker Pool:", value=DEFAULT_500_POOL, height=200)

# Parse inputs into a robust list format
watchlist = [ticker.strip().upper() for ticker in watch_input.split(",") if ticker.strip()]

if st.button("?? Run Live 500-Ticker Mass Scan", use_container_width=True):
    st.info(f"Initiating institutional scan across {len(watchlist)} targets...")
    breakout_detected = False
   
    # 1. DATE BOUNDARIES FOR HISTORICAL ANALYSIS
    # Look back 365 calendar days to guarantee we cover 200 trading days for the SMA
    end_date = datetime.date.today().isoformat()
    start_date = (datetime.date.today() - datetime.timedelta(days=365)).isoformat()
               
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
       
        # try:
        #     # 3. HIGH-SPEED BULK SNAPSHOT REQUEST
        #     snapshot_url = f"{DATA_URL}/stocks/snapshots?symbols={ticker_string}"
        #     snapshot_res = requests.get(snapshot_url, headers=headers)
            
        #     if snapshot_res.status_code != 200:
        #         continue
        try:
            # 3. INDIVIDUAL LOOP ENGINE (Matches your working test script format)
            for symbol in batch:
                snapshot_url = f"{DATA_URL}/stocks/{symbol}/snapshot"
                snapshot_res = requests.get(snapshot_url, headers=headers)
                
                if snapshot_res.status_code != 200:
                    continue
                   
                stock_data = snapshot_res.json()       
                snapshots = snapshot_res.json().get('snapshots', {})
           
            # 4. INDIVIDUAL SYMBOL ANALYSIS LOOP
            for symbol in batch:
                #if symbol not in snapshots or snapshots[symbol] is None:
                  #  continue
               
                try:
                    stock_data = snapshots[symbol]
                    latest_quote = stock_data.get('latestQuote', {})
                    live_price = latest_quote.get('ap', 0)     # Current Ask Price
                    bid_price = latest_quote.get('bp', 0)      # Current Bid Price
                    today_vol = stock_data.get('dailyBar', {}).get('v', 0)

                    # Guardrail against dead tickers or pre-open zeroes
                    if live_price <= 0 or bid_price <= 0:
                        continue
                   
                    # 5. HISTORICAL BARS ENDPOINT
                    hist_url = f"{DATA_URL}/stocks/{symbol}/bars?timeframe=1Day&start={start_date}&end={end_date}&limit=1000"
                    hist_res = requests.get(hist_url, headers=headers)
                    if hist_res.status_code != 200:
                        continue
                   
                    bars = hist_res.json().get('bars', [])
                    if len(bars) < 200:
                        continue # Safely skip newly listed tickers lacking a 200-day trend history
                   
                    # 6. MATHEMATICAL CALCULATIONS
                    df = pd.DataFrame(bars)
                    df['200_SMA'] = df['c'].rolling(window=200).mean()
                   
                    sma_200 = df['200_SMA'].iloc[-1]
                    avg_20_vol = df['v'].tail(20).mean()
                   
                    # 7. ORIGINAL STRATEGIC MOMENTUM CRITERIA
                    is_above_200_sma = live_price > sma_200
                    is_rallying = live_price >= (bid_price * 0.999)
                    has_huge_volume = today_vol > (avg_20_vol * 1.5)
                   
                    # 8. MATCH DISCOVERY DISPLAY LOGIC
                    if is_above_200_sma and is_rallying and has_huge_volume:
                        breakout_detected = True
                        volume_ratio = today_vol / avg_20_vol
                        
                        st.success(
                            f"?? **INSTITUTIONAL BREAKOUT IDENTIFIED: {symbol}**\n\n"
                            f"* **Live Price:** ${live_price:.2f} (Above 200-SMA of ${sma_200:.2f})\n"
                            f"* **Volume Surge:** {volume_ratio:.2f}x average daily institutional baseline.\n"
                            f"?? *Action: Review setup on Trading 212.*"
                        )
                except Exception as single_ticker_error:
                    continue # Isolates errors to the specific ticker without losing the whole batch
           
            # Rate-limit safety bumper
            time.sleep(0.4)
           
        except Exception as batch_error:
            continue
           
    progress_bar.progress(100)
   
    if not breakout_detected:
        st.warning("Scan complete. No stock currently matches the filtering criteria.")
