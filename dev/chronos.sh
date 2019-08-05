
source "dev/vars.sh"

## Chronos
CHRONOS_PORT=9090


function chronos_start(){
  ip=${1}
  id=${RANDOM}
  echo -n "Chronos (${ip}) "
  docker run -d -it --ip ${ip} \
    --restart always \
    --name asgard_chronos_${id} \
    --net ${NETWORK_NAME} \
    -e HOST=${CHRONOS_IP} \
    b2wasgard/chronos:0.1.0 java \
          -jar \
          /chronos/chronos.jar \
          --zk_hosts \
          zk://${ZK_CLUSTER_IPS}/mesos \
          --zk_path \
          /asgard-chronos \
          --master \
          zk://${ZK_CLUSTER_IPS}/mesos \
          --http_port \
          ${CHRONOS_PORT} \
          --mesos_framework_name \
          asgard-chronos \
          --hostname \
          asgard-chronos \
          --min_revive_offers_interval \
          60000
}

chronos_start ${CHRONOS_IP}
