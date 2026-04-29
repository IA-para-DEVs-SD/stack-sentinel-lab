# Cola — LangGraph no `graph.py`

Use esta cola quando estiver migrando o Ex08 de um grafo didatico para LangGraph.

## Imports principais

```python
from langgraph.graph import END, START, StateGraph

from stack_sentinel.agent.state import AgentState
```

## Ideia central

Um grafo LangGraph tem tres partes:

1. um schema de state;
2. nodes que recebem state e devolvem atualizacoes;
3. edges que definem a ordem de execucao.

## Estrutura esperada

```python
def compile_minimal_graph():
    def echo_node(state: AgentState) -> AgentState:
        # Leia state["user_input"]
        # Devolva uma atualizacao contendo final_answer
        ...

    graph = StateGraph(AgentState)
    graph.add_node("echo", echo_node)
    graph.add_edge(START, "echo")
    graph.add_edge("echo", END)
    return graph.compile()
```

## Como executar

Um grafo compilado de LangGraph usa `invoke`, nao `run`:

```python
graph = compile_minimal_graph()
result = graph.invoke({"user_input": "ping"})
```

O resultado esperado no Ex08 deve preservar `user_input` e preencher `final_answer`.

## Erros comuns

- Executar o grafo no import do modulo. O arquivo deve apenas definir funcoes.
- Retornar o `StateGraph` sem chamar `.compile()`.
- Criar um node que retorna string em vez de dicionario de atualizacao do state.
- Esquecer de conectar `START` e `END`.
