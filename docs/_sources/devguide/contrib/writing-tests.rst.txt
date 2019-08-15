
.. _writing-tests:

Escrevendo testes para o projeto
================================


Os testes do projeto Asgard estão dvididos em duas categorias:

- Testes unitários
- Testes funcionais

Os testes unitários estão abaixo da pasta ``tests/`` e os funcionais estão abaixo da pasta ``itests/``. A diferença entre eles é que os testes funcionais dependem de recursos externos, como por exemplo Banco de daos, ElasticSearch, etc.


Localização dos testes dentro de suas respectivas pastas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Os arquivos de teste devem seguir a mesma hierarquia de pastas do código que está sendo testando. Pegando um exemplo: Os testes da classe :py:class:`asgard.services.apps.AppsService` que está declarada em ``asgard/services/apps.py`` devem estar abaixo da pasta ``tests/asgard/service/``. Nesse caso estão em ``tests/asgard/services/test_apps_service.py``.

Testes unitários
----------------

Os testes unitários são escritos com ``asynctest`` e devem ser subclasse de ``asynctest.TestCase``.

Testes funcionais
-----------------

Todos os testes funcionais são subclasses da classe ``itests.util.BaseTestCase``. Importante notar que todos as classes de teste precisam implementar os métodos ``setUp(self)`` e ``tearDown(self)``. Esses métodos são, na verdade, corotinas. Então sua classe de teste deve declará-los também como corotinas. Um exemplo de caso de teste para um teste funcional.

.. code:: python

 class MyTestCase(BaseTestCase):
    async def setUp(self):
      await super(MyTestCase, self).setUp()

    async def tearDown(self):
      await super(MyTestCase, self).tearDown()

Essa é a base para uma nova classe de teste que implementa testes funcionais.

Se se teste é um teste que chama a API do asgard, existe uma corotina que que te devolve um ``aiohttp_client``, dessa forma:

.. code:: python

  from asgard.app import app


  async def setUp(self):
    self.client = await self.aiohttp_client(app)


A partir desse momento você pode chamar a API do Asgard usando esse client, como se fosse um cliente http comum.

Usando aiohttp_client com aioresponses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Quando estamos escrevendo testes que fazem chamadaas reais à API do Asgard e ao mesmo tempo precisamos mocker alguma outra requisição que o código da API fará, precisamos passar uma opção especial para o aioresponses, que é o ``passthrough``.

.. code:: python

  from tests.conf import TEST_LOCAL_AIOHTTP_ADDRESS

  async def test_uses_api_and_needs_mock(self):
    async with aioresponses(passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS]) as rsps:
      rsps.get(...)


Quaisquer outros serviços HTTP que precisarem ser usados pelo teste (sem mock) devem ser adicionados à lista que está sendo passada para o ``aioresponses``.
