# Guia do Professor — Stack Sentinel Lab

Este guia serve como referência rápida durante a aula. Ele assume que os alunos estão trabalhando no repositório do Stack Sentinel Lab e implementando um exercício por vez.

## Roteiro geral de condução

Para cada exercício, use o ciclo:

```text
1. Briefing — 3 a 5 min
2. Implementação — 10 a 15 min
3. Teste local — 2 min
4. Debug orientado — 5 a 8 min
5. Fechamento — 2 min
```

Comandos principais:

```bash
python run.py setup
python run.py doctor
python run.py mock-api
python run.py test exNN
python run.py test all
python run.py demo
```

Regra de ouro para os alunos:

```text
Leia exercises/exNN.md.
Edite apenas os arquivos indicados.
Rode python run.py test exNN.
Leia a falha como feedback de contrato.
```

## Diagnóstico rápido de falhas

| Sintoma | Provável causa | Ação |
|---|---|---|
| `ModuleNotFoundError` | Rodando fora da raiz ou setup faltando | `cd Semana3/src`, depois `python run.py doctor` |
| API não responde | Mock API não subiu ou porta ocupada | `python run.py mock-api --port 8010` |
| Teste diz `NotImplementedError` | Exercício ainda não implementado | Voltar ao arquivo indicado no enunciado |
| Assertion de chave ausente | Retorno não respeita contrato | Conferir nomes exatos das chaves |
| Retorno bruto da API aparece na tool | Falta normalização | Tool deve retornar apenas campos esperados |
| Rota cai em fallback | `intent` errada ou routing incorreto | Checar Ex10 e Ex11 |

## Modelo mental para repetir em aula

```text
Service responde dados.
Tool normaliza uma capacidade.
MCP Server expõe a capacidade.
MCP Client chama a capacidade.
LangGraph decide o fluxo.
State carrega evidências.
Teste valida o contrato.
```

## Mock API

A mock API é FastAPI real, com lógica mockada por arquivos JSON.

Subir:

```bash
python run.py setup
python run.py mock-api
```

Docs interativas:

```text
http://127.0.0.1:8000/docs
```

Endpoints úteis:

```text
GET /health
GET /tickets
GET /tickets/TCK-101
GET /builds/BLD-203
GET /docs/incident-response
GET /services/auth-service/health
GET /incidents/INC-9001
```

## Dia 1 — Setup, mock service e primeiro MCP server

### Ex00 — Setup e smoke test

Objetivo: validar estrutura, imports e dados.

Comando:

```bash
python run.py test ex00
```

Não há código a implementar.

Fechamento sugerido:

```text
Antes de construir agente, garantimos que o ambiente e os dados existem.
```

### Ex01 — Health check do mock service

Arquivo:

```text
stack_sentinel/clients/mock_service_client.py
```

Função:

```python
check_mock_service_health(client=None) -> bool
```

O que precisa acontecer:

- criar `MockServiceClient` se `client` for `None`;
- chamar `/health`;
- retornar `True` apenas se `ok is True`;
- retornar `False` em falhas controladas.

Erro comum:

```text
Retornar o dicionário inteiro em vez de booleano.
```

Fechamento:

```text
O service é externo ao agente. Primeiro validamos que ele responde.
```

### Ex02 — Primeira tool: ticket

Arquivo:

```text
stack_sentinel/mcp_server/tools.py
```

Função:

```python
fetch_ticket_context(ticket_id, client=None) -> dict
```

Retorno esperado em sucesso:

```python
{
    "ok": True,
    "id": "TCK-101",
    "summary": "...",
    "severity": "high",
    "service": "auth-service",
    "status": "open",
    "build_id": "BLD-203",
}
```

Ponto didático:

```text
Endpoint bruto vira contrato de capacidade.
```

Erros comuns:

- retornar `description` e payload completo;
- esquecer `build_id`;
- lançar exceção quando o ticket não existe.

### Ex03 — MCP server mínimo

Arquivo:

```text
stack_sentinel/mcp_server/server.py
```

Função:

```python
create_mcp_server() -> SimpleMCPServer
```

Contrato:

- `name == "stack-sentinel-mcp"`;
- `description` não vazia;
- `metadata["domain"] == "incident-investigation"`;
- `metadata["version"] == "0.1.0"`;
- listas vazias de tools/resources/prompts.

Ponto didático:

```text
O servidor primeiro existe; depois expõe capacidades.
```

### Ex04 — Registrar tool de ticket

Arquivo:

```text
stack_sentinel/mcp_server/server.py
```

Função:

```python
register_ticket_tool(server) -> SimpleMCPServer
```

Contrato:

- registrar `ToolDefinition`;
- nome `TICKET_TOOL_NAME`;
- handler `tools.fetch_ticket_context`;
- schema com `ticket_id` obrigatório;
- retornar o mesmo `server`.

Ponto didático:

```text
MCP Server não executa mágica. Ele mantém um catálogo de capacidades.
```

### Ex04.5 — Refatorar para FastMCP

Arquivo:

```text
stack_sentinel/mcp_server/fastmcp_server.py
```

Função:

```python
create_fastmcp_server()
```

Contrato:

- criar `FastMCP("stack-sentinel-mcp")`;
- registrar `fetch_ticket_context` com `@mcp.tool()`;
- delegar para `tools.fetch_ticket_context`;
- manter a regra de dominio fora do arquivo de servidor.

Ponto didático:

```text
SimpleMCPServer ajudou a enxergar o contrato; FastMCP é a exposição real.
```

## Dia 2 — Mais MCP e início do agente

### Ex05 — Tool de build

Arquivo:

```text
stack_sentinel/mcp_server/tools.py
stack_sentinel/mcp_server/fastmcp_server.py
```

Função:

```python
fetch_build_status(build_id, client=None) -> dict
```

Campos esperados:

```python
ok, id, status, service, branch, failed_step, log_excerpt
```

Ponto didático:

```text
Repetir o padrão confirma que tools são contratos reutilizáveis e podem ser expostos no FastMCP sem mover a regra de domínio.
```

Erro comum:

```text
Retornar `failed_step` ausente quando o build falhou.
```

### Ex06 — Resources

Arquivo:

```text
stack_sentinel/mcp_server/resources.py
stack_sentinel/mcp_server/fastmcp_server.py
```

Função:

```python
read_doc_resource(uri, client=None) -> dict
```

Contrato:

- validar `uri` em `RESOURCE_TO_SLUG`;
- buscar o doc por slug;
- retornar `ok`, `uri`, `title`, `content`;
- erro controlado para resource desconhecido.

Ponto didático:

```text
Tool faz algo. Resource dá contexto. Ambos podem ser capacidades MCP no FastMCP.
```

### Ex07 — Prompt MCP

Arquivo:

```text
stack_sentinel/mcp_server/prompts.py
stack_sentinel/mcp_server/fastmcp_server.py
```

Função:

```python
incident_triage_prompt(user_question, available_context) -> str
```

O texto deve conter a orientação para:

- resumir problema;
- citar severidade;
- sugerir próximo passo;
- não inventar dados;
- usar pergunta e contexto.

Ponto didático:

```text
Prompt MCP padroniza comportamento dentro de um domínio e também deve ser registrado no FastMCP.
```

### Ex08 — Grafo mínimo

Arquivo:

```text
stack_sentinel/agent/graph.py
```

Função:

```python
compile_minimal_graph() -> SimpleGraph
```

Contrato:

- criar `SimpleGraph`;
- adicionar pelo menos um node;
- `graph.run({"user_input": "ping"})["final_answer"] == "ping"`;
- preservar `user_input`.

Ponto didático:

```text
O grafo é uma sequência explícita de transformações de state.
```

### Ex09 — AgentState

Arquivo:

```text
stack_sentinel/agent/state.py
```

Função:

```python
create_initial_state(user_input) -> AgentState
```

Campos:

```text
user_input
intent
ticket_id
build_id
context
error
final_answer
```

Todos exceto `user_input` começam como `None`.

Ponto didático:

```text
State é contrato entre nodes, não memória mágica.
```

### Ex10 — Classificação de intenção

Arquivo:

```text
stack_sentinel/agent/nodes.py
```

Função:

```python
classify_intent_node(state, llm) -> AgentState
```

Contrato:

- chamar `llm.classify_intent`;
- aceitar apenas `ticket`, `build`, `docs`, `unknown`;
- converter respostas inválidas para `unknown`;
- retornar novo state sem mutar o original.

Ponto didático:

```text
FakeLLM testa fluxo e contrato, não inteligência.
```

## Dia 3 — Integração LangGraph + MCP

### Ex11 — Routing

Arquivo:

```text
stack_sentinel/agent/graph.py
```

Função:

```python
route_by_intent(state) -> str
```

Mapeamento:

```text
ticket -> fetch_ticket
build -> fetch_build
docs -> fetch_docs
outros -> fallback
```

Ponto didático:

```text
LangGraph/host decide caminho. MCP Client não decide sozinho.
```

### Ex12 — Node de ticket via MCP

Arquivo:

```text
stack_sentinel/agent/nodes.py
```

Função:

```python
fetch_ticket_node(state, mcp_client) -> AgentState
```

Fluxo:

```text
state/user_input -> ticket_id -> MCP Client -> tool -> context
```

Contrato:

- usar `state["ticket_id"]` se existir;
- senão extrair `TCK-000` do texto;
- chamar `mcp_client.call_tool(TICKET_TOOL_NAME, ...)`;
- preencher `context` em sucesso;
- preencher `error` em falha.

Ponto didático:

```text
O agente não monta JSON-RPC. Ele chama uma API de alto nível do MCP Client.
```

### Ex13 — Node de build via MCP

Arquivo:

```text
stack_sentinel/agent/nodes.py
```

Função:

```python
fetch_build_node(state, mcp_client) -> AgentState
```

Mesmo padrão do Ex12, usando:

```text
BUILD_TOOL_NAME
build_id
BLD-000
```

Ponto didático:

```text
O padrão de node é reaproveitável entre rotas.
```

### Ex14 — Resource e prompt no fluxo

Arquivo:

```text
stack_sentinel/agent/nodes.py
```

Função:

```python
fetch_docs_node(state, mcp_client) -> AgentState
```

Contrato:

- ler `INCIDENT_RESPONSE_RESOURCE`;
- obter `INCIDENT_TRIAGE_PROMPT`;
- passar `user_question` e `available_context`;
- salvar `context = {"resource": resource, "prompt": prompt}`.

Ponto didático:

```text
Nem toda rota precisa de tool. Algumas precisam de contexto e orientação.
```

### Ex15 — Resposta final

Arquivo:

```text
stack_sentinel/agent/nodes.py
```

Função:

```python
final_answer_node(state) -> AgentState
```

A resposta deve conter:

```text
Resumo
Evidências
Próximo passo
```

Casos:

- ticket;
- build;
- docs;
- unknown/fallback.

Ponto didático:

```text
Usuário não quer JSON cru. Usuário quer orientação útil.
```

### Ex16 — Integração final

Arquivo:

```text
stack_sentinel/agent/graph.py
```

Função:

```python
run_stack_sentinel_flow(state, llm, mcp_client) -> AgentState
```

Fluxo:

```text
classify -> route -> fetch node -> final answer
```

Rotas:

```text
fetch_ticket -> fetch_ticket_node
fetch_build -> fetch_build_node
fetch_docs -> fetch_docs_node
fallback -> fallback_node
```

Validação:

```bash
python run.py test ex16
python run.py demo
```

Ponto didático:

```text
Agora o Stack Sentinel atravessa todas as camadas: linguagem, fluxo, MCP, dados e resposta.
```

## Checkpoints de turma

Use ao fim de cada bloco:

```text
Quem passou?
Quem falhou por setup?
Quem falhou por lógica?
Quem ainda não conseguiu rodar?
```

Peça que os alunos respondam com:

```text
ex02 passed
ex02 falhou: assertion de chave
ex02 travado: erro de import
```

## Fechamentos curtos por tema

MCP:

```text
MCP expõe capacidades. Ele não decide sozinho.
```

Tools/resources/prompts:

```text
Tools fazem coisas. Resources dão contexto. Prompts orientam comportamento.
```

LangGraph:

```text
LangGraph organiza estado, nodes e caminhos explícitos.
```

FakeLLM:

```text
FakeLLM torna teste previsível. LLM real pode entrar depois sem mudar o contrato.
```

Integração:

```text
O agente decide o que chamar. O MCP Client sabe como chamar. O MCP Server sabe adaptar. O service responde.
```
