
.. _asgard.http:

Endpoints HTTP
==============

O pacote ``asgard.api`` contém a definição de todos os endpoints HTTP e os objetos que representam as resposram serializadas por esses endpoints.


Para cada endpoint na API HTTP, por exemplo, ``/agents``, temos nesse pacote a definição das rotas desse endpoint em ``asgard/api/agents.py``. Isso deve valer para todas as rotas do projeto.

Para cada sub-rota de um endpoint, por exemplo, ``/agents/with-attrs`` temos definido em ``asgard/api/resources`` um modelo que representa essa resposta que será serializada por essa rota.

Pegando então o exemplo do endpoint ``/agents/with-attrs``, esse é modelo serializado por esse endpoint:

.. literalinclude:: ../../asgard/api/resources/agents.py

Perceba que esse modelo faz referência a outros modelos. Já o código da view que vai serializar esse modelo vai apenas construir esse objeto usando os outros objetos menionados acima, ex:

.. code:: python

  async def handler(...):

    agents = await agents_service.get_agents(user, account, backend=mesos)
    filtered_agents = apply_attr_filter(filters, agents)

    stats = calculate_stats(filtered_agents)
    return web.json_response(
        AgentsResource(agents=filtered_agents, stats=stats).dict()
    )

Essa é a ideia. Rotas HTTP estão mapeadas no pacote ``asgard.api`` serializando objetos mapeados que estão em ``asgard.api.resources``.
