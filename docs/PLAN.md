# Plano de ação do desenvolvimento

## Objetivo

Criar um scaffolding estável para que os alunos implementem o Stack Sentinel progressivamente, sem alterar contratos de entrada/saída nem testes.

## Decisões técnicas

- Usar apenas biblioteca padrão do Python para reduzir atrito.
- Introduzir MCP com `SimpleMCPServer` e `MCPClient` em memoria, depois refatorar a exposicao real para `FastMCP` a partir do Ex04.5.
- Simular LangGraph com um grafo simples e testável, preservando os conceitos de state, nodes e routing.
- Persistir dados mockados em JSON para facilitar leitura, edição e versionamento.
- Criar testes por exercício usando `unittest`, executados por `run.py`.

## Estrutura

```text
Semana3/src/
├── README.md
├── RULES.md
├── run.py
├── stack_sentinel/
│   ├── data/
│   ├── mock_api/
│   ├── clients/
│   ├── mcp_server/
│   ├── agent/
│   ├── llm/
│   └── shared/
└── tests/
```

## Contratos preservados

- Tools retornam dicionários com `ok`.
- AgentState é dicionário tipado com campos fixos.
- MCP server lista e chama capabilities por nome.
- Nodes recebem `state` e devolvem novo `state`.
- Routing retorna nomes de rotas estáveis.

## Estratégia de exercícios

Os arquivos incluem apenas assinaturas e contratos mínimos nos pontos de implementação. Os testes e os enunciados em `exercises/` documentam o comportamento esperado. O professor deve orientar os alunos a implementar um exercício por vez e rodar apenas o teste daquele exercício.
