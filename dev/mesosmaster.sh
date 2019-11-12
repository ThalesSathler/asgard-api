
source "dev/vars.sh"

## MESOS
MESOS_QUORUM=1
MESOS_WORK_DIR=/var/lib/mesos
MESOS_HOSTNAME_LOOKUP=false
MESOS_ZK=zk://${ZK_CLUSTER_IPS}/mesos

function mesos_master_start() {
  id=${1}
  ip=${2}
  echo -n "Mesos Master (${ip}) "
  docker run -d -it --ip ${ip} \
    --name asgard_mesosmaster_${id} \
    --net ${NETWORK_NAME} \
    -e MESOS_IP=${ip} \
    --env-file <(
      echo MESOS_QUORUM=${MESOS_QUORUM}
      echo MESOS_WORK_DIR=${MESOS_WORK_DIR}
      echo MESOS_HOSTNAME_LOOKUP=${MESOS_HOSTNAME_LOOKUP}
      echo MESOS_ZK=${MESOS_ZK}
      ) b2wasgard/mesos:0.0.3 /usr/sbin/mesos-master
}

mesos_master_start 1 ${MESOS_MASTER_1_IP}
