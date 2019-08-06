.. _asgard.models:

Models
======


Os models são os objetos que todo o codebase da Asgard API deve usar para transitar informações entre suas camadas, desde o request HTTP que chegou no endpoint até o momento em que temos que falar com a API do :ref:`Orquestrador <asgard.backends.orquestrador>` real.



Existem 2 tipos de modelos no projeto:


- :ref:`Asgard Models <asgard.models.base>`, estão no pacote :py:mod:`asgard.models`
- :ref:`Client Models <asgard.models.client>`, estão o pacote ``asgard.client.*.models``

E existe também um modelo "especial", que é na verdade, uma interface de conversão entre um ClientModel e um AsgardModel. Essa conversão é de **total responsabilidade** da implementação do :ref:`Backend <asgard.backends>` em questão.

Todos os conversõres entre modelos preciam implementar a interface :ref:`ModelConverterInterface <asgard.models.converters>`.

Abaixo temos uma explicação sobre cada um deles.

.. _asgard.models.base:

Asgard Models
-------------

Esses são os modelos oficiais do projeto Asgard. Todas as passagens de informação entre as camadas do código (HTTP, Service, Backend, etc) devem ser feitas com instancias desses modelos. A única exceção é quando buscamos um modelo pelo seu ``id`` canonico. Nesse caso o método que faz essa busca recebe o ``id`` puro, mas retorna um Asgard Model preenchido.

.. _asgard.models.client:

Client Models
-------------

Os Client Models são models usados internamente pelos :ref:`Clients <asgard.clients>`. Cada implementação de :ref:`asgard.clients` precisa falar com uma API para implementar suas funcionalidades. O :py:class:`~asgard.clients.chronos.ChronosClient` por exemplo precisa falar com a API do `chronos <https://mesos.github.io/chronos/docs/api.html>`_ para fornecer os dados corretos.

O Client model é o mapeamento exato do que a API (com a qual esse client está faladndo) retorna. Pegando um exemplo de retorno da API do Chronos, endpoint ``/v1/scheduler/job/{job_id}``.

Esse endpoint retorna um Job do Chronos, com definido na `Documentação do projeto <https://mesos.github.io/chronos/docs/api.html#job-configuration>`_

::

  {
    "name": "asgard-curator-delete-indices-asgard-app-stats",
    "command": "curator --config /opt/curator.yml /opt/actions/delete-indices-hours-old.yml",
    "shell": true,
    "executor": "",
    "executorFlags": "",
    "taskInfoData": "",
    "retries": 2,
    "owner": "",
    "ownerName": "",
    "description": "",
    "successCount": 2658,
    "errorCount": 1,
    "lastSuccess": "2019-07-22T16:02:49.359Z",
    "lastError": "2019-05-18T00:02:28.330Z",
    "cpus": 0.1,
    "disk": 256,
    "mem": 32,
    "disabled": false,
    "softError": false,
    "dataProcessingJobType": false,
    "errorsSinceLastSuccess": 0,
    "fetch": [],
    "uris": [
    ],
    "environmentVariables": [
      {
        "name": "MY_ENV_VAR",
        "value": "ME_ENV_VALUE"
      }
    ],
    "arguments": [],
    "highPriority": false,
    "runAsUser": "root",
    "concurrent": false,
    "container": {
      "type": "DOCKER",
      "image": "alpine:3",
      "network": "BRIDGE",
      "networkInfos": [],
      "volumes": [],
      "forcePullImage": true,
      "parameters": []
    },
    "constraints": [
      [
        "workload",
        "LIKE",
        "general"
      ],
      [
        "owner",
        "LIKE",
        "asgard"
      ]
    ],
    "schedule": "R/2019-07-22T14:00:00.000-03:00/PT1H",
    "scheduleTimeZone": "America/Sao_Paulo"
  }

O mapeamento do :ref:`Client Model <asgard.models.client>` para esse retorno está em:

.. autoclass:: asgard.clients.chronos.models.job.ChronosJob
    :noindex:


A responsabilidade transformar esse model em AsgardModel pertence ao Backend. A forma que escolhemos de transformar um Client Model em seu respectivo Asgard Model é através do :ref:`ModelConverter <asgard.models.converters>`, que veremos mais em detalhes a seguir.



.. _asgard.models.converters:

Model Converters
----------------


Um ModelConverter é uma interface absrata que deve ser implementada para que seja possível transformar um :ref:`Client Model <asgard.models.client>` em um :ref:`Asgard Model <asgard.models.base>` e vice-versa. Esses converters são implementados por :ref:`Backends <asgard.backends>`.

Isso foi pensado dessa forma para que os Asgard Models não tenham dependências de nada externo e também para que os Cliets Models também não tenham nenhuma dependência externa. A princípio, um client implementado no respositório da Asgard API pode ser externalizado para um projeto próprio sem muitas dificuldades.

A ideia é que cada backend tenha seus próprios ModelConverters.

Todos os ModelConverters devem implementar a seguinte interface:

.. autoclass:: asgard.backends.models.converters.ModelConverterInterface
    :members:
    :noindex:

Essa interface é também um tipo generico parametrizado com dois outros tipos: O primeiro parametro é o AsgardModel e o segundo é o ClientModel.

Exemplo de um ModelConverter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Seguindo com o exemplo acima, de um client pro Chronos.

O Model Converter implementado pelo :py:class:`~asgard.backends.chronos.impl.ChronosScheduledJobBackend` é esse:

.. autoclass:: asgard.backends.chronos.models.converters.ChronosScheduledJobConverter
    :noindex:
    :members:
    :undoc-members:

O papel do Model Converter é bem simples. O que ele faz é copiar todos os valores de um Client Model para seus respectivos campos em um Asgard Models. Dessa forma podemos ter no Asgard Model campos com nomes e formatos diferentes do Client Model.

Como nesse caso o modelo do ScheduledJob do Chronos é um objeto bem complexo, a implementação completa da transformação entre esses dois models (ChronosJob e ScheduledJob) demanda mais do que somente um ModelConverter.

Temos, por exemplo, um outro converter dedicado para o campo ``container``, que é o :py:class:`~asgard.backends.chronos.models.converters.ChronosContainerSpecConverter`.

Um converter pode usar outro, assim:

.. code:: python

  class ChronosScheduledJobConverter(
      ModelConverterInterface[ScheduledJob, ChronosJob]
  ):
      @classmethod
      def to_asgard_model(cls, other: ChronosJob) -> ScheduledJob:
          return ScheduledJob(
              id=other.name,
              ...
              ...
              container=ChronosContainerSpecConverter.to_asgard_model(
                  other.container
              )
          )


Veja que nesse caso a transformação do campo ``container`` foi "delegada" para o ModelConverter especializado nesse campo.

Esse tipo de "delegação" simplifica o código de conversão de objetos grandes e complexos.
