from app.baserow_client.user import User
from baserowapi import Filter
import datetime
import pytest
from . import login

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_request_code_without_email(async_client):
    response = await async_client.post("/request-code/", {
        'email': '',
    })
    assert response.status_code == 422
    data = response.json()
    assert data['errors'] == {'email': ['This field may not be blank.']}

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_login(async_client):
    user = User.table.get_rows(
        filters=[Filter("email", 'root@mail.com')], 
        return_single=True
    )
    five_minutes_from_now = datetime.datetime.now() + datetime.timedelta(minutes=5)
    user.update({"auth_code": '9999', "auth_expiry": five_minutes_from_now})

    response = await async_client.post("/login/", {
        'email': 'root@mail.com',
        'code': '9999'
    })
    assert response.status_code == 200

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_login_wrong_code(async_client):
    user = User.table.get_rows(
        filters=[Filter("email", "root@mail.com")], 
        return_single=True
    )
    five_minutes_from_now = datetime.datetime.now() + datetime.timedelta(minutes=5)
    user.update({"auth_code": '9999', "auth_expiry": five_minutes_from_now})

    response = await async_client.post("/login/", {
        'email': 'root@mail.com',
        'code': '8888'
    })
    assert response.status_code == 400

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_login_late(async_client):
    user = User.table.get_rows(
        filters=[Filter("email", "root@mail.com")], 
        return_single=True
    )
    five_minutes_earlier = datetime.datetime.now() - datetime.timedelta(minutes=5)
    user.update({"auth_code": '9999', "auth_expiry": five_minutes_earlier})

    response = await async_client.post("/login/", {
        'email': 'root@mail.com',
        'code': '9999'
    })
    assert response.status_code == 400

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_logout(async_client):
    token = await login(async_client)

    response = await async_client.post("/logout/", headers={'Authorization': f'Token {token}'})
    assert response.status_code == 204

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_get_user(async_client):
    token = await login(async_client)

    response = await async_client.get("/get-user/", headers={'Authorization': f'Token {token}'})

    assert response.json() == {'email': 'root@mail.com', 'role': 1}

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_get_user_not_logged_in(async_client):
    response = await async_client.get("/get-user/")
    
    assert response.status_code == 403