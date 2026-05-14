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
    assert len(payload["questions"]) == 3

    question = payload["questions"][0]
    correct_option = next(option for option in question["options"] if option["label"] == "A")
    answer_response = client.post(
        f"/api/v1/daily-evaluations/{payload['session_id']}/answers",
        json={
            "question_id": question["id"],
            "option_id": correct_option["id"],
            "confidence": 6,
        },
    )

    assert answer_response.status_code == 200
    assert answer_response.json()["is_correct"] is True
    assert answer_response.json()["next_review_label"] == "Review in 3 days"


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
