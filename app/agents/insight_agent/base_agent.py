import abc

class BaseAgent(abc.ABC):
    """
    Abstract base class for all agents in the Harmony Engine.
    Defines the sense-plan-act interface.
    """

    def __init__(self, shared_memory=None):
        self.shared_memory = shared_memory

    @abc.abstractmethod
    def sense(self, *args, **kwargs):
        """
        Gather data or context needed for planning.
        """
        pass

    @abc.abstractmethod
    def plan(self, *args, **kwargs):
        """
        Develop a plan or strategy based on sensed data.
        """
        pass

    @abc.abstractmethod
    def act(self, *args, **kwargs):
        """
        Execute the planned actions.
        """
        pass
