from uuid import uuid4


async def test_get_user(client, get_user_from_database, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Vasja",
        "surname": "Pupkin",
        "email": "user@example.com",
        "is_active": True,
    }
    await create_user_in_database(**user_data)

    resp = await client.get(f"/users/{user_data['user_id']}")

    assert 200 == resp.status_code

    users_from_db = await get_user_from_database(user_data["user_id"])
    user_from_db = dict(users_from_db[0])

    assert user_data["user_id"] == user_from_db["user_id"]
    assert user_data["name"] == user_from_db["name"]
    assert user_data["surname"] == user_from_db["surname"]
    assert user_data["email"] == user_from_db["email"]
    assert user_data["is_active"] == user_from_db["is_active"]


async def test_get_user_id_validation_error(client):
    invalid_user_id = 123

    resp = await client.get(f"/users/{invalid_user_id}")
    expected_detail = [{'loc': ['path', 'user_id'], 'msg': 'value is not a valid uuid', 'type': 'type_error.uuid'}]

    assert 422 == resp.status_code
    assert expected_detail == resp.json()["detail"]


async def test_get_user_not_found(client):
    user_id = uuid4()

    resp = await client.get(f"/users/{user_id}")

    assert 404 == resp.status_code
    assert f'User with id {user_id} not found.' == resp.json()["detail"]
