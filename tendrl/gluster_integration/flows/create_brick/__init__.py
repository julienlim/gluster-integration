from tendrl.commons import flows
from tendrl.commons.utils import log_utils as logger


class CreateBrick(flows.BaseFlow):
    def run(self):
        logger.log(
            "info",
            NS.publisher_id,
            {"message": "Starting Brick creation flow"},
            job_id=self.job_id,
            flow_id=self.parameters['flow_id'],
            integration_id=NS.tendrl_context.integration_id
        )
        super(CreateBrick, self).run()
