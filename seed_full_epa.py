import requests

API = 'http://127.0.0.1:8000'

r = requests.post(API + '/marketplace/listings', json={
    'assessment_id': 6,
    'dataset_name': 'EPA Air Quality Monitor — Oklahoma & Kansas 2025-2026',
    'description': 'Comprehensive daily air quality measurements across 8 EPA monitoring stations in Oklahoma City, Tulsa, Wichita, and Topeka. 25,296 records covering all of 2025 through June 2026. Six pollutants: PM2.5, PM10, Ozone, NO2, SO2, and CO. Includes AQI values, NAAQS compliance flags, and GPS coordinates for each station. FORGE Gold certified. The most complete regional air quality dataset available for the Oklahoma-Kansas corridor.',
    'price_per_call': 0.002,
    'price_monthly': 45.0,
    'price_annual': 450.0,
    'currency': 'CSPR',
    'data_file_path': 'data/epa_air_quality_ok_ks_2025_2026.csv',
    'tags': 'air-quality,EPA,Oklahoma,Kansas,environment,public-health,PM2.5,ozone,NAAQS',
    'row_count': 25296,
    'file_size_mb': 4.0,
    'seller_user_id': 'USR-98C9B6DF',
    'seller_name': 'Paula Ditallo'
})
print(r.json())

# Also have Dr. Sarah Chen and Marcus Webb purchase it
purchases = [
    ('BUYER-7C096FA7', 'sarah-full-epa-1'),
    ('BUYER-EE958DA2', 'marcus-full-epa-1'),
]

listing_id = r.json().get('listing_id')
for buyer_id, proof in purchases:
    r2 = requests.get(
        API + '/marketplace/data/' + str(listing_id),
        params={'buyer_id': buyer_id, 'payment_proof': proof}
    )
    data = r2.json()
    print(f'{buyer_id}: {data.get("api_import_id")} — {data.get("records_delivered")} records')
