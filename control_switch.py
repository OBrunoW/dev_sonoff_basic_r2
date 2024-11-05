import base64
import ipaddress
import json
import asyncio
import aiohttp
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Random import get_random_bytes
from zeroconf import Zeroconf, ServiceStateChange
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo
from device_data import device_info  # Importa a variável compartilhada

# Funções auxiliares para criptografia
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
    plaintext = json.dumps(payload["data"]).encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    padded = pad(plaintext, AES.block_size)
    ciphertext = cipher.encrypt(padded)
    payload["encrypt"] = True
    payload["data"] = base64.b64encode(ciphertext).decode("utf-8")
    payload["iv"] = base64.b64encode(iv).decode("utf-8")
    return payload

async def discover_device():
    global device_info
    zeroconf = Zeroconf()
    try:
        browser = AsyncServiceBrowser(zeroconf, "_ewelink._tcp.local.", [on_service_state_change])
        await asyncio.sleep(10)  # Aguarda por dispositivos na rede
    finally:
        await browser.async_cancel()
        zeroconf.close()

def on_service_state_change(zeroconf, service_type, name, state_change):
    if state_change == ServiceStateChange.Added and name.startswith("eWeLink"):
        asyncio.create_task(handle_device_info(zeroconf, service_type, name))

async def handle_device_info(zeroconf, service_type, name):
    global device_info
    deviceid = name[8:18]
    info = AsyncServiceInfo(service_type, name)
    if await info.async_request(zeroconf, 3000):
        for addr in info.addresses:
            addr = ipaddress.IPv4Address(addr)
            host = f"{addr}:{info.port}" if info.port else str(addr)
            print(f"Dispositivo encontrado: {deviceid} em {host}")
            # Armazena o endereço IP e porta no device_info
            device_info["deviceid"] = deviceid
            device_info["ip"] = str(addr)
            device_info["port"] = info.port

async def send_command(command):
    global device_info
    device_ip = device_info["ip"]
    deviceid = device_info["deviceid"]
    devicekey = device_info["apikey"]

    payload = {
        "deviceid": deviceid,
        "data": {"switch": command}
    }
    payload = encrypt(payload, devicekey)
    url = f"http://{device_ip}/zeroconf/switch"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                print(f"Comando '{command}' enviado com sucesso.")
            else:
                print("Erro ao enviar comando.")
