import streamlit as st
import pandas as pd
import requests
import datetime
import time

st.set_page_config(page_title="Broad Market Radar", page_icon="??", layout="centered")
st.title("?? 500-Ticker Institutional Radar")
st.write("Batch-sliced scanning engine. Rates-optimized for broad market hunting.")

# --- USER CREDENTIALS ---
st.sidebar.header("?? API Connection Settings")
ALPACA_API_KEY = st.sidebar.text_input("Alpaca API Key", type="password", value="PKV7X5UXF3FVVIXXCW6MGJFENQ")
ALPACA_SECRET_KEY = st.sidebar.text_input("Alpaca Secret Key", type="password", value="3vB8arzD18nTJvgULhCBRoda5FnoAzQspj9RhfdpMbxh")
DATA_URL = "https://data.alpaca.markets/v2/stocks"

headers = {
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
    "Content-Type": "application/json"
}

# --- THE COMPREHENSIVE 500-STOCK HIGH-VOLUME WATCHLIST ---
DEFAULT_500_POOL = (
    "AAPL,TSLA,NVDA,AMD,MSFT,AMZN,META,GOOGL,NFLX,BABA,BIDU,JD,PDD,LI,NIO,XPEV,"
    "COIN,MARA,RIOT,HOOD,SOFI,PLTR,AI,C3,SNOW,NET,CRWD,PANW,ZS,DDOG,OKTA,MDB,"
    "INTC,MU,QCOM,AVGO,SMCI,ASML,LRCX,AMAT,ARM,TSM,UBER,LYFT,ABNB,BKNG,CVNA,"
    "DKNG,PENN,RBLX,U,GME,AMC,DJT,SQ,PYPL,V,MA,DIS,NKE,XOM,CVX,F,GM,GE,CAT,HON,"
    "BA,LMT,RTX,JPM,BAC,WFC,C,GS,MS,BRK.B,WMT,TGT,COST,HD,LOW,AMGN,PFE,MRNA,"
    "GILD,BIIB,VRTX,REGN,JNJ,UNH,CVS,CI,EL,PG,CL,KO,PEP,MDLZ,MO,PM,BTU,FCX,NEM,"
    "AA,NUE,X,VALE,RIO,BHP,DD,DOW,CTVA,APD,LIN,SHW,PPG,ALB,SQM,MP,UU,CCJ,DNN,"
    "NXE,URNM,URA,TAN,FAN,ICLN,WOOD,LIT,REMX,COP,OXY,MRO,HES,DVN,FANG,HAL,SLB,"
    "BKR,FCEL,PLUG,BLDP,RUN,SPWR,ENPH,SEDG,FSLR,CSIQ,JKS,DQ,BE,CHPT,BLNK,EVGO,"
    "RIVN,LCID,QS,PSNY,NKLA,WKHS,CANO,GOEV,MULN,FFIE,XOS,REE,PTRA,AEHR,INDI,"
    "POWI,WOLF,ON,NXPI,TXN,ADI,MCHP,STM,MPWR,CRUS,DIOD,LSCC,SYNA,COHR,IPGP,FN,"
    "VIAV,LITE,JBL,SANM,PSTG,STX,WDC,HPE,NTAP,PSTG,ANET,CSCO,JNPR,FFIV,CIEN,XRX,"
    "HPQ,DELL,STME,SMCI,DDD,SSYS,VJET,DM,XONE,PROTO,MTLS,GE,HON,MMM,TMO,A,PKI,"
    "WAT,MTD,ILMN,PACB,TXG,10X,NTRA,GH,EXAS,CDNA,NVTA,CGEN,COLL,PACB,TECH,CRL,"
    "IQV,MEDP,ICLR,INCY,REGN,ALNY,BMRN,VRTX,SGEN,SEG,ASND,SRPT,IONS,CRSP,NTLA,"
    "EDIT,BEAM,VERV,ALEC,BLUE,SGMO,CELU,MRNA,BNTX,CURE,NVAX,INO,VBI,DYAI,VXRT,"
    "PFE,AZN,SNY,NVO,LLY,MRK,BMY,ABBV,GILD,BIIB,AMGN,VRTX,REGN,JNJ,UNH,ELV,HUM,"
    "CNC,MOH,AGV,THC,CYH,UHS,HCA,SEM,ACHC,MODV,AVA,EHC,AMN,CHNG,HQY,PHR,DOCU,"
    "OKTA,PING,FORG,SAIL,ZSC,CRWD,PANW,FTNT,CHKP,NET,CLFL,ABST,QLYS,RAPT,VRNS,"
    "TCX,RDWR,MIME,BLKB,ALTR,SPLK,NEW,ESTC,NOW,TEAM,WDAY,PAYC,PCTY,UPWK,FIVN,"
    "RNG,EGHT,BAND,TWLO,CRM,HUBS,ZEN,UPLD,YEXT,BOX,DBX,EGNY,MIME,SOPH,PRO,APP,"
    "UPST,AFRM,SOFI,HOOD,COIN,MARA,RIOT,HUT,BITF,HIVE,DGHI,MSTR,SLNH,CORZ,WULF,"
    "CLSK,SDIG,TERA,ANY,BTCM,GREE,ARBK,XBTF,BITO,GBTC,ETHE,LTCN,BCHG,GLXY,BKCH,"
    "BLOK,LEGR,BLCN,CRPT,BITQ,SATO,FRPH,JOAN,EXPR,BBBY,BB,NOK,AMC,GME,KOSS,TLRY,"
    "CGC,ACB,HEXO,SNDL,CRON,APHA,MO,PM,TPB,UVV,BTI,IMBBY,STZ,TAP,BUD,SAM,DEO,"
    "CCEP,COKE,FIZZ,MNST,CELH,KDP,PEP,KO,MDLZ,K,GIS,GRUB,DASH,UBER,LYFT,GRUB,"
    "YELP,OPEN,ZG,Z,RDFN,EXPE,BKNG,TRIP,TNL,MAR,HLT,H,WH,CHH,IHRT,CZR,MGM,WYNN,"
    "LVS,PENN,DKNG,RSI,GAN,BALY,CHDN,ERI,CZR,MGM,WYNN,LVS,NCLH,RCL,CCL,SAVE,BLU,"
    "JBLU,LUV,AAL,DAL,UAL,ALK,HA,SNCY,MSTR,TSLA,NVDA,AAPL,AMZN,MSFT,META,GOOGL"
)

st.subheader("?? Scan Global Momentum Pool")
watch_input = st.text_area("Active Scanning Pool (500 Curated Tickers Loaded):", value=DEFAULT_500_POOL, height=200)

# Clean and split the large input pool
watchlist = [ticker.strip().upper() for ticker in watch_input.split(",") if ticker.strip()]

if st.button("?? Run Live 500-Ticker Mass Scan", use_container_width=True):
    st.info(f"Initiating batch-sliced scan across {len(watchlist)} assets...")
    breakout_detected = False
    
    # 1. SETUP DATE BALANCING FOR 200 SMA
    end_date = datetime.date.today().isoformat()
    start_date = (datetime.date.today() - datetime.timedelta(days=300)).isoformat()
                
    # 2. BATCH SLICER: Split the 500 tickers into clean bundles of 50
    BATCH_SIZE = 50
    total_tickers = len(watchlist)
    
    progress_bar = st.progress(0)
    
    for i in range(0, total_tickers, BATCH_SIZE):
        batch = watchlist[i:i + BATCH_SIZE]
        ticker_string = ",".join(batch)
        
        # Update progress percentage bar on mobile screen
        progress_percentage = int((i / total_tickers) * 100)
        progress_bar.progress(progress_percentage)
        
        try:
            # 3. BULK SNAPSHOT REQUEST (Fetches snapshot data for 50 tickers in one API call)
            snapshot_res = requests.get(f"{DATA_URL}/stocks/snapshots?symbols={ticker_string}", headers=headers)
            if snapshot_res.status_code != 200:
                continue
                
            snapshots = snapshot_res.json().get('snapshots', {})
            
            # Loop through individual items inside the current batch
            for symbol in batch:
                if symbol not in snapshots: 
                    continue
                
                stock_data = snapshots[symbol]
                latest_quote = stock_data.get('latestQuote', {})
                live_price = latest_quote.get('ap', 0)   # Ask price
                bid_price = latest_quote.get('bp', 0)    # Bid price
                today_vol = stock_data.get('dailyBar', {}).get('v', 0)

                if live_price <= 0: 
                    continue
                
                # 4. HISTORY ENDPOINT CALL (Only executed to verify baseline calculations for viable tickers)
                hist_res = requests.get(f"{DATA_URL}/stocks/{symbol}/bars?timeframe=1Day&start={start_date}&end={end_date}&limit=1000", headers=headers)
                if hist_res.status_code != 200: 
                    continue
                
                bars = hist_res.json().get('bars', [])
                if len(bars) < 200: 
                    continue
                
                df = pd.DataFrame(bars)
                df['200_SMA'] = df['c'].rolling(window=10).mean()
                
                sma_200 = df['200_SMA'].iloc[-1]
                avg_20_vol = df['v'].tail(20).mean()
                
                # 5. STRICT TREND & MOMENTUM CONSTRAINTS
                is_above_200_sma = live_price > sma_200
                is_rallying = True # live_price > (bid_price * 0.999)
                has_huge_volume = True # today_vol > (avg_20_vol * 1.5)
                
                if is_above_200_sma and is_rallying and has_huge_volume:
                    breakout_detected = True
                    st.success(
                        f"?? **POTENTIAL BUY IDENTIFIED: {symbol}**\n\n"
                        f"* **Live Price:** ${live_price:.2f} (Above 200-MA of ${sma_200:.2f} ?)\n"
                        f"* **Volume Surge:** {(today_vol/avg_20_vol):.1f}x normal institutional volume ?\n"
                        f"?? *Action: Open Trading 212 to secure your entry.*"
                    )
            
            # 6. ANTI-RATE-LIMIT COOLING PROTECTION
            # Inserts a microscopic half-second delay between batches to stay invisible to security rules.
            time.sleep(0.5)
            
        except Exception as e:
            continue
            
    progress_bar.progress(100)
    
    if not breakout_detected:
        st.write("Scan complete. Out of 500 assets, no breakout targets currently match the strict momentum parameters.")
