.. _asgard.backends:

Backends
========


Os Backends são a cola entre o core do asgard e as outras APIs com as quais a Asgard API consegue se comunicar.

Na mesma linha dos :ref:`Services <asgard.services>`, esses objetos devem mapear todas as ações que um determinado backend deve ser capaz de realizar. A comunicação entre o backend e suas respectivas APIs lowlevel deve ser feita atráves de um o mais :ref:`Clients <asgard.clients>`.

O backend estão atualmente divididos em:

- :py:class:`AgentsBackend <asgard.backends.base.AgentsBackend>`
- :py:class:`AppsBackends <asgard.backends.base.AppsBackend>`
- :py:class:`ScheduledJobsBackend <asgard.backends.jobs.ScheduledJobsBackend>`


Esss são objetos abstratos que definem quais ações cada um desses backends podem executar. As implementações desses backends é que vão adicionar suporte ao projeto Asgard a falar com múltiplos outros projetos/APIs.

A junção de múltiplos ``Backends`` forma um "Orquestrador", modelado no objeto :py:class:`Orchestrator <asgard.backends.base.Orchestrator>`. Esse é o objeto principal em termos de funcionalidades da Asgard API, é esse objeto quem define o que a Asgard API consegue fazer, em termos de orquestração de containers.


.. _asgard.backends.orquestrador:

Orquestrador
------------

O Objeto :py:class:`Orchestrator <asgard.backends.base.Orchestrator>` é a junção de múltiplos backends. Uma instância de Orquestator recebe seus backends como parâmetros em seu construtor.


Abaixo está a implementação do objeto ``Orchestrator``:

.. autoclass:: asgard.backends.base.Orchestrator
   :members:
   :undoc-members:
   :noindex:

Orquetsradores atualmente suportados
------------------------------------

Mesos
~~~~~

O Mesos é um cluster manager que suporta uma variadeade de orquestrdores de containers. Como temos modelado o backend de Agents separados do Backend de Apps podemos ter múltiplas implementações do Orchestrator Mesos com backends variados.

Atualmente a Asgard API já possui implementação de :py:class:`AgentsService <asgard.services.agents.AgentsService>` para `Apache Mesos <https://mesos.apache.org/>`_ e faremos uma implementação de AppsService (interface ainda a ser definida) para Mesosphere Marathon.

Kubernetes - Futuro
~~~~~~~~~~~~~~~~~~~

Assim que as interfaces ``AgentsService`` e ``AppsServices`` estiverem mais bem defindas poderemos começar uma implementação para suportar orquestração de containers com `Kubernetes <https://kubernetes.io/>`_.
