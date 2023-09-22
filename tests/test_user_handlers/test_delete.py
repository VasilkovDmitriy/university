from uuid import uuid4


async def test_delete_user(client, get_user_from_database, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Vasja",
        "surname": "Pupkin",
        "email": "user@example.com",
        "is_active": True,
    }
    await create_user_in_database(**user_data)

    resp = await client.delete(f"/users/{user_data['user_id']}")
    
    assert 200 == resp.status_code
    assert {"deleted_user_id": str(user_data["user_id"])} == resp.json()

    users_from_db = await get_user_from_database(user_data["user_id"])
    user_from_db = dict(users_from_db[0])

    assert user_data["user_id"] == user_from_db["user_id"]
    assert user_data["name"] == user_from_db["name"]
    assert user_data["surname"] == user_from_db["surname"]
    assert user_data["email"] == user_from_db["email"]
    assert user_from_db["is_active"] is False
