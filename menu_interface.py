import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import darkdetect
from tkinter import messagebox, StringVar, Frame
import asyncio
import ctypes
from ctypes import windll, c_int, byref
from configure_device import get_device_info, configure_wifi
from control_switch import send_command, discover_device

# Constante para o tema da barra de título
DWMWA_USE_IMMERSIVE_DARK_MODE = 20

# Função para aplicar tema do sistema à barra de título no Windows
def apply_title_bar_theme():
    hwnd = windll.user32.GetParent(app.winfo_id())  # Identifica a janela do app
    is_dark_mode = darkdetect.isDark()  # Detecta se o sistema está no modo escuro
    value = c_int(1 if is_dark_mode else 0)  # Define o valor para modo claro ou escuro
    windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, byref(value), ctypes.sizeof(value))

# Funções de configuração e controle
async def configure_device(ssid, password, status_label, loading_label):
    status_label.config(text="Configurando dispositivo...", bootstyle=INFO)
    loading_label.pack()  # Mostra o loading
    await asyncio.sleep(1)  # Simula o tempo de processamento

    device_info = get_device_info()
    if device_info:
        configure_wifi(device_info, ssid, password)
        status_label.config(text="Dispositivo configurado com sucesso!", bootstyle=SUCCESS)
    else:
        status_label.config(text="Falha ao configurar o dispositivo.", bootstyle=DANGER)

    loading_label.pack_forget()  # Esconde o loading

async def control_switch(action, status_label, loading_label):
    status_label.config(text=f"Executando '{action}'...", bootstyle=INFO)
    loading_label.pack()  # Mostra o loading
    await asyncio.sleep(1)  # Simula o tempo de processamento

    device_ip = "192.168.0.128:8081"
    device_info = await discover_device()
    if device_info:
        deviceid = device_info["deviceid"]
        devicekey = device_info["apikey"]
        await send_command(device_ip, deviceid, devicekey, action)
        status_label.config(text=f"Switch {action} com sucesso!", bootstyle=SUCCESS)
    else:
        status_label.config(text="Dispositivo não encontrado na rede.", bootstyle=DANGER)

    loading_label.pack_forget()  # Esconde o loading

# Funções auxiliares para manipulação da GUI
def ligar_switch():
    asyncio.run(control_switch("on", status_label, loading_label))

def desligar_switch():
    asyncio.run(control_switch("off", status_label, loading_label))

def iniciar_configuracao():
    ssid = ssid_var.get()
    password = password_var.get()
    if ssid and password:
        asyncio.run(configure_device(ssid, password, status_label, loading_label))
    else:
        status_label.config(text="Por favor, insira o SSID e a senha.", bootstyle=WARNING)

# Configuração do tema com base no modo do sistema
theme = "darkly" if darkdetect.isDark() else "flatly"
app = ttk.Window(themename=theme)
app.title("Controle Sonoff Bixs")
app.geometry("500x250")

# Aplica o tema do sistema à barra de título no Windows
apply_title_bar_theme()

# Criação do frame principal
main_frame = ttk.Frame(app)
main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

# Divisão em colunas
left_frame = Frame(main_frame)
left_frame.grid(row=0, column=0, sticky="nswe", padx=10)

right_frame = Frame(main_frame)
right_frame.grid(row=0, column=1, sticky="nswe", padx=10)

# Centralizar o conteúdo nos frames
left_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_columnconfigure(0, weight=1)

# Elementos da coluna esquerda (Configuração de Wi-Fi)
ssid_var = StringVar()
password_var = StringVar()

ssid_label = ttk.Label(left_frame, text="SSID do Wi-Fi:", font=("Helvetica", 10))
ssid_label.pack(pady=(5, 2), anchor=CENTER)
ssid_entry = ttk.Entry(left_frame, textvariable=ssid_var, font=("Helvetica", 9))
ssid_entry.pack(pady=(0, 10), fill=X, padx=20)

password_label = ttk.Label(left_frame, text="Senha do Wi-Fi:", font=("Helvetica", 10))
password_label.pack(pady=(5, 2), anchor=CENTER)
password_entry = ttk.Entry(left_frame, textvariable=password_var, show="*", font=("Helvetica", 9))
password_entry.pack(pady=(0, 10), fill=X, padx=20)

btn_configurar = ttk.Button(left_frame, text="Configurar Dispositivo", bootstyle=PRIMARY, command=iniciar_configuracao, width=20)
btn_configurar.pack(pady=10, anchor=CENTER)

# Elementos da coluna direita (Controle do Switch)
btn_ligar = ttk.Button(right_frame, text="Ligar Switch", bootstyle=SUCCESS, command=ligar_switch, width=15, padding=10)
btn_ligar.pack(pady=(10, 5), fill=X, padx=20)

btn_desligar = ttk.Button(right_frame, text="Desligar Switch", bootstyle=DANGER, command=desligar_switch, width=15, padding=10)
btn_desligar.pack(pady=(5, 10), fill=X, padx=20)

# Elemento de loading e status (posicionado abaixo das colunas)
loading_label = ttk.Label(app, text="Processando...", font=("Helvetica", 10, "italic"), bootstyle="secondary")
status_label = ttk.Label(app, text="", font=("Helvetica", 10))
status_label.pack(pady=10)

# Executa a interface gráfica
app.mainloop()
