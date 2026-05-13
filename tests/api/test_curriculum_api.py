def test_get_subjects_returns_seeded_subject_catalog(client, seeded_curriculum):
    response = client.get("/api/v1/subjects")

    assert response.status_code == 200
    payload = response.json()
    assert [subject["code"] for subject in payload["items"]] == [
        "matematika",
        "ipas",
        "ipa",
        "fisika",
        "kimia",
        "biologi",
    ]
    assert payload["items"][0]["name"] == "Matematika"
    assert payload["items"][0]["metadata"]["curriculum"] == "kurikulum_merdeka"


def test_get_knowledge_map_returns_mobile_ready_kurikulum_graph(client, seeded_curriculum):
    response = client.get("/api/v1/knowledge-map?subject=matematika")

    assert response.status_code == 200
    payload = response.json()

    assert payload["subject"]["code"] == "matematika"
    assert payload["graph"]["title"] == "Kurikulum Merdeka Matematika Knowledge Map"
    assert payload["graph"]["top_down"] is True
    assert payload["groups"][0] == {"label": "Fase A / Aljabar", "x": 28.0}

    nodes_by_id = {node["id"]: node for node in payload["nodes"]}
    assert nodes_by_id["km_d_matematika_bilangan_bulat"]["status"] == "active"
    assert nodes_by_id["km_d_matematika_bilangan_bulat"]["status_label"] == "IN PROGRESS"
    assert nodes_by_id["km_d_matematika_bilangan_bulat"]["metadata"]["preview_status_only"] is True
    assert nodes_by_id["km_d_matematika_bilangan_bulat"]["group"] == "Fase D / Bilangan"

    edges = {(edge["from"], edge["to"], edge["edge_type"]) for edge in payload["edges"]}
    assert (
        "km_d_matematika_bilangan_bulat",
        "km_d_matematika_bilangan_rasional",
        "prerequisite",
    ) in edges


def test_get_knowledge_map_supports_math_alias(client, seeded_curriculum):
    response = client.get("/api/v1/knowledge-map?subject=math")

    assert response.status_code == 200
    assert response.json()["subject"]["code"] == "matematika"


def test_get_knowledge_map_returns_science_subject_graph(client, seeded_curriculum):
    response = client.get("/api/v1/knowledge-map?subject=kimia")

    assert response.status_code == 200
    payload = response.json()
    assert payload["subject"]["code"] == "kimia"
    assert payload["nodes"]
    assert payload["groups"]


def test_get_concept_detail_returns_mock_mastery_and_relations(
    client,
    seeded_curriculum,
):
    response = client.get(
        "/api/v1/knowledge-map/concepts/km_d_matematika_bilangan_rasional"
        "?subject=matematika"
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["concept"]["id"] == "km_d_matematika_bilangan_rasional"
    assert payload["subject"]["code"] == "matematika"
    assert payload["metadata"]["mock_mastery"] is True
    assert isinstance(payload["mastery_confidence"], float)

    prerequisite_ids = {item["id"] for item in payload["prerequisites"]}
    related_ids = {item["id"] for item in payload["related_concepts"]}
    assert "km_d_matematika_bilangan_bulat" in prerequisite_ids
    assert "km_d_matematika_bilangan_irasional" in related_ids


def test_get_concept_detail_unknown_concept_returns_404(client, seeded_curriculum):
    response = client.get("/api/v1/knowledge-map/concepts/unknown")

    assert response.status_code == 404


def test_get_knowledge_map_unknown_subject_returns_404(client, seeded_curriculum):
    response = client.get("/api/v1/knowledge-map?subject=history")

    assert response.status_code == 404
