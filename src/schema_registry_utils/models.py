from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.11.0"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'screg',
     'default_range': 'string',
     'description': 'Meta-model for the schema registry: defines the registered '
                    'object types (RegistryClass, RegistryProperty, and related '
                    'support classes) used to describe classes and data elements '
                    'that can be registered, versioned, related to each other, and '
                    'compared for similarity. NOTE: `id` above is a placeholder '
                    'namespace — replace before publishing.',
     'id': 'https://example.org/schema-registry-utils/meta-model',
     'imports': ['linkml:types'],
     'name': 'schema_registry_meta_model',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'prov': {'prefix_prefix': 'prov',
                           'prefix_reference': 'http://www.w3.org/ns/prov#'},
                  'screg': {'prefix_prefix': 'screg',
                            'prefix_reference': 'https://example.org/schema-registry-utils/'},
                  'skos': {'prefix_prefix': 'skos',
                           'prefix_reference': 'http://www.w3.org/2004/02/skos/core#'}},
     'source_file': 'schema/registry_meta_model.yaml'} )

class SkosMappingTypeEnum(str, Enum):
    """
    The kind of SKOS mapping relation between a registry entity and an external concept.
    """
    EXACT_MATCH = "EXACT_MATCH"
    """
    The registry entity is equivalent to the external concept.
    """
    CLOSE_MATCH = "CLOSE_MATCH"
    """
    The registry entity is sufficiently similar to the external concept.
    """
    BROAD_MATCH = "BROAD_MATCH"
    """
    The external concept is broader than the registry entity.
    """
    NARROW_MATCH = "NARROW_MATCH"
    """
    The external concept is narrower than the registry entity.
    """
    RELATED_MATCH = "RELATED_MATCH"
    """
    The registry entity is related to the external concept.
    """



class RegistryEntity(ConfiguredBaseModel):
    """
    Common base for content-addressed, provenance-tracked objects registered in the schema registry. Identity (hash_id) is derived from an entity's content, so there is no separate version slot: a change in content produces a new hash_id, with lineage tracked via provenance.derived_from.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True,
         'from_schema': 'https://example.org/schema-registry-utils/meta-model'})

    hash_id: str = Field(default=..., description="""Content-hash-derived identifier for this entity (format TBD).""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity', 'Relation']} })
    name: str = Field(default=..., description="""Human-readable label for this entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity']} })
    definition: str = Field(default=..., description="""Human-readable definition of this entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity']} })
    provenance: ProvenanceInfo = Field(default=..., description="""Structured provenance for this entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity', 'Relation']} })
    skos_mappings: Optional[list[SkosMapping]] = Field(default=None, description="""Semantic mappings to external vocabulary concepts.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity']} })


class RegistryClass(RegistryEntity):
    """
    A registered class (object class) representing a concept or entity type in the registry, e.g. \"Patient\".
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/schema-registry-utils/meta-model'})

    properties: Optional[list[str]] = Field(default=None, description="""The set of properties that belong to this class.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryClass']} })
    relations: Optional[list[str]] = Field(default=None, description="""Relations from this class to other registry entities.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryClass']} })
    parent_class: Optional[str] = Field(default=None, description="""The class this class inherits from.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryClass']} })
    mixins: Optional[list[str]] = Field(default=None, description="""Additional classes mixed into this class.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryClass']} })
    hash_id: str = Field(default=..., description="""Content-hash-derived identifier for this entity (format TBD).""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity', 'Relation']} })
    name: str = Field(default=..., description="""Human-readable label for this entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity']} })
    definition: str = Field(default=..., description="""Human-readable definition of this entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity']} })
    provenance: ProvenanceInfo = Field(default=..., description="""Structured provenance for this entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity', 'Relation']} })
    skos_mappings: Optional[list[SkosMapping]] = Field(default=None, description="""Semantic mappings to external vocabulary concepts.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity']} })


class RegistryProperty(RegistryEntity):
    """
    A registered property (data element) representing a characteristic or attribute that can be attached to a RegistryClass, e.g. \"age\".
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/schema-registry-utils/meta-model'})

    value_type: str = Field(default=..., description="""The data type or value range for this property (e.g. a primitive type name, or the id of a ValueSet for enumerated values).""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryProperty']} })
    units: Optional[str] = Field(default=None, description="""Unit of measure for this property's values, if applicable.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryProperty']} })
    hash_id: str = Field(default=..., description="""Content-hash-derived identifier for this entity (format TBD).""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity', 'Relation']} })
    name: str = Field(default=..., description="""Human-readable label for this entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity']} })
    definition: str = Field(default=..., description="""Human-readable definition of this entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity']} })
    provenance: ProvenanceInfo = Field(default=..., description="""Structured provenance for this entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity', 'Relation']} })
    skos_mappings: Optional[list[SkosMapping]] = Field(default=None, description="""Semantic mappings to external vocabulary concepts.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity']} })


class ProvenanceInfo(ConfiguredBaseModel):
    """
    Structured provenance metadata for a registry entity or action.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/schema-registry-utils/meta-model'})

    created_by: str = Field(default=..., description="""Who or what created this entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceInfo']} })
    created_at: datetime  = Field(default=..., description="""When this entity was created.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceInfo']} })
    modified_by: Optional[str] = Field(default=None, description="""Who or what last modified this entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceInfo']} })
    modified_at: Optional[datetime ] = Field(default=None, description="""When this entity was last modified.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceInfo']} })
    derived_from: Optional[list[str]] = Field(default=None, description="""Identifiers of the source(s) this entity was derived from.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceInfo']} })
    method: Optional[str] = Field(default=None, description="""Free-text description of how this entity/action was carried out.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProvenanceInfo']} })


class SkosMapping(ConfiguredBaseModel):
    """
    A semantic mapping from a registry entity to an external vocabulary concept (SKOS mapping relation).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/schema-registry-utils/meta-model'})

    mapping_type: Optional[SkosMappingTypeEnum] = Field(default=None, description="""The kind of SKOS mapping relation this represents.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SkosMapping']} })
    target: Optional[str] = Field(default=None, description="""The external concept this mapping points to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SkosMapping']} })


class Relation(ConfiguredBaseModel):
    """
    A directed relationship between two registry entities (classes or properties), so that any object's relations can be retrieved.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/schema-registry-utils/meta-model'})

    hash_id: str = Field(default=..., description="""Content-hash-derived identifier for this entity (format TBD).""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity', 'Relation']} })
    subject: str = Field(default=..., description="""The entity the relation is from.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Relation']} })
    predicate: str = Field(default=..., description="""The type of relationship (e.g. isPartOf, isSimilarTo, isDerivedFrom).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Relation']} })
    object: str = Field(default=..., description="""The entity the relation is to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Relation']} })
    provenance: ProvenanceInfo = Field(default=..., description="""Structured provenance for this entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RegistryEntity', 'Relation']} })


class Rule(ConfiguredBaseModel):
    """
    STUB — a validation or business rule applicable to one or more registry entities (e.g. min/max value, pattern, required, multivalued constraints on a RegistryProperty). Slots intentionally left undefined; scope TBD.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/schema-registry-utils/meta-model'})

    pass


class Transform(ConfiguredBaseModel):
    """
    STUB — a transformation between two RegistryClass definitions. Slots intentionally left undefined; scope TBD.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/schema-registry-utils/meta-model'})

    pass


class ValueSet(ConfiguredBaseModel):
    """
    STUB — a controlled set of permissible values, usable as a RegistryProperty value_type. Slots intentionally left undefined; scope TBD.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/schema-registry-utils/meta-model'})

    pass


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
RegistryEntity.model_rebuild()
RegistryClass.model_rebuild()
RegistryProperty.model_rebuild()
ProvenanceInfo.model_rebuild()
SkosMapping.model_rebuild()
Relation.model_rebuild()
Rule.model_rebuild()
Transform.model_rebuild()
ValueSet.model_rebuild()
