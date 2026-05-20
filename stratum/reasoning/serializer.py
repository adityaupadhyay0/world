import json
from typing import Dict, Any, List

class StateSerializer:
    @staticmethod
    def serialize_to_json(snapshot: Dict[str, Any]) -> str:
        """
        Converts a world state snapshot to a pretty-printed JSON string for LLM consumption.
        """
        return json.dumps(snapshot, indent=2)

    @staticmethod
    def serialize_to_narrative(snapshot: Dict[str, Any]) -> str:
        """
        Converts a world state snapshot to a natural language description.
        Useful for models that perform better with narrative context.
        """
        lines = ["# Current World State"]

        entities = snapshot.get("entities", [])
        relations = snapshot.get("relations", [])

        lines.append("\n## Entities")
        for ent in entities:
            etype = ent.get("type", "Unknown")
            eid = ent.get("id")
            name = ent.get("name", eid)
            props = {k: v for k, v in ent.items() if k not in ["type", "id", "metadata", "last_updated"]}
            lines.append(f"- {etype} [{eid}]: {name}")
            for k, v in props.items():
                lines.append(f"  - {k}: {v}")

        lines.append("\n## Relationships")
        for rel in relations:
            source = rel.get("source_id")
            target = rel.get("target_id")
            rtype = rel.get("relation_type")
            props = rel.get("properties", {})
            prop_str = f" ({props})" if props else ""
            lines.append(f"- {source} --[{rtype}]--> {target}{prop_str}")

        return "\n".join(lines)
