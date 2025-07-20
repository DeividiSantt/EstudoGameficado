import time
import json
import os
from datetime import datetime, timedelta
from git import Repo

DATA_FILE = "progresso.json"
MARCOS = list(range(1, 1001))  # Marcos de 1h até 1000h

def commit_git(mensagem):
    try:
        dados = carregar_dados()
        token = dados.get("token")
        if not token:
            print("⚠️ Token não encontrado no arquivo progresso.json")
            return

        caminho_repo = os.path.dirname(os.path.abspath(__file__))
        repo = Repo(caminho_repo)

        remote_url = f"https://{token}@github.com/DeividiSantt/EstudoGameficado"
        repo.remote(name='origin').set_url(remote_url)

        repo.git.add(update=True)
        repo.git.commit(allow_empty=True, m=mensagem)
        repo.remote(name='origin').push()
        print("✅ Commit enviado para o GitHub.")
    except Exception as e:
        print(f"⚠️ Erro ao enviar commit: {e}")

def limpar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return {
            "total_segundos": 0,
            "gemas": 0,
            "recompensas_conquistadas": [],
            "sessoes": [],
            "exercicios": 0,
            "projetos": 0
        }
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(DATA_FILE, "w") as f:
        json.dump(dados, f, indent=2)

def formatar_tempo(segundos):
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    return f"{horas}h {minutos}min"

def calcular_horas_semana(dados):
    agora = datetime.now()
    inicio_semana = agora - timedelta(days=agora.weekday())
    total_segundos = 0
    for sessao in dados["sessoes"]:
        inicio = datetime.fromisoformat(sessao["inicio"])
        if inicio >= inicio_semana:
            total_segundos += sessao["duracao_segundos"]
    return total_segundos

def verificar_commit_por_hora(dados):
    total_horas = int(dados["total_segundos"] // 3600)
    ultima_commitada = dados.get("ultima_hora_commit", 0)

    if total_horas > ultima_commitada:
        commit_git(f"⏱️ Estudo acumulado: {total_horas}h")
        dados["ultima_hora_commit"] = total_horas
        salvar_dados(dados)

def estudar():
    print("\n📚 Iniciando sessão de estudo. Pressione ENTER para encerrar.")
    inicio = time.time()
    input()
    fim = time.time()
    duracao = fim - inicio

    dados = carregar_dados()
    dados["total_segundos"] += duracao

    dados["sessoes"].append({
        "inicio": datetime.fromtimestamp(inicio).isoformat(),
        "fim": datetime.fromtimestamp(fim).isoformat(),
        "duracao_segundos": duracao
    })

    total_horas = dados["total_segundos"] / 3600
    novas_recompensas = [
        m for m in MARCOS
        if m <= total_horas and m not in dados["recompensas_conquistadas"]
    ]

    if novas_recompensas:
        for r in novas_recompensas:
            print(f"🎉 Parabéns! Você atingiu o marco de {r} hora(s)!")
        dados["recompensas_conquistadas"].extend(novas_recompensas)
        dados["gemas"] += len(novas_recompensas)
        print(f"💎 Você ganhou {len(novas_recompensas)} gema(s)!")

    salvar_dados(dados)
    verificar_commit_por_hora(dados)
    print(f"⏱️ Tempo total estudado: {formatar_tempo(dados['total_segundos'])}")

def ver_historico():
    dados = carregar_dados()
    print("\n--- HISTÓRICO DE SESSÕES ---")
    if not dados["sessoes"]:
        print("Nenhuma sessão registrada ainda.")
    else:
        for i, sessao in enumerate(dados["sessoes"], 1):
            inicio = datetime.fromisoformat(sessao["inicio"]).strftime("%d/%m/%Y %H:%M")
            fim = datetime.fromisoformat(sessao["fim"]).strftime("%H:%M")
            duracao = formatar_tempo(sessao["duracao_segundos"])
            print(f"{i}. {inicio} - {fim} ({duracao})")

    horas_semana_segundos = calcular_horas_semana(dados)
    horas_semana = int(horas_semana_segundos // 3600)
    minutos_semana = int((horas_semana_segundos % 3600) // 60)

    print(f"\n⏳ Total estudado: {formatar_tempo(dados['total_segundos'])}")
    print(f"📆 Horas estudadas nesta semana: {horas_semana}h {minutos_semana}min")
    print(f"💎 Gemas disponíveis: {dados['gemas']:.1f}")
    print(f"🏆 Recompensas conquistadas: {dados['recompensas_conquistadas']}")
    print(f"📝 Exercícios feitos: {dados['exercicios']}")
    print(f"🚀 Projetos feitos: {dados['projetos']}")

def trocar_gemas():
    dados = carregar_dados()
    print(f"\n💎 Você tem {dados['gemas']:.1f} gema(s).")
    print("Escolha uma recompensa:")
    print("1. Jogar videogame (2 gemas)")
    print("2. Ver série (1 gema)")
    print("3. Assistir vídeo (1 gema)")
    print("4. Voltar")
    escolha = input("Opção: ")

    recompensas = {
        "1": ("Jogar videogame", 2),
        "2": ("Ver série", 1),
        "3": ("Assistir vídeo", 1)
    }

    if escolha in recompensas:
        nome, custo = recompensas[escolha]
        if dados["gemas"] >= custo:
            dados["gemas"] -= custo
            salvar_dados(dados)
            print(f"✅ Você trocou {custo} gema(s) por: {nome}")
        else:
            print("⚠️ Gemas insuficientes.")
    elif escolha == "4":
        return
    else:
        print("Opção inválida.")

def registrar_bonus():
    dados = carregar_dados()
    print("\n📝 Registrar exercícios e projetos concluídos.")
    try:
        ex = int(input("Quantos exercícios você fez? "))
        pr = int(input("Quantos projetos você fez? "))
        if ex < 0 or pr < 0:
            print("Número inválido, use valores positivos.")
            return
    except ValueError:
        print("Entrada inválida, digite números inteiros.")
        return

    dados["exercicios"] += ex
    dados["projetos"] += pr

    gemas_bonus = ex * 0.2 + pr * 3
    dados["gemas"] += gemas_bonus

    salvar_dados(dados)
    print(f"🎉 Você ganhou {gemas_bonus:.1f} gema(s) de bônus!")

def sincronizar_gemas(dados):
    total_horas = dados["total_segundos"] / 3600
    novos = [m for m in MARCOS if m <= total_horas and m not in dados["recompensas_conquistadas"]]
    if novos:
        dados["recompensas_conquistadas"].extend(novos)
        dados["gemas"] += len(novos)
        salvar_dados(dados)
        print(f"🔄 Sincronização: adicionadas {len(novos)} gema(s) pelos marcos antigos: {novos}")

def menu():
    while True:
        limpar_terminal()
        dados = carregar_dados()
        sincronizar_gemas(dados)
        horas_total = int(dados['total_segundos'] // 3600)
        minutos_total = int((dados['total_segundos'] % 3600) // 60)

        print("\n=== MENU ===")
        print("1. Iniciar sessão de estudo")
        print("2. Ver histórico")
        print("3. Trocar gemas por recompensa")
        print("4. Registrar exercícios/projetos concluídos")
        print("5. Sair")

        print(f"\n⏳ Total de horas estudadas: {horas_total}h {minutos_total}min")
        print(f"💎 Gemas disponíveis: {dados['gemas']:.1f}")
        print(f"📝 Exercícios completos: {dados['exercicios']} | 🚀 Projetos completos: {dados['projetos']}")

        opcao = input("\nEscolha: ")

        if opcao == "1":
            estudar()
            input("\nPressione ENTER para voltar ao menu.")
        elif opcao == "2":
            ver_historico()
            input("\nPressione ENTER para voltar ao menu.")
        elif opcao == "3":
            trocar_gemas()
            input("\nPressione ENTER para voltar ao menu.")
        elif opcao == "4":
            registrar_bonus()
            input("\nPressione ENTER para voltar ao menu.")
        elif opcao == "5":
            print("👋 Até a próxima! Continue focado!")
            break
        else:
            print("Opção inválida.")
            input("\nPressione ENTER para tentar novamente.")

if __name__ == "__main__":
    menu()
