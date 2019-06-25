
Organização do código
=====================

Esse documento dá uma visão geral de como o código do asgard está organizado.

O pacote principal é o :py:mod:`asgard`. Dentro deste pacote temos algumas macro-subdivisões.

- ``asgard/api``: Contém todo o código que lida com a camada HTTP, ou seja, são os endpoints da API;
- ``asgard/services``: É o código que faz a "ponte" entre os enpoints HTTP e o restante do código do projeto. A ideia principal é que os endpoints HTTP não conheçam nada além dessa camada de services.
- ``asgard/backends``: Aqui estão as implementações concretas de todos os backends que o Asgard suporta. Backend são serviços com os quais a Asgard API consegue se comunicar. Atualmente a Asgard API se comunica com a API do Mesos e do Marathon para prover suas funcionalidades.
- ``asgard/models``: Contém os objetos que são usados para passar dados entre as camadas (http, service, backends) do projeto.

Conteúdo:

.. toctree::
    :maxdepth: 2

    legacy-api.rst
    api.rst
    services.rst
    backends.rst
    models.rst
