.. _asgard.doc-gen:

Gerando a versão html da documentação
-------------------------------------

Antes de conseguir gerar a documentação do projeto você precisa estar com ele :ref:`Rodando localmente <asgard.running.local>`.


Para gerar a versão final da documentação, entre na pasta ``docs-src/`` e rode:

::

  pipenv run make docs


Isso vai gerar todas as documentações, em todas as línguas configuradas. Atualmente ``pt_BR`` em ``en``. A documentação ``pt_BR`` será gerada na pasta ``docs/`` e as traduçõees estarão também dentro dessa pasta, abaixo de sub-pastas com o código da língua escolhida.

por exemplo, a tradução para ``en`` estará em ``docs/en``.
