from typing import Any, Optional

import uvicorn
from a2a.server.apps.jsonrpc import JSONRPCApplication

from isek.node.node_v2 import Node
from isek.node.registry import Registry
from isek.squad.squad import Squad


class A2ANode(Node):
    def __init__(
        self,
        a2a_application: Optional[JSONRPCApplication] = None,
        host: str = "localhost",
        port: int = 8080,
        node_id: Optional[str] = None,
        registry: Optional[Registry] = None,
        squad: Optional[Squad] = None,
        **kwargs: Any,
    ):
        super().__init__(
            host=host,
            port=port,
            node_id=node_id,
            registry=registry,
            squad=squad,
            **kwargs,
        )
        self.a2a_application = a2a_application
        # todo: squad to a2a_application if a2a_application is None

    def bootstrap_server(self):
        uvicorn.run(self.a2a_application.build(), host="0.0.0.0", port=self.port)

    def stop_server(self) -> None:
        pass
