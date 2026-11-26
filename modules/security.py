"""Modulo Firewall/Seguranca do Windows.

Liga/desliga o Firewall do Windows e a protecao em tempo real do
Windows Defender. Isso reduz a seguranca do PC - por isso a interface
sempre pede confirmacao explicita antes de desativar qualquer um dos dois.
Se a "Protecao contra adulteracao" (Tamper Protection) do Windows estiver
ativa, o Windows bloqueia a desativacao do Defender por script; nesse caso
avisamos o usuario a desativar a Protecao contra adulteracao manualmente
primeiro (Configuracoes do Windows > Privacidade e seguranca).
"""
from . import utils


def firewall_status():
    ok, out = utils.run(["netsh", "advfirewall", "show", "allprofiles", "state"])
    if not ok:
        return None
    ligado = out.lower().count("on") > 0 or "ativado" in out.lower()
    return ligado


def set_firewall(enabled: bool):
    estado = "on" if enabled else "off"
    ok, out = utils.run(["netsh", "advfirewall", "set", "allprofiles", "state", estado])
    return ok, out or f"Firewall do Windows {'ativado' if enabled else 'desativado'}."


def defender_realtime_status():
    ok, out = utils.run_powershell("(Get-MpComputerStatus).RealTimeProtectionEnabled")
    if not ok:
        return None
    return "true" in out.lower()


def set_defender_realtime(enabled: bool):
    valor = "$false" if enabled else "$true"
    ok, out = utils.run_powershell(f"Set-MpPreference -DisableRealtimeMonitoring {valor}")
    if not ok:
        return False, (
            "Nao foi possivel alterar o Defender. Se a 'Protecao contra adulteracao' estiver "
            "ativa, desative-a manualmente em Configuracoes > Privacidade e seguranca > "
            "Seguranca do Windows > Protecao contra virus e ameacas, e tente novamente.\n" + out
        )
    return True, f"Protecao em tempo real do Defender {'ativada' if enabled else 'desativada'}."
