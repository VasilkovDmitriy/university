from uuid import uuid4


async def test_update_user(
    client, create_user_in_database, get_user_from_database
):
    user_data = {
        "user_id": uuid4(),
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

    resp = await client.patch(f"/users/{user_data['user_id']}", json=user_data_updated)

    assert resp.status_code == 200

    resp_data = resp.json()

    assert resp_data["updated_user_id"] == str(user_data["user_id"])

    users_from_db = await get_user_from_database(user_data["user_id"])
    user_from_db = dict(users_from_db[0])

    assert user_from_db["name"] == user_data_updated["name"]
    assert user_from_db["surname"] == user_data_updated["surname"]
    assert user_from_db["email"] == user_data_updated["email"]
    assert user_from_db["is_active"] is user_data["is_active"]
    assert user_from_db["user_id"] == user_data["user_id"]
