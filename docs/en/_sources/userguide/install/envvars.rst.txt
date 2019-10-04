.. _asgard.envvars:

Variáveis de Ambiente
=====================


Toda a parametrização da asgard API é feita via variáveis de ambiente. Nesse documento vamos explicar cada uma das variáveis de ambiente (ENVs) que a Asgard API conhece.

Todas as ENVs são lidas no arquivo :py:mod:`asgard.conf`. Todas as envs estão sendo movidas para o objeto :py:class:`asgard.conf.Settings`, que é um objeto ``BaseSettings`` do pydantic (`docs <https://pydantic-docs.helpmanual.io/#settings>`_).


As envs estão sempre prefixadas com algum valor. O prefixo padrão, caso você não escolhada nada é ``ASGARD_``.

Abaixo está a transcrição completa do modulo :py:mod:`asgard.conf`.

.. literalinclude:: /../asgard/conf.py
    :linenos:


Todos os atributos da classe :py:class:`asgard.conf.Settings` já lêm seus valores de envs **com prefixo**.


Lista de ENVs conhecidas pela Asgard API
----------------------------------------

**Nota**: Todos nomes descritos aqui devem receber o prefixo ``ASGARD_`` quando forem criadas as ENVs no momento de rodar a Asgard API.

 - ``ASGARD_API_ADDRESS``
  Obrigatório. Recebe o endereço onde a Asgard API responde. Essa env é usada pelo código que faz o auto-tuning das aplicações. Ex: ``https://api.asgard.server.com``
 - ``AUTOSCALER_AUTH_TOKEN``
  Obrigatório. Recebe o token de autenticação que será usado para falar com a Asgard API no momento de aplicar as alterações de tuning de alguma app.
 - ``AUTOSCALER_MARGIN_THRESHOLD``
  Obrigatório. Recebe o percentual que indica se uma app será modificada pelo tuning ou não. É um float no formato (<margem>/100). Ou seja, se você quiser uma margem de 10%, deve colocar aqui ``0.10``. Aplicações com uma diferença de uso de CPU e RAM **menor** que esse threshold não serão modificadas pelo auto-tunig.
 - ``MESOS_API_URLS``
  Obrigatório. Recebe uma lista, contendo os endereços de todos os mesos que formam o cluster. Ex: ``["http://10.0.0.1:5050", "http://10.0.0.2:5050"]``
 - ``DB_URL``
  Obrigatório. Recebe a URI de conexão com o banco de dados. Esse banco guarda os dados relacionaos de usuários e contas. O código da Asgard API usa `SQLAlchemy <https://www.sqlalchemy.org/>`_.
 - ``STATS_API_URL``
  Obrigatório. Endereço da API onde as estatísticas de uso de recursos das apps serão gravadas. Atualmente Asgard API fala com `ElasticSearch <https://www.elastic.co/pt/products/elasticsearch>`_.
 - ``SCHEDULED_JOBS_SERVICE_ADDRESS``
  Obrigatório. Endereço da API responsável pela gerência de tarefas agendadas. Atualmente a asgard API suporta falar com o `Chronos <https://mesos.github.io/chronos/docs/api.html>`_.
 - ``SCHEDULED_JOBS_SERVICE_AUTH``
  Opcional. Dados de autenticação para falar com a API de tarefas agendadas. Recebe um objeto (:py:class:`asgard.conf.AuthSpec`) com user e password. Ex: ``{"user": "chronos", "password": "secret"}``
 - ``SCHEDULED_JOBS_DEFAULT_FETCH_URIS``
  Opcional. Recebe uma lista de objetos :py:class:`asgard.models.spec.fetch.FetchURLSpec`. Ex: ``[{"uri": "http://static.server.com.br/content.txt"}, {"uri": "file:///etc/config.tar.bz2"}]``
