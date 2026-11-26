"""Modulo Ping/Rota.

Honestidade primeiro: a "rota" fisica do seu pacote ate o servidor do jogo e
decidida pelo seu provedor de internet (ISP) e pela internet em si - nenhum
programa no seu PC consegue escolher outro caminho pela rede do provedor.
O que de fato ajuda e verificavel por aqui:
  - medir a latencia (ping) para varios DNS publicos e sugerir o mais rapido;
  - limpar o cache de DNS e resetar o Winsock (corrige configuracoes de rede
    corrompidas, que sao uma causa comum de ping alto/instavel);
  - desativar o algoritmo de Nagle / ajustar TcpAckFrequency, uma otimizacao
    de baixa latencia conhecida para jogos online.
"""
import re
import statistics

from . import utils

DNS_SERVERS = {
    "Cloudflare": "1.1.1.1",
    "Google": "8.8.8.8",
    "Quad9": "9.9.9.9",
    "OpenDNS": "208.67.222.222",
    "NordVPN DNS": "103.86.96.100",
}


def ping_host(host: str, count: int = 4):
    ok, out = utils.run(["ping", "-n", str(count), host], timeout=count * 2 + 5)
    tempos = [int(m) for m in re.findall(r"tempo[=<](\d+)ms", out, re.IGNORECASE)]
    if not tempos:
        tempos = [int(m) for m in re.findall(r"time[=<](\d+)ms", out, re.IGNORECASE)]
    perda = None
    m = re.search(r"(\d+)% (?:de perda|loss)", out, re.IGNORECASE)
    if m:
        perda = int(m.group(1))
    if not tempos:
        return {"host": host, "media": None, "perda": perda if perda is not None else 100, "ok": False}
    return {
        "host": host,
        "media": round(statistics.mean(tempos), 1),
        "perda": perda if perda is not None else 0,
        "ok": True,
    }


def test_dns_latency():
    resultados = []
    for nome, ip in DNS_SERVERS.items():
        r = ping_host(ip, count=4)
        r["nome"] = nome
        resultados.append(r)
    resultados.sort(key=lambda r: (not r["ok"], r["media"] if r["media"] is not None else 9999))
    return resultados


def flush_dns():
    return utils.run(["ipconfig", "/flushdns"])


def reset_winsock():
    ok, out = utils.run(["netsh", "winsock", "reset"])
    return ok, (out or "") + "\n(Reinicie o PC para concluir o reset do Winsock.)"


def set_dns(adapter_name: str, primary: str, secondary: str = None):
    ok1, out1 = utils.run(["netsh", "interface", "ip", "set", "dns", f"name={adapter_name}", "static", primary])
    if ok1 and secondary:
        utils.run(["netsh", "interface", "ip", "add", "dns", f"name={adapter_name}", secondary, "index=2"])
    return ok1, out1


def get_active_adapters():
    ok, out = utils.run_powershell(
        "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object -ExpandProperty Name"
    )
    if not ok:
        return []
    return [l.strip() for l in out.splitlines() if l.strip()]


def disable_nagle_algorithm():
    """Aplica TcpAckFrequency=1 e TCPNoDelay=1 em todas as interfaces TCP/IP."""
    ps = (
        "$base = 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces';"
        "Get-ChildItem $base | ForEach-Object {"
        "  New-ItemProperty -Path $_.PSPath -Name 'TcpAckFrequency' -Value 1 -PropertyType DWord -Force | Out-Null;"
        "  New-ItemProperty -Path $_.PSPath -Name 'TCPNoDelay' -Value 1 -PropertyType DWord -Force | Out-Null;"
        "}"
    )
    ok, out = utils.run_powershell(ps)
    return ok, out or "Nagle desativado em todas as interfaces (efeito completo apos reiniciar o PC)."
