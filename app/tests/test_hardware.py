from app.baserow_client.hardware import Hardware
from baserowapi import Filter
import pytest
from . import login

def create_hardware():
    return Hardware.create(
        'Test Hardware', 
        'Test Brand', 
        'Test Type', 
        'Test Model Number', 
        'Test Description',
        [{
            'serial_number': 'Test Serial Number',
            'procurement_date': '2021-01-01',
        }])

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_hardware_read_when_not_logged_in(async_client):
    response = await async_client.get('/hardware/1/')
    assert response.status_code == 403

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_hardware_read_when_logged_in(async_client):
    token = await login(async_client)
    hardware = create_hardware()
    response = await async_client.get(
        f'/hardware/{hardware.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    assert response.status_code == 200
    data = response.json()['data']
    del data['one2m']
    assert data == {
        'id': hardware.id,
        'name': 'Test Hardware',
        'brand': 'Test Brand',
        'type': 'Test Type',
        'model_number': 'Test Model Number',
        'description': 'Test Description',
        'for_deletion': False,
    }

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_hardware_post_when_not_logged_in(async_client):
    response = await async_client.post('/hardware/')
    assert response.status_code == 403

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_hardware_post_when_viewer(async_client):
    token = await login(async_client, 'viewer@mail.com')
    response = await async_client.post('/hardware/', headers={'Authorization': f'Token {token}'})
    assert response.status_code == 401

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_hardware_post_when_inventory_clerk(async_client):
    token = await login(async_client, 'clerk@mail.com')
    response = await async_client.post('/hardware/', headers={'Authorization': f'Token {token}'})
    assert response.status_code == 401

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_hardware_post_when_admin(async_client):
    token = await login(async_client, 'admin@mail.com')
    response = await async_client.post('/hardware/', {
        'name': 'Test Hardware',
        'brand': 'Test Brand',
        'type': 'Test Type',
        'model_number': 'Test Model Number',
        'description': 'Test Description',
        'one2m': {
            'instances': {
                'data': []
            }
        }
    }, headers={'Authorization': f'Token {token}'}, content_type='application/json')
    assert response.status_code == 201

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_hardware_post_when_super_admin(async_client):
    token = await login(async_client, 'super@mail.com')
    response = await async_client.post('/hardware/', {
        'name': 'Test Hardware',
        'brand': 'Test Brand',
        'type': 'Test Type',
        'model_number': 'Test Model Number',
        'description': 'Test Description',
        'one2m': {
            'instances': {
                'data': []
            }
        }
    }, headers={'Authorization': f'Token {token}'}, content_type='application/json')
    assert response.status_code == 201

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_hardware_post_when_root_admin(async_client):
    token = await login(async_client, 'root@mail.com')
    response = await async_client.post('/hardware/', {
        'name': 'Test Hardware',
        'brand': 'Test Brand',
        'type': 'Test Type',
        'model_number': 'Test Model Number',
        'description': 'Test Description',
        'one2m': {
            'instances': {
                'data': []
            }
        }
    }, headers={'Authorization': f'Token {token}'}, content_type='application/json')
    assert response.status_code == 201

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_hardware_put_when_viewer(async_client):
    token = await login(async_client, 'viewer@mail.com')
    response = await async_client.put('/hardware/1/', headers={'Authorization': f'Token {token}'})
    assert response.status_code == 401

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_hardware_put_when_inventory_clerk(async_client):
    token = await login(async_client, 'clerk@mail.com')
    hardware = create_hardware()

    response = await async_client.get(
        f'/hardware/{hardware.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    data['name'] = 'Ignored Hardware'
    data['brand'] = 'Ignored Brand'
    data['type'] = 'Ignored Type'
    data['model_number'] = 'Ignored Model Number'
    data['description'] = 'Ignored Description'
    data['one2m']['instances']['data'][0]['assignee'] = 1
    data['one2m']['instances']['delete'] = []

    await async_client.put(f'/hardware/{hardware.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/hardware/{hardware.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    one2m = data['one2m']
    del data['one2m']
    assert data == {
        'id': hardware.id,
        'name': 'Test Hardware',
        'brand': 'Test Brand',
        'type': 'Test Type',
        'model_number': 'Test Model Number',
        'description': 'Test Description',
        'for_deletion': False,
    }

    assert one2m['instances']['data'][0]['assignee'] == 1

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_hardware_put_when_admin(async_client):
    token = await login(async_client, 'admin@mail.com')
    hardware = create_hardware()

    response = await async_client.get(
        f'/hardware/{hardware.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    data['name'] = 'Not Ignored Hardware'
    data['brand'] = 'Not Ignored Brand'
    data['type'] = 'Not Ignored Type'
    data['model_number'] = 'Not Ignored Model Number'
    data['description'] = 'Not Ignored Description'
    data['one2m']['instances']['data'][0]['assignee'] = 1
    data['one2m']['instances']['delete'] = []

    await async_client.put(f'/hardware/{hardware.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/hardware/{hardware.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    one2m = data['one2m']
    del data['one2m']
    assert data == {
        'id': hardware.id,
        'name': 'Not Ignored Hardware',
        'brand': 'Not Ignored Brand',
        'type': 'Not Ignored Type',
        'model_number': 'Not Ignored Model Number',
        'description': 'Not Ignored Description',
        'for_deletion': False,
    }

    assert one2m['instances']['data'][0]['assignee'] == 1

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_hardware_put_when_super_admin(async_client):
    token = await login(async_client, 'super@mail.com')
    hardware = create_hardware()

    response = await async_client.get(
        f'/hardware/{hardware.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    data['name'] = 'Not Ignored Hardware'
    data['brand'] = 'Not Ignored Brand'
    data['type'] = 'Not Ignored Type'
    data['model_number'] = 'Not Ignored Model Number'
    data['description'] = 'Not Ignored Description'
    data['one2m']['instances']['data'][0]['assignee'] = 1
    data['one2m']['instances']['delete'] = []

    await async_client.put(f'/hardware/{hardware.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/hardware/{hardware.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    one2m = data['one2m']
    del data['one2m']
    assert data == {
        'id': hardware.id,
        'name': 'Not Ignored Hardware',
        'brand': 'Not Ignored Brand',
        'type': 'Not Ignored Type',
        'model_number': 'Not Ignored Model Number',
        'description': 'Not Ignored Description',
        'for_deletion': False,
    }

    assert one2m['instances']['data'][0]['assignee'] == 1

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_hardware_put_when_root_admin(async_client):
    token = await login(async_client, 'root@mail.com')
    hardware = create_hardware()

    response = await async_client.get(
        f'/hardware/{hardware.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    data['name'] = 'Not Ignored Hardware'
    data['brand'] = 'Not Ignored Brand'
    data['type'] = 'Not Ignored Type'
    data['model_number'] = 'Not Ignored Model Number'
    data['description'] = 'Not Ignored Description'
    data['one2m']['instances']['data'][0]['assignee'] = 1
    data['one2m']['instances']['delete'] = []

    await async_client.put(f'/hardware/{hardware.id}/', data, headers={'Authorization': f'Token {token}'}, content_type='application/json')

    response = await async_client.get(
        f'/hardware/{hardware.id}/', 
        headers={'Authorization': f'Token {token}'}
        )
    data = response.json()['data']
    one2m = data['one2m']
    del data['one2m']
    assert data == {
        'id': hardware.id,
        'name': 'Not Ignored Hardware',
        'brand': 'Not Ignored Brand',
        'type': 'Not Ignored Type',
        'model_number': 'Not Ignored Model Number',
        'description': 'Not Ignored Description',
        'for_deletion': False,
    }

    assert one2m['instances']['data'][0]['assignee'] == 1