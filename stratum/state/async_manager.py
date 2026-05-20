from typing import List, Dict, Any, Optional
from stratum.state.world_state import WorldState
from stratum.state.async_event_log import AsyncEventLog
from stratum.ontology.schema import Entity, Relation
from stratum.ontology.registry import OntologyRegistry
import logging

class AsyncStateManager:
    def __init__(self, world_state: WorldState, event_log: AsyncEventLog):
        self.world_state = world_state
        self.event_log = event_log
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        await self.event_log._init_db()

    async def create_entity(self, entity: Entity, cause: Optional[str] = None):
        self.world_state.add_entity(entity)
        await self.event_log.log_event(
            event_type="ENTITY_CREATED",
            data=entity.model_dump(mode='json'),
            source_id=entity.id,
            cause=cause
        )

    async def update_entity(self, entity: Entity, cause: Optional[str] = None):
        old_entity = self.world_state.get_entity(entity.id)
        if not old_entity:
            raise ValueError(f"Entity {entity.id} does not exist.")

        self.world_state.update_entity(entity)
        await self.event_log.log_event(
            event_type="ENTITY_UPDATED",
            data={
                "old": old_entity.model_dump(mode='json'),
                "new": entity.model_dump(mode='json')
            },
            source_id=entity.id,
            cause=cause
        )

    async def add_relation(self, relation: Relation, cause: Optional[str] = None):
        self.world_state.add_relation(relation)
        await self.event_log.log_event(
            event_type="RELATION_ADDED",
            data=relation.model_dump(mode='json'),
            source_id=relation.source_id,
            cause=cause
        )

    async def validate_and_commit_update(self, update_data: Dict[str, Any], cause: Optional[str] = None):
        for entity_dict in update_data.get('entities', []):
            entity = OntologyRegistry.create_instance(entity_dict)
            if self.world_state.get_entity(entity.id):
                await self.update_entity(entity, cause=cause)
            else:
                await self.create_entity(entity, cause=cause)

        for rel_dict in update_data.get('relations', []):
            relation = Relation(**rel_dict)
            await self.add_relation(relation, cause=cause)

    def get_state_snapshot(self, entity_ids: List[str]) -> Dict[str, Any]:
        # Snapshot reading remains sync as it's memory-bound
        snapshot = {"entities": [], "relations": []}
        for eid in entity_ids:
            entity = self.world_state.get_entity(eid)
            if entity:
                snapshot["entities"].append(entity.model_dump(mode='json'))
                relations = self.world_state.get_relations(source_id=eid)
                for rel in relations:
                    snapshot["relations"].append(rel.model_dump(mode='json'))
        return snapshot
