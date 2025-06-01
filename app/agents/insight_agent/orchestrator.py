import logging
from .eda_agent import EDAAgent
from .model_agent import ModelAgent
from .eval_agent import EvalAgent
# ReportAgent will be a placeholder for now

class HarmonyOrchestrator:
    """
    Orchestrates the sense-plan-act loop across agents.
    """

    def __init__(self, shared_memory=None):
        self.shared_memory = shared_memory
        self.logger = logging.getLogger("HarmonyOrchestrator")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.eda_agent = EDAAgent(shared_memory)
        self.model_agent = ModelAgent(shared_memory)
        self.eval_agent = EvalAgent(shared_memory)
        self.report_agent = None  # Placeholder

    def run(self, *args, **kwargs):
        self.logger.info("Starting HarmonyOrchestrator sense-plan-act loop.")

        self.logger.info("Activating EDAAgent.")
        self.eda_agent.sense()
        self.eda_agent.plan()
        self.eda_agent.act()

        self.logger.info("Activating ModelAgent.")
        self.model_agent.sense()
        self.model_agent.plan()
        self.model_agent.act()

        self.logger.info("Activating EvalAgent.")
        self.eval_agent.sense()
        self.eval_agent.plan()
        self.eval_agent.act()

        self.logger.info("Activating ReportAgent (placeholder).")
        # Placeholder for ReportAgent logic

        self.logger.info("HarmonyOrchestrator loop complete.")
