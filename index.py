import time
import json
import os
from datetime import datetime

DATA_FILE = "progresso.json"
MARCOS = [10, 15, 20, 30, 50, 100, 200, 300, 500, 1000]  # em horas

def limpar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return {
            "total_segundos": 0,
            "gemas": 0,
            "recompensas_conquistadas": [],
            "sessoes": []
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

def estudar():
    print("\n📚 Iniciando sessão de estudo. Pressione ENTER para encerrar.")
    inicio = time.time()
    input()
    fim = time.time()
    duracao = fim - inicio

    dados = carregar_dados()
    dados["total_segundos"] += duracao

    # Salvar sessão
    dados["sessoes"].append({
        "inicio": datetime.fromtimestamp(inicio).isoformat(),
        "fim": datetime.fromtimestamp(fim).isoformat(),
        "duracao_segundos": duracao
    })

    # Verificar marcos atingidos
    total_horas = dados["total_segundos"] / 3600
    novas_recompensas = [
        m for m in MARCOS
        if m <= total_horas and m not in dados["recompensas_conquistadas"]
    ]

    if novas_recompensas:
        for r in novas_recompensas:
            print(f"🎉 Parabéns! Você atingiu o marco de {r} horas!")
        dados["recompensas_conquistadas"].extend(novas_recompensas)
        dados["gemas"] += len(novas_recompensas)
        print(f"💎 Você ganhou {len(novas_recompensas)} gema(s)!")

    salvar_dados(dados)
    print(f"⏱️ Tempo total estudado: {total_horas:.2f} horas.")

def ver_historico():
    dados = carregar_dados()
    print("\n--- HISTÓRICO DE SESSÕES ---")
    for i, sessao in enumerate(dados["sessoes"], 1):
        inicio = datetime.fromisoformat(sessao["inicio"]).strftime("%d/%m/%Y %H:%M")
        fim = datetime.fromisoformat(sessao["fim"]).strftime("%H:%M")
        duracao = formatar_tempo(sessao["duracao_segundos"])
        print(f"{i}. {inicio} - {fim} ({duracao})")

    print(f"\n⏳ Total estudado: {formatar_tempo(dados['total_segundos'])}")
    print(f"💎 Gemas disponíveis: {dados['gemas']}")
    print(f"🏆 Recompensas conquistadas: {dados['recompensas_conquistadas']}")

def trocar_gemas():
    dados = carregar_dados()
    print(f"\n💎 Você tem {dados['gemas']} gema(s).")
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

def menu():
    while True:
        limpar_terminal()
        print("\n=== MENU ===")
        print("1. Iniciar sessão de estudo")
        print("2. Ver histórico")
        print("3. Trocar gemas por recompensa")
        print("4. Sair")
        opcao = input("Escolha: ")

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
            print("👋 Até a próxima! Continue focado!")
            break
        else:
            print("Opção inválida.")
            input("\nPressione ENTER para tentar novamente.")

if __name__ == "__main__":
    menu()
