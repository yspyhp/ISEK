from isek.utils.logger import logger
import json
from typing import Dict, Any, List  # Added for type hinting


class Persona:
    """
    Represents the identity, characteristics, and background of an agent.

    A persona defines how an agent behaves, its knowledge base, its mission,
    and its typical routines or operational procedures.
    """

    def __init__(self, name: str, bio: str, lore: str, knowledge: str, routine: str):
        """
        Initializes a new Persona instance.

        :param name: The name of the persona.
        :type name: str
        :param bio: A short biography or description of the persona (e.g., "You are good at...").
        :type bio: str
        :param lore: The background story, mission, or core directives of the persona.
        :type lore: str
        :param knowledge: A description of the persona's knowledge domain or how it provides information.
        :type knowledge: str
        :param routine: A description of the typical operational flow or routine the persona follows.
        :type routine: str
        """
        self.name: str = name
        self.bio: str = bio
        self.lore: str = lore
        self.knowledge: str = knowledge
        self.routine: str = routine
        self.agencies: List[
            Any
        ] = []  # Assuming agencies could be a list of related agent instances or identifiers
        logger.info(f"Created Persona: {self.name}")

    def __str__(self) -> str:
        """
        Returns the string representation of the Persona, which is its name.

        :return: The name of the persona.
        :rtype: str
        """
        return self.name

    @classmethod
    def default(cls) -> "Persona":
        """
        Creates a default Persona instance.

        This persona is a general-purpose "Helper" with predefined attributes.

        :return: A default Persona instance.
        :rtype: Persona
        """
        return cls.from_json(
            {
                "name": "Helper",
                "bio": "You are good at handling various things",
                "lore": "Your mission is to provide users with various assistance. "
                "Be sure to reject all requests involving politics, religion, and pornography, "
                "and do not provide anything that violates the law or morality.",
                "knowledge": "Provide solutions and implementation steps",
                "routine": "You should first understand the user's request, then provide a solution, "
                "and finally ask the user if the solution is satisfactory.",
            }
        )

    @classmethod
    def load(cls, path: str) -> "Persona":
        """
        Loads Persona data from a JSON file and creates a Persona instance.

        :param path: The file path to the JSON file containing persona data.
        :type path: str
        :return: A Persona instance created from the data in the file.
        :rtype: Persona
        :raises FileNotFoundError: If the specified file path does not exist.
        :raises json.JSONDecodeError: If the file content is not valid JSON.
        :raises KeyError: If the JSON data is missing required fields for persona creation.
        """
        try:
            with open(path, "r") as file:
                data: Dict[str, str] = json.load(file)
                return cls.from_json(data)
        except FileNotFoundError:
            logger.error(
                f"Persona file not found: {path}"
            )  # Changed to error for missing file
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from persona file {path}: {e}")
            raise
        # KeyError will be handled by from_json if data structure is incorrect

    @classmethod
    def from_json(cls, data: Dict[str, str]) -> "Persona":
        """
        Creates a Persona instance from a dictionary of data.

        The dictionary keys should correspond to the Persona's constructor parameters
        (`name`, `bio`, `lore`, `knowledge`, `routine`).

        :param data: A dictionary containing the persona attributes.
        :type data: typing.Dict[str, str]
        :return: A Persona instance created from the provided data.
        :rtype: Persona
        :raises KeyError: If the `data` dictionary is missing one or more required keys
                          (name, bio, lore, knowledge, routine).
        """
        try:
            # Ensure all required keys are present before unpacking
            required_keys = {"name", "bio", "lore", "knowledge", "routine"}
            if not required_keys.issubset(data.keys()):
                missing_keys = required_keys - data.keys()
                err_msg = f"Invalid persona data: Missing required keys: {missing_keys}"
                logger.error(err_msg)
                raise KeyError(err_msg)
            return cls(**data)
        except TypeError as e:  # Handles incorrect argument types if not caught by simple presence check
            logger.error(f"Type error creating Persona from data: {data}. Error: {e}")
            raise
        # No need for a specific KeyError catch here if the above check is robust,
        # as cls(**data) itself will raise KeyError for missing args not caught above,
        # or TypeError for unexpected args.
