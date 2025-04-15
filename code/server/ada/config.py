from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import yaml

DEFAULT_CONFIG_PATH = "config/config.yaml"


@dataclass
class MySQLConfig:
    host: str
    user: str
    password: str
    database: str


@dataclass
class ElasticSearchConfig:
    host: str
    index: str
    field: str


@dataclass
class NLUConfig:
    model_path: str


@dataclass
class TopicSuggestorConfig:
    model_path: str


@dataclass
class NLGeneratorConfig:
    class_name: str
    args: Optional[Dict[str, Any]] = None


@dataclass
class NLGConfig:
    generators: List[NLGeneratorConfig]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> NLGConfig:
        generators = [
            NLGeneratorConfig(**item) for item in data.get("generators", [])
        ]
        return cls(generators=generators)


class Config:
    _instance = None
    _initialized = False

    def __init__(self, path: str = DEFAULT_CONFIG_PATH) -> None:
        if Config._initialized:
            return

        data = self._load_config(path)
        self.sql = MySQLConfig(**data["mysql"])
        self.es = ElasticSearchConfig(**data["elasticsearch"])
        self.nlu = NLUConfig(**data["nlu"])
        self.nlg = NLGConfig.from_dict(data["nlg"])
        self.topic_suggestor = TopicSuggestorConfig(**data["topic_suggestor"])
        Config._initialized = True

    def __new__(cls, path: str = DEFAULT_CONFIG_PATH) -> Config:
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def _load_config(self, path: str) -> Dict[str, Any]:
        with open(path, "r") as config:
            return yaml.safe_load(config)
