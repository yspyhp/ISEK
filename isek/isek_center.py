import json
import threading
import time
from typing import Dict, Any, Optional, Tuple, Union # Added Optional, Tuple, Union

from flask import Flask, request, jsonify, Blueprint
from werkzeug.exceptions import HTTPException # For type hinting Flask error responses

# --- Global State & Configuration ---
isek_center_blueprint = Blueprint('isek_center_blueprint', __name__, url_prefix='/isek_center')

# In-memory storage for registered nodes.
# Structure: { "node_id": {"node_id": str, "host": str, "port": int, "metadata": dict, "expires_at": float} }
nodes: Dict[str, Dict[str, Any]] = {}
NODE_LOCK = threading.Lock() # To protect access to the 'nodes' dictionary

LEASE_DURATION: int = 30  # Seconds for node lease


# --- Response Helper Class ---
class CommonResponse:
    """
    A helper class to standardize JSON API responses.
    """
    def __init__(self, data: Optional[Any], code: int, message: str):
        """
        Initializes a CommonResponse object.

        :param data: The payload data of the response. Can be None.
        :type data: typing.Optional[typing.Any]
        :param code: The HTTP-like status code for the response (e.g., 200 for success, 500 for fail).
        :type code: int
        :param message: A descriptive message accompanying the response.
        :type message: str
        """
        self.data: Optional[Any] = data
        self.code: int = code
        self.message: str = message

    @classmethod
    def success(cls, data: Optional[Any] = None, code: int = 200, message: str = 'success') -> Tuple[Dict[str, Any], int]:
        """
        Creates a standardized success response.

        :param data: Optional data payload for the success response.
        :type data: typing.Optional[typing.Any]
        :param code: The success code. Defaults to 200.
        :type code: int
        :param message: The success message. Defaults to 'success'.
        :type message: str
        :return: A tuple containing the response dictionary and the HTTP status code.
        :rtype: typing.Tuple[typing.Dict[str, typing.Any], int]
        """
        return jsonify(cls(data, code, message).to_dict()), code

    @classmethod
    def fail(cls, message: str, code: int = 400, data: Optional[Any] = None) -> Tuple[Dict[str, Any], int]:
        """
        Creates a standardized failure/error response.

        Commonly used for client errors (e.g., bad request, not found).

        :param message: The failure message.
        :type message: str
        :param code: The error code. Defaults to 400 (Bad Request).
        :type code: int
        :param data: Optional data payload accompanying the failure.
        :type data: typing.Optional[typing.Any]
        :return: A tuple containing the response dictionary and the HTTP status code.
        :rtype: typing.Tuple[typing.Dict[str, typing.Any], int]
        """
        return jsonify(cls(data, code, message).to_dict()), code

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the CommonResponse instance to a dictionary.

        :return: A dictionary representation of the response.
        :rtype: typing.Dict[str, typing.Any]
        """
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }

# --- Flask Route Definitions ---
FlaskResponse = Tuple[Dict[str, Any], int] # Type alias for Flask view return

@isek_center_blueprint.route('/register', methods=['POST'])
def register_node_route() -> FlaskResponse:
    """
    Registers a new node or updates an existing node's registration.

    Expects a JSON payload with `node_id`, `host`, `port`, and optional `metadata`.
    Assigns an expiration time to the node's registration (lease).

    **Request JSON Body:**
    
    .. code-block:: json

        {
            "node_id": "unique_node_identifier",
            "host": "node_hostname_or_ip",
            "port": 8080,
            "metadata": {"key": "value"} 
        }

    **Responses:**
    
    - **200 OK:** Node registered successfully.
    - **400 Bad Request:** Missing required fields (`node_id`, `host`, `port`).

    :return: A Flask JSON response.
    :rtype: FlaskResponse
    """
    data = request.json
    if not data:
        return CommonResponse.fail(message="Request body must be JSON.", code=400)

    node_id = data.get('node_id')
    host = data.get('host')
    port = data.get('port')
    metadata = data.get('metadata') # Optional

    if not all([node_id, host, port]): # Port can be 0, but typically not for services.
        return CommonResponse.fail(message="'node_id', 'host', and 'port' are required fields.", code=400)
    
    if not isinstance(port, int):
        return CommonResponse.fail(message="'port' must be an integer.", code=400)

    with NODE_LOCK:
        nodes[node_id] = {
            "node_id": node_id,
            "host": host,
            "port": port,
            "metadata": metadata or {}, # Ensure metadata is a dict
            "expires_at": time.time() + LEASE_DURATION
        }
    # print(f"Node registered/updated: {node_id}, Expires at: {nodes[node_id]['expires_at']}") # Debug
    return CommonResponse.success(message=f"Node '{node_id}' registered successfully.")


@isek_center_blueprint.route('/deregister', methods=['POST'])
def deregister_node_route() -> FlaskResponse:
    """
    Deregisters a node from the service.

    Expects a JSON payload with `node_id`.

    **Request JSON Body:**
    
    .. code-block:: json

        {
            "node_id": "unique_node_identifier"
        }

    **Responses:**
    
    - **200 OK:** Node deregistered successfully.
    - **400 Bad Request:** Missing or invalid `node_id`.
    - **404 Not Found:** If `node_id` does not exist (alternative to 400 for invalid).

    :return: A Flask JSON response.
    :rtype: FlaskResponse
    """
    data = request.json
    if not data:
        return CommonResponse.fail(message="Request body must be JSON.", code=400)

    node_id = data.get('node_id')

    if not node_id:
        return CommonResponse.fail(message="'node_id' is required.", code=400)

    with NODE_LOCK:
        if node_id not in nodes:
            return CommonResponse.fail(message=f"Node '{node_id}' not found for deregistration.", code=404)
        removed_node = nodes.pop(node_id)
    # print(f"Node deregistered: {node_id}, Details: {removed_node}") # Debug
    return CommonResponse.success(message=f"Node '{node_id}' deregistered successfully.")


@isek_center_blueprint.route('/available_nodes', methods=['GET'])
def get_available_nodes_route() -> FlaskResponse:
    """
    Retrieves a list of all currently active (non-expired) registered nodes.

    **Responses:**
    
    - **200 OK:** Returns a list of available nodes.
      The response data will be structured as follows:
      
      .. code-block:: json
      
          {
              "available_nodes": {
                  "node_id_1": {
                      "node_id": "node_id_1",
                      "host": "host1.example.com",
                      "port": 8080,
                      "metadata": {"key1": "value1"},
                      "expires_at": 1678886400.0
                  },
                  "node_id_2": {
                      "node_id": "node_id_2",
                      "host": "host2.example.com",
                      "port": 8081,
                      "metadata": {},
                      "expires_at": 1678886500.0
                  }
              }
          }

    :return: A Flask JSON response containing the available nodes.
    :rtype: FlaskResponse
    """
    current_time = time.time()
    with NODE_LOCK:
        # Create a copy to iterate over, in case cleanup_expired_nodes runs concurrently
        # (though cleanup also uses the lock, this is safer for reads if not).
        # More importantly, this filters based on expiration.
        active_nodes = {
            k: v for k, v in nodes.items() if v.get('expires_at', 0) > current_time
        }
    
    response_payload = {"available_nodes": active_nodes}
    # print(f"Returning {len(active_nodes)} available nodes.") # Debug
    return CommonResponse.success(data=response_payload)


@isek_center_blueprint.route('/renew', methods=['POST'])
def renew_lease_route() -> FlaskResponse:
    """
    Renews the lease for an existing registered node.

    Expects a JSON payload with `node_id`. Updates the node's `expires_at` timestamp.

    **Request JSON Body:**
    
    .. code-block:: json

        {
            "node_id": "unique_node_identifier"
        }

    **Responses:**
    
    - **200 OK:** Lease renewed successfully.
    - **400 Bad Request:** Missing or invalid `node_id`.
    - **404 Not Found:** If `node_id` does not exist.

    :return: A Flask JSON response.
    :rtype: FlaskResponse
    """
    data = request.json
    if not data:
        return CommonResponse.fail(message="Request body must be JSON.", code=400)

    node_id = data.get('node_id')

    if not node_id:
        return CommonResponse.fail(message="'node_id' is required.", code=400)

    with NODE_LOCK:
        if node_id not in nodes:
            return CommonResponse.fail(message=f"Node '{node_id}' not found for lease renewal.", code=404)
        
        # Check if it's already expired before renewing (optional, but good for consistency)
        # if nodes[node_id].get('expires_at', 0) <= time.time():
        #     return CommonResponse.fail(message=f"Node '{node_id}' lease has already expired. Please re-register.", code=410) # 410 Gone

        nodes[node_id]['expires_at'] = time.time() + LEASE_DURATION
    # print(f"Lease renewed for node: {node_id}, New expires_at: {nodes[node_id]['expires_at']}") # Debug
    return CommonResponse.success(message=f"Lease for node '{node_id}' renewed successfully.")

# --- Background Task for Node Cleanup ---
def cleanup_expired_nodes() -> None:
    """
    Periodically removes expired nodes from the `nodes` dictionary.

    This function runs in a separate daemon thread.
    It checks every 5 seconds for nodes whose lease (`expires_at`) has passed.
    """
    # print("Cleanup thread started.") # Debug
    while True:
        time.sleep(5) # Check interval
        current_time = time.time()
        expired_node_ids: List[str] = []
        
        with NODE_LOCK:
            # Identify expired nodes without modifying dict during iteration
            for node_id, node_data in nodes.items():
                if node_data.get('expires_at', 0) <= current_time:
                    expired_node_ids.append(node_id)
            
            # Remove expired nodes
            for node_id in expired_node_ids:
                removed_node = nodes.pop(node_id, None) # Safely remove
                if removed_node:
                    # print(f"Cleanup: Removed expired node '{node_id}'. Expired at: {removed_node.get('expires_at')}") # Debug
                    pass # Optionally log to Flask/app logger if configured

# --- Main Application Setup ---
def main() -> None:
    """
    Sets up and runs the Flask application for the Isek Center.

    Initializes a background thread for cleaning up expired node registrations
    and starts the Flask development server.
    """
    # Start the cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_expired_nodes, daemon=True)
    cleanup_thread.start()

    # Create and configure the Flask app
    app = Flask(__name__)
    app.register_blueprint(isek_center_blueprint)

    # Optional: Add a root/health check endpoint
    @app.route('/')
    def health_check() -> str:
        """Basic health check endpoint."""
        return "Isek Center is running!"

    # Run the Flask app
    # For production, use a proper WSGI server like Gunicorn or uWSGI
    # print("Starting Isek Center Flask application on http://0.0.0.0:8088") # Debug
    app.run(host='0.0.0.0', port=8088, debug=False) # debug=False for production-like behavior

if __name__ == '__main__':
    main()