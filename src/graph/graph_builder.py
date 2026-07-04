import uuid


class GraphBuilder:
    group_attribute: str = "group"

    def build(self, extractions: list) -> tuple[dict[str, str], list[dict]]:
        groups: dict[str, list] = {}
        for ext in extractions:
            if not ext.attributes or self.group_attribute not in ext.attributes:
                continue
            group_name = ext.attributes[self.group_attribute]
            groups.setdefault(group_name, []).append(ext)

        nodes: dict[str, str] = {}
        relationships: list[dict] = []

        for group_name, group_extractions in groups.items():
            anchor_ext = self._pick_anchor(group_extractions)
            anchor_text = anchor_ext.extraction_text if anchor_ext else group_name

            if anchor_text not in nodes:
                nodes[anchor_text] = str(uuid.uuid4())

            for ext in group_extractions:
                if ext is anchor_ext:
                    continue

                target_text = ext.extraction_text
                if target_text not in nodes:
                    nodes[target_text] = str(uuid.uuid4())

                relationships.append(
                    {
                        "source": nodes[anchor_text],
                        "target": nodes[target_text],
                        "type": ext.extraction_class,
                    }
                )

        return nodes, relationships

    def _pick_anchor(self, group_extractions: list):
        """Default anchor: simply the first extraction seen in the group."""
        return group_extractions[0] if group_extractions else None


class LegalGraphBuilder(GraphBuilder):
    group_attribute = "document_group"

    anchor_classes = ("document_type", "reference_number")

    def _pick_anchor(self, group_extractions: list):
        for anchor_class in self.anchor_classes:
            anchor_ext = next(
                (e for e in group_extractions if e.extraction_class == anchor_class),
                None,
            )
            if anchor_ext is not None:
                return anchor_ext
        return None