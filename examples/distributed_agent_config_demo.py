import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../isek")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../examples")))
import time
from isek.isek_config import IsekConfig


def main():
    
    sylana_config = IsekConfig("sylana/sylana_config.yaml")
    sylana_agent = sylana_config.load_agent()
    sylana_agent.build(daemon=True)

    dobby_config = IsekConfig("dobby/dobby_config.yaml")
    dobby_agent = dobby_config.load_agent()
    dobby_agent.build(daemon=True)

    time.sleep(5)
    hello = f"Hello! My name is {sylana_agent.persona.name}"
    print(f"{sylana_agent.persona.name}: {hello}")

    response = sylana_agent.send_message(dobby_agent.node_id, hello)
    print(f"{dobby_agent.persona.name}: {response}")


if __name__ == '__main__':
    main()
