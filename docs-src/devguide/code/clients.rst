.. _asgard.clients:

Clients
=======

Os clients fazem o papel de implementar a comunicação mais lowlevel com as APIs finals. Por exemplo a comunicação com o Marathon seria feita toda por um client específico.

Esse client é o mapeamento exato das entradas e saídas dess API com a qual ele se comunica.

Todos os clients devem enviar e retornar modelos dos recursos que a API em questão expõe. Um exemplo é o client para o chronos:

.. autoclass:: asgard.clients.chronos.ChronosClient
    :members:
    :undoc-members:
    :noindex:

Como exemplo o método :py:meth:`~asgard.clients.chronos.ChronosClient.get_job_by_id()` retorna um modelo que representa um Job no Chronos, exatamente como a API original do Chronos retorna. Esse modelo está aqui:

.. autoclass:: asgard.clients.chronos.models.job.ChronosJob
    :noindex:

Mapeando todas as entradas e saídas das APIs acabamos tendo validação de schema quando nos comunicamos com essas APIs. Essa é a ideia de um client, apenas ser um wrapper para uma API com validação de schema das entradas e saídas.

Os clients não possuem uma interface abstrata fixa, podemos escolher quais são as ações disponíveis. Um :ref:`Backend <asgard.backends>` pode usar múltiplas ações de um client para exeutar uma de suas próprias ações.
