import requests

host_session = "http://127.0.0.1:8090/is_session_valid"
host_login = "http://127.0.0.1:8090/login"
data = {'username': 'x@gmail.com',
        'password': 'x'}

request = requests.post(host_login, json=data)
print(request.text, request.status_code)

#header = {'username': 'bionlukbionluk400@gmail.com'}
#req = requests.get(host, params=header)
#print(req.text)
#print(req.status_code)
