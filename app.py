import streamlit as st
import pandas as pd
import requests
import datetime
import time

st.set_page_config(page_title="Broad Market Radar", page_icon="📡", layout="centered")
st.title("📡 Momentum Radar")
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
"NVDA"
)

st.subheader("📋 Scan Global Momentum Pool")
watch_input = st.text_area("Active Scanning Pool (500 Curated Tickers Loaded):", value=DEFAULT_500_POOL, height=200)

watchlist = [ticker.strip().upper() for ticker in watch_input.split(",") if ticker.strip()]
if st.button("🚀 Run Live 500-Ticker Mass Scan", use_container_width=True):
    st.info(f"Initiating scan across {len(watchlist)} assets...")
    breakout_detected = False
   
    # Clean keys exactly like the successful test code
    clean_headers = {
        "APCA-API-KEY-ID": ALPACA_API_KEY.strip(),
        "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY.strip()
    }
   
    BATCH_SIZE = 50
    total_tickers = len(watchlist)
    progress_bar = st.progress(0)
   
    for i in range(0, total_tickers, BATCH_SIZE):
        batch = watchlist[i:i + BATCH_SIZE]
        ticker_string = ",".join(batch)
       
        progress_percentage = int((i / total_tickers) * 100)
        progress_bar.progress(progress_percentage)
       
        # 1. FETCH SNAPSHOTS
        test_url = f"{DATA_URL}/stocks/snapshots?symbols={ticker_string}"
        snapshot_res = requests.get(test_url, headers=clean_headers)
        
        if snapshot_res.status_code != 200:
            st.error(f"⚠️ API Error on batch {i}: Status Code {snapshot_res.status_code}")
            continue
           
        snapshots = snapshot_res.json().get('snapshots', {})
       
        # 2. EVALUATE TICKERS
        for symbol in batch:
            # If Alpaca returns no data for this ticker right now, show it explicitly
            if symbol not in snapshots or snapshots[symbol] is None:
                st.write(f"⚪ {symbol}: No active pre-market data on feed.")
                continue
           
            # Force print whatever data exists, bypass all filters
            stock_data = snapshots[symbol]
            latest_quote = stock_data.get('latestQuote', {})
            live_price = latest_quote.get('ap', 0)
            
            breakout_detected = True
            st.success(f"🟢 FOUND DATA FOR {symbol} | Live Price: ${live_price}")
       
        time.sleep(0.4)
           
    progress_bar.progress(100)
   
    if not breakout_detected:
        st.warning("Scan finished. No tickers returned valid data from the server.")
# if st.button("🚀 Run Live 500-Ticker Mass Scan", use_container_width=True):
#     st.info(f"Initiating batch-sliced scan across {len(watchlist)} assets...")
#     breakout_detected = False
   
#     end_date = datetime.date.today().isoformat()
#     start_date = (datetime.date.today() - datetime.timedelta(days=40)).isoformat()
               
#     BATCH_SIZE = 50
#     total_tickers = len(watchlist)
   
#     progress_bar = st.progress(0)
   
#     for i in range(0, total_tickers, BATCH_SIZE):
#         batch = watchlist[i:i + BATCH_SIZE]
#         ticker_string = ",".join(batch)
       
#         progress_percentage = int((i / total_tickers) * 100)
#         progress_bar.progress(progress_percentage)
       
#         try:
#             # 3. BULK SNAPSHOT REQUEST
#             snapshot_res = requests.get(f"{DATA_URL}/stocks/snapshots?symbols={ticker_string}", headers=headers)
#             if snapshot_res.status_code != 200:
#                 continue
               
#             snapshots = snapshot_res.json().get('snapshots', {})
           
#             for symbol in batch:
#                 if symbol not in snapshots or snapshots[symbol] is None:
#                     continue
               
#                 try:
#                     stock_data = snapshots[symbol]
#                     latest_quote = stock_data.get('latestQuote', {})
#                     live_price = latest_quote.get('ap', 0)   
#                     bid_price = latest_quote.get('bp', 0)    
#                     today_vol = stock_data.get('dailyBar', {}).get('v', 0)

#                     if live_price <= 0:
#                         continue
                   
#                     # 4. HISTORY ENDPOINT CALL
#                     # hist_res = requests.get(f"{DATA_URL}/stocks/{symbol}/bars?timeframe=1Day&start={start_date}&end={end_date}&limit=100", headers=headers)
#                     # if hist_res.status_code != 200:
#                     #     continue
                   
#                     # bars = hist_res.json().get('bars', [])
#                     # if len(bars) < 10: # Spaced down safely to verify the 10-period window
#                     #     continue
                   
#                     # df = pd.DataFrame(bars)
#                     # df['10_SMA'] = df['c'].rolling(window=10).mean()
                   
#                     sma_10 = 1.0 #df['10_SMA'].iloc[-1]
#                     avg_20_vol = 1.0 # df['v'].tail(20).mean()
                   
#                     # 5. CONSTRAINTS (Adjust filters back to strict targets during open hours)
#                     # is_above_sma = live_price > sma_10
#                     # is_rallying = True 
#                     # has_huge_volume = True 
                   
#                     # if is_above_sma and is_rallying and has_huge_volume:
#                     if True:
#                         breakout_detected = True
#                         st.success(
#                             f"🟢 **BUY TARGET IDENTIFIED: {symbol}**\n\n"
#                             f"* **Live Price:** ${live_price:.2f}\n"
#                             f"* **IEX Volume Status:** Tracked and online.\n"
#                         )
#                         breakout_detected = True
#                         st.success(
#                             f"🟢 **BUY TARGET IDENTIFIED: {symbol}**\n\n"
#                             f"* **Live Price:** ${live_price:.2f} (MA-10 baseline: ${sma_10:.2f})\n"
#                             f"* **IEX Volume:** {today_vol:,} shares tracked.\n"
#                         )
#                 except Exception as ticker_error:
#                     continue # Skips a single bad asset (like formatting bugs) instead of ruining the whole batch
           
#             time.sleep(0.4) # Rates-compliance pause
           
#         except Exception as batch_error:
#             continue
           
#     progress_bar.progress(100)
   
#     if not breakout_detected:
#         st.warning("Scan complete. No stock currently matches the filtering criteria.")
