from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
import json
import os
import time
import threading

app = Flask(__name__)
CORS(app)

CACHE_FILE = 'crypto_cache.json'
API_KEYS_FILE = 'api_keys.json'
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

def load_api_keys():
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    return {}

API_KEYS = list(load_api_keys().values())

def get_crypto_price(crypto_id):
    try:
        response = requests.get(f"{COINGECKO_API_URL}/simple/price?ids={crypto_id}&vs_currencies=usd")
        response.raise_for_status()
        data = response.json()
        return data[crypto_id]['usd']
    except Exception as e:
        print(e, f"Couldn't fetch price for {crypto_id} from CoinGecko.")
        return None

def is_cache_valid(timestamp, max_age=timedelta(minutes=5)):
    return datetime.now() - datetime.fromisoformat(timestamp) < max_age

def should_retry(timestamp):
    return datetime.now() - datetime.fromisoformat(timestamp) > timedelta(hours=1)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, default=str)

def update_cache():
    global cache
    while True:
        current_time = datetime.now()
        for crypto_id in list(cache.keys()):
            if 'error' in cache[crypto_id]:
                if should_retry(cache[crypto_id]['timestamp']):
                    price = get_crypto_price(crypto_id)
                    if price is not None:
                        cache[crypto_id] = {'price': price, 'timestamp': current_time.isoformat()}
                    else:
                        cache[crypto_id] = {'error': 'Unable to fetch price', 'timestamp': current_time.isoformat()}
            else:
                price = get_crypto_price(crypto_id)
                if price is not None:
                    cache[crypto_id] = {'price': price, 'timestamp': current_time.isoformat()}
                else:
                    cache[crypto_id] = {'error': 'Unable to fetch price', 'timestamp': current_time.isoformat()}
        save_cache(cache)
        time.sleep(300)  # Wait for 5 minutes

cache = load_cache()

update_thread = threading.Thread(target=update_cache, daemon=True)
update_thread.start()

@app.route('/prices', methods=['POST'])
def get_prices():
    api_key = request.headers.get('X-API-Key')
    if api_key not in API_KEYS:
        return jsonify({'error': 'Invalid API key'}), 401
    
    data = request.get_json()
    if not data or 'cryptos' not in data:
        return jsonify({'error': 'No cryptocurrencies provided'}), 400
    
    cryptos = data['cryptos']
    if not isinstance(cryptos, list):
        return jsonify({'error': 'Cryptocurrencies must be provided as a list'}), 400
    
    current_time = datetime.now()
    results = {}
    
    for crypto_id in cryptos:
        crypto_id = crypto_id.lower()
        if crypto_id in cache:
            if 'error' in cache[crypto_id]:
                if should_retry(cache[crypto_id]['timestamp']):
                    price = get_crypto_price(crypto_id)
                    if price is not None:
                        cache[crypto_id] = {'price': price, 'timestamp': current_time.isoformat()}
                        results[crypto_id] = {'price': price, 'source': 'coingecko'}
                    else:
                        cache[crypto_id] = {'error': 'Unable to fetch price', 'timestamp': current_time.isoformat()}
                        results[crypto_id] = {'error': 'Unable to fetch price'}
                else:
                    results[crypto_id] = {'error': 'Unable to fetch price', 'cached': True}
            elif is_cache_valid(cache[crypto_id]['timestamp']):
                results[crypto_id] = {'price': cache[crypto_id]['price'], 'source': 'cache'}
            else:
                price = get_crypto_price(crypto_id)
                if price is not None:
                    cache[crypto_id] = {'price': price, 'timestamp': current_time.isoformat()}
                    results[crypto_id] = {'price': price, 'source': 'coingecko'}
                else:
                    cache[crypto_id] = {'error': 'Unable to fetch price', 'timestamp': current_time.isoformat()}
                    results[crypto_id] = {'error': 'Unable to fetch price'}
        else:
            price = get_crypto_price(crypto_id)
            if price is not None:
                cache[crypto_id] = {'price': price, 'timestamp': current_time.isoformat()}
                results[crypto_id] = {'price': price, 'source': 'coingecko'}
            else:
                cache[crypto_id] = {'error': 'Unable to fetch price', 'timestamp': current_time.isoformat()}
                results[crypto_id] = {'error': 'Unable to fetch price'}
    
    save_cache(cache)
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


