Autoscaler
==========

O Autoscaler é um worker que coleta e processa métricas de aplicações para determinar os parâmetros de CPU e memória que devem ser configurados para cada aplicação dentro do Asgard. Atualmente o Autoscaler só é capaz de ajustar a quantidade de CPU e memória das instâncias mas não o número de instâncias.

Funcionamento básico
=========================

Cada aplicação é configurada por meio da parametrização de porcentages de uso de memória e CPU que as aplicações devem manter. O Autoscaler fará polling dos status das aplicações e, caso verifique que o uso de recursos de uma aplicação não esteja de acordo com os parâmetros configurados, fará ajustes das configurações e solicitará um redeploy.

Por exemplo: se uma aplicação está configurada para manter o uso de memória em 50% e ocorre um spike de requests que aumenta o uso de memória para 80%, o autoscaler irá aumentar a quantidade de memória disponível para a aplicação de maneira que ela volte a utilizar 50% de memória. Quando o fluxo de requests voltar ao normal, o autoscaler notará uma redução no uso de memória e configurará a aplicação para usar a quantidade de memória habitual.

Configurando aplicações
=======================

A configuração é feita individualmente para cada aplicação, por meio das seguintes labels:

- `asgard.autoscale.cpu`: um valor entre 0 e 1 que indica a porcentagem de uso de CPU que o autoscaler deve manter
- `asgard.autoscale.mem`: um valor entre 0 e 1 que indica a porcentagem de uso de memória que o autoscaler deve manter
- `asgard.autoscale.ignore`: lista separada por ponto e vírgula indicando parâmetros que o autoscaler deve ignorar. Essa label serve para que features do autoscaler possam ser desativadas sem a necessidade de alteração de outras labels. São itens válidos para a lista:
    - `cpu`: Desativar autoscaling de CPU para a aplicação;
    - `mem`: Desativar autoscaling de memória para a aplicação;
    - `all`: Desativar completamente autoscaling para a aplicação
- `asgard.autoscale.max_cpu_limit`: valor máximo que o autoscaler pode aplicar como parâmetro para CPU
- `asgard.autoscale.min_cpu_limit`: valor mínimo que o autoscaler pode aplicar como parâmetro para CPU
- `asgard.autoscale.max_mem_limit`: valor máximo que o autoscaler pode aplicar como parâmetro para memória
- `asgard.autoscale.min_mem_limit`: valor mínimo que o autoscaler pode aplicar como parâmetro para memória

Aplicações que não possuam as labels `asgard.autoscale.cpu` ou `asgard.autoscale.mem` serão ignoradas pelo autoscaler.

