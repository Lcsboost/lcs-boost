"""Modulo Jogos: deteta jogos em execucao e prioriza desempenho.

Limitacao honesta: nao existe forma generica de "forcar grafico no minimo"
dentro de qualquer jogo - cada jogo guarda suas configuracoes num lugar e
formato diferentes, e varios jogos com anti-cheat bloqueiam ou banem quem
edita esses arquivos por fora. Por isso este modulo:
  1) sempre aplica o que É seguro e genérico pra qualquer jogo: prioridade de
     processo no Windows, afinidade de nucleos e Game Mode do Windows;
  2) opcionalmente aplica "perfis" que o usuario mesmo cria, apontando pra um
     arquivo de configuracao de um jogo especifico e as linhas a trocar.
"""
import json
import os
import threading
import time

import psutil

from . import utils

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
GAMES_FILE = os.path.join(CONFIG_DIR, "games.json")

DEFAULT_GAMES = [
    "csgo.exe", "cs2.exe", "valorant.exe", "valorant-win64-shipping.exe",
    "leagueoflegends.exe", "league of legends.exe", "fortniteclient-win64-shipping.exe",
    "gta5.exe", "rdr2.exe", "apex_legends.exe", "r5apex.exe", "overwatch.exe",
    "destiny2.exe", "warzone.exe", "modernwarfare.exe", "eldenring.exe",
    "minecraft.exe", "javaw.exe", "rocketleague.exe", "pubg.exe", "tslgame.exe",
]


def _ensure_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(GAMES_FILE):
        with open(GAMES_FILE, "w", encoding="utf-8") as f:
            json.dump({"processos": DEFAULT_GAMES, "perfis": {}}, f, ensure_ascii=False, indent=2)


def load_config():
    _ensure_config()
    with open(GAMES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    _ensure_config()
    with open(GAMES_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def add_game(exe_name: str):
    cfg = load_config()
    exe_name = exe_name.strip().lower()
    if exe_name and exe_name not in cfg["processos"]:
        cfg["processos"].append(exe_name)
        save_config(cfg)
    return cfg["processos"]


def remove_game(exe_name: str):
    cfg = load_config()
    cfg["processos"] = [g for g in cfg["processos"] if g != exe_name]
    save_config(cfg)
    return cfg["processos"]


def list_running_processes():
    procs = []
    for p in psutil.process_iter(["pid", "name"]):
        try:
            procs.append((p.info["pid"], p.info["name"]))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(procs, key=lambda x: (x[1] or "").lower())


def boost_process(pid: int, realtime: bool = False):
    """Prioridade maxima + afinidade total + libera o jogo pra usar tudo."""
    p = psutil.Process(pid)
    try:
        p.nice(psutil.REALTIME_PRIORITY_CLASS if realtime else psutil.HIGH_PRIORITY_CLASS)
    except psutil.AccessDenied:
        return False, "Sem permissao para mudar prioridade (rode o LCS BOOST como administrador)."
    try:
        p.cpu_affinity(list(range(psutil.cpu_count())))
    except Exception:
        pass
    try:
        p.ionice(psutil.IOPRIO_HIGH)
    except Exception:
        pass
    return True, f"Prioridade de '{p.name()}' (PID {pid}) ajustada para {'Tempo Real' if realtime else 'Alta'}."


def enable_windows_game_mode(enable: bool = True):
    val = "1" if enable else "0"
    ok, out = utils.run_powershell(
        f"New-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\GameBar' -Name 'AutoGameModeEnabled' "
        f"-Value {val} -PropertyType DWord -Force | Out-Null"
    )
    return ok, out


def apply_profile(profile: dict):
    """Aplica um perfil de troca de texto num arquivo .ini/.cfg de um jogo.

    profile = {"arquivo": "C:\\...\\config.cfg", "trocas": {"linha_antiga": "linha_nova", ...}}
    O usuario eh quem define o que trocar; nao inventamos valores por jogo.
    """
    caminho = profile.get("arquivo")
    trocas = profile.get("trocas", {})
    if not caminho or not os.path.exists(caminho):
        return False, f"Arquivo nao encontrado: {caminho}"
    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
        conteudo = f.read()
    alterado = conteudo
    aplicadas = 0
    for antigo, novo in trocas.items():
        if antigo in alterado:
            alterado = alterado.replace(antigo, novo)
            aplicadas += 1
    if alterado != conteudo:
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(alterado)
    return True, f"{aplicadas} linha(s) trocada(s) em {os.path.basename(caminho)}."


class GameMonitor:
    """Fica de olho nos processos e aplica o boost assim que um jogo da lista abre."""

    def __init__(self, log_callback, realtime=False, interval=2.0):
        self.log = log_callback
        self.realtime = realtime
        self.interval = interval
        self._thread = None
        self._stop = threading.Event()
        self._boosted_pids = set()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self.log("Monitor de jogos iniciado. Esperando algum jogo da lista abrir...")

    def stop(self):
        self._stop.set()
        self.log("Monitor de jogos parado.")

    def _loop(self):
        while not self._stop.is_set():
            cfg = load_config()
            alvo = set(n.lower() for n in cfg["processos"])
            for pid, name in list_running_processes():
                if not name:
                    continue
                if name.lower() in alvo and pid not in self._boosted_pids:
                    ok, msg = boost_process(pid, realtime=self.realtime)
                    self.log(msg if ok else f"Falha ao priorizar {name}: {msg}")
                    enable_windows_game_mode(True)
                    for perfil_nome, perfil in cfg.get("perfis", {}).items():
                        pok, pmsg = apply_profile(perfil)
                        self.log(f"Perfil '{perfil_nome}': {pmsg}" if pok else f"Perfil '{perfil_nome}' falhou: {pmsg}")
                    self._boosted_pids.add(pid)
            self._stop.wait(self.interval)
