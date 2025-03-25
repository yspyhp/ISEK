from flask import Flask, request, jsonify, Blueprint
import threading
import time

isek_center_blueprint = Blueprint('isek_center_blueprint', __name__, url_prefix='/isek_center')

nodes = {}

LEASE_DURATION = 30


class CommonResponse(object):
    def __init__(self, data, code, message):
        self.data = data
        self.code = code
        self.message = message

    @classmethod
    def success(cls, data=None, code=200, message='success'):
        return cls(data, code, message).to_dict()

    @classmethod
    def fail(cls, data=None, code=500, message='fail'):
        return cls(data, code, message).to_dict()

    @classmethod
    def error(cls, e):
        return cls(None, e.code, e.message).to_dict()

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }


@isek_center_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    node_id = data.get('node_id')
    host = data.get('host')
    port = data.get('port')
    metadata = data.get('metadata')

    if not node_id or not host or not port:
        return CommonResponse.fail(message="node_id and host/port are required", code=400)

    nodes[node_id] = {
        "node_id": node_id,
        "host": host,
        "port": port,
        "metadata": metadata,
        "expires_at": time.time() + LEASE_DURATION
    }

    return CommonResponse.success()


@isek_center_blueprint.route('/deregister', methods=['POST'])
def deregister():
    data = request.json
    node_id = data.get('node_id')

    if not node_id or node_id not in nodes:
        return CommonResponse.fail(message="Invalid node_id", code=400)

    nodes.pop(node_id)

    return CommonResponse.success()


@isek_center_blueprint.route('/available_nodes', methods=['GET'])
def get_available_nodes():
    current_time = time.time()
    available_nodes = {k: v for k, v in nodes.items() if v['expires_at'] > current_time}
    response = {
        "available_nodes": available_nodes
    }
    return CommonResponse.success(response)


@isek_center_blueprint.route('/renew', methods=['POST'])
def renew():
    data = request.json
    node_id = data.get('node_id')

    if not node_id or node_id not in nodes:
        return CommonResponse.fail(message="Invalid node_id", code=400)

    nodes[node_id]['expires_at'] = time.time() + LEASE_DURATION

    return CommonResponse.success()


def cleanup_expired_nodes():
    while True:
        current_time = time.time()
        expired_nodes = [k for k, v in nodes.items() if v['expires_at'] <= current_time]

        for node_id in expired_nodes:
            nodes.pop(node_id, None)

        time.sleep(5)


def main():
    cleanup_thread = threading.Thread(target=cleanup_expired_nodes, daemon=True)
    cleanup_thread.start()
    app = Flask(__name__)
    app.register_blueprint(isek_center_blueprint)
    app.run(host='0.0.0.0', port=8088, debug=False)

if __name__ == '__main__':
    main()
