from stratum.state.world_state import WorldState

class WorldVisualizer:
    @staticmethod
    def to_mermaid(world_state: WorldState) -> str:
        """
        Generates a Mermaid graph definition for the current world state.
        """
        lines = ["graph TD"]

        # Nodes
        for nid, data in world_state.graph.nodes(data=True):
            etype = data.get('type', 'Entity')
            entity = world_state.get_entity(nid)
            name = entity.name if hasattr(entity, 'name') else nid
            lines.append(f'    {nid}["{name} ({etype})"]')

        # Edges
        for u, v, data in world_state.graph.edges(data=True):
            rtype = data.get('relation_type', 'rel')
            lines.append(f'    {u} -- "{rtype}" --> {v}')

        return "\n".join(lines)

    @staticmethod
    def to_dot(world_state: WorldState) -> str:
        """
        Generates a Graphviz DOT definition.
        """
        lines = ["digraph World {"]
        for nid, data in world_state.graph.nodes(data=True):
            entity = world_state.get_entity(nid)
            name = entity.name if hasattr(entity, 'name') else nid
            lines.append(f'    {nid} [label="{name}\\n({data.get("type")})"];')

        for u, v, data in world_state.graph.edges(data=True):
            lines.append(f'    {u} -> {v} [label="{data.get("relation_type")}"];')

        lines.append("}")
        return "\n".join(lines)
