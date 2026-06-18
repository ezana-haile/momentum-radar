import requests 
import streamlit as st 
# 1. PASTE YOUR EXACT KEYS HERE 
ALPACA_API_KEY = "PKV7X5UXF3FVVIXXCW6MGJFENQ" 
ALPACA_SECRET_KEY = "3vB8arzD18nTJvgULhCBRoda5FnoAzQspj9RhfdpMbxh" 
DATA_URL = "https://data.alpaca.markets/v2" 

st.title("🔌 Alpaca Connection Tester") 
st.write("Attempting to connect to Alpaca servers...") 

headers = { 
    "Khronos-Id": "community", 
    "APCA-API-KEY-ID": ALPACA_API_KEY.strip(), 
    "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY.strip()
} 

# 2. RUN A SINGLE TICKER TEST (NVDA) 
try: 
    test_url = f"{DATA_URL}/stocks/snapshots?symbols=NVDA" 
    response = requests.get(test_url, headers=headers) 
    
    st.write(f"📡 Server Status Code: `{response.status_code}`") 
    
    if response.status_code == 200: 
        data = response.json() 
        st.success("✅ SUCCESS! Your API keys and URL connection are working perfectly.") 
        st.json(data) # This will print the raw data on your screen 
    elif response.status_code == 401: 
        st.error("❌ AUTHENTICATION FAILED: Your API Key or Secret Key is incorrect or invalid.") 
    else: st.error(f"❌ SERVER ERROR: Received unexpected response. Raw output: {response.text}") 
        
except Exception as e: 
    st.error(f"💥 CRITICAL CODE ERROR: {str(e)}")
