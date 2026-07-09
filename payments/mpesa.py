import base64
import json
import logging
from datetime import datetime

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_timestamp():
    return datetime.now().strftime('%Y%m%d%H%M%S')


def generate_password(shortcode, passkey, timestamp):
    data = shortcode + passkey + timestamp
    return base64.b64encode(data.encode()).decode()


def get_access_token():
    url = settings.MPESA_AUTH_URL
    key = settings.MPESA_CONSUMER_KEY
    secret = settings.MPESA_CONSUMER_SECRET
    auth = base64.b64encode(f'{key}:{secret}'.encode()).decode()
    headers = {'Authorization': f'Basic {auth}'}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()['access_token']


def stk_push(phone, amount, account_ref, callback_url):
    token = get_access_token()
    timestamp = generate_timestamp()
    password = generate_password(
        settings.MPESA_SHORTCODE, settings.MPESA_PASSKEY, timestamp
    )

    payload = {
        'BusinessShortCode': settings.MPESA_SHORTCODE,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': int(amount),
        'PartyA': phone,
        'PartyB': settings.MPESA_SHORTCODE,
        'PhoneNumber': phone,
        'CallBackURL': callback_url,
        'AccountReference': account_ref[:12],
        'TransactionDesc': f'Payment for {account_ref}',
    }

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    logger.info(f'STK push payload: {json.dumps(payload)}')
    r = requests.post(
        settings.MPESA_STK_URL, json=payload, headers=headers, timeout=30
    )

    try:
        resp = r.json()
    except Exception:
        resp = {'raw': r.text}

    logger.error(f'STK push response ({r.status_code}): {json.dumps(resp)}')

    if r.status_code != 200:
        error_msg = resp.get('errorMessage', resp.get('errorCode', r.text))
        raise RuntimeError(f'M-Pesa API error ({r.status_code}): {error_msg}')

    return resp


def query_status(checkout_request_id):
    token = get_access_token()
    timestamp = generate_timestamp()
    password = generate_password(
        settings.MPESA_SHORTCODE, settings.MPESA_PASSKEY, timestamp
    )

    payload = {
        'BusinessShortCode': settings.MPESA_SHORTCODE,
        'Password': password,
        'Timestamp': timestamp,
        'CheckoutRequestID': checkout_request_id,
    }

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    r = requests.post(
        settings.MPESA_QUERY_URL, json=payload, headers=headers, timeout=15
    )
    r.raise_for_status()
    return r.json()
