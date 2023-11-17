from uuid import uuid4

import pytest


async def test_update_user(client, create_user_in_database, get_user_from_database):
    user_data = {
        "id": uuid4(),
        "name": "Vasja",
        "surname": "Pupkin",
        "email": "user@example.com",
        "is_active": True,
    }
    user_data_updated = {
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "cheburek@kek.com",
    }
    await create_user_in_database(**user_data)

    resp = await client.patch(f"/users/{user_data['id']}", json=user_data_updated)

    assert resp.status_code == 200

    resp_data = resp.json()

    assert resp_data["updated_user_id"] == str(user_data["id"])

    users_from_db = await get_user_from_database(user_data["id"])
    user_from_db = dict(users_from_db[0])

    assert user_from_db["name"] == user_data_updated["name"]
    assert user_from_db["surname"] == user_data_updated["surname"]
    assert user_from_db["email"] == user_data_updated["email"]
    assert user_from_db["is_active"] is user_data["is_active"]
    assert user_from_db["id"] == user_data["id"]


async def test_update_user_check_one_is_updated(
    client, create_user_in_database, get_user_from_database
):
    not_updated_user = {
        "id": uuid4(),
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "ivan@kek.com",
        "is_active": True,
    }
    updated_user = {
        "id": uuid4(),
        "name": "Vasja",
        "surname": "Pupkin",
        "email": "user@example.com",
        "is_active": True,
    }
    data_for_update = {
        "name": "Nikifor",
        "surname": "Nikiforov",
        "email": "cheburek@kek.com",
    }
    await create_user_in_database(**not_updated_user)
    await create_user_in_database(**updated_user)

    resp = await client.patch(f"/users/{updated_user['id']}", json=data_for_update)

    assert resp.status_code == 200

    resp_data = resp.json()
    assert resp_data["updated_user_id"] == str(updated_user["id"])

    users_from_db = await get_user_from_database(updated_user["id"])
    user_from_db = dict(users_from_db[0])

    assert user_from_db["id"] == updated_user["id"]
    assert user_from_db["is_active"] == updated_user["is_active"]

    assert user_from_db["name"] == data_for_update["name"]
    assert user_from_db["surname"] == data_for_update["surname"]
    assert user_from_db["email"] == data_for_update["email"]

    # check other user that data has not been changed
    users_from_db = await get_user_from_database(not_updated_user["id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == not_updated_user["name"]
    assert user_from_db["surname"] == not_updated_user["surname"]
    assert user_from_db["email"] == not_updated_user["email"]
    assert user_from_db["is_active"] == not_updated_user["is_active"]
    assert user_from_db["id"] == not_updated_user["id"]


@pytest.mark.parametrize(
    "user_data_updated, expected_status_code, expected_detail",
    [
        (
            {},
            422,
            "At least one parameter for user update info should be provided",
        ),
        ({"name": "123"}, 422, "Name should contains only letters"),
        (
            {"email": ""},
            422,
            [
                {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address",
                    "type": "value_error.email",
                }
            ],
        ),
        (
            {"surname": ""},
            422,
            [
                {
                    "loc": ["body", "surname"],
                    "msg": "ensure this value has at least 1 characters",
                    "type": "value_error.any_str.min_length",
                    "ctx": {"limit_value": 1},
                }
            ],
        ),
        (
            {"name": ""},
            422,
            [
                {
                    "loc": ["body", "name"],
                    "msg": "ensure this value has at least 1 characters",
                    "type": "value_error.any_str.min_length",
                    "ctx": {"limit_value": 1},
                }
            ],
        ),
        ({"surname": "123"}, 422, "Surname should contains only letters"),
        (
            {"email": "123"},
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
async def test_update_user_validation_error(
    client,
    create_user_in_database,
    user_data_updated,
    expected_status_code,
    expected_detail,
):
    user_data = {
        "id": uuid4(),
        "name": "Vasja",
        "surname": "Pupkin",
        "email": "user@example.com",
        "is_active": True,
    }
    await create_user_in_database(**user_data)
    resp = await client.patch(f"/users/{user_data['id']}", json=user_data_updated)

    assert resp.status_code == expected_status_code
    assert resp.json()["detail"] == expected_detail


async def test_update_user_id_validation_error(client):
    user_data_updated = {
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "cheburek@kek.com",
    }
    resp = await client.patch("/users/123", json=user_data_updated)

    assert resp.status_code == 422
    assert resp.json()["detail"] == [
        {
            "loc": ["path", "user_id"],
            "msg": "value is not a valid uuid",
            "type": "type_error.uuid",
        }
    ]


async def test_update_user_not_found_error(client):
    user_data_updated = {
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "cheburek@kek.com",
    }
    user_id = uuid4()
    resp = await client.patch(f"/users/{user_id}", json=user_data_updated)

    assert resp.status_code == 404
    assert resp.json()["detail"] == f"User with id {user_id} not found."


async def test_update_user_duplicate_email_error(client, create_user_in_database):
    user_data_1 = {
        "id": uuid4(),
        "name": "Vasja",
        "surname": "Pupkin",
        "email": "user@example.com",
        "is_active": True,
    }
    user_data_2 = {
        "id": uuid4(),
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "ivan@kek.com",
        "is_active": True,
    }
    user_data_updated = {
        "email": user_data_2["email"],
    }

    await create_user_in_database(**user_data_1)
    await create_user_in_database(**user_data_2)

    resp = await client.patch(f"/users/{user_data_1['id']}", json=user_data_updated)

    assert resp.status_code == 409
    assert resp.json()["detail"] == "A user with this email already exists"
