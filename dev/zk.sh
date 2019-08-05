
source "dev/vars.sh"

ZOO_PURGE_INTERVAL=10

function zk_node_start() {
    id=${1}
    ip=${2}
    echo -n "ZK (${ip}) "
    docker run -d \
      --name asgard_zk_${id} \
      --rm -it --ip ${ip} \
      -e ZOO_MY_ID=${id} \
      --net ${NETWORK_NAME} \
      --env-file <(
    echo ZOO_PURGE_INTERVAL=${ZOO_PURGE_INTERVAL}
    ) b2wasgard/zookeeper:0.0.1
}


zk_node_start 1 ${ZK_1_IP}
