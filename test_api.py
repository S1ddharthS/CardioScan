import requests
import json

url = 'http://127.0.0.1:5000/predict'
data = {'age': '68', 'sex': '1', 'cp': '1', 'trestbps': '166', 'chol': '330', 'fbs': '0', 'restecg': '1', 'thalach': '141', 'exang': '1', 'oldpeak': '2.7', 'slope': '0', 'ca': '2', 'thal': '3'}

print("Sending High Risk Profile...")
response = requests.post(url, data=data)
print("Server Result:", response.json())
