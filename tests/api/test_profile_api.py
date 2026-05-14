from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.modules.accounts.dependencies import get_current_account
from app.modules.accounts.models import UserAccount


ACCOUNT_ID = UUID("11111111-1111-4111-8111-111111111111")


def test_profile_onboarding_can_be_saved_and_read(client):
    def override_current_account(
        session: Session = Depends(get_session),
    ) -> UserAccount:
        account = session.get(UserAccount, ACCOUNT_ID)
        if account is None:
            account = UserAccount(
                id=ACCOUNT_ID,
                supabase_user_id="supabase-user-1",
                email="learner@example.com",
                display_name="Learner",
                provider_subject="supabase-user-1",
            )
            session.add(account)
            session.commit()
            session.refresh(account)
        return account

    client.app.dependency_overrides[get_current_account] = override_current_account

    missing_response = client.get("/api/v1/me/profile")
    assert missing_response.status_code == 404

    payload = {
        "full_name": "Budi Santoso",
        "country_name": "Indonesia",
        "grade_level": "Kelas 8",
        "preferred_language": "id",
        "study_goal": "Belajar aljabar dasar",
        "daily_study_time_label": "30 menit",
        "selected_subjects": ["Matematika", "IPA"],
    }

    save_response = client.put("/api/v1/me/profile/onboarding", json=payload)
    assert save_response.status_code == 200
    saved = save_response.json()
    assert saved["user_id"] == str(ACCOUNT_ID)
    assert saved["full_name"] == "Budi Santoso"
    assert saved["country_name"] == "Indonesia"
    assert saved["grade_level"] == "Kelas 8"
    assert saved["preferred_language"] == "id"
    assert saved["study_goal"] == "Belajar aljabar dasar"
    assert saved["daily_study_time_label"] == "30 menit"
    assert saved["selected_subjects"] == ["matematika", "ipa"]
    assert saved["onboarding_completed"] is True

    read_response = client.get("/api/v1/me/profile")
    assert read_response.status_code == 200
    assert read_response.json() == saved
