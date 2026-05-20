import networkx as nx
import copy
from typing import Dict, List, Optional, Any, Union
from stratum.ontology.schema import Entity, Relation, Employee, Project, Organization
import logging

class WorldState:
    def clone(self) -> 'WorldState':
        new_ws = WorldState()
        new_ws.entities = copy.deepcopy(self.entities)
        new_ws.graph = self.graph.copy()
        return new_ws

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.graph = nx.MultiDiGraph()
        self.logger = logging.getLogger(__name__)

    def add_entity(self, entity: Entity):
        if entity.id in self.entities:
            self.logger.warning(f"Entity {entity.id} already exists. Overwriting.")
        self.entities[entity.id] = entity
        self.graph.add_node(entity.id, type=entity.type)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)

    def add_relation(self, relation: Relation):
        if relation.source_id not in self.entities:
            raise ValueError(f"Source entity {relation.source_id} does not exist.")
        if relation.target_id not in self.entities:
            raise ValueError(f"Target entity {relation.target_id} does not exist.")

        self.graph.add_edge(
            relation.source_id,
            relation.target_id,
            key=relation.relation_type,
            relation_type=relation.relation_type,
            **relation.properties
        )

    def get_relations(self, source_id: Optional[str] = None, target_id: Optional[str] = None) -> List[Relation]:
        relations = []
        if source_id and target_id:
            if self.graph.has_edge(source_id, target_id):
                all_data = self.graph.get_edge_data(source_id, target_id)
                for key, data in all_data.items():
                    relations.append(Relation(
                        source_id=source_id,
                        target_id=target_id,
                        relation_type=data['relation_type'],
                        properties={k: v for k, v in data.items() if k != 'relation_type'}
                    ))
        elif source_id:
            if source_id in self.graph:
                for target in self.graph.successors(source_id):
                    all_data = self.graph.get_edge_data(source_id, target)
                    for key, data in all_data.items():
                        relations.append(Relation(
                            source_id=source_id,
                            target_id=target,
                            relation_type=data['relation_type'],
                            properties={k: v for k, v in data.items() if k != 'relation_type'}
                        ))
        elif target_id:
            if target_id in self.graph:
                for source in self.graph.predecessors(target_id):
                    all_data = self.graph.get_edge_data(source, target_id)
                    for key, data in all_data.items():
                        relations.append(Relation(
                            source_id=source,
                            target_id=target_id,
                            relation_type=data['relation_type'],
                            properties={k: v for k, v in data.items() if k != 'relation_type'}
                        ))
        return relations

    def remove_entity(self, entity_id: str):
        if entity_id in self.entities:
            del self.entities[entity_id]
        if entity_id in self.graph:
            self.graph.remove_node(entity_id)

    def update_entity(self, entity: Entity):
        if entity.id not in self.entities:
            raise ValueError(f"Entity {entity.id} does not exist.")
        self.entities[entity.id] = entity
        # Update node metadata if needed, though most lives in self.entities
        self.graph.nodes[entity.id]['type'] = entity.type
