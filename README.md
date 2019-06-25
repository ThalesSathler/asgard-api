# Asgard API [![Build Status](https://travis-ci.org/B2W-BIT/asgard-api.svg?branch=master)](https://travis-ci.org/B2W-BIT/asgard-api)

|   |   |
|---:|---|
|Test Coverage   |[![codecov](https://codecov.io/gh/B2W-BIT/asgard-api/branch/master/graph/badge.svg?flag=unittest)](https://codecov.io/gh/B2W-BIT/asgard-api)   |
|Typehint Coverage  |![codecov](https://codecov.io/gh/B2W-BIT/asgard-api/branch/master/graph/badge.svg?flag=typehint)   |


https://docs.asgard.b2w.io

## Projeto Asgard

O Projeto Asgard existe com dois propósitos principais:

 - Facilitar a vida de quem desenvolve aplicações (de todo tipo);
 - Facilitar a vida de quem mantém uma infra-estrutura onde rodam centenas/milhares de aplicações

O primeiro ponto é alcançado provendo uma Interface WEB (e uma API) universal onde a pessoa
responsável por um conjunto de aplicações possa ver, em um único lugar, todas as informações
sobre essas aplicações, como por exemplo: Quantiade de CPU/RAM alocada, Logs recentes gerados por
cada instâncias dessas aplicações, lista das instâncias de cada aplicação, etc.

O segundo ponto é alcançado abstraindo toda a infra-estrutura atrás de um conjunto de APIs onde é possível
permitir que o time responsável pela infra-estrutura possa escolher a melhor opção para orquestração das apps
dos times de dev.


## Features principais

 * Multi-tenant, permitindo que múltiplos times possam usar a mesma UI/API;
 * Separação de recursos de cada time, ou seja, um time não consegue rodar tarefas que consumam recursos de outro time;
 * Permitir que múltiplos orquestradores de containers possam ser usados (Trabalho futuro).

## Ideia geral de implementação

A ideia da Asgard API é ser o único ponto com o qual qualquer código (ou pessoa) deve falar. Essa API
é quem vai abstrair todos os orquestradores suportados pelo projeto. A ideia do projeto é definir seus
próprios Endpoints e Resources genéricos o suficiente para poderem ser transformados/traduzidos em
Endpoints e Resources específicos do orquestrador escolhido.

É a asgard API quem fala com os múltiplos orquestradores, é papel dela receber uma requisição da UI (ou
de um client HTTP qualquer), decidir para qual backend aquele request deve ser encaminhado e então ela
faz todas as transformações necessárias para mudar o request sendo recebido para um formato em que o
orquestrador em questão consiga entender.


## Componentes principais do Projeto Asgard

### Componentes essenciais

- Asgard API (esse repositório)
- Asgard UI, que é a UI oficial do projeto Asgard. (https://github.com/B2W-BIT/asgard-ui)
  - Essa é a UI original do Marathon, com algumas poucas modificações. Modificações não triviais foram submetidas com PRs ao projeto orginal e já foram mergeadas.
- https://github.com/B2W-BIT/asgard-ui-session-checker-plugin
  - Plugin para a UI do Asgard que adiciona o token JWT em todas as requisições feitas à API.

### Componentes opcionais

- https://github.com/B2W-BIT/asgard-log-ingestor
  - Ingestor genérico de logs que lê as linhas de log de um RabbitMQ e indexa em vários destinos possíveis (elasticsearch, cloudwatch logs, etc)
- https://github.com/B2W-BIT/asgard-counts-ingestor
  - Ingestor de metadados de logs, contendo apenas as contagens (de linhas de logs e de byes de logs) de cada aplicação. Esses dados são também lidos de um RabbitMQ e indexados em um elasticsearch.
- https://github.com/B2W-BIT/asgard-app-stats-collector
  - Coletor genérico de estatísticas de uso de CPU/RAM de todas as tarefas do cluster, indexa no elasticsearch já adicionando o nome da App original. Esse coletor será o responsável por falar com outros orquestradores, à medida que suporte a eles for sendo adicionado ao projeto.

## Orquestradores atualmente suportados

Atualmente a Asgard API suporta:

* Mesosphere Marathon (https://mesosphere.github.io/marathon/)
  - Confirmamos que funciona até a versão 1.4.12. Ainda não testamos com versões posteriores (`1.5.x`, `.1.6.x`) mas pretendemos fazer isso em algum momento.
