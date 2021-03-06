import etcd

from tendrl.commons import objects
from tendrl.commons.utils import log_utils as logger


class Create(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(Create, self).__init__(*args, **kwargs)

    def run(self):
        args = {}
        if self.parameters.get('Volume.replica_count') is not None:
            args.update({
                "replica_count": self.parameters.get('Volume.replica_count')
            })
        if self.parameters.get('Volume.transport') is not None:
            args.update({
                "transport": self.parameters.get('Volume.transport')
            })
        if self.parameters.get('Volume.disperse_count') is not None:
            args.update({
                "disperse_count": self.parameters.get('Volume.disperse_count')
            })
        if self.parameters.get('Volume.redundancy_count') is not None:
            args.update({
                "redundancy_count": self.parameters.get(
                    'Volume.redundancy_count'
                )
            })
        if self.parameters.get('Volume.tuned_profile') is not None:
            args.update({
                "tuned_profile": self.parameters.get('Volume.tuned_profile')
            })
        if self.parameters.get('Volume.force') is not None:
            args.update({
                "force": self.parameters.get('Volume.force')
            })

        logger.log(
            "info",
            NS.publisher_id,
            {"message": "Creating the volume %s" %
             self.parameters['Volume.volname']},
            job_id=self.parameters["job_id"],
            flow_id=self.parameters["flow_id"],
            integration_id=NS.tendrl_context.integration_id
        )

        if NS.gdeploy_plugin.create_volume(
                self.parameters.get('Volume.volname'),
                self.parameters.get('Volume.bricks'),
                **args
        ):
            logger.log(
                "info",
                NS.publisher_id,
                {"message": "Created the volume %s" %
                 self.parameters['Volume.volname']},
                job_id=self.parameters["job_id"],
                flow_id=self.parameters["flow_id"],
                integration_id=NS.tendrl_context.integration_id
            )

            # mark the bricks that were used to create this volume as
            # used bricks so that they are not consumed again
            for sub_vol in self.parameters.get('Volume.bricks'):
                for brick in sub_vol:
                    ip = brick.keys()[0]
                    brick_path = brick.values()[0]
                    try:
                        # Find node id using ip
                        node_id = NS._int.client.read(
                            "indexes/ip/%s" % ip
                        ).value
                    except etcd.EtcdKeyNotFound:
                        # Find node id using hostname
                        nodes = NS._int.client.read("nodes/")
                        for node in nodes.leaves:
                            hostname = NS._int.client.read(
                                "%s/NodeContext/fqdn" % node.key).value
                            if hostname == ip:
                                node_id = node.key.split("/")[-1]
                    key = "nodes/%s/NodeContext/fqdn" % node_id
                    host = NS._int.client.read(key).value
                    brick_path = host + "/" + brick_path.replace("/", "_")[1:]
                    NS._int.wclient.delete(
                        ("clusters/%s/Bricks/free/%s") % (
                            NS.tendrl_context.integration_id,
                            brick_path
                        )
                    )
                    NS._int.wclient.write(
                        ("clusters/%s/Bricks/used/%s") % (
                            NS.tendrl_context.integration_id,
                            brick_path
                        ),
                        ""
                    )
        else:
            logger.log(
                "error",
                NS.publisher_id,
                {"message": "Volume creation failed for volume %s" %
                 self.parameters['Volume.volname']},
                job_id=self.parameters["job_id"],
                flow_id=self.parameters["flow_id"],
                integration_id=NS.tendrl_context.integration_id
            )
            return False
        return True
