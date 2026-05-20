import asyncio
import pytest
import os
from stratum.state.world_state import WorldState
from stratum.state.async_event_log import AsyncEventLog
from stratum.state.async_manager import AsyncStateManager
from stratum.ontology.schema import Organization

@pytest.mark.asyncio
async def test_async_state_manager():
    db_path = "test_async.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    ws = WorldState()
    el = AsyncEventLog(db_path=db_path)
    sm = AsyncStateManager(ws, el)
    await sm.initialize()

    org = Organization(id="o1", name="Test", balance=100)
    await sm.create_entity(org)

    retrieved = ws.get_entity("o1")
    assert retrieved.name == "Test"

    events = await el.get_events(limit=1)
    assert len(events) == 1
    assert events[0]['event_type'] == 'ENTITY_CREATED'

    if os.path.exists(db_path):
        os.remove(db_path)
