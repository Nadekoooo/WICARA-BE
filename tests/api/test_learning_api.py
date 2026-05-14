from datetime import UTC, datetime
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.modules.accounts.dependencies import get_current_account
from app.modules.accounts.models import UserAccount


ACCOUNT_ID = UUID("22222222-2222-4222-8222-222222222222")


def test_learning_goal_bootstraps_seeded_pretest_and_track(client):
    _override_account(client)

    goal_response = client.post(
        "/api/v1/learning-goals",
        json={"raw_topic": "derivative rules"},
    )

    assert goal_response.status_code == 200
    goal = goal_response.json()
    assert goal["status"] == "pretest_ready"
    assert goal["pretest_session_id"]
    assert goal["track_id"]

    pretest_response = client.get(f"/api/v1/pretests/{goal['learning_goal_id']}")
    assert pretest_response.status_code == 200
    pretest = pretest_response.json()
    assert pretest["session_id"] == goal["pretest_session_id"]
    assert pretest["questions"]

    question = pretest["questions"][0]
    correct_option = next(option for option in question["options"] if option["label"] == "B")
    answer_response = client.post(
        f"/api/v1/pretests/{pretest['session_id']}/answers",
        json={
            "question_id": question["id"],
            "option_id": correct_option["id"],
            "confidence": 7,
        },
    )
    assert answer_response.status_code == 200
    assert answer_response.json()["is_correct"] is True

    reasoning_response = client.post(
        f"/api/v1/pretests/{pretest['session_id']}/reasoning",
        json={
            "question_id": question["id"],
            "option_id": correct_option["id"],
            "confidence": 7,
            "explanation": "Limits are the prerequisite signal.",
            "used_canvas": False,
        },
    )
    assert reasoning_response.status_code == 200
    assert reasoning_response.json()["path_title"] == "Personalized path generated"

    tracks_response = client.get("/api/v1/tracks")
    assert tracks_response.status_code == 200
    tracks = tracks_response.json()["items"]
    assert tracks[0]["id"] == goal["track_id"]
    assert len(tracks[0]["modules"]) == 3


def test_daily_evaluation_returns_seeded_review_questions_and_persists_answer(client):
    _override_account(client)

    response = client.get("/api/v1/daily-evaluations/today")

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"]
    assert payload["review_policy"]["strategy"] == "spaced_repetition_mvp"
    assert payload["language"] == "en"
    assert payload["source"] == "seeded_spaced_repetition_mvp"
    assert payload["review_due"]["due_count"] == 3
    assert payload["progress"] == {
        "current": 1,
        "total": 3,
        "completed": 0,
        "label": "1 of 3",
    }
    assert payload["question"]["id"] == payload["questions"][0]["id"]
    assert payload["retention_forecast"]["points"][0] == {
        "label": "Today",
        "retention_percent": 100,
        "projected": False,
    }
    assert payload["recommendation_callout"]["action_label"] == "Review now"
    assert len(payload["questions"]) == 3

    for index, question in enumerate(payload["questions"]):
        correct_label = ("A", "B", "D")[index]
        correct_option = next(option for option in question["options"] if option["label"] == correct_label)
        answer_response = client.post(
            f"/api/v1/daily-evaluations/{payload['session_id']}/answers",
            json={
                "question_id": question["id"],
                "option_id": correct_option["id"],
                "confidence": 6,
            },
        )

        assert answer_response.status_code == 200
        answer_payload = answer_response.json()
        assert answer_payload["is_correct"] is True
        assert answer_payload["next_review_label"] == "Review in 3 days"
        assert answer_payload["completed"] == (index == len(payload["questions"]) - 1)

    result_response = client.get(f"/api/v1/daily-evaluations/{payload['session_id']}/result")
    assert result_response.status_code == 200
    result = result_response.json()
    assert result["score_percent"] == 100
    assert result["reviewed_count"] == 3
    assert result["correct_count"] == 3
    assert result["review_again_count"] == 0
    assert len(result["reviewed_concepts"]) == 3
    assert {item["status_label"] for item in result["reviewed_concepts"]} <= {"Good", "Strong"}
    assert result["spaced_repetition_impact"]["retention_lift_percent"] > 0
    assert result["next_review"]["interval_days"] == 7
    assert result["recommended_next_actions"][0]["action_type"] == "review"
    assert result["back_to_home"] == {
        "label": "Back to Home",
        "action_type": "navigate",
        "target": "/home",
    }


def test_weekly_report_returns_richer_learning_report_payload(client):
    _override_account(client)

    response = client.get("/api/v1/reports/weekly/latest")

    assert response.status_code == 200
    payload = response.json()
    assert payload["range_label"]
    assert payload["range_start"]
    assert payload["range_end"]
    assert payload["source"] in {
        "seeded_mvp",
        "derived_from_mastery_state",
        "derived_from_range_assessments_and_mastery",
        "derived_from_range_assessments_no_baseline",
    }
    assert [item["label"] for item in payload["performance_groups"]] == [
        "Overall",
        "Application",
        "Analysis",
    ]
    assert payload["gap_metrics"]["fixed"]["delta_label"]
    assert payload["gap_metrics"]["remaining"]["delta_label"]
    assert payload["unlocked_this_week"]["count"] >= 1
    assert payload["upcoming_recommendations"][0]["action_type"] == "review"
    assert payload["consistency_summary"]["title"] == "Consistency is compounding."


def test_weekly_report_range_uses_selected_dates_and_attempt_scores(client):
    _override_account(client)

    daily_response = client.get("/api/v1/daily-evaluations/today")
    assert daily_response.status_code == 200
    daily = daily_response.json()
    today = datetime.now(UTC).date()

    for index, question in enumerate(daily["questions"]):
        correct_label = ("A", "B", "D")[index]
        correct_option = next(option for option in question["options"] if option["label"] == correct_label)
        response = client.post(
            f"/api/v1/daily-evaluations/{daily['session_id']}/answers",
            json={
                "question_id": question["id"],
                "option_id": correct_option["id"],
                "confidence": 8,
            },
        )
        assert response.status_code == 200

    report_response = client.get(
        f"/api/v1/reports/weekly?start={today.isoformat()}&end={today.isoformat()}"
    )

    assert report_response.status_code == 200
    payload = report_response.json()
    assert payload["range_start"] == today.isoformat()
    assert payload["range_end"] == today.isoformat()
    assert payload["source"] == "derived_from_range_assessments_no_baseline"
    assert payload["score"] == 100
    assert payload["performance_groups"][0] == {
        "label": "Overall",
        "pre_test_percent": 84,
        "post_test_percent": 100,
    }
    assert payload["upcoming_recommendations"][0]["title"] != "Review: Market Equilibrium"


def test_weekly_report_range_rejects_invalid_dates(client):
    _override_account(client)

    response = client.get("/api/v1/reports/weekly?start=2026-05-17&end=2026-05-11")

    assert response.status_code == 422
    assert "start date" in response.json()["detail"]


def test_daily_result_recommends_missed_concept_review(client):
    _override_account(client)

    daily_response = client.get("/api/v1/daily-evaluations/today")
    assert daily_response.status_code == 200
    daily = daily_response.json()

    for index, question in enumerate(daily["questions"]):
        correct_label = ("A", "B", "D")[index]
        selected_option = next(
            option
            for option in question["options"]
            if option["label"] != correct_label
        ) if index == 0 else next(
            option for option in question["options"] if option["label"] == correct_label
        )
        answer_response = client.post(
            f"/api/v1/daily-evaluations/{daily['session_id']}/answers",
            json={
                "question_id": question["id"],
                "option_id": selected_option["id"],
                "confidence": 5,
            },
        )
        assert answer_response.status_code == 200

    result_response = client.get(f"/api/v1/daily-evaluations/{daily['session_id']}/result")

    assert result_response.status_code == 200
    result = result_response.json()
    assert result["review_again_count"] == 1
    assert result["recommended_next_actions"][0]["action_type"] == "review"
    assert result["recommended_next_actions"][0]["title"].startswith("Review:")
    assert result["recommended_next_actions"][0]["reason"] == (
        "You missed this concept in today's evaluation."
    )


def test_media_artifacts_contains_demo_supabase_videos(client):
    _override_account(client)

    response = client.get("/api/v1/media-artifacts")

    assert response.status_code == 200
    payload = response.json()
    playback_urls = {item["playback_url"] for item in payload["items"]}
    assert (
        "https://gwbqhirtkgkghnpahtgt.supabase.co/storage/v1/object/public/video/perkalian.mp4"
        in playback_urls
    )
    assert (
        "https://gwbqhirtkgkghnpahtgt.supabase.co/storage/v1/object/public/video/aljabar.mp4"
        in playback_urls
    )


def _override_account(client) -> None:
    def override_current_account(
        session: Session = Depends(get_session),
    ) -> UserAccount:
        account = session.get(UserAccount, ACCOUNT_ID)
        if account is None:
            account = UserAccount(
                id=ACCOUNT_ID,
                supabase_user_id="supabase-user-learning",
                email="learner-learning@example.com",
                display_name="Learning User",
                provider_subject="supabase-user-learning",
            )
            session.add(account)
            session.commit()
            session.refresh(account)
        return account

    client.app.dependency_overrides[get_current_account] = override_current_account
