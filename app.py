import streamlit as st
import pandas as pd
import requests
import datetime

st.set_page_config(page_title="Momentum Radar", page_icon="📡", layout="centered")
st.title("📡 Momentum Breakout Radar")
st.write("Pure identification engine. No trading, no noise.")

# --- USER CREDENTIALS ---
st.sidebar.header("🔑 API Connection Settings")
ALPACA_API_KEY = st.sidebar.text_input("Alpaca API Key", type="password", value="https://paper-api.alpaca.markets/v2")
ALPACA_SECRET_KEY = st.sidebar.text_input("Alpaca Secret Key", type="password", value="PK5EJCWF5I262C7RFZBAWOW5UY")
DATA_URL = "https://data.alpaca.markets/v2"

headers = {
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
    "Content-Type": "application/json"
}

# --- THE IDENTIFICATION ENGINE ---
st.subheader("🔍 Scan Watchlist for Buy Signals")
watch_input = st.text_input("Watchlist tickers:", "AAPL,TSLA,NVDA,AMD,MSFT,AMZN,META")
watchlist = [ticker.strip().upper() for ticker in watch_input.split(",") if ticker.strip()]

if st.button("🚀 Run Live Breakout Scan", use_container_width=True):
    st.info("Scanning history and live volume...")
    breakout_detected = False
    
    # Dates for 200-day baseline calculation
    end_date = datetime.date.today().isoformat()
    start_date = (datetime.date.today() - datetime.timedelta(days=300)).isoformat()

    for symbol in watchlist:
        try:
            # 1. Fetch History for 200 SMA and Average Volume
            hist_res = requests.get(f"{DATA_URL}/stocks/{symbol}/bars?timeframe=1Day&start={start_date}&end={end_date}&limit=1000", headers=headers)
            if hist_res.status_code != 200: continue
            
            bars = hist_res.json().get('bars', [])
            if len(bars) < 200: continue
            
            df = pd.DataFrame(bars)
            df['200_SMA'] = df['c'].rolling(window=200).mean()
            
            sma_200 = df['200_SMA'].iloc[-1]
            avg_20_vol = df['v'].tail(20).mean()
            
            # 2. Fetch Live Price & Today's Volume
            quote_res = requests.get(f"{DATA_URL}/stocks/{symbol}/quotes/latest", headers=headers)
            snapshot_res = requests.get(f"{DATA_URL}/stocks/snapshots?symbols={symbol}", headers=headers)
            
            if quote_res.status_code == 200 and snapshot_res.status_code == 200:
                live_price = quote_res.json().get('quote', {}).get('ap', 0)
                today_vol = snapshot_res.json().get('snapshots', {}).get(symbol, {}).get('dailyBar', {}).get('v', 0)
                
                # 3. Strict Signal Conditions
                is_above_200_sma = live_price > sma_200
                is_rallying = live_price > (quote_res.json().get('quote', {}).get('bp', 0) * 0.999)
                has_huge_volume = today_vol > (avg_20_vol * 1.5)
                
                # 4. Print the Potential Buy Match
                if is_above_200_sma and is_rallying and has_huge_volume:
                    breakout_detected = True
                    st.toast(f"🚨 BUY SIGNAL: {symbol}!", icon="🔥")
                    st.success(
                        f"🎯 **POTENTIAL BUY IDENTIFIED: {symbol}**\n\n"
                        f"* **Live Price:** ${live_price:.2f} (Bullish: Above 200-MA of ${sma_200:.2f} ✓)\n"
                        f"* **Volume Surge:** {(today_vol/avg_20_vol):.1f}x normal institutional volume ✓\n\n"
                        f"👉 *Action: Open Trading 212 and manage your manual entry.*"
                    )
        except:
            continue
            
    if not breakout_detected:
        st.write("Scan complete. No stocks currently fit the strict breakout criteria.")