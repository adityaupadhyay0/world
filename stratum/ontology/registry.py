from typing import Dict, Type, Any, Optional
from stratum.ontology.schema import Entity

class OntologyRegistry:
    _registry: Dict[str, Type[Entity]] = {}

    @classmethod
    def register(cls, entity_type: str, model_class: Type[Entity]):
        cls._registry[entity_type] = model_class

    @classmethod
    def get_model(cls, entity_type: str) -> Optional[Type[Entity]]:
        return cls._registry.get(entity_type)

    @classmethod
    def create_instance(cls, entity_dict: Dict[str, Any]) -> Entity:
        entity_type = entity_dict.get('type')
        model_class = cls.get_model(entity_type)
        if not model_class:
            raise ValueError(f"Unknown entity type: {entity_type}")
        return model_class(**entity_dict)

# Register default types
from stratum.ontology.schema import Organization, Employee, Project
OntologyRegistry.register("Organization", Organization)
OntologyRegistry.register("Employee", Employee)
OntologyRegistry.register("Project", Project)
OntologyRegistry.register("Entity", Entity)
