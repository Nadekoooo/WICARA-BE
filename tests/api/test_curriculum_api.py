def test_get_subjects_returns_seeded_subject_catalog(client, seeded_curriculum):
    response = client.get("/api/v1/subjects")

    assert response.status_code == 200
    payload = response.json()
    assert [subject["code"] for subject in payload["items"]] == [
        "math",
        "physics",
        "chemistry",
        "biology",
    ]
    assert payload["items"][0]["name"] == "Mathematics"


def test_get_knowledge_map_returns_mobile_ready_math_graph(client, seeded_curriculum):
    response = client.get("/api/v1/knowledge-map?subject=math")

    assert response.status_code == 200
    payload = response.json()

    assert payload["subject"]["code"] == "math"
    assert payload["graph"] == {
        "title": "Mathematics Prerequisite Map",
        "width": 2260.0,
        "height": 600.0,
        "top_down": True,
    }
    assert payload["groups"][0] == {"label": "Primary Math", "x": 28.0}

    nodes_by_id = {node["id"]: node for node in payload["nodes"]}
    assert nodes_by_id["intuitive_limits"]["status"] == "active"
    assert nodes_by_id["intuitive_limits"]["status_label"] == "IN PROGRESS"
    assert nodes_by_id["derivative_rules"]["status"] == "locked"
    assert nodes_by_id["derivative_rules"]["group"] == "Calculus 1"

    edges = {(edge["from"], edge["to"], edge["edge_type"]) for edge in payload["edges"]}
    assert ("derivative_definition", "derivative_rules", "prerequisite") in edges


def test_get_knowledge_map_unknown_subject_returns_404(client, seeded_curriculum):
    response = client.get("/api/v1/knowledge-map?subject=history")

    assert response.status_code == 404
