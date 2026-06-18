import streamlit as st
import pandas as pd
import requests
import datetime
import time

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Debug Radar", page_icon="🪲", layout="centered")
st.title("🪲 Diagnostic Momentum Radar")
st.write("Equipped with deep terminal logging to identify structural pipeline blocks.")

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

# --- THE WATCHLIST (For testing, use a small set so we don't spam the log) ---
DEFAULT_500_POOL = "AAPL,TSLA,NVDA,AMD,MSFT"

st.subheader("📋 Debug Scanning Pool")
watch_input = st.text_area("Testing Pool (Shortened for clear log viewing):", value=DEFAULT_500_POOL, height=100)
watchlist = [ticker.strip().upper() for ticker in watch_input.split(",") if ticker.strip()]

if st.button("🚀 Run Diagnostic Mass Scan", use_container_width=True):
    st.info(f"Checking {len(watchlist)} assets...")
    st.markdown("---")
    breakout_detected = False
   
    # Setup Lookback
    end_date = datetime.date.today().isoformat()
    start_date = (datetime.date.today() - datetime.timedelta(days=365)).isoformat()
               
    for symbol in watchlist:
        st.markdown(f"### 🔍 Testing Pipeline for: **{symbol}**")
        
        # ----------------------------------------------------
        # STEP 1: TEST SNAPSHOT PIPELINE
        # ----------------------------------------------------
        snapshot_url = f"{DATA_URL}/stocks/{symbol}/snapshot"
        st.write(f"ℹ️ *Step 1: Requesting snapshot via:* `{snapshot_url}`")
        
        try:
            snapshot_res = requests.get(snapshot_url, headers=headers)
            st.write(f"📡 Snapshot Server Status Code: `{snapshot_res.status_code}`")
            
            if snapshot_res.status_code != 200:
                st.error(f"❌ Step 1 Failed: Server rejected request. Raw body: {snapshot_res.text}")
                continue
                
            stock_data = snapshot_res.json()
            latest_quote = stock_data.get('latestQuote', {})
            live_price = latest_quote.get('ap', 0)     
            bid_price = latest_quote.get('bp', 0)      
            today_vol = stock_data.get('dailyBar', {}).get('v', 0)
            
            st.write(f"📊 Values parsed -> Ask: `${live_price}`, Bid: `${bid_price}`, Today's Vol: `{today_vol}`")
            
            if live_price <= 0 or bid_price <= 0:
                st.warning(f"⚠️ Step 1 Block: Price is zero or empty. Market feed could be dead.")
                continue
                
            st.success("✅ Step 1 Passed: Snapshot data validated.")
            
        except Exception as e:
            st.error(f"💥 Step 1 Crash: Code blew up while reading snapshot: {str(e)}")
            continue

        # ----------------------------------------------------
        # STEP 2: TEST HISTORICAL PIPELINE
        # ----------------------------------------------------
        hist_url = f"{DATA_URL}/stocks/{symbol}/bars?timeframe=1Day&start={start_date}&end={end_date}&limit=1000"
        st.write(f"ℹ️ *Step 2: Requesting historical bars via:* `{hist_url}`")
        
        try:
            hist_res = requests.get(hist_url, headers=headers)
            st.write(f"📡 History Server Status Code: `{hist_res.status_code}`")
            
            if hist_res.status_code != 200:
                st.error(f"❌ Step 2 Failed: Server rejected historical bars. Raw body: {hist_res.text}")
                continue
                
            bars = hist_res.json().get('bars', [])
            st.write(f"📊 Total daily bars returned by server: `{len(bars)}`")
            
            if len(bars) < 200:
                st.warning(f"⚠️ Step 2 Block: Not enough history to compute a 200 SMA (`{len(bars)}/200`).")
                continue
                
            st.success("✅ Step 2 Passed: Historical charts validated.")
            
        except Exception as e:
            st.error(f"💥 Step 2 Crash: Code blew up while reading bars: {str(e)}")
            continue

        # ----------------------------------------------------
        # STEP 3: TEST MATHEMATICS & FILTER LOGIC
        # ----------------------------------------------------
        try:
            st.write("ℹ️ *Step 3: Calculating Moving Averages and Volume Spikes...*")
            df = pd.DataFrame(bars)
            df['200_SMA'] = df['c'].rolling(window=200).mean()
           
            sma_200 = df['200_SMA'].iloc[-1]
            avg_20_vol = df['v'].tail(20).mean()
           
            is_above_200_sma = live_price > sma_200
            is_rallying = live_price >= (bid_price * 0.999)
            has_huge_volume = today_vol > (avg_20_vol * 1.5)
            
            st.write(f"🧐 Math Check:")
            st.write(f"* Is Price (${live_price}) > 200-SMA (${sma_200:.2f})? -> **{is_above_200_sma}**")
            st.write(f"* Is Price close to Bid (${bid_price})? -> **{is_rallying}**")
            st.write(f"* Is Today's Vol ({today_vol}) > 1.5x Avg Vol ({avg_20_vol:.0f})? -> **{has_huge_volume}**")
           
            if is_above_200_sma and is_rallying and has_huge_volume:
                breakout_detected = True
                st.balloons()
                st.success(f"🎯 **MATCH FOUND FOR {symbol}!**")
            else:
                st.info("ℹ️ Step 3 Complete: Stock is online but didn't pass all momentum rules.")
                
        except Exception as e:
            st.error(f"💥 Step 3 Crash: Code blew up inside math section: {str(e)}")
            
        st.markdown("---")
        time.sleep(0.5) # Anti-throttle break
        
    if not breakout_detected:
        st.warning("All diagnostics complete. No technical breakout target discovered in this specific pool.")
