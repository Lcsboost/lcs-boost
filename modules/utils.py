"""Helpers compartilhados: execução de comandos e checagem de admin."""
import ctypes
import subprocess

# Ferramentas de console do Windows (ping, netsh, ipconfig...) escrevem no
# codepage OEM do sistema, nao em UTF-8 - em PT-BR normalmente cp860/cp850.
# Decodificar como UTF-8 direto quebra em qualquer acento (causava
# UnicodeDecodeError). Por isso capturamos bytes e decodificamos com o
# codepage OEM real da maquina, ignorando o que nao bater.
try:
    _OEM_CODEPAGE = f"cp{ctypes.windll.kernel32.GetOEMCP()}"
except Exception:
    _OEM_CODEPAGE = "cp850"


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run(args, timeout=30):
    """Executa um comando e devolve (ok, saida)."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        ok = result.returncode == 0
        stdout = result.stdout.decode(_OEM_CODEPAGE, errors="replace") if result.stdout else ""
        stderr = result.stderr.decode(_OEM_CODEPAGE, errors="replace") if result.stderr else ""
        return ok, (stdout + stderr).strip()
    except Exception as e:
        return False, str(e)


def run_powershell(command, timeout=30):
    return run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command], timeout=timeout)
