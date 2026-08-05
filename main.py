import requests

YOUR_API_KEY = input("Введите свой API-ключ: ")

api = requests.get('https://api.ipify.org')
my_ip = api.text
print(f"Ваш IP: {my_ip}")

url = f"https://geo.ipify.org/api/v2/country?apiKey={YOUR_API_KEY}&ipAddress={my_ip}"

response = requests.get(url)
my_local =response.text
print(my_local)

if response.status_code == 200:
    filename = f"{my_local}_geo.txt"
    with open(f"PY156/{filename}", "w", encoding="utf-8") as file:
            file.write(my_local)
    print(f"✅ Сохранены геоданные в PY156/{filename}")
else:
    filename = f"{my_ip}.txt"
    with open(f"PY156/{filename}", "w", encoding="utf-8") as file:
            file.write(my_ip)
    print(f"✅ Сохранен IP в PY156/{filename}")

    with open(filename, "w", encoding="utf-8") as file:
        file.write("PY156")

token = input("Введите свой token: ")
header = {"Authorization": f"OAuth {token}"}
params = {"path" : "PY156"}
response = requests.put('https://cloud-api.yandex.net/v1/disk/resources', params=params, headers=header)
print(response.text)

response = requests.get("https://cloud-api.yandex.net/v1/disk/resources/upload", params = { "path" : f"PY156/{my_ip}"}, headers=header)
print(response.text)

upload_url = response.json()["href"]
print(upload_url)

with open(f"PY156/{filename}", "rb") as file:
    requests.put(upload_url, files={"file": file})
