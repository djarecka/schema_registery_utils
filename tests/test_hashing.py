import hashlib
import itertools
import json

import pytest

from schema_registry_utils.hashing import assign_hash_id, compute_hash_id
from schema_registry_utils.models import ProvenanceInfo, RegistryClass, RegistryProperty

PROV_A = ProvenanceInfo(created_by="alice", created_at="2026-01-01T00:00:00")
PROV_B = ProvenanceInfo(created_by="bob", created_at="2026-06-01T00:00:00")


def _property(**overrides):
    fields = dict(
        hash_id="placeholder",
        name="age",
        definition="Age of a patient in years",
        provenance=PROV_A,
        value_type="integer",
        units="years",
    )
    fields.update(overrides)
    return RegistryProperty(**fields)


def test_same_content_same_hash():
    assert compute_hash_id(_property()) == compute_hash_id(_property())


def test_hash_id_field_is_ignored():
    a = _property(hash_id="sha256:aaa")
    b = _property(hash_id="sha256:bbb")
    assert compute_hash_id(a) == compute_hash_id(b)


def test_provenance_is_ignored():
    a = _property(provenance=PROV_A)
    b = _property(provenance=PROV_B)
    assert compute_hash_id(a) == compute_hash_id(b)


def test_skos_mappings_is_ignored():
    a = _property()
    b = _property(skos_mappings=[])
    assert compute_hash_id(a) == compute_hash_id(b)


def test_content_change_changes_hash():
    a = _property(units="years")
    b = _property(units="months")
    assert compute_hash_id(a) != compute_hash_id(b)


@pytest.mark.parametrize(
    "field,other_value",
    [
        ("name", "weight"),
        ("definition", "Weight of a patient in kg"),
        ("value_type", "float"),
        ("units", "months"),
    ],
)
def test_property_every_hashed_field_changes_hash(field, other_value):
    a = _property()
    b = _property(**{field: other_value})
    assert compute_hash_id(a) != compute_hash_id(b), f"changing {field!r} did not change the hash"


def test_class_property_reference_order_is_insensitive():
    a = RegistryClass(
        hash_id="placeholder",
        name="Patient",
        definition="A person receiving care",
        provenance=PROV_A,
        properties=["screg:age", "screg:name"],
    )
    b = RegistryClass(
        hash_id="placeholder",
        name="Patient",
        definition="A person receiving care",
        provenance=PROV_A,
        properties=["screg:name", "screg:age"],
    )
    assert compute_hash_id(a) == compute_hash_id(b)


def _class(**overrides):
    fields = dict(
        hash_id="placeholder",
        name="Patient",
        definition="A person receiving care",
        provenance=PROV_A,
    )
    fields.update(overrides)
    return RegistryClass(**fields)


def test_class_properties_order_insensitive_across_all_permutations():
    property_hashes = ["screg:zzz", "screg:aaa", "screg:mmm"]
    hashes = {
        compute_hash_id(_class(properties=list(perm)))
        for perm in itertools.permutations(property_hashes)
    }
    assert len(hashes) == 1


def test_class_hash_uses_alphabetically_sorted_property_hashes():
    property_hashes = ["screg:zzz", "screg:aaa", "screg:mmm"]
    entity = _class(properties=property_hashes)

    expected_content = {
        "name": "Patient",
        "definition": "A person receiving care",
        "properties": sorted(property_hashes),
        "relations": None,
        "parent_class": None,
        "mixins": None,
    }
    expected_canonical = json.dumps(expected_content, sort_keys=True, separators=(",", ":"))
    expected_hash = f"sha256:{hashlib.sha256(expected_canonical.encode('utf-8')).hexdigest()}"

    assert compute_hash_id(entity) == expected_hash


def test_class_property_set_change_changes_hash():
    a = RegistryClass(
        hash_id="placeholder",
        name="Patient",
        definition="A person receiving care",
        provenance=PROV_A,
        properties=["screg:age"],
    )
    b = RegistryClass(
        hash_id="placeholder",
        name="Patient",
        definition="A person receiving care",
        provenance=PROV_A,
        properties=["screg:age", "screg:name"],
    )
    assert compute_hash_id(a) != compute_hash_id(b)


@pytest.mark.parametrize(
    "field,other_value",
    [
        ("name", "Provider"),
        ("definition", "A person providing care"),
        ("properties", ["screg:age"]),
        ("relations", ["screg:rel-1"]),
        ("parent_class", "screg:Person"),
        ("mixins", ["screg:Auditable"]),
    ],
)
def test_class_every_hashed_field_changes_hash(field, other_value):
    a = _class()
    b = _class(**{field: other_value})
    assert compute_hash_id(a) != compute_hash_id(b), f"changing {field!r} did not change the hash"


def test_assign_hash_id_sets_hash_id_from_original_content():
    entity = _property()
    expected_hash_id = compute_hash_id(entity)

    assign_hash_id(entity)

    assert entity.hash_id == expected_hash_id


def test_assign_hash_id_appends_first_four_hex_chars_to_name():
    entity = _property(name="age")
    digest = compute_hash_id(entity).split(":", 1)[1]

    assign_hash_id(entity)

    assert entity.name == f"age_{digest[:4]}"


def test_assign_hash_id_mutates_in_place_and_returns_same_object():
    entity = _property()

    result = assign_hash_id(entity)

    assert result is entity


def test_assign_hash_id_works_for_class():
    entity = _class(name="Patient")
    digest = compute_hash_id(entity).split(":", 1)[1]

    assign_hash_id(entity)

    assert entity.name == f"Patient_{digest[:4]}"
    assert entity.hash_id.startswith("sha256:")
