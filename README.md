# Cryptocurrency Price Fetcher API

## Overview
The Cryptocurrency Price Fetcher API is a Flask-based service that retrieves current cryptocurrency prices using the CoinGecko API. This service can be deployed on cloud platforms like Google Cloud Run and is ideal for integration into various projects requiring real-time cryptocurrency price data.

## Features
- Fetches real-time cryptocurrency prices from CoinGecko.
- Implements caching to reduce API calls and improve performance.
- Includes a retry mechanism for failed fetch attempts.
- Secures access with API key authentication.
- Supports multiple cryptocurrency queries in a single request.

## Prerequisites
- Python 3.7+
- Docker
- A Docker Hub account
- Google Cloud account (for Google Cloud Run deployment)

## Setup

### Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configure API Keys
Create an `api_keys.json` file in the project root:
```json
{
  "key1": "your_api_key_1",
  "key2": "your_api_key_2"
}
```

### Build and Push Docker Image
```bash
docker build -t crypto-price-fetcher .
docker tag crypto-price-fetcher <your-dockerhub-username>/crypto_price_fetcher:latest
docker push <your-dockerhub-username>/crypto_price_fetcher:latest
```

### Deploy to Google Cloud Run
1. Ensure you have the Google Cloud SDK installed and configured.
2. Deploy the container:
```bash
gcloud run deploy --image <your-dockerhub-username>/crypto_price_fetcher:latest --platform managed
```

## Usage

### API Endpoint
`POST /prices`

### Headers
- `Content-Type: application/json`
- `X-API-Key: your-api-key`

### Request Body
```json
{
  "cryptos": ["bitcoin", "ethereum", "dogecoin"]
}
```

### Response
```json
{
  "bitcoin": {"price": 50000.25, "source": "cache"},
  "ethereum": {"price": 3000.80, "source": "coingecko"},
  "dogecoin": {"price": 0.25, "source": "coingecko"}
}
```

## Configuration
- `CACHE_FILE`: Set the path for the cache file (default: 'crypto_cache.json')
- `API_KEYS_FILE`: Set the path for the API keys file (default: 'api_keys.json')
- Caching duration: Modify `max_age` in the `is_cache_valid` function (default: 5 minutes)
- Retry interval: Adjust the `should_retry` function (default: 1 hour)
- Cache update interval: Change the `sleep` duration in the `update_cache` function (default: 5 minutes)

## Error Handling
- Invalid API key: Returns a 401 Unauthorized error
- Missing or invalid request body: Returns a 400 Bad Request error
- Failed to fetch cryptocurrency price: Returns an error message in the response for the specific cryptocurrency

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
