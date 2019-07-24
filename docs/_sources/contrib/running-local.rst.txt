
.. _asgard.running.local:

Rodando o projeto localmente
============================

Essa é lista de ENVs já com os valores para o ambiente de desenvolvimento:

::

  ASGARD_CACHE_KEY_PREFIX=asgard-api-dev/
  ASGARD_DB_URL=postgresql://postgres:@172.18.0.41/asgard
  ASGARD_FILTER_TRANSFORMJSON_ENABLED=1
  ASGARD_LOGLEVEL=DEBUG
  ASGARD_MESOS_API_URLS=["http://172.18.0.11:5050", "http://172.18.0.12:5050", "http://172.18.0.13:5050"]
  ASGARD_STATS_API_URL=http://172.18.70.1:9200
  ASGARD_SCHEDULED_JOBS_SERVICE_ADDRESS=http://172.18.0.40:9090
  HOLLOWMAN_CORS_WHITELIST=http://localhost:4200,http://localhost
  HOLLOWMAN_GOOGLE_OAUTH2_CLIENT_ID=""
  HOLLOWMAN_GOOGLE_OAUTH2_CLIENT_SECRET=""
  HOLLOWMAN_MARATHON_ADDRESS_0=http://172.18.0.31:8080
  HOLLOWMAN_MARATHON_ADDRESS_0=http://172.18.0.31:8080
  HOLLOWMAN_MARATHON_ADDRESS_1=http://172.18.0.31:8080
  HOLLOWMAN_MARATHON_ADDRESS_2=http://172.18.0.31:8080
  HOLLOWMAN_MESOS_ADDRESS_0=http://172.18.0.11:5050
  HOLLOWMAN_MESOS_ADDRESS_1=http://172.18.0.12:5050
  HOLLOWMAN_MESOS_ADDRESS_2=http://172.18.0.13:5050
  HOLLOWMAN_METRICS_ZK_ID_0=172.18.0.2
  HOLLOWMAN_METRICS_ZK_ID_1=172.18.0.3
  HOLLOWMAN_METRICS_ZK_ID_2=172.18.0.4
  HOLLOWMAN_REDIRECT_AFTER_LOGIN=http://localhost:4200/authenticated/
  HOLLOWMAN_SECRET_KEY=secret__
  MARATHON_CREDENTIALS=marathon:secret
  UWSGI_EXTRA_ARGS=--static-map2 /static=/opt/app --honour-stdin

Você precisa passar todas as envs para ser possível rodar o código da API. O jeito mais simples de fazer isso é criar um arquivo chamado ``.env``
na raiz do projeto, contento todas as envs mostradas acima, exatamente com esses valores. Esse arquivo já está no ``.gitignore``, por isso não será comitado.

.. note::
  Todas as ENVs com prefrixo ``HOLLOWMAN_`` são usadas pelo :ref:`código legado <hollowman.api>`. As ENVs novas possuem o prefixo ``ASGARD_``. Aos poucos vamos migrando o cógido e as envs.

Rodando a Asgard API localmente
-------------------------------

O projeto Asgard API usa o `pipenv <https://pipenv.readthedocs.io/en/latest/>`_ e precisa do python 3.6.x. Antes de instalar as dependências, certifique-se que o python 3.6 esteja instalado e funcionando.

.. note::
  Recomendamos o uso do `pyenv <https://github.com/pyenv/pyenv#table-of-contents>`_ para gerenciar a versões locais do python.

Para instalar as dependências rode:

::

  $ pipenv install --dev


.. _asgard-run.sh:

Ligando todos os containers necesários para rodar o projeto completo
--------------------------------------------------------------------

Depois disso você precisa subir um ambiente de desenvolvimento local, contento todas as dependencias que a Asgard API precisa para funcionar. Isso inclui: Mesos, Elasticsearch, Marathon, Zookeeper, PgSQL, etc.

Para subir todos esses containers, rode:

::

  $ ./asgard-run.sh

Isso vai baixar todas as imagens docker e rodar todos os conatainers necessários.

.. note::
  A primeira rodada do asgard-run.sh vai produzir bastante output, pois os outputs do docker pull também serão exibidos.


Desligando todo o ambiente
--------------------------

Para desligar todos os containers, basta rodar novamente o script ``asgard-run.sh`` e pressionar ``^C`` assim que essa mensagem aparecer:

::

  ./asgard-run.sh
  Removing any old containers...
  Sleeping for 3s, ^C to cancel now.
  ^C

Esse "sleep" que o script faz é justamente para dar tempo de interrompermos o rodada antes dele começar a ligar todos os containers.

Rodando a API
-------------

Para rodar a API, use:

::

  $ ./run-api-proxy.sh

Esse script abre a porta ``5000`` e redireciona os requests para a API correta. Para entender o porque desse script precisamos entender a :ref:`re-escrita de código <hollowman.api>` que estamos fazendo na Asgard API.


Quando tiver a API rodando, você pode fazer um request para validar:

::

  $ curl -i http://127.0.0.1:5000/v2/apps/
  {"msg": "Authorization token is invalid"}%



Isso significa que você não está autenticado, o que é verdade, já que nem criamos seu novo usuário. Faremos isso agora.

Criando um novo usuário para desenvolvimento
--------------------------------------------

Para criar um novo usuário, você pode editar o arquivo ``scripts/sql/user.sql`` a adicionar ali um trecho de SQL que vincula seu user a uma das contas
de dev que existem no banco. Usando um exemplo: Novo usuário tem email ``mail@server.com``, faríamos o seguinte:

.. code:: sql

  INSERT INTO "user" (tx_name, tx_email, tx_authkey, bl_system)
    VALUES ('Novo User', 'mail@server.com', 'a648638d589740879f25bf55648ccc21', false);

  INSERT INTO user_has_account (account_id, user_id) VALUES (
    (SELECT id from account where name = 'Asgard/DEV'),
    (SELECT id from "user" where tx_email='mail@server.com')
  );

  INSERT INTO user_has_account (account_id, user_id) VALUES (
    (SELECT id from account where name = 'Asgard/INFRA'),
    (SELECT id from "user" where tx_email='mail@server.com')
  );


Agora rode novamente o :ref:`script que sobe o ambiente de desenvolvimento <asgard-run.sh>`. Isso vai recriar todos os componentes, incluindo o baco de dados.

Dessa forma, agora podemos fazer a seguinte requisição:

::

  curl -H "Authorization: Token a648638d589740879f25bf55648ccc21" \
  http://127.0.0.1:5000/v2/apps
  {"apps": []}%


Agora sim você está vendo sua lista de apps, que obviamente é vazia. Nesse momento você está pronto
para começar a desenvolver novos códigos para a Asgard API.


Logando na UI
-------------

Depois de rodar um ambiente completo com o script ``asgard-run.sh`` você poderá acessar a Asgard UI no endereço `<http://localhost:4200>`_.
O único login suportado atualmente pela UI é oauth2, especificamente com Google sendo o provider.

.. note::
  **Atenção**: Para o processo de login funcionar você precisa criar uma Oauth2 app no console do Google. Mais detalhes aqui: https://developers.google.com/identity/protocols/OAuth2
  Depois de criar essa app, preencha as ENVs: ``HOLLOWMAN_GOOGLE_OAUTH2_CLIENT_ID`` e ``HOLLOWMAN_GOOGLE_OAUTH2_CLIENT_SECRET`` com os valores que o Google gerou pra você.


Evoluindo o banco de dados
--------------------------

Sempre que fizermos uma mudança no banco, vamos guardar o SQL na pasta ``sql/`` . Os arquivos têm nome prefixado por um número (``date +"%s"``),
pois isso indica a ordem em que devem ser rodados. Por enquanto vamos assim até migrar para um projeto que gerencie essas migrações.

Para pegar o SQL que o Alchemy gera para um model:
Abra o ipython (também passando as mesmas envs que você passou para rodar a API)

.. code:: ipython

  >>> from sqlalchemy.schema import CreateTable
  >>> from hollowman.models import <Model>
  >>> from hollowman.models import engine
  >>> print (CreateTable(Account.__table__).compile(engine))


Rodando os testes do projeto
----------------------------

Os testes estão divididos em dois: Unitários (``tests/``) e de Integração (``itests/``). [1]_

Rodando os testes unitários
~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  PIPENV_DONT_LOAD_ENV=1 pipenv run test

Rodando os testes de integração
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Para rodar os testes de integração você precisa de alguns serviços rodando.
Para ligar esses serviços localmente rode, na raiz do projeto:

::

  source dev/vars.sh
  source dev/network.sh
  source dev/pgsql.sh
  source dev/elasticsearch.sh

depois rode os testes:

::

  PIPENV_DONT_LOAD_ENV=1 pipenv run itest


.. rubric:: Notas
.. [1] Mais sobre os testes do projeto: :ref:`writing-tests`
