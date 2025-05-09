import time

import isek.agent.persona
from isek.isek_config import IsekConfig


def main():
    sylana_config = IsekConfig("sylana/sylana_config.yaml")
    sylana_agent = sylana_config.load_agent()
    sylana_agent.persona = isek.agent.persona.Persona.default()
    sylana_agent.tool_manager.register_tools([sylana_agent.send_message])
    sylana_agent.build(daemon=True)

    dobby_config = IsekConfig("dobby/dobby_config.yaml")
    dobby_agent = dobby_config.load_agent()
    dobby_agent.build(daemon=True)

    time.sleep(5)
    hello = f"Hello! My name is {sylana_agent.persona.name}"
    print(f"{sylana_agent.persona.name}: {hello}")

    response = sylana_agent.run(f"call Dobby and say: {hello}")
    print(f"{dobby_agent.persona.name}: {response}")


if __name__ == '__main__':
    main()
