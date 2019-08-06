
Criando código para o projeto
=============================

Todos os PRs do projeto passam por um pipeline que conferem algumas coisas:

- type checking (feito com mypy)
- code formatting (feito com black)
- import sorting (feito com isort)

Todas as checagens estão disponíveis como comandos do ``pipenv``. Então antes de cada push o ideal é rodas todas essas checagens.

Para rodar as checagens faça:

::

  $ pipenv run fmt
  $ pipenv run isort-fmt
  $ pipenv run lint

O recomendado é que essas checagens estejam configuradas para rodarem automaticamente na ferramenta que você estiver usando para desenvolver o projeto. As opções que são passadas para cada check podem ser vistas no ``Pipfile``.
