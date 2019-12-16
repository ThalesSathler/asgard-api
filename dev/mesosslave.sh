source "dev/vars.sh"

## MESOS SLAVE
MESOS_ATTRIBUTES=";mesos:slave;"
MESOS_RESOURCES="cpus(*):2;mem(*):2048;ports(*):[31000-31999];cpus(asgard):0.5;mem(asgard):512;ports(asgard):[30000-30999]"
MESOS_MASTER=zk://${ZK_CLUSTER_IPS}/mesos

function start_mesos_slave() {
    id=${RANDOM}
    ip=${1}
    namespace=${2}
    aditional_attrs=$(echo ${3} | cut -f 2 -d '=')

    all_attrs="${MESOS_ATTRIBUTES};${aditional_attrs};owner:${namespace}"
    container_id=$(docker run -d -it --ip ${ip} \
      --name asgard_mesosslave_${RANDOM} \
      --net ${NETWORK_NAME} \
      --restart always \
      --env-file <(
    echo MESOS_SYSTEMD_ENABLE_SUPPORT=false
    echo MESOS_WORK_DIR=/var/lib/mesos
    echo MESOS_IP=${ip}
    echo LIBPROCESS_ADVERTISE_IP=${ip}
    echo MESOS_ATTRIBUTES="${MESOS_ATTRIBUTES};${aditional_attrs};owner:${namespace}"
    echo MESOS_MASTER=${MESOS_MASTER}
    echo MESOS_RESOURCES=${MESOS_RESOURCES}
    echo MESOS_CGROUPS_ENABLE_CFS=1
    echo MESOS_CGROUPS_CPU_ENABLE_PIDS_AND_TIDS_COUNT=1
    ) \
      -v /sys/fs/cgroup:/sys/fs/cgroup \
      -v /var/run/docker.sock:/var/run/docker.sock \
      -v $(dirname $(readlink --canonicalize ${0}))/scripts/docker.tar.bz2:/etc/docker.tar.bz2 \
      ${MESOS_IMAGE} /usr/sbin/mesos-agent)

    echo "Mesos Slave conatiner_id=${container_id:0:7} ns=${namespace} addr=${ip} attrs=${all_attrs}"
}

# Slaves do time asgard-infra, datacenters `gcp` e `aws`
start_mesos_slave "172.18.0.51" "asgard-infra" "extra_attrs=workload:general;dc:gcp"
#start_mesos_slave "172.18.0.52" "asgard-infra" "extra_attrs=workload:general;dc:gcp"
#start_mesos_slave "172.18.4.10" "asgard-infra" "extra_attrs=workload:general;dc:aws"
#start_mesos_slave "172.18.4.11" "asgard-infra" "extra_attrs=workload:general;dc:aws"
#
## Slaves do time asgard-dev, datacenters `gcp` e `aws`
#start_mesos_slave "172.18.2.10" "asgard-dev" "extra_attrs=workload:general;dc:gcp"
#start_mesos_slave "172.18.2.11" "asgard-dev" "extra_attrs=workload:general;dc:gcp"
#start_mesos_slave "172.18.3.20" "asgard-dev" "extra_attrs=workload:general;dc:aws"
#start_mesos_slave "172.18.3.30" "asgard-dev" "extra_attrs=workload:general;dc:aws"
#
## MysQL
#start_mesos_slave "172.18.5.1" "asgard-dev" "extra_attrs=workload:mysql-wordpress;dc:aws"
#
#
## Slaves do Core do Asgard
#start_mesos_slave "172.18.0.18" "asgard" "extra_attrs=workload:general;dc:aws"
#start_mesos_slave "172.18.0.19" "asgard" "extra_attrs=workload:general;dc:aws"
#start_mesos_slave "172.18.0.20" "asgard" "extra_attrs=workload:asgard-cache;dc:aws"
#start_mesos_slave "172.18.0.21" "asgard" "extra_attrs=workload:asgard-log-ingest-rabbitmq;dc:aws"
#
