# Guia de implementação — Processo 5: Relatórios e Gerência

## 1. O que o Processo 5 precisa fazer

De acordo com o roteiro da atividade, o Processo 5 recebe a saída do Processo 4 e encerra o fluxo da automação. Ele deve consolidar os resultados, gerar métricas e indicadores, registrar logs, permitir o monitoramento da execução e manter versões dos relatórios gerados. O fluxo esperado é: **Processo 4 → Consolidação → Métricas e indicadores → Relatório gerencial → Processo concluído**. [1]

O Processo 5 não deve refazer os Processos 1 a 4. A responsabilidade dele é transformar os atendimentos/resultados recebidos em uma visão gerencial compreensível e verificável.

## 2. Contrato de entrada recomendado

Combine com a pessoa responsável pelo Processo 4 que a saída seja uma lista de dicionários. Os nomes dos campos podem ser ajustados ao projeto, mas uma estrutura simples é:

```python
[
    {
        "id_cliente": "C001",
        "status": "sucesso",
        "duracao_segundos": 2.4,
        "mensagem": "Cadastro e atendimento concluídos",
        "erro": None
    },
    {
        "id_cliente": "C002",
        "status": "falha",
        "duracao_segundos": 1.1,
        "mensagem": "Não foi possível concluir o atendimento",
        "erro": "Timeout da integração"
    }
]
```

O ponto mais importante é haver um campo de status consistente. Recomenda-se usar `sucesso`, `falha` e `pendente`. Se o Processo 4 já usa nomes diferentes, altere apenas o adaptador da função `normalizar_registro`.

## 3. Estrutura sugerida

```text
projeto-hyperautomation/
├── processo5/
│   ├── __init__.py
│   ├── relatorios.py
│   ├── logs/
│   └── saidas/
├── tests/
│   └── test_processo5.py
└── pai.bot.py
```

A pasta `saidas/` deve guardar os relatórios versionados em JSON e CSV. A pasta `logs/` deve guardar o log da execução do Processo 5. Se o projeto da equipe já possui pastas centrais para logs e resultados, mantenha a estrutura existente e altere os caminhos no código.

## 4. Métricas mínimas para demonstrar

Para atender ao roteiro, o relatório deve apresentar pelo menos o total de registros processados, a quantidade e o percentual de sucessos, falhas e pendências, além da duração média quando essa informação estiver disponível. Também é útil registrar o horário da execução, a versão do relatório e o nome dos arquivos gerados.

| Indicador | Descrição |
|---|---|
| Total processado | Quantidade total de resultados recebidos do Processo 4. |
| Sucessos | Registros com status `sucesso`. |
| Falhas | Registros com status `falha`. |
| Pendências | Registros com status `pendente` ou equivalente. |
| Taxa de sucesso | `sucessos / total × 100`, quando o total for maior que zero. |
| Duração média | Média de `duracao_segundos`, quando houver valores válidos. |

## 5. Como integrar ao `pai.bot.py`

O arquivo principal deve chamar o Processo 5 depois do Processo 4 e passar o retorno recebido, em vez de criar dados fictícios dentro do próprio Processo 5:

```python
from processo5.relatorios import executar_processo5

# ... execução dos Processos 1, 2, 3 e 4 ...
resultado_processo4 = executar_processo4(resultado_processo3)
resultado_processo5 = executar_processo5(resultado_processo4)

print("Processo 5 concluído")
print(resultado_processo5["arquivos"])
```

Os nomes das funções dos Processos 1 a 4 devem ser substituídos pelos nomes reais do projeto da equipe.

## 6. Como validar

Execute localmente os testes com:

```bash
python -m pytest -v
```

Depois, execute a solução completa:

```bash
python pai.bot.py
```

Confira se o terminal informa a conclusão, se a pasta `processo5/saidas/` contém um JSON e um CSV versionados e se a pasta `processo5/logs/` contém o registro da execução. A validação final da atividade também deve mostrar que o fluxo foi executado no container publicado, seguindo Processo 1 → Processo 2 → Processo 3 → Processo 4 → Processo 5. [1]

## 7. Versionamento dos resultados

O código deve ser versionado pelo Git, com um commit específico, por exemplo:

```bash
git add processo5 tests/test_processo5.py pai.bot.py
git commit -m "feat: implementa processo 5 de relatorios e metricas"
git push
```

Além do versionamento do código, o Processo 5 cria versões dos relatórios com nomes como `relatorio_v001.json` e `relatorio_v001.csv`. O arquivo `manifest_v001.json` registra a versão, a data, os arquivos e o hash SHA-256 do JSON, permitindo comprovar a integridade do resultado.

## 8. Critérios de aceite do Processo 5

| Critério | Evidência esperada |
|---|---|
| Consolidação | O Processo 5 recebe a saída do Processo 4 e informa a quantidade de registros. |
| Métricas | O relatório apresenta total, sucessos, falhas, pendências, taxa de sucesso e duração média. |
| Monitoramento | O terminal e o log mostram início, quantidade processada, versão gerada e conclusão/erro. |
| Logs | Existe um arquivo `.log` com data e nível da execução. |
| Versionamento | Existem arquivos `relatorio_vNNN.json`, `relatorio_vNNN.csv` e manifesto. |
| Integração | `pai.bot.py` chama o Processo 5 depois do Processo 4. |
| Testes | `pytest` valida pelo menos o cálculo das métricas e a criação dos arquivos. |
| Container | O Processo 5 é executado quando a imagem publicada é iniciada por `docker run`. |

## 9. O que apresentar ao grupo/professor

Na demonstração, explique que o Processo 5 é a camada de fechamento gerencial: ele não altera o atendimento, apenas consolida o que ocorreu, calcula indicadores, registra a execução e preserva uma versão auditável do relatório. Mostre o código, a chamada no `pai.bot.py`, a saída do `pytest`, os arquivos gerados e, por fim, a execução integrada no container.

### Referência

[1]: /home/ubuntu/upload/ROTEIRO13–Integração,CICD,ContainerizaçãoePublicaçãodaAutomaçãonoGHCR.pdf "Roteiro 13 — Integração, CI/CD, Containerização e Publicação da Automação no GHCR", especialmente páginas 3–5, 16–19 e 34–45.
