
.. _hollowman.api:

Código legado da Asgard API
===========================

A Asgard API começou com sendo um projeto `flask <http://flask.pocoo.org/docs/1.0/>`_, usando python 2.7.

Todo esse código está abaixo da pasta ``hollowman/``, que inclusive era o nome antigo do projeto, antes de se chamar Asgard.

O código da Asgard API está sendo re-escrito com `aiohttp <https://aiohttp.readthedocs.io/en/stable/>`_ sendo o motor HTTP por baixo dos panos. Não usamos o aiohttp diretamente, o re-write da Asgard API usa como framework o `asyncworker <https://github.com/B2W-BIT/async-worker>`_, que é um framework genérico, multi-backend para escrever workers em python assíncrono.

Escrevemos alguns posts sobre esse framework, estão aqui:

- `Asyncworker — Microframework para consumers assíncronos em Python <https://medium.com/@diogommartins/asyncworker-microframework-de-consumers-ass%C3%ADncronos-em-python-f97cf64c6d1b>`_
- `Escrevendo workers assíncronos em python com asyncowrker <https://daltonmatos.com/2019/03/escrevendo-workers-assincronos-em-python-com-asyncowrker/>`_

O início do código da Asgard API está na :ref:`definição das rotas HTTP <asgard.http>`.
