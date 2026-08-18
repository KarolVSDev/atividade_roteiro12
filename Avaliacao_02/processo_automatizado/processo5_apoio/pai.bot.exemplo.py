"""Exemplo mínimo de integração do Processo 5.

Substitua `resultado_processo4` pela saída real do Processo 4 da equipe.
"""

from processo5.relatorios import executar_processo5


def main() -> None:
    # Exemplo de contrato vindo do Processo 4.
    resultado_processo4 = [
        {
            "id_cliente": "C001",
            "status": "sucesso",
            "duracao_segundos": 2.4,
            "mensagem": "Cadastro e atendimento concluídos",
            "erro": None,
        },
        {
            "id_cliente": "C002",
            "status": "falha",
            "duracao_segundos": 1.1,
            "mensagem": "Atendimento não concluído",
            "erro": "Timeout da integração",
        },
    ]

    resultado_processo5 = executar_processo5(resultado_processo4)
    print("Processo 5 concluído")
    print(f"Versão: {resultado_processo5['versao']}")
    print(f"Métricas: {resultado_processo5['metricas']}")
    print(f"Arquivos: {resultado_processo5['arquivos']}")


if __name__ == "__main__":
    main()
