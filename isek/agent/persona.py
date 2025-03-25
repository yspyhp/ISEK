from isek.util.logger import logger
import json


class Persona:
    def __init__(self, name, bio, lore, knowledge, routine):
        self.name = name
        self.bio = bio
        self.lore = lore
        self.knowledge = knowledge
        self.routine = routine
        self.agencies = []
        logger.info(f'Created Persona: {self.name}')
    
    def __str__(self):
        return self.name

    @classmethod
    def default(cls):
        return cls.from_json({
            "name": "Helper",
            "bio": "You are good at handling various things",
            "lore": "Your mission is to provide users with various assistance Be sure to reject all requests involving politics, religion, and pornography, and do not provide anything that violates the law or morality.",
            "knowledge": "Provide solutions and implementation steps",
            "routine": "You should first understand the user's request, then provide a solution, and finally ask the user if the solution is satisfactory."
        })
    
    @classmethod
    def load(cls, path):
        try:
            with open(path, 'r') as file:
                data = json.load(file)
                return cls.from_json(data)
        except FileNotFoundError:
            logger.exception(f'File not found: {path}')
            raise

    @classmethod
    def from_json(cls, data):
        try:
            return cls(**data)
        except KeyError:
            logger.exception(f'Invalid data: {data}')
            raise
