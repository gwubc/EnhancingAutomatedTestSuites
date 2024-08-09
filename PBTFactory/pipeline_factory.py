from PBTFactory.cut_data import CUT_data
from PBTFactory.pipeline import IPipeline
from PBTFactory.pipeline_pbt_base import pipeline_pbt_base
from PBTFactory.pipeline_pbt_v1 import pipeline_pbt_v1
from PBTFactory.pipeline_pbt_v2 import pipeline_pbt_no_expert_knowledge
from PBTFactory.pipeline_unit_base import pipeline_unit_base


class PipelineFactory:
    def __init__(self, pipeline_type: str, config: dict):
        required_keys = ["max_retry", "max_fix", "max_hypothesis_examples"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")
        if "system_message" in config:
            self.system_message = config["system_message"]
        else:
            self.system_message = None

        assert pipeline_type in [
            "pipeline_pbt_v1",
            "pipeline_pbt_v2",
            "pipeline_pbt_base",
            "pipeline_unit_base",
        ], f"Invalid pipeline type: {pipeline_type}"

        self.pipeline_type = pipeline_type
        self.config = config

    def create(self, cut_data: CUT_data) -> IPipeline:
        if self.pipeline_type == "pipeline_unit_base":
            return pipeline_unit_base(
                cut_data,
                max_retry=self.config["max_retry"],
                max_fix=self.config["max_fix"],
                max_hypothesis_examples=self.config["max_hypothesis_examples"],
                system_message=self.system_message,
            )

        if self.pipeline_type == "pipeline_pbt_base":
            return pipeline_pbt_base(
                cut_data,
                max_retry=self.config["max_retry"],
                max_fix=self.config["max_fix"],
                max_hypothesis_examples=self.config["max_hypothesis_examples"],
                system_message=self.system_message,
            )

        if self.pipeline_type == "pipeline_pbt_v1":
            assert "max_strategy_retry" in self.config
            assert "max_strategy_fix" in self.config
            return pipeline_pbt_v1(
                cut_data,
                max_retry=self.config["max_retry"],
                max_fix=self.config["max_fix"],
                max_strategy_retry=self.config["max_strategy_retry"],
                max_strategy_fix=self.config["max_strategy_fix"],
                max_hypothesis_examples=self.config["max_hypothesis_examples"],
                system_message=self.system_message,
            )

        if self.pipeline_type == "pipeline_pbt_v2":
            assert "max_strategy_retry" in self.config
            assert "max_strategy_fix" in self.config
            return pipeline_pbt_no_expert_knowledge(
                cut_data,
                max_retry=self.config["max_retry"],
                max_fix=self.config["max_fix"],
                max_strategy_retry=self.config["max_strategy_retry"],
                max_strategy_fix=self.config["max_strategy_fix"],
                max_hypothesis_examples=self.config["max_hypothesis_examples"],
                system_message=self.system_message,
            )
