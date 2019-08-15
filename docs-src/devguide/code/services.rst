.. _asgard.services:

Services
========


Service faz o papel da "ponte" entre os endpoints HTTP e todo restante do código. E ideia é que os endppints HTTP só consigam interagir com o restante do código através de um "Service".

A ideia dos "Services" é mapear todas as possíveis ações que a Asgard API pode executar.


Os services estão hoje divididos em:

- :py:class:`AgentsService <asgard.services.agents.AgentsService>`
- :py:class:`AppsSerivce <asgard.services.apps.AppsService>`

Essas são classes concretas e ali estão todas as ações que podem ser executadas em cada service. À medida em que mais endpints HTTP forem surgindo podemos criar novos services para que esses endpoints possam executar suas funções.

O papel dos Services é falar com os backends, que são as implementações efetivas, que realmente vão às APIs que compõem o projeto Asgard.

AgentsService
-------------

Aqui está a implementação do ``AgentsService``, mostrando os métodos disponíveis:

.. autoclass:: asgard.services.agents.AgentsService
   :members:
   :undoc-members:
   :noindex:


Perceba como os métodos do ``AgentsService`` recebem objetos concretos em vez de tipos primitivos, esses são os :py:mod:`Models <asgard.models>`. A única exceção é quando precisamos buscar um objeto usando seu identificador único (``id``), nesse caso passamos o valor do ``id`` mesmo, já que essa busca é justamente quem vai fazer a troca de um "id" por um objeto preenchido.

AppsService
-----------

Aqui está a implementação do :py:class:`AppsService <asgard.services.apps.AppsServices>`:


.. autoclass:: asgard.services.apps.AppsService
   :members:
   :undoc-members:
   :noindex:
