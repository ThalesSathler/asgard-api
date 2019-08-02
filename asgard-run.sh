#!/bin/bash

# Porque não fizemos isso aqui com docker-commpose?
# 1. Existem inúmeras variaveias compartilhadas, por exmeplo, o IP dos ZKs.
# Fazendo isso com compose teríamos que repetir esses valores para todos os compose-files que precisassem deles,
# 2. Existem variáveis compostas por valores de outras variáveis e não podemos fazer essa composição em um envfile; Por isso não usamos envfile.
# 3. Não é possivel passar um envfile pro docker-compose, apenas dentro do compose-file. Se pudéssemos passar até seria pssível
# criar um grande arquivo de env e passar para todas as chamadas do compose.

source "dev/vars.sh"
source "dev/cleanup.sh"

echo "Sleeping for 3s, ^C to cancel now."
sleep 3

source "dev/network.sh"
source "dev/pgsql.sh"
source "dev/elasticsearch.sh"
source "dev/zk.sh"
source "dev/chronos.sh"
sleep 1

source "dev/marathon.sh"
source "dev/mesosmaster.sh"
source "dev/mesosslave.sh"
source "dev/asgard-ui.sh"

#CREATE INITIAL GROUP
echo "Creating initial groups. Waiting for Marathon to come up..."
while true; do
  curl -s -X PUT -d '{"id": "/", "groups": [{"id": "/asgard-dev"}, {"id": "/asgard-infra"}, {"id": "/asgard"}]}' http://${MARATHON_IP}:8080/v2/groups
  if [ $? -eq 0 ]; then
    break;
  fi
done

source "dev/create-apps.sh"

#pipenv run python hollowman/main.py
