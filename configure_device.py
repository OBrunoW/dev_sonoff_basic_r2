import requests
import json
from device_data import device_info  # Importa a variável compartilhada

# IP do AP do Sonoff
ap_ip = "http://10.10.7.1"

def get_device_info():
    global device_info
    try:
        response = requests.get(f"{ap_ip}/device")
        response.raise_for_status()
        device_info = response.json()
        print("Informações do dispositivo obtidas:", device_info)
        return device_info
    except requests.RequestException as e:
        print("Erro ao obter informações do dispositivo:", e)
        return None

def configure_wifi(device_info, ssid, password):
    try:
        payload = {
            "deviceid": device_info["deviceid"],
            "data": {
                "ssid": ssid,
                "password": password
            }
        }
        response = requests.post(f"{ap_ip}/zeroconf/wifi", json=payload)
        response.raise_for_status()
        print("Configuração Wi-Fi enviada com sucesso.")
    except requests.RequestException as e:
        print("Erro ao configurar Wi-Fi:", e)
