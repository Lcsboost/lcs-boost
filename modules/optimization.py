"""Modulo Otimizacao: plano de energia, itens de inicializacao e overclock.

Sobre overclock: overclock real (subir clock/voltagem de CPU/GPU) depende de
cada fabricante (Intel, AMD, NVIDIA...) e de acesso de baixo nivel ao
hardware. Fazer isso de forma generica e automatica, sem o usuario escolher
valores com cuidado, pode travar o PC ou danificar o hardware - por isso o
LCS BOOST NAO aplica overclock por conta propria. Em vez disso, ele detecta
e abre pra voce o utilitario oficial ja instalado (MSI Afterburner, AMD
Ryzen Master, Intel XTU, ASUS GPU Tweak etc).
"""
import os
import winreg

from . import utils

POWER_PLANS = {
    "equilibrado": "381b4222-f694-41f0-9685-ff5bb260df2e",
    "alto_desempenho": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
    "desempenho_maximo": "e9a42b02-d5df-448d-aa00-03f14749eb61",  # Ultimate Performance
}

OC_TOOLS = [
    (r"C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe", "MSI Afterburner"),
    (r"C:\Program Files\AMD\RyzenMaster\AMDRyzenMasterDriverV27.exe", "AMD Ryzen Master"),
    (r"C:\Program Files (x86)\AMD\RyzenMaster", "AMD Ryzen Master"),
    (r"C:\Program Files (x86)\Intel\Intel(R) Extreme Tuning Utility\XTU.exe", "Intel XTU"),
    (r"C:\Program Files\ASUS\GPU Tweak III\GPUTweakIII.exe", "ASUS GPU Tweak III"),
]


def set_power_plan(mode: str):
    guid = POWER_PLANS.get(mode)
    if not guid:
        return False, "Plano desconhecido."
    if mode == "desempenho_maximo":
        # O plano Ultimate Performance vem oculto por padrao; duplica se preciso.
        ok, out = utils.run(["powercfg", "-duplicatescheme", guid])
        if ok and out:
            # A ultima linha costuma trazer o novo GUID gerado.
            for token in out.replace("\r", "").split():
                if len(token) == 36 and token.count("-") == 4:
                    guid = token
    ok, out = utils.run(["powercfg", "-setactive", guid])
    return ok, out or "Plano de energia aplicado."


def restore_balanced_plan():
    return set_power_plan("equilibrado")


def find_installed_oc_tools():
    found = []
    for path, name in OC_TOOLS:
        if os.path.exists(path):
            found.append((path, name))
    return found


def launch_oc_tool(path):
    try:
        os.startfile(path)
        return True, "Utilitario de overclock aberto."
    except Exception as e:
        return False, str(e)


# --- Itens de inicializacao (equivalente a aba "Inicializacao" do msconfig) ---

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def list_startup_items():
    items = []
    for hive, hive_name in ((winreg.HKEY_CURRENT_USER, "HKCU"), (winreg.HKEY_LOCAL_MACHINE, "HKLM")):
        try:
            with winreg.OpenKey(hive, RUN_KEY, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        items.append({"hive": hive_name, "nome": name, "comando": value})
                        i += 1
                    except OSError:
                        break
        except OSError:
            continue
    return items


def disable_startup_item(hive_name: str, nome: str):
    """Remove da chave Run e guarda backup pra poder reativar depois."""
    hive = winreg.HKEY_CURRENT_USER if hive_name == "HKCU" else winreg.HKEY_LOCAL_MACHINE
    try:
        with winreg.OpenKey(hive, RUN_KEY, 0, winreg.KEY_READ) as key:
            valor, _ = winreg.QueryValueEx(key, nome)
    except OSError:
        return False, "Item nao encontrado."
    backup_key = RUN_KEY + "_LCSBOOST_DISABLED"
    try:
        with winreg.CreateKey(hive, backup_key) as bkey:
            winreg.SetValueEx(bkey, nome, 0, winreg.REG_SZ, valor)
        with winreg.OpenKey(hive, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, nome)
        return True, f"'{nome}' desativado da inicializacao."
    except OSError as e:
        return False, str(e)


def enable_startup_item(hive_name: str, nome: str):
    hive = winreg.HKEY_CURRENT_USER if hive_name == "HKCU" else winreg.HKEY_LOCAL_MACHINE
    backup_key = RUN_KEY + "_LCSBOOST_DISABLED"
    try:
        with winreg.OpenKey(hive, backup_key, 0, winreg.KEY_READ) as bkey:
            valor, _ = winreg.QueryValueEx(bkey, nome)
        with winreg.CreateKey(hive, RUN_KEY) as key:
            winreg.SetValueEx(key, nome, 0, winreg.REG_SZ, valor)
        with winreg.OpenKey(hive, backup_key, 0, winreg.KEY_SET_VALUE) as bkey:
            winreg.DeleteValue(bkey, nome)
        return True, f"'{nome}' reativado na inicializacao."
    except OSError as e:
        return False, str(e)


def list_disabled_startup_items():
    items = []
    backup_key = RUN_KEY + "_LCSBOOST_DISABLED"
    for hive, hive_name in ((winreg.HKEY_CURRENT_USER, "HKCU"), (winreg.HKEY_LOCAL_MACHINE, "HKLM")):
        try:
            with winreg.OpenKey(hive, backup_key, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        items.append({"hive": hive_name, "nome": name, "comando": value})
                        i += 1
                    except OSError:
                        break
        except OSError:
            continue
    return items
