# LCS BOOST

Programa (`LCS BOOST.exe`) com 4 abas, feito em Python + Tkinter e empacotado com PyInstaller.

## Como usar
- Dê duplo clique em `dist\LCS BOOST.exe`. O Windows vai pedir permissão de
  Administrador (UAC) — aceite, pois quase todas as funções precisam disso.

## O que cada aba faz de verdade

### Jogos
- Monitora processos e, quando um jogo da lista abre, aumenta a prioridade
  dele no Windows (Alta ou Tempo Real), libera todos os núcleos de CPU para
  ele e ativa o Modo de Jogo do Windows.
- **Não existe forma genérica de forçar "gráficos no mínimo" em qualquer
  jogo** — cada jogo guarda isso num formato próprio, e editar o config de
  jogos com anti-cheat (Valorant, CS2, etc.) pode gerar banimento. Por isso
  a aba deixa você criar manualmente, em `config/games.json`, um "perfil"
  apontando para o arquivo de config de um jogo específico seu e as linhas
  a trocar — isso é opcional e sob seu controle.

### Otimização
- Troca o plano de energia do Windows (Equilibrado / Alto Desempenho /
  Desempenho Máximo).
- Lista, desativa e reativa programas de inicialização (o equivalente real
  da aba "Inicialização" do msconfig).
- **Overclock real não é aplicado automaticamente** — mudar clock/voltagem
  de CPU/GPU sem cuidado pode travar o PC ou danificar o hardware. O botão
  dessa seção procura e abre o utilitário oficial já instalado (MSI
  Afterburner, Ryzen Master, Intel XTU, GPU Tweak) para você ajustar com
  segurança.

### Ping / Rota
- Testa a latência para vários DNS públicos (Cloudflare, Google, Quad9,
  OpenDNS, NordVPN) e aplica o mais rápido.
- Limpa cache de DNS, reseta o Winsock e desativa o algoritmo de Nagle
  (ajuste clássico de baixa latência para jogos online).
- **Honestidade**: a rota física até o servidor do jogo é controlada pelo
  seu provedor de internet, não pelo seu PC — nenhum programa local "escolhe
  uma rota melhor" de verdade. O que este app faz é o que é realmente
  possível e verificável a partir da sua máquina.

### Firewall / Segurança
- Ativa/desativa o Firewall do Windows e a proteção em tempo real do
  Windows Defender, sempre com confirmação antes de desativar.
- Se a "Proteção contra adulteração" do Windows estiver ligada, ela bloqueia
  a desativação do Defender por script — o app avisa isso na tela.

## Recompilar o .exe
```powershell
py -m pip install pyinstaller psutil pywin32
py -m PyInstaller --noconfirm --onefile --windowed --uac-admin --name "LCS BOOST" --add-data "config;config" main.py
```
O executável final fica em `dist\LCS BOOST.exe`.
