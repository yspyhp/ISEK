import threading
from isek.agent.abstract_agent import AbstractAgent
from typing import Any  # Added for **kwargs type hint


class SingleAgent(AbstractAgent):
    """
    A concrete implementation of an agent that runs as a single, standalone instance.

    This agent type typically interacts via a command-line interface (CLI)
    and does not inherently possess distributed or networked capabilities
    unless explicitly added through its tools or persona logic. It builds upon
    the :class:`~isek.agent.abstract_agent.AbstractAgent`.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the SingleAgent.

        This constructor directly calls the initializer of the parent class,
        :class:`~isek.agent.abstract_agent.AbstractAgent`, passing along any
        provided keyword arguments.

        :param kwargs: Keyword arguments to be passed to the
                       :class:`~isek.agent.abstract_agent.AbstractAgent` constructor
                       (e.g., `persona`, `model`, `tools`).
        :type kwargs: typing.Any
        """
        super().__init__(**kwargs)

    def build(self, daemon: bool = False) -> None:
        """
        Builds and starts the single agent, typically by launching its command-line interface.

        If `daemon` is `False` (the default), the agent's CLI
        (:meth:`~isek.agent.abstract_agent.AbstractAgent.run_cli`)
        is run in the current thread, which will block further execution in that thread
        until the CLI is exited.

        If `daemon` is `True`, the CLI is started in a separate daemon thread,
        allowing the main program to continue executing while the agent runs
        in the background.

        :param daemon: If `True`, run the agent's CLI in a daemon thread.
                       Defaults to `False`.
        :type daemon: bool
        """
        if not daemon:
            # This will block if run_cli is a blocking loop
            self.run_cli()
        else:
            # run_cli will execute in a separate thread
            cli_thread = threading.Thread(target=self.run_cli, daemon=True)
            cli_thread.start()
