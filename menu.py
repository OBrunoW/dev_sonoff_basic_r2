import asyncio
from configure_device import get_device_info, configure_wifi
from control_switch import send_command, discover_device

# Funções de menu

def display_menu():
    print("=== Menu de Controle Sonoff ===")
    print("1. Configurar Dispositivo (Modo AP)")
    print("2. Ligar Switch")
    print("3. Desligar Switch")
    print("0. Sair")

async def configure_device():
    print("\nConfigurando dispositivo...")
    device_info = get_device_info()
    if device_info:
        configure_wifi(device_info)
    else:
        print("Falha ao obter informações do dispositivo no modo AP.")

async def control_switch(action):
    device_ip = "192.168.0.128:8081"  # Defina o IP do dispositivo após configuração
    device_info = await discover_device()  # Descobre o dispositivo na rede local
    if device_info:
        deviceid = device_info["deviceid"]
        devicekey = device_info["apikey"]
        await send_command(device_ip, deviceid, devicekey, action)
    else:
        print("Dispositivo não encontrado na rede local.")

async def main_menu():
    while True:
        display_menu()
        choice = input("Escolha uma opção: ")
        
        if choice == "1":
            await configure_device()
        elif choice == "2":
            await control_switch("on")
        elif choice == "3":
            await control_switch("off")
        elif choice == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Executa o menu
asyncio.run(main_menu())
