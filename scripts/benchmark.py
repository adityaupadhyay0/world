import time
import asyncio
import os
from stratum.state.world_state import WorldState
from stratum.state.async_event_log import AsyncEventLog
from stratum.state.async_manager import AsyncStateManager
from stratum.ontology.schema import Organization

async def benchmark():
    db_path = "bench.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    ws = WorldState()
    el = AsyncEventLog(db_path=db_path)
    sm = AsyncStateManager(ws, el)
    await sm.initialize()

    n = 100
    start = time.time()
    for i in range(n):
        org = Organization(id=f"o{i}", name=f"Org {i}", balance=100)
        await sm.create_entity(org)

    end = time.time()
    print(f"Time for {n} async entity creations: {end - start:.4f}s")
    print(f"Avg latency: {(end - start)/n * 1000:.2f}ms")

    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    asyncio.run(benchmark())
