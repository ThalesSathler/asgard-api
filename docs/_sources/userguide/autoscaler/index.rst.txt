Utilizando o Autoscaler
========================

O Autoscaler é um worker que coleta e processa métricas de aplicações para determinar os parâmetros de CPU e memória que devem ser configurados para cada aplicação dentro do Asgard. Atualmente o Autoscaler só é capaz de ajustar a quantidade de CPU e memória das instâncias mas não o número de instâncias.

Funcionamento básico
---------------------

Cada aplicação é configurada por meio da parametrização de porcentages de uso de memória e CPU que as aplicações devem manter. O Autoscaler verificará os status das aplicações a cada 5 minutos e, caso verifique que o uso de recursos de uma aplicação não esteja de acordo com os parâmetros configurados, fará ajustes das configurações e solicitará um redeploy.

Por exemplo: se uma aplicação está configurada para manter o uso de memória em 50% e ocorre um spike de requests que aumenta o uso de memória para 80%, o autoscaler irá aumentar a quantidade de memória disponível para a aplicação de maneira que ela volte a utilizar 50% de memória. Quando o uso de memória voltar ao valor anterior, o autoscaler notará e reduzirá a memória disponível para a aplicação.

Instalando Autoscaler no Asgard
--------------------------------

O autoscaler está contido na própria `imagem docker do Asgard <https://hub.docker.com/r/b2wasgard/asgard-api>`_. Para utilizá-lo é necessário inicializar a imagem passando o comando correto e configurar algumas varíaveis de ambiente.

Os recursos mínimos testados para funcionamento normal do autoscaler são 128mb de RAM e 10% de um processador moderno para um ambiente com 20 aplicações onde uma delas está configurada para ser escalada. A recomendação é sempre que a performance do autoscaler seja monitorada para garantir que os recursos configurados sejam suficientes para o ambiente específico. O Autoscaler não é capaz de utilizar mais do que uma unidade de processamento.

Importante ressaltar que o Asgard não filtra as aplicações antes de enviar ao autoscaler. Isso significa que o autoscaler deve ser configurado para suportar a filtragem de todas as aplicações gerenciadas pelo Asgard. A `issue #198 <https://github.com/b2wdigital/asgard-api/issues/198>`_ foi aberta para melhoria desse cenário.

Comando de Inicialização
--------------------------------

O seguinte comando deve ser passado para a imagem no momento de sua inicialização:

.. code:: bash

 python -m asgard.workers.autoscaler


Dentro do Asgard, isso pode ser feito adicionando o seguinte parâmetro no primeiro nível do JSON de configuração da aplicação:

.. code:: javascript

 "args": [
   "python",
   "-m",
   "asgard.workers.autoscaler"
 ]

Variáveis de Ambiente Obrigatórias
------------------------------------

- ``ASGARD_ASGARD_API_ADDRESS``: endereço da API do Asgard;
- ``ASGARD_AUTOSCALER_AUTH_TOKEN``: token para autenticacao na API do Asgard. Esse token deve ser criado diretamente na base de dados do Asgard e é feita para um único usuário de uma única conta;
- ``ASGARD_AUTOSCALER_MARGIN_THRESHOLD``: valor entre 0 e 1 indicando a margem de erro que Autoscaler considera aceitável ao avaliar as aplicações.
    Eg.: Se uma aplicação está configurada para utilizar 80% de um recurso (CPU ou memória) e a margem é de 0.05 o Autoscaler não tomará nenhuma ação caso o uso da aplicação esteja entre 75-85%

Variáveis de Ambiente Opcionais
--------------------------------

- ``ASGARD_MAX_CPU_SCALE_LIMIT``: valor padrão para ``asgard.autoscale.max_cpu_limit`` caso este não seja especificado pela aplicação;
- ``ASGARD_MIN_CPU_SCALE_LIMIT``: valor padrão para ``asgard.autoscale.min_cpu_limit`` caso este não seja especificado pela aplicação;
- ``ASGARD_MAX_MEM_SCALE_LIMIT``: valor padrão para ``asgard.autoscale.max_mem_limit`` caso este não seja especificado pela aplicação;
- ``ASGARD_MIN_MEM_SCALE_LIMIT``: valor padrão para ``asgard.autoscale.min_mem_limit`` caso este não seja especificado pela aplicação;

Configurando aplicações
-------------------------

A configuração é feita individualmente para cada aplicação, por meio das seguintes labels:

- ``asgard.autoscale.cpu``: um valor entre 0 e 1 que indica a porcentagem de uso de CPU que o autoscaler deve manter
- ``asgard.autoscale.mem``: um valor entre 0 e 1 que indica a porcentagem de uso de memória que o autoscaler deve manter
- ``asgard.autoscale.ignore``: lista separada por ponto e vírgula indicando parâmetros que o autoscaler deve ignorar. Essa label serve para que features do autoscaler possam ser desativadas sem a necessidade de alteração de outras labels. São itens válidos para a lista:
    - ``cpu``: Desativar autoscaling de CPU para a aplicação;
    - ``mem``: Desativar autoscaling de memória para a aplicação;
    - ``all``: Desativar completamente autoscaling para a aplicação
- ``asgard.autoscale.max_cpu_limit``: valor máximo que o autoscaler pode aplicar como parâmetro para CPU
- ``asgard.autoscale.min_cpu_limit``: valor mínimo que o autoscaler pode aplicar como parâmetro para CPU
- ``asgard.autoscale.max_mem_limit``: valor máximo que o autoscaler pode aplicar como parâmetro para memória
- ``asgard.autoscale.min_mem_limit``: valor mínimo que o autoscaler pode aplicar como parâmetro para memória

Os valores para limite mínimo e máximo utilizam as mesmas unidades de medida utilizadas para configuração dos recursos na interface do Asgard.

Aplicações que não possuam as labels ``asgard.autoscale.cpu`` ou ``asgard.autoscale.mem`` serão ignoradas pelo autoscaler.
