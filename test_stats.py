from app import app as flask_app
import json
with flask_app.test_client() as client:
    resp = client.get('/api/stats')
    print('Status:', resp.status_code)
    try:
        data = resp.get_json()
        print('JSON:', json.dumps(data, indent=2))
    except Exception as e:
        print('Error parsing JSON:', e)
