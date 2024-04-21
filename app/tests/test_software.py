from app.baserow_client.software import Software
from baserowapi import Filter
import pytest
import json
from . import login

def create_software():
    return Software.create(
        'Test Software',
        'Test Brand',
        '1.0.0',
        'Test Description',
        '2022-01-01',
        [
            {
                'serial_key': '123456',
            }
        ],
        [
            {
                'start': '2021-01-01',
                'end': '2022-01-01',
                'number_of_licenses': 3,
            }
        ]
    )

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_read_when_not_logged_in(async_client):
    response = await async_client.get('/software/1/')
    assert response.status_code == 403

@pytest.mark.parametrize('email', ['viewer@mail.com', 'clerk@mail.com', 'admin@mail.com', 'super@mail.com', 'root@mail.com'])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_read_when_logged_in(async_client, email):
    token = await login(async_client, email)
    software = create_software()
    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    assert response.status_code == 200
    data = response.json()['data']
    del data['one2m']
    assert data == {
        'id': software.id,
        'name': 'Test Software',
        'brand': 'Test Brand',
        'version_number': '1.0.0',
        'description': 'Test Description',
        'expiration_date': '2022-01-01',
        'for_deletion': False,
    }

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_post_when_not_logged_in(async_client):
    response = await async_client.post('/software/')
    assert response.status_code == 403

@pytest.mark.parametrize('email', ['viewer@mail.com', 'clerk@mail.com',])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_post_when_non_admin(async_client, email):
    token = await login(async_client, email)
    response = await async_client.post('/software/', headers={'Authorization': f'Token {token}'})
    assert response.status_code == 401

@pytest.mark.parametrize('email', ['admin@mail.com', 'super@mail.com', 'root@mail.com'])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_post_when_admin(async_client, email):
    token = await login(async_client, email)
    response = await async_client.post('/software/', {
        'name': 'Test Hardware',
        'brand': 'Test Brand',
        'version_number': '1.0.0',
        'description': 'Test Description',
        'one2m': {
            'instances': {
                'data': [],
            },
            'subscriptions': {
                'data': [],
            }
        }
    }, headers={'Authorization': f'Token {token}'}, content_type='application/json')
    assert response.status_code == 201

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_when_viewer(async_client):
    token = await login(async_client, 'viewer@mail.com')
    response = await async_client.put('/software/1/', headers={'Authorization': f'Token {token}'})
    assert response.status_code == 401

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_inventory_clerk_can_edit_assignees(async_client):
    token = await login(async_client, 'clerk@mail.com')
    software = create_software()

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    data['name'] = 'Ignored Software'
    data['brand'] = 'Ignored Brand'
    data['version_number'] = '2.0.0'
    data['description'] = 'Ignored Description'
    data['expiration_date'] = '2000-01-01'
    data['one2m']['instances']['data'][0]['assignee'] = 1
    data['one2m']['instances']['delete'] = []
    data['one2m']['subscriptions']['delete'] = []

    await async_client.put(f'/software/{software.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    one2m = data['one2m']
    del data['one2m']
    assert data == {
        'id': software.id,
        'name': 'Test Software',
        'brand': 'Test Brand',
        'version_number': '1.0.0',
        'description': 'Test Description',
        'expiration_date': '2022-01-01',
        'for_deletion': False,
    }

    assert one2m['instances']['data'][0]['assignee'] == 1

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_inventory_clerk_can_not_add_instances(async_client):
    token = await login(async_client, 'clerk@mail.com')
    software = create_software()

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']

    data['one2m']['instances']['data'].append({
        'serial_key': '654321',
    })

    data['one2m']['instances']['delete'] = []
    data['one2m']['subscriptions']['delete'] = []

    await async_client.put(f'/software/{software.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    
    assert len(data['one2m']['instances']['data']) == 1

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_inventory_clerk_can_not_add_subscriptions(async_client):
    token = await login(async_client, 'clerk@mail.com')
    software = create_software()

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']

    data['one2m']['subscriptions']['data'].append({
        'start': '2023-01-01',
        'end': '2024-01-01',
        'number_of_licenses': 50,
    })

    data['one2m']['instances']['delete'] = []
    data['one2m']['subscriptions']['delete'] = []

    await async_client.put(f'/software/{software.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    
    assert len(data['one2m']['subscriptions']['data']) == 1

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_inventory_clerk_can_not_delete_instances(async_client):
    token = await login(async_client, 'clerk@mail.com')
    software = create_software()

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']

    data['one2m']['instances']['delete'] = [
        data['one2m']['instances']['data'][0]['id']
    ]

    data['one2m']['subscriptions']['delete'] = []

    await async_client.put(f'/software/{software.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']

    assert len(data['one2m']['instances']['data']) == 1

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_inventory_clerk_can_not_delete_subscriptions(async_client):
    token = await login(async_client, 'clerk@mail.com')
    software = create_software()

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']

    data['one2m']['subscriptions']['delete'] = [
        data['one2m']['subscriptions']['data'][0]['id']
    ]

    data['one2m']['instances']['delete'] = []

    await async_client.put(f'/software/{software.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']

    assert len(data['one2m']['subscriptions']['data']) == 1

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_inventory_clerk_can_not_edit_instances(async_client):
    token = await login(async_client, 'clerk@mail.com')
    software = create_software()

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    data['name'] = 'Ignored Software'
    data['brand'] = 'Ignored Brand'
    data['version_number'] = '2.0.0'
    data['description'] = 'Ignored Description'
    data['expiration_date'] = '2000-01-01'

    data['one2m']['instances']['data'][0]['status'] = 2
    data['one2m']['instances']['data'][0]['serial_key'] = 'Ignored Serial Number'

    data['one2m']['instances']['delete'] = []
    data['one2m']['subscriptions']['delete'] = []

    await async_client.put(f'/software/{software.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    one2m = data['one2m']
    del data['one2m']
    assert data == {
        'id': software.id,
        'name': 'Test Software',
        'brand': 'Test Brand',
        'version_number': '1.0.0',
        'expiration_date': '2022-01-01',
        'description': 'Test Description',
        'for_deletion': False,
    }

    assert one2m['instances']['data'][0]['assignee'] is None
    assert one2m['instances']['data'][0]['status'] is None
    assert one2m['instances']['data'][0]['serial_key'] == '123456'

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_inventory_clerk_can_not_edit_subscriptions(async_client):
    token = await login(async_client, 'clerk@mail.com')
    software = create_software()

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    data['one2m']['subscriptions']['data'][0]['start'] = '2020-01-01'
    data['one2m']['subscriptions']['data'][0]['end'] = '2020-12-31'
    data['one2m']['subscriptions']['data'][0]['number_of_licenses'] = 50

    data['one2m']['instances']['delete'] = []
    data['one2m']['subscriptions']['delete'] = []

    await async_client.put(f'/software/{software.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']

    assert data['one2m']['subscriptions']['data'][0]['start'] == '2021-01-01'
    assert data['one2m']['subscriptions']['data'][0]['end'] == '2022-01-01'
    assert data['one2m']['subscriptions']['data'][0]['number_of_licenses'] == 3

@pytest.mark.parametrize('email', ['admin@mail.com', 'super@mail.com', 'root@mail.com'])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_admins_can_add_instances(async_client, email):
    token = await login(async_client, email)
    software = create_software()

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
    )
    data = response.json()['data']
    data['one2m']['instances']['data'].append({
        'serial_key': '654321',
    })

    data['one2m']['instances']['delete'] = []
    data['one2m']['subscriptions']['delete'] = []

    await async_client.put(f'/software/{software.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
    )
    data = response.json()['data']
    assert len(data['one2m']['instances']['data']) == 2

@pytest.mark.parametrize('email', ['admin@mail.com', 'super@mail.com', 'root@mail.com'])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_admins_can_add_subscriptions(async_client, email):
    token = await login(async_client, email)
    software = create_software()

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
    )
    data = response.json()['data']
    data['one2m']['subscriptions']['data'].append({
        'start': '2023-01-01',
        'end': '2024-01-01',
        'number_of_licenses': 5
    })
    data['one2m']['subscriptions']['data'].append({
        'start': '2019-01-01',
        'end': '2020-01-01',
        'number_of_licenses': 5
    })

    data['one2m']['instances']['delete'] = []
    data['one2m']['subscriptions']['delete'] = []

    await async_client.put(f'/software/{software.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
    )
    data = response.json()['data']
    assert len(data['one2m']['subscriptions']['data']) == 3

@pytest.mark.parametrize('email', ['admin@mail.com', 'super@mail.com', 'root@mail.com'])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_admin_can_edit(async_client, email):
    token = await login(async_client, email)
    software = create_software()

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
    )

    data = response.json()['data']
    data['name'] = 'Not Ignored Software'
    data['brand'] = 'Not Ignored Brand'
    data['version_number'] = '2.0.0'
    data['description'] = 'Not Ignored Description'
    data['expiration_date'] = '2000-01-01'

    data['one2m']['instances']['delete'] = []
    data['one2m']['subscriptions']['delete'] = []

    await async_client.put(f'/software/{software.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
    )

    data = response.json()['data']
    del data['one2m']

    assert data == {
        'id': software.id,
        'name': 'Not Ignored Software',
        'brand': 'Not Ignored Brand',
        'version_number': '2.0.0',
        'description': 'Not Ignored Description',
        'expiration_date': '2000-01-01',
        'for_deletion': False,
    }

@pytest.mark.parametrize('email', ['admin@mail.com', 'super@mail.com', 'root@mail.com'])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_admin_can_edit_instances(async_client, email):
    token = await login(async_client, email)
    software = create_software()

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
    )

    data = response.json()['data']

    data['one2m']['instances']['data'][0]['serial_key'] = '654321'
    data['one2m']['instances']['data'][0]['status'] = 2

    data['one2m']['instances']['delete'] = []
    data['one2m']['subscriptions']['delete'] = []

    await async_client.put(f'/software/{software.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
    )

    data = response.json()['data']

    assert data['one2m']['instances']['data'][0]['serial_key'] == '654321'
    assert data['one2m']['instances']['data'][0]['status'] == 2

@pytest.mark.parametrize('email', ['admin@mail.com', 'super@mail.com', 'root@mail.com'])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_admin_can_edit_subscriptions(async_client, email):
    token = await login(async_client, email)
    software = create_software()

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
    )

    data = response.json()['data']

    data['one2m']['subscriptions']['data'][0]['start'] = '2020-01-01'
    data['one2m']['subscriptions']['data'][0]['end'] = '2021-01-01'
    data['one2m']['subscriptions']['data'][0]['number_of_licenses'] = 5

    data['one2m']['instances']['delete'] = []
    data['one2m']['subscriptions']['delete'] = []

    await async_client.put(f'/software/{software.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
    )

    data = response.json()['data']

    assert data['one2m']['subscriptions']['data'][0]['start'] == '2020-01-01'
    assert data['one2m']['subscriptions']['data'][0]['end'] == '2021-01-01'
    assert data['one2m']['subscriptions']['data'][0]['number_of_licenses'] == 5

@pytest.mark.parametrize('email', ['admin@mail.com', 'super@mail.com', 'root@mail.com'])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_admin_can_delete_instances(async_client, email):
    token = await login(async_client, email)
    software = create_software()

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
    )

    data = response.json()['data']

    data['one2m']['instances']['delete'] = [
        data['one2m']['instances']['data'][0]['id']
    ]
    data['one2m']['subscriptions']['delete'] = []

    await async_client.put(f'/software/{software.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
    )

    data = response.json()['data']
    assert len(data['one2m']['instances']['data']) == 0

@pytest.mark.parametrize('email', ['admin@mail.com', 'super@mail.com', 'root@mail.com'])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_put_admin_can_delete_subscriptions(async_client, email):
    token = await login(async_client, email)
    software = create_software()

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
    )

    data = response.json()['data']

    data['one2m']['instances']['delete'] = []
    data['one2m']['subscriptions']['delete'] = [
        data['one2m']['subscriptions']['data'][0]['id']
    ]

    await async_client.put(f'/software/{software.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/software/{software.id}/', 
        headers={'Authorization': f'Token {token}'}
    )

    data = response.json()['data']
    assert len(data['one2m']['subscriptions']['data']) == 0

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_instance_read_when_not_logged_in(async_client):
    response = await async_client.get('/software-instance/?search=%7B%7D')
    assert response.status_code == 403

@pytest.mark.parametrize('email', ['viewer@mail.com', 'clerk@mail.com', 'admin@mail.com', 'super@mail.com', 'root@mail.com'])
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_software_instance_read_when_logged_in(async_client, email):
    token = await login(async_client, email)
    search = {
        'page': 1,
        'rows': 5,
        'sortField': 'name',
        'sortOrder': 1,
        'filters': []
    }
    response = await async_client.get(
        f'/software-instance/?search={json.dumps(search)}',
        headers={'Authorization': f'Token {token}'}
        )
    assert response.status_code == 200
