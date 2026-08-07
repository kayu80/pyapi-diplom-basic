import requests
import os

DIRECTORY = "PY156"

def ensure_directory():
    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)

class IPGeoClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.my_ip = None
        self.geo_data = None

    def get_my_ip(self):
        resp = requests.get("https://api.ipify.org", timeout=10)
        resp.raise_for_status()
        self.my_ip = resp.text
        print(f"Ваш IP: {self.my_ip}")
        return self.my_ip

    def get_geo_data(self):
        if self.my_ip is None:
            self.get_my_ip()

        # Пробуем ipify (нужен валидный ключ и тариф)
        try:
            url = f"https://geo.ipify.org/api/v2/country?apiKey={self.api_key}&ipAddress={self.my_ip}"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            self.geo_data = resp.json()
            print("Геоданные (ipify):", self.geo_data)
            return self.geo_data
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print("⚠️ ipify вернул 403 — пробуем запасной сервис (ipapi.co)...")
            else:
                raise

        # Fallback: ipapi.co (без ключа, бесплатно)
        try:
            url_fallback = f"https://ipapi.co/{self.my_ip}/json/"
            resp = requests.get(url_fallback, timeout=10)
            resp.raise_for_status()
            self.geo_data = resp.json()
            print("Геоданные (ipapi.co):", self.geo_data)
            return self.geo_data
        except Exception as e:
            print("❌ Не удалось получить геоданные ни из одного источника:", e)
            self.geo_data = {"error": "geo_fetch_failed"}
            return self.geo_data

    def save_local_data(self):
        ensure_directory()

        if self.geo_data and self.geo_data.get("error") != "geo_fetch_failed":
            country = self.geo_data.get("country_name") or self.geo_data.get("country") or "unknown"
            filename = f"{country}_geo.txt"
            content = str(self.geo_data)
        else:
            filename = f"{self.my_ip}.txt"
            content = self.my_ip or "IP not available"

        filepath = os.path.join(DIRECTORY, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Сохранены данные в {filepath}")
        return filepath


class YandexDiskClient:
    def __init__(self, token):
        self.token = token
        self.headers = {"Authorization": f"OAuth {self.token}"}

    def create_folder(self, path="PY156"):
        resp = requests.put(
            "https://cloud-api.yandex.net/v1/disk/resources",
            params={"path": path},
            headers=self.headers,
            timeout=10
        )
        resp.raise_for_status()
        print("Папка создана или уже существует")
        return resp.json()

    def get_upload_url(self, filename, folder="PY156"):
        path = f"{folder}/{filename}"
        resp = requests.get(
            "https://cloud-api.yandex.net/v1/disk/resources/upload",
            params={"path": path, "overwrite": "true"},
            headers=self.headers,
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        upload_url = data["href"]
        return upload_url

    def upload_file(self, filepath, filename, folder="PY156"):
        upload_url = self.get_upload_url(filename, folder)
        with open(filepath, "rb") as f:
            resp = requests.put(upload_url, data=f, timeout=30)
        resp.raise_for_status()
        print("✅ Файл загружен на Яндекс Диск")


if __name__ == "__main__":
    api_key = input("Введите API-ключ для geo.ipify.org (или оставьте пустым для использования fallback): ").strip()
    yandex_token = input("Введите OAuth-токен для Яндекс Диска: ").strip()

    client = IPGeoClient(api_key)
    client.get_my_ip()
    client.get_geo_data()
    local_filepath = client.save_local_data()

    disk = YandexDiskClient(yandex_token)
    disk.create_folder()
    _, filename = os.path.split(local_filepath)
    disk.upload_file(local_filepath, filename)
