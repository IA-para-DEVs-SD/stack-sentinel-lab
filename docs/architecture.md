# Arquitetura do Stack Sentinel

```text
Usuario
  ↓
Agent / Graph
  ↓
MCP Client
  ↓
MCP Server
  ↓
Mock API / Dados locais
```

## Responsabilidades

- **Mock API**: simula sistemas internos.
- **MockServiceClient**: chama a mock API.
- **MCP Server**: registra tools, resources e prompts.
- **MCP Client**: chama capabilities do servidor.
- **Agent**: classifica intenção, roteia fluxo, busca contexto e gera resposta final.
- **FakeLLM**: torna os testes determinísticos.

## SimpleMCPServer e FastMCP

O lab comeca com `SimpleMCPServer` como harness didatico: ele nao implementa o protocolo MCP completo, mas deixa os contratos de tools, resources e prompts faceis de testar.

Depois do Ex04.5, a exposicao MCP real passa a ser feita com `FastMCP`. Os handlers de dominio continuam os mesmos; o que muda e a camada de registro:

```text
SimpleMCPServer.register_tool(...)
```

por:

```text
@mcp.tool()
```

Os testes locais ainda podem usar `SimpleMCPServer` quando precisarem de execucao em memoria, mas a arquitetura da aula passa a apontar para `FastMCP` como servidor MCP real.
