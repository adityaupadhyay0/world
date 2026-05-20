from typing import List, Dict, Any, Optional
from stratum.state.world_state import WorldState
from stratum.state.event_log import EventLog
from stratum.ontology.schema import Entity, Relation, Employee, Project, Organization
import logging

class StateManager:
    def __init__(self, world_state: WorldState, event_log: EventLog):
        self.world_state = world_state
        self.event_log = event_log
        self.logger = logging.getLogger(__name__)

    def create_entity(self, entity: Entity, cause: Optional[str] = None):
        self.world_state.add_entity(entity)
        self.event_log.log_event(
            event_type="ENTITY_CREATED",
            data=entity.model_dump(mode='json'),
            source_id=entity.id,
            cause=cause
        )

    def update_entity(self, entity: Entity, cause: Optional[str] = None):
        old_entity = self.world_state.get_entity(entity.id)
        if not old_entity:
            raise ValueError(f"Entity {entity.id} does not exist.")

        self.world_state.update_entity(entity)
        self.event_log.log_event(
            event_type="ENTITY_UPDATED",
            data={
                "old": old_entity.model_dump(mode='json'),
                "new": entity.model_dump(mode='json')
            },
            source_id=entity.id,
            cause=cause
        )

    def add_relation(self, relation: Relation, cause: Optional[str] = None):
        self.world_state.add_relation(relation)
        self.event_log.log_event(
            event_type="RELATION_ADDED",
            data=relation.model_dump(mode='json'),
            source_id=relation.source_id,
            cause=cause
        )

    def get_state_snapshot(self, entity_ids: List[str]) -> Dict[str, Any]:
        """
        Returns a snapshot of the requested entities and their relations.
        This is the 'StateReader' functionality.
        """
        snapshot = {
            "entities": [],
            "relations": []
        }
        for eid in entity_ids:
            entity = self.world_state.get_entity(eid)
            if entity:
                snapshot["entities"].append(entity.model_dump(mode='json'))
                relations = self.world_state.get_relations(source_id=eid)
                for rel in relations:
                    snapshot["relations"].append(rel.model_dump(mode='json'))
        return snapshot

    def validate_and_commit_update(self, update_data: Dict[str, Any], cause: Optional[str] = None):
        """
        Validates and commits an update. This is the 'StateWriter' functionality.
        Expected format: {'entities': [EntityDict], 'relations': [RelationDict]}
        """
        # In a real implementation, this would use the ontology to parse the dicts
        # and check against causal constraints. For now, we perform basic validation.

        for entity_dict in update_data.get('entities', []):
            # Dynamic re-instantiation to validate schema
            entity_type = entity_dict.get('type')
            if entity_type == "Employee":
                entity = Employee(**entity_dict)
            elif entity_type == "Project":
                entity = Project(**entity_dict)
            elif entity_type == "Organization":
                entity = Organization(**entity_dict)
            else:
                entity = Entity(**entity_dict)

            if self.world_state.get_entity(entity.id):
                self.update_entity(entity, cause=cause)
            else:
                self.create_entity(entity, cause=cause)

        for rel_dict in update_data.get('relations', []):
            relation = Relation(**rel_dict)
            self.add_relation(relation, cause=cause)
