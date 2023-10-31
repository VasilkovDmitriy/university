import pytest


async def test_create_user(client, get_user_from_database):
    user_data = {"name": "Vasja", "surname": "Pupkin", "email": "user@example.com"}

    resp = await client.post("/users/", json=user_data)
    data_from_resp = resp.json()

    assert 200 == resp.status_code

    assert data_from_resp["name"] == user_data["name"]
    assert data_from_resp["surname"] == user_data["surname"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True

    users_from_db = await get_user_from_database(data_from_resp["user_id"])

    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])

    assert user_from_db["name"] == user_data["name"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is True
    assert str(user_from_db["user_id"]) == data_from_resp["user_id"]


async def test_create_user_duplicate_email_error(client):
    user_data = {"name": "Vasja", "surname": "Pupkin", "email": "user@example.com"}

    resp = await client.post("/users/", json=user_data)
    assert 200 == resp.status_code

    another_user_data_with_duplicate_email = {
        "name": "Petr",
        "surname": "Petrov",
        "email": "user@example.com",
    }
    resp = await client.post("/users/", json=another_user_data_with_duplicate_email)

    assert 409 == resp.status_code
    assert "A user with this email already exists" == resp.json()["detail"]


@pytest.mark.parametrize(
    "user_data_for_creation, expected_status_code, expected_detail",
    [
        (
            {},
            422,
            [
                {
                    "loc": ["body", "name"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
                {
                    "loc": ["body", "surname"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
                {
                    "loc": ["body", "email"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
            ],
        ),
        (
            {"name": 123, "surname": 456, "email": "lol"},
            422,
            "Name should contains only letters",
        ),
        (
            {"name": "Vasja", "surname": 456, "email": "lol"},
            422,
            "Surname should contains only letters",
        ),
        (
            {"name": "Vasja", "surname": "Pupkin", "email": "lol"},
            422,
            [
                {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address",
                    "type": "value_error.email",
                }
            ],
        ),
    ],
)
async def test_create_user_validation_error(
    client, user_data_for_creation, expected_status_code, expected_detail
):
    resp = await client.post("/users/", json=user_data_for_creation)
    data_from_resp = resp.json()

    assert expected_status_code == resp.status_code
    assert expected_detail == data_from_resp["detail"]
