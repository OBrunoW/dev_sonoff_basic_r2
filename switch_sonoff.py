import base64
import json
import requests
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Random import get_random_bytes

def pad(data_to_pad: bytes, block_size: int):
    padding_len = block_size - len(data_to_pad) % block_size
    padding = bytes([padding_len]) * padding_len
    return data_to_pad + padding

def encrypt(payload: dict, devicekey: str):
    devicekey = devicekey.encode('utf-8')
    hash_ = MD5.new()
    hash_.update(devicekey)
    key = hash_.digest()
    iv = get_random_bytes(16)
    plaintext = json.dumps(payload['data']).encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    padded = pad(plaintext, AES.block_size)
    ciphertext = cipher.encrypt(padded)

    payload['encrypt'] = True
    payload['data'] = base64.b64encode(ciphertext).decode('utf-8')
    payload['iv'] = base64.b64encode(iv).decode('utf-8')
    return payload

def send_command(command):
    payload = {
        "sequence": "0",
        "deviceid": "100231a5e0",
        "selfApikey": "dff4b831-d833-4919-ad90-2232d21e451c",
        "data": {"switch": command}
    }
    payload = encrypt(payload, 'dff4b831-d833-4919-ad90-2232d21e451c')
    headers = {'Connection': 'close'}
    try:
        response = requests.post(url='http://192.168.0.128:8081/zeroconf/switch', json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Comando '{command}' enviado com sucesso.")
        else:
            print("Erro ao enviar comando.")
    except requests.RequestException as e:
        print("Erro de conexão:", e)

# Loop infinito para o menu
while True:
    print("\n=== Menu de Controle do Dispositivo ===")
    print("1. Ligar Switch (on)")
    print("2. Desligar Switch (off)")
    print("3. Sair")
    choice = input("Escolha uma opção (1/2/3): ")

    if choice == "1":
        send_command("on")
    elif choice == "2":
        send_command("off")
    elif choice == "3":
        print("Encerrando o programa.")
        break
    else:
        print("Opção inválida. Por favor, escolha 1, 2 ou 3.")
