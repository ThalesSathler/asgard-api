Escrevendo uma implementação de um novo Orquestrador
====================================================

Aqui descreveremos como implementar o suporte a um novo orquestrador, quais classes abstratas temos que implementar, com organizar o código de forma que fique análogo ao que já existe e por isso fique mais fácil de compreender, à medida que o codebase for crescendo.


A implementação do suporte a um novo Orquestrador começa na classe :py:class:`asgard.backends.base.Orchestrator`.


.. autoclass:: asgard.backends.base.Orchestrator
   :noindex:
   :undoc-members:
   :members: get_agents
   :special-members: __init__

Perceba que o ``__init__()`` já recebe dois parametros, que são dois backends. Um para Apps e outro para Agents.
Como o ``Orchestrator`` é uma classse abstrata, precisamos implementar todos os métodos. Cada método tem relação com algum backend, nesse caso a implementação vai usar esse backend específico para poder obter as informações.

Vejamos os métodos de cada backend.

Agents backend
--------------

.. autoclass:: asgard.backends.base.AgentsBackend
   :noindex:
   :undoc-members:
   :members: get_agents


Vamos pegar como exemplo o método :py:meth:`~asgard.backends.base.AgentsBackend.get_agents`. Esse método é quem deve retornar a lista de agents desse novo orquestrador. Então uma possível implementação, considerando um backend fictício chamado ``K8S``, poderia ser:


Modelo:

.. code:: python

  from asgard.models.agent import Agent


  class K8SAgent(Agent):
      type = "K8S"

      def is_from_account(self, account) -> bool:
          return self.attributes["owner"] == account.owner

Código do ``AgentsBackend``:

.. code:: python

  from asgard.backend.k8s.models.agent import K8SAgent
  from asgard.backends.base import AgentsBackend
  from asgard.conf import settings
  from asgard.http.client import http_client
  from asgard.models.account import Account
  from asgard.models.user import User


  class K8SAgentBackend(AgentsBackend):

    async def get_agents(sefl, user: User, account: account) -> List[K8SAgent]:
      async with http_client.get(settings.K8S_API_URL) as response:
        agents: List[K8SAgent] = []
        data = await response.json()
        for agent in data["objects"]:
          new_agent = K8SAgent(id=agent["id"], attributes=agent["labels"], ...)
          if new_agent.is_from_account(account):
            agents.append(new_agent)
        return agents

Código do ``K8SOrchestrator``:

.. code:: python

  from asgard.backend.k8s.models.agent import K8SAgent
  from asgard.backens.base import Orchestrator
  from asgard.models.account import Account
  from asgard.models.user import User


  class K8SOrchestrator(Orquestrador):
      async def get_agents(self, user, account) -> List[K8SAgent]:
          return self.agents_backend.get_agents(user, account)

Com uma implementação nessa linha, seria possível listar todos os agents desse novo Orchestrador dessa forma:


.. code:: python

  from asgard.backends.k8s.agent import K8SAgentBackend
  from asgard.backends.k8s.impl import K8SOrchestrator

  orchestrator = K8SOrchestrator(agents_backend=K8SAgentBackend(), ...)
  agents = await orchestrator.get_agents(user, account)

Pensando nos endpoints HTTP, que são todos autenticados, o valor de ``user`` (:py:class:`asgard.models.user.User`) e ``account`` (:py:class:`asgard.models.account.Account`) são descobertos assim que a view HTTP começa a rodar.
