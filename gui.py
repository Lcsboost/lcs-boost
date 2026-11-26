"""Interface grafica do LCS BOOST (CustomTkinter - visual moderno)."""
import threading
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from modules import games, optimization, network, security, utils

BG = "#0f1117"
SIDEBAR = "#151823"
CARD = "#1a1d2a"
CARD_HOVER = "#202434"
ROW = "#11131b"
ACCENT = "#7c5cff"
ACCENT_HOVER = "#9174ff"
ACCENT2 = "#00d4ff"
TEXT = "#eceef5"
MUTED = "#8c8fa3"
OK = "#39d98a"
WARN = "#ff5c6a"
WARN_HOVER = "#ff7b86"
BORDER = "#262a3a"

ctk.set_appearance_mode("dark")


def run_async(fn, on_done=None):
    def wrapper():
        result = fn()
        if on_done:
            on_done(result)
    threading.Thread(target=wrapper, daemon=True).start()


def section_title(master, text):
    return ctk.CTkLabel(master, text=text, text_color=ACCENT2, font=("Segoe UI", 15, "bold"), anchor="w")


def hint(master, text):
    return ctk.CTkLabel(master, text=text, text_color=MUTED, font=("Segoe UI", 11), anchor="w",
                         justify="left", wraplength=620)


def card(master):
    return ctk.CTkFrame(master, fg_color=CARD, corner_radius=12, border_width=1, border_color=BORDER)


def primary_button(master, text, command, danger=False):
    if danger:
        return ctk.CTkButton(master, text=text, command=command, fg_color=WARN, hover_color=WARN_HOVER,
                              text_color="#1a0506", font=("Segoe UI", 12, "bold"), corner_radius=8, height=34)
    return ctk.CTkButton(master, text=text, command=command, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                          text_color="#ffffff", font=("Segoe UI", 12, "bold"), corner_radius=8, height=34)


def ghost_button(master, text, command):
    return ctk.CTkButton(master, text=text, command=command, fg_color="transparent", hover_color=CARD_HOVER,
                          text_color=ACCENT2, border_width=1, border_color=BORDER,
                          font=("Segoe UI", 12), corner_radius=8, height=34)


class LogPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=SIDEBAR, corner_radius=12, border_width=1, border_color=BORDER)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(8, 0))
        ctk.CTkLabel(top, text="REGISTRO DE ATIVIDADE", text_color=MUTED,
                     font=("Segoe UI", 10, "bold")).pack(side="left")
        self.box = ctk.CTkTextbox(self, height=120, fg_color="#0a0b11", text_color=ACCENT2,
                                   font=("Consolas", 10), corner_radius=8, wrap="word")
        self.box.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        self.box.configure(state="disabled")

    def log(self, msg: str):
        self.box.configure(state="normal")
        self.box.insert("end", f"›  {msg}\n")
        self.box.see("end")
        self.box.configure(state="disabled")


class Row(ctk.CTkFrame):
    """Linha de card reutilizavel: titulo + subtitulo a esquerda, acoes a direita."""

    def __init__(self, master, title, subtitle=None, badge=None, badge_color=MUTED):
        super().__init__(master, fg_color=ROW, corner_radius=10)
        self.grid_columnconfigure(0, weight=1)
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=12, pady=8)
        ctk.CTkLabel(left, text=title, text_color=TEXT, font=("Segoe UI", 12, "bold"), anchor="w").pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(left, text=subtitle, text_color=MUTED, font=("Consolas", 10), anchor="w").pack(anchor="w")
        self.actions = ctk.CTkFrame(self, fg_color="transparent")
        self.actions.grid(row=0, column=1, sticky="e", padx=12, pady=8)
        if badge:
            ctk.CTkLabel(self.actions, text=badge, text_color=badge_color,
                         font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LCS BOOST")
        self.geometry("1000x700")
        self.minsize(900, 600)
        self.configure(fg_color=BG)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self._build_sidebar()

        self.content = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nswe", padx=(10, 16), pady=(16, 8))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.log_panel = LogPanel(self)
        self.log_panel.grid(row=1, column=1, sticky="we", padx=(10, 16), pady=(0, 16))

        self.pages = {}
        self._build_page_games()
        self._build_page_opt()
        self._build_page_net()
        self._build_page_sec()
        self._select_page("games")

        self.monitor = games.GameMonitor(self.log_panel.log)
        self.log_panel.log("LCS BOOST iniciado." if utils.is_admin() else
                            "AVISO: sem privilégios de administrador — a maioria das ações vai falhar.")

    # ---------------- sidebar ----------------
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=230, fg_color=SIDEBAR, corner_radius=0)
        sb.grid(row=0, column=0, rowspan=2, sticky="nswe")
        sb.grid_propagate(False)

        brand = ctk.CTkFrame(sb, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(26, 4))
        ctk.CTkLabel(brand, text="LCS", text_color=ACCENT, font=("Segoe UI", 24, "bold")).pack(side="left")
        ctk.CTkLabel(brand, text=" BOOST", text_color=TEXT, font=("Segoe UI", 24, "bold")).pack(side="left")
        ctk.CTkLabel(sb, text="Performance Suite", text_color=MUTED, font=("Segoe UI", 10)).pack(
            anchor="w", padx=22, pady=(0, 18))

        status_ok = utils.is_admin()
        badge = ctk.CTkFrame(sb, fg_color=CARD, corner_radius=20, height=30)
        badge.pack(fill="x", padx=18, pady=(0, 22))
        dot = ctk.CTkFrame(badge, fg_color=OK if status_ok else WARN, width=9, height=9, corner_radius=5)
        dot.pack(side="left", padx=(12, 8), pady=8)
        ctk.CTkLabel(badge, text="Administrador" if status_ok else "Sem admin",
                     text_color=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left", pady=8)

        self._nav_buttons = {}
        nav_items = [
            ("games", "🎮  Jogos"),
            ("opt", "⚙️  Otimização"),
            ("net", "📡  Ping / Rota"),
            ("sec", "🛡️  Firewall / Segurança"),
        ]
        for key, label in nav_items:
            b = ctk.CTkButton(sb, text=label, anchor="w", font=("Segoe UI", 13),
                               fg_color="transparent", hover_color=CARD, text_color=MUTED,
                               corner_radius=8, height=42, command=lambda k=key: self._select_page(k))
            b.pack(fill="x", padx=14, pady=3)
            self._nav_buttons[key] = b

        ctk.CTkLabel(sb, text="v1.0", text_color=MUTED, font=("Segoe UI", 9)).pack(side="bottom", pady=14)

    def _select_page(self, key):
        for k, frame in self.pages.items():
            frame.grid_remove()
        self.pages[key].grid(row=0, column=0, sticky="nswe")
        for k, b in self._nav_buttons.items():
            if k == key:
                b.configure(fg_color=ACCENT, text_color="#ffffff")
            else:
                b.configure(fg_color="transparent", text_color=MUTED)

    def log(self, msg):
        self.log_panel.log(msg)

    def _new_page(self, key):
        page = ctk.CTkScrollableFrame(self.content, fg_color=BG, scrollbar_button_color=CARD,
                                       scrollbar_button_hover_color=CARD_HOVER)
        page.grid(row=0, column=0, sticky="nswe")
        page.grid_columnconfigure(0, weight=1)
        self.pages[key] = page
        return page

    # ---------------- pagina Jogos ----------------
    def _build_page_games(self):
        page = self._new_page("games")

        c1 = card(page)
        c1.pack(fill="x", pady=(0, 14))
        section_title(c1, "Boost automático de jogos").pack(anchor="w", padx=18, pady=(16, 4))
        hint(c1, "Quando um jogo da lista abrir, o LCS BOOST aumenta a prioridade dele no Windows, "
                 "libera todos os núcleos de CPU e ativa o Modo de Jogo.").pack(anchor="w", padx=18)

        row = ctk.CTkFrame(c1, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=12)
        self.var_realtime = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(row, text="Usar prioridade Tempo Real (mais agressivo)", variable=self.var_realtime,
                         fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=TEXT,
                         font=("Segoe UI", 11)).pack(side="left")

        row2 = ctk.CTkFrame(c1, fg_color="transparent")
        row2.pack(fill="x", padx=18, pady=(0, 18))
        self.btn_monitor = primary_button(row2, "▶  Iniciar monitor de jogos", self._toggle_monitor)
        self.btn_monitor.pack(side="left", padx=(0, 10))
        ghost_button(row2, "Ativar Modo de Jogo agora", self._enable_game_mode).pack(side="left")

        c2 = card(page)
        c2.pack(fill="x", pady=(0, 14))
        section_title(c2, "Priorizar um processo agora").pack(anchor="w", padx=18, pady=(16, 8))
        row3 = ctk.CTkFrame(c2, fg_color="transparent")
        row3.pack(fill="x", padx=18, pady=(0, 18))
        self.combo_proc = ctk.CTkComboBox(row3, width=360, state="readonly", fg_color=ROW,
                                           border_color=BORDER, button_color=ACCENT, dropdown_fg_color=ROW,
                                           text_color=TEXT, values=[])
        self.combo_proc.pack(side="left", padx=(0, 8))
        ghost_button(row3, "Atualizar", self._refresh_processes).pack(side="left", padx=(0, 8))
        primary_button(row3, "Priorizar agora", self._boost_selected).pack(side="left")
        self._refresh_processes()

        c3 = card(page)
        c3.pack(fill="x", pady=(0, 14))
        section_title(c3, "Jogos monitorados").pack(anchor="w", padx=18, pady=(16, 8))
        row4 = ctk.CTkFrame(c3, fg_color="transparent")
        row4.pack(fill="x", padx=18)
        self.entry_game = ctk.CTkEntry(row4, width=320, placeholder_text="nomedojogo.exe", fg_color=ROW,
                                        border_color=BORDER, text_color=TEXT)
        self.entry_game.pack(side="left", padx=(0, 8))
        primary_button(row4, "Adicionar", self._add_game).pack(side="left")

        self.games_list_frame = ctk.CTkFrame(c3, fg_color="transparent")
        self.games_list_frame.pack(fill="x", padx=18, pady=14)
        self._reload_games_list()

    def _reload_games_list(self):
        for w in self.games_list_frame.winfo_children():
            w.destroy()
        for nome in games.load_config()["processos"]:
            r = ctk.CTkFrame(self.games_list_frame, fg_color=ROW, corner_radius=8)
            r.pack(fill="x", pady=3)
            ctk.CTkLabel(r, text=nome, text_color=TEXT, font=("Consolas", 11)).pack(side="left", padx=12, pady=6)
            ctk.CTkButton(r, text="Remover", width=70, height=24, fg_color="transparent", hover_color=CARD_HOVER,
                          text_color=WARN, font=("Segoe UI", 10),
                          command=lambda n=nome: self._remove_game(n)).pack(side="right", padx=8, pady=4)

    def _add_game(self):
        nome = self.entry_game.get().strip()
        if not nome:
            return
        games.add_game(nome)
        self.entry_game.delete(0, "end")
        self._reload_games_list()
        self.log(f"'{nome}' adicionado à lista de jogos.")

    def _remove_game(self, nome):
        games.remove_game(nome)
        self._reload_games_list()
        self.log(f"'{nome}' removido da lista de jogos.")

    def _refresh_processes(self):
        procs = games.list_running_processes()
        self._proc_map = {f"{name}  (PID {pid})": pid for pid, name in procs if name}
        self.combo_proc.configure(values=list(self._proc_map.keys()))
        if self._proc_map:
            self.combo_proc.set(list(self._proc_map.keys())[0])

    def _boost_selected(self):
        sel = self.combo_proc.get()
        pid = self._proc_map.get(sel)
        if not pid:
            messagebox.showinfo("LCS BOOST", "Escolha um processo na lista.")
            return
        ok, msg = games.boost_process(pid, realtime=self.var_realtime.get())
        self.log(msg)

    def _enable_game_mode(self):
        run_async(lambda: games.enable_windows_game_mode(True),
                  lambda r: self.log("Modo de Jogo do Windows ativado." if r[0] else f"Falha: {r[1]}"))

    def _toggle_monitor(self):
        if self.monitor._thread and self.monitor._thread.is_alive():
            self.monitor.stop()
            self.btn_monitor.configure(text="▶  Iniciar monitor de jogos")
        else:
            self.monitor.realtime = self.var_realtime.get()
            self.monitor.start()
            self.btn_monitor.configure(text="■  Parar monitor de jogos")

    # ---------------- pagina Otimizacao ----------------
    def _build_page_opt(self):
        page = self._new_page("opt")

        c1 = card(page)
        c1.pack(fill="x", pady=(0, 14))
        section_title(c1, "Plano de energia do Windows").pack(anchor="w", padx=18, pady=(16, 8))
        row = ctk.CTkFrame(c1, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 18))
        primary_button(row, "Desempenho máximo", lambda: self._set_plan("desempenho_maximo")).pack(side="left", padx=(0, 8))
        primary_button(row, "Alto desempenho", lambda: self._set_plan("alto_desempenho")).pack(side="left", padx=(0, 8))
        ghost_button(row, "Restaurar equilibrado", lambda: self._set_plan("equilibrado")).pack(side="left")

        c2 = card(page)
        c2.pack(fill="x", pady=(0, 14))
        section_title(c2, "Overclock").pack(anchor="w", padx=18, pady=(16, 4))
        hint(c2, "O LCS BOOST não aplica overclock sozinho — mudar clock/voltagem de CPU/GPU sem cuidado "
                 "pode travar o PC ou danificar o hardware. Em vez disso, ele abre o utilitário oficial do "
                 "fabricante já instalado no seu PC (MSI Afterburner, Ryzen Master, Intel XTU, GPU Tweak).").pack(
            anchor="w", padx=18)
        ghost_button(c2, "Procurar e abrir utilitário instalado", self._find_oc_tool).pack(
            anchor="w", padx=18, pady=16)

        c3 = card(page)
        c3.pack(fill="x", pady=(0, 14))
        section_title(c3, "Inicialização do Windows").pack(anchor="w", padx=18, pady=(16, 4))
        hint(c3, "Equivalente real da aba 'Inicialização' do msconfig.").pack(anchor="w", padx=18)
        row2 = ctk.CTkFrame(c3, fg_color="transparent")
        row2.pack(fill="x", padx=18, pady=10)
        ghost_button(row2, "Listar programas de inicialização", self._list_startup).pack(side="left")

        self.startup_list_frame = ctk.CTkFrame(c3, fg_color="transparent")
        self.startup_list_frame.pack(fill="x", padx=18, pady=(0, 16))

    def _set_plan(self, mode):
        run_async(lambda: optimization.set_power_plan(mode),
                  lambda r: self.log(r[1] if r[0] else f"Falha ao aplicar plano: {r[1]}"))

    def _find_oc_tool(self):
        tools = optimization.find_installed_oc_tools()
        if not tools:
            self.log("Nenhum utilitário de overclock conhecido foi encontrado instalado neste PC.")
            return
        path, name = tools[0]
        ok, msg = optimization.launch_oc_tool(path)
        self.log(f"Abrindo {name}..." if ok else f"Falha ao abrir {name}: {msg}")

    def _list_startup(self):
        for w in self.startup_list_frame.winfo_children():
            w.destroy()
        itens = [(i, True) for i in optimization.list_startup_items()] + \
                [(i, False) for i in optimization.list_disabled_startup_items()]
        if not itens:
            ctk.CTkLabel(self.startup_list_frame, text="Nenhum item encontrado.", text_color=MUTED).pack(anchor="w")
            return
        for item, ativo in itens:
            r = Row(self.startup_list_frame, item["nome"], item["comando"][:70],
                    badge="ATIVO" if ativo else "DESATIVADO", badge_color=OK if ativo else MUTED)
            r.pack(fill="x", pady=4)
            if ativo:
                btn = ctk.CTkButton(r.actions, text="Desativar", width=90, height=28, fg_color="transparent",
                                     hover_color=CARD_HOVER, text_color=WARN, border_width=1, border_color=BORDER,
                                     font=("Segoe UI", 10),
                                     command=lambda h=item["hive"], n=item["nome"]: self._disable_startup(h, n))
            else:
                btn = ctk.CTkButton(r.actions, text="Reativar", width=90, height=28, fg_color="transparent",
                                     hover_color=CARD_HOVER, text_color=OK, border_width=1, border_color=BORDER,
                                     font=("Segoe UI", 10),
                                     command=lambda h=item["hive"], n=item["nome"]: self._enable_startup(h, n))
            btn.pack(side="left")

    def _disable_startup(self, hive, nome):
        ok, msg = optimization.disable_startup_item(hive, nome)
        self.log(msg)
        self._list_startup()

    def _enable_startup(self, hive, nome):
        ok, msg = optimization.enable_startup_item(hive, nome)
        self.log(msg)
        self._list_startup()

    # ---------------- pagina Ping/Rota ----------------
    def _build_page_net(self):
        page = self._new_page("net")

        c1 = card(page)
        c1.pack(fill="x", pady=(0, 14))
        section_title(c1, "Melhor servidor DNS (latência)").pack(anchor="w", padx=18, pady=(16, 4))
        hint(c1, "A rota física até o servidor do jogo depende do seu provedor de internet — nenhum "
                 "programa local consegue trocar isso. O que ajuda de fato é testar qual DNS responde mais "
                 "rápido e aplicá-lo.").pack(anchor="w", padx=18)
        ghost_button(c1, "Testar latência dos DNS", self._test_dns).pack(anchor="w", padx=18, pady=12)

        self.dns_list_frame = ctk.CTkFrame(c1, fg_color="transparent")
        self.dns_list_frame.pack(fill="x", padx=18)

        row = ctk.CTkFrame(c1, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=16)
        primary_button(row, "Aplicar DNS mais rápido encontrado", self._apply_best_dns).pack(side="left")

        c2 = card(page)
        c2.pack(fill="x", pady=(0, 14))
        section_title(c2, "Manutenção de rede").pack(anchor="w", padx=18, pady=(16, 8))
        row2 = ctk.CTkFrame(c2, fg_color="transparent")
        row2.pack(fill="x", padx=18, pady=(0, 18))
        ghost_button(row2, "Limpar cache DNS", self._flush_dns).pack(side="left", padx=(0, 8))
        ghost_button(row2, "Resetar Winsock", self._reset_winsock).pack(side="left", padx=(0, 8))
        ghost_button(row2, "Desativar algoritmo de Nagle", self._disable_nagle).pack(side="left")

    def _test_dns(self):
        self.log("Testando latência dos servidores DNS...")
        for w in self.dns_list_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.dns_list_frame, text="Testando...", text_color=MUTED).pack(anchor="w", pady=6)

        def done(resultados):
            for w in self.dns_list_frame.winfo_children():
                w.destroy()
            self._dns_results = resultados
            for r in resultados:
                status = f"{r['media']} ms  •  perda {r['perda']}%" if r["ok"] else "sem resposta"
                cor = OK if (r["ok"] and r["media"] is not None and r["media"] < 60) else (
                    ACCENT2 if r["ok"] else WARN)
                row = Row(self.dns_list_frame, f"{r['nome']}", r["host"], badge=status, badge_color=cor)
                row.pack(fill="x", pady=4)
            self.log("Teste de latência concluído.")

        run_async(network.test_dns_latency, done)

    def _apply_best_dns(self):
        if not getattr(self, "_dns_results", None):
            messagebox.showinfo("LCS BOOST", "Teste a latência primeiro.")
            return
        melhor = next((r for r in self._dns_results if r["ok"]), None)
        if not melhor:
            self.log("Nenhum DNS respondeu ao teste.")
            return
        adapters = network.get_active_adapters()
        if not adapters:
            self.log("Nenhum adaptador de rede ativo encontrado.")
            return

        def apply_all():
            return [network.set_dns(a, melhor["host"]) for a in adapters]

        def done(_):
            self.log(f"DNS '{melhor['nome']}' ({melhor['host']}) aplicado em: {', '.join(adapters)}.")

        run_async(apply_all, done)

    def _flush_dns(self):
        run_async(network.flush_dns, lambda r: self.log(r[1] if r[0] else f"Falha: {r[1]}"))

    def _reset_winsock(self):
        run_async(network.reset_winsock, lambda r: self.log(r[1]))

    def _disable_nagle(self):
        run_async(network.disable_nagle_algorithm, lambda r: self.log(r[1]))

    # ---------------- pagina Firewall/Seguranca ----------------
    def _build_page_sec(self):
        page = self._new_page("sec")

        warn = card(page)
        warn.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(warn, text="⚠  Desativar proteções reduz a segurança do seu PC. Use só se tiver certeza "
                                 "do motivo e reative depois.", text_color=WARN, font=("Segoe UI", 12, "bold"),
                     wraplength=640, justify="left", anchor="w").pack(anchor="w", padx=18, pady=14)

        c1 = card(page)
        c1.pack(fill="x", pady=(0, 14))
        section_title(c1, "Firewall do Windows").pack(anchor="w", padx=18, pady=(16, 8))
        row = ctk.CTkFrame(c1, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 18))
        primary_button(row, "Ativar Firewall", lambda: self._set_firewall(True)).pack(side="left", padx=(0, 8))
        primary_button(row, "Desativar Firewall", lambda: self._set_firewall(False), danger=True).pack(side="left")

        c2 = card(page)
        c2.pack(fill="x", pady=(0, 14))
        section_title(c2, "Windows Defender (proteção em tempo real)").pack(anchor="w", padx=18, pady=(16, 8))
        row2 = ctk.CTkFrame(c2, fg_color="transparent")
        row2.pack(fill="x", padx=18)
        primary_button(row2, "Ativar Defender", lambda: self._set_defender(True)).pack(side="left", padx=(0, 8))
        primary_button(row2, "Desativar Defender", lambda: self._set_defender(False), danger=True).pack(side="left")
        hint(c2, "Se a desativação falhar, a 'Proteção contra adulteração' do Windows está bloqueando — "
                 "desative-a manualmente em Configurações > Privacidade e segurança > Segurança do Windows, "
                 "e tente de novo.").pack(anchor="w", padx=18, pady=(10, 18))

    def _set_firewall(self, enabled):
        acao = "ativar" if enabled else "DESATIVAR"
        if not messagebox.askyesno("LCS BOOST", f"Tem certeza que quer {acao} o Firewall do Windows?"):
            return
        run_async(lambda: security.set_firewall(enabled), lambda r: self.log(r[1]))

    def _set_defender(self, enabled):
        acao = "ativar" if enabled else "DESATIVAR"
        if not messagebox.askyesno("LCS BOOST", f"Tem certeza que quer {acao} a proteção em tempo real do Defender?"):
            return
        run_async(lambda: security.set_defender_realtime(enabled), lambda r: self.log(r[1]))


def run():
    app = App()
    app.mainloop()
