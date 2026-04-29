# Stack Sentinel Lab

Laboratorio da Semana 3 para construir, em camadas, o **Stack Sentinel**: um agente que investiga tickets, builds, documentacao operacional e saude de servicos usando MCP com FastMCP e LangGraph.

## Como rodar

Use sempre os comandos abaixo a partir da raiz do repositorio:

```bash
python3.10 run.py doctor
python3.10 run.py setup
python3.10 run.py mock-api
python3.10 run.py test ex00
python3.10 run.py test all
python3.10 run.py demo
```

O projeto usa FastMCP e LangGraph, entao requer Python 3.10 ou superior.

No Windows, se `python` nao funcionar:

```bash
py run.py doctor
```

## Contratos que nao devem ser alterados

Os alunos podem implementar o corpo das funcoes indicadas nos enunciados dos exercicios, mas nao devem alterar:

- nomes de arquivos e modulos;
- nomes de funcoes publicas;
- parametros das funcoes;
- tipos e chaves dos dicionarios retornados;
- nomes das tools, resources e prompts;
- IDs dos dados mockados usados nos testes;
- arquivos em `tests/`, exceto se o professor pedir explicitamente.

## Mock API

A mock API e um servico FastAPI real. A logica e mockada, mas os endpoints HTTP existem de verdade e leem dados locais em `stack_sentinel/data/*.json`.

Para subir:

```bash
python run.py setup
python run.py mock-api
```

Depois acesse:

```text
http://127.0.0.1:8000/docs
```

Endpoints principais:

- `GET /health`
- `GET /tickets`
- `GET /tickets/{ticket_id}`
- `GET /builds`
- `GET /builds/{build_id}`
- `GET /docs`
- `GET /docs/{slug}`
- `GET /services`
- `GET /services/{service_name}/health`
- `GET /incidents`
- `GET /incidents/{incident_id}`

## Sequencia de exercicios

- Ex00: validar setup, imports e dados.
- Ex01: explorar mock service e health check.
- Ex02: criar `fetch_ticket_context`.
- Ex03: criar MCP server minimo.
- Ex04: registrar primeira tool MCP.
- Ex04.5: refatorar a exposicao MCP para FastMCP.
- Ex05: criar e registrar tool de build no FastMCP.
- Ex06: criar resources MCP e expo-los no FastMCP.
- Ex07: criar prompt MCP e expo-lo no FastMCP.
- Ex08: criar grafo minimo.
- Ex09: definir `AgentState`.
- Ex10: criar node de classificacao.
- Ex11: configurar routing condicional.
- Ex12: consultar ticket via MCP no node.
- Ex13: consultar build via MCP no node.
- Ex14: usar resource/prompt no fluxo.
- Ex15: gerar resposta final.
- Ex16: integracao ponta a ponta.

## LLM real opcional

Os exercicios obrigatorios usam `FakeLLMClient`, porque ele torna os testes deterministicos e nao depende de chave, rede ou custo.

Se voce ja tiver uma chave pronta e quiser experimentar uma LLM real, existe o scaffolding opcional em:

```text
stack_sentinel/llm/provider_client.py
```

Essa trilha nao e necessaria para passar nos testes. Ao implementar uma LLM real, preserve o contrato de `classify_intent`: retornar apenas `ticket`, `build`, `docs` ou `unknown`.
