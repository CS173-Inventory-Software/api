from app.baserow_client.software import Software
from baserowapi import Filter
from ..baserow_client.user import User, UserType, UserTypeEnum
import pytest
import json
from . import login

def create_user(email:str = 'test@mail.com', user_type:int=UserTypeEnum.VIEWER.value):
    return User.create(email, user_type)

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_read_when_not_logged_in(async_client):
    response = await async_client.get('/users/')
    assert response.status_code == 403

@pytest.mark.parametrize('email', ['viewer@mail.com', 'clerk@mail.com', 'admin@mail.com', 'super@mail.com', 'root@mail.com'])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_read_when_logged_in(async_client, email):
    token = await login(async_client, email)
    response = await async_client.get(f'/users/?search={json.dumps({})}', headers={'Authorization': f'Token {token}'})
    assert response.status_code == 200

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_post_when_not_logged_in(async_client):
    response = await async_client.post(f'/users/', {'email': 'test@mail.com', 'type': UserTypeEnum.VIEWER.value})
    assert response.status_code == 403

@pytest.mark.parametrize('email', ['viewer@mail.com', 'clerk@mail.com', 'admin@mail.com',])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_post_when_not_authorised(async_client, email):
    token = await login(async_client, email)
    response = await async_client.post(f'/users/', {'email': 'test@mail.com', 'type': UserTypeEnum.VIEWER.value}, headers={'Authorization': f'Token {token}'})
    assert response.status_code == 401

@pytest.mark.parametrize('email', ['super@mail.com', 'root@mail.com',])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_post_when_authorised(async_client, email):
    token = await login(async_client, email)
    response = await async_client.post(f'/users/', {'email': 'test@mail.com', 'type': UserTypeEnum.VIEWER.value}, headers={'Authorization': f'Token {token}'}, content_type='application/json')
    assert response.status_code == 201

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_detail_read_when_not_logged_in(async_client):
    response = await async_client.get(f'/users/1/')
    assert response.status_code == 403

@pytest.mark.parametrize('email', ['viewer@mail.com', 'clerk@mail.com', 'admin@mail.com', 'super@mail.com', 'root@mail.com'])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_detail_read_when_logged_in(async_client, email):
    user = create_user()
    token = await login(async_client, email)
    response = await async_client.get(f'/users/{user.id}/', headers={'Authorization': f'Token {token}'})
    assert response.status_code == 200
    assert response.json()['data'] == {
        'id': user.id,
        'email': 'test@mail.com',
        'type': UserTypeEnum.VIEWER.value,
        'type_formula': 'Viewer',
        'type_lookup': [{'id': UserTypeEnum.VIEWER.value, 'value': 'Viewer'}]
    }

@pytest.mark.parametrize('email', ['viewer@mail.com', 'clerk@mail.com', 'admin@mail.com',])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_put_when_not_authorised(async_client, email):
    token = await login(async_client, email)
    response = await async_client.put(f'/users/1/', headers={'Authorization': f'Token {token}'})
    assert response.status_code == 401

@pytest.mark.parametrize('email', ['super@mail.com', 'root@mail.com',])
@pytest.mark.parametrize('user_type', [UserTypeEnum.VIEWER.value, UserTypeEnum.CLERK.value, UserTypeEnum.ADMIN.value, UserTypeEnum.SUPER_ADMIN.value])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_put_when_authorised(async_client, email, user_type):
    user = create_user()
    token = await login(async_client, email)
    response = await async_client.put(
        f'/users/{user.id}/', 
        {
            'email': 'test2@mail.com', 
            'type': user_type
        },
        headers={'Authorization': f'Token {token}'}, 
        content_type='application/json'
    )
    assert response.status_code == 200

    response = await async_client.get(f'/users/{user.id}/', headers={'Authorization': f'Token {token}'})
    data = response.json()['data']

    assert data['email'] == 'test2@mail.com'
    assert data['type'] == user_type

@pytest.mark.parametrize('email', ['super@mail.com', 'root@mail.com',])
@pytest.mark.parametrize('user_type', [0, 1, 6])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_put_when_authorised_wrong_type(async_client, email, user_type):
    user = create_user()
    token = await login(async_client, email)
    response = await async_client.put(
        f'/users/{user.id}/', 
        {
            'email': 'test2@mail.com', 
            'type': user_type
        },
        headers={'Authorization': f'Token {token}'}, 
        content_type='application/json'
    )
    assert response.status_code == 422
    assert response.json()['message'] == 'Invalid user type'

@pytest.mark.parametrize('email', ['viewer@mail.com', 'clerk@mail.com', 'admin@mail.com',])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_delete_when_not_authorised(async_client, email):
    token = await login(async_client, email)
    response = await async_client.delete(f'/users/1/', headers={'Authorization': f'Token {token}'})
    assert response.status_code == 401

@pytest.mark.parametrize('email', ['super@mail.com', 'root@mail.com',])
@pytest.mark.parametrize('user_type', [UserTypeEnum.VIEWER.value, UserTypeEnum.CLERK.value, UserTypeEnum.ADMIN.value])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_delete_when_authorised(async_client, email, user_type):
    user = create_user(user_type=user_type)
    token = await login(async_client, email)
    response = await async_client.delete(
        f'/users/{user.id}/', 
        headers={'Authorization': f'Token {token}'}, 
    )
    assert response.status_code == 204

    response = await async_client.get(f'/users/{user.id}/', headers={'Authorization': f'Token {token}'})

    assert response.status_code == 404

@pytest.mark.parametrize('user_type', [UserTypeEnum.SUPER_ADMIN.value, UserTypeEnum.ROOT_ADMIN.value])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_delete_super_admin_can_not_delete_equal_or_higher(async_client, user_type):
    user = create_user(user_type=user_type)
    token = await login(async_client, 'super@mail.com')
    response = await async_client.delete(
        f'/users/{user.id}/', 
        headers={'Authorization': f'Token {token}'}, 
    )
    assert response.status_code == 401

    response = await async_client.get(f'/users/{user.id}/', headers={'Authorization': f'Token {token}'})

    assert response.status_code == 200

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_delete_root_admin_can_delete_super_admin(async_client):
    user = create_user(user_type=UserTypeEnum.SUPER_ADMIN.value)
    token = await login(async_client, 'root@mail.com')
    response = await async_client.delete(
        f'/users/{user.id}/', 
        headers={'Authorization': f'Token {token}'}, 
    )
    assert response.status_code == 204

    response = await async_client.get(f'/users/{user.id}/', headers={'Authorization': f'Token {token}'})

    assert response.status_code == 404

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_types_read_when_not_logged_in(async_client):
    response = await async_client.get('/user-types/')
    assert response.status_code == 403

@pytest.mark.parametrize('email', ['viewer@mail.com', 'clerk@mail.com', 'admin@mail.com', 'super@mail.com', 'root@mail.com'])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_user_types_read_when_logged_in(async_client, email):
    token = await login(async_client, email)
    response = await async_client.get(f'/user-types/', headers={'Authorization': f'Token {token}'})
    assert response.status_code == 200
