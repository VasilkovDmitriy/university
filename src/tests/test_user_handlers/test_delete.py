from uuid import uuid4


async def test_delete_user(client, get_user_from_database, create_user_in_database):
    user_data = {
        "id": uuid4(),
        "name": "Vasja",
        "surname": "Pupkin",
        "email": "user@example.com",
        "is_active": True,
    }
    await create_user_in_database(**user_data)

    resp = await client.delete(f"/users/{user_data['id']}")

    assert 200 == resp.status_code
    assert {"deleted_user_id": str(user_data["id"])} == resp.json()

    users_from_db = await get_user_from_database(user_data["id"])
    user_from_db = dict(users_from_db[0])

    assert user_data["id"] == user_from_db["id"]
    assert user_data["name"] == user_from_db["name"]
    assert user_data["surname"] == user_from_db["surname"]
    assert user_data["email"] == user_from_db["email"]
    assert user_from_db["is_active"] is False


async def test_delete_user_not_found(client):
    user_id = uuid4()
    resp = await client.delete(f"/users/{user_id}")

    assert 404 == resp.status_code
    assert f"User with id {user_id} not found." == resp.json()["detail"]


async def test_delete_user_validation_error(client):
    user_id = 123
    resp = await client.delete(f"/users/{user_id}")

    expected_detail = [
        {
            "loc": ["path", "user_id"],
            "msg": "value is not a valid uuid",
            "type": "type_error.uuid",
        }
    ]

    assert 422 == resp.status_code
    assert expected_detail == resp.json()["detail"]
