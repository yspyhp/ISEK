import threading
from isek.agent.abstract_agent import AbstractAgent


class SingleAgent(AbstractAgent):

    def __init__(
            self,
            **kwargs
    ):
        super().__init__(**kwargs)

    def build(self, daemon=False):
        if not daemon:
            self.run_cli()
        else:
            termination_thread = threading.Thread(target=self.run_cli, daemon=True)
            termination_thread.start()


