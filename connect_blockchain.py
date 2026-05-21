from web3 import Web3

# Connect to Ganache
ganache_url = "http://127.0.0.1:7545"

web3 = Web3(Web3.HTTPProvider(ganache_url))

# Check connection
if web3.is_connected():
    print("✅ Connected to Ganache Blockchain!")
else:
    print("❌ Connection Failed!")