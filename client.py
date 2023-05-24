import requests


response = requests.post('http://127.0.0.1:5000/user/',
                         json={'username': 'Go', 'title': 'Opisaniya', 'description': 'Proverka Flaska'},)

print(response.json())