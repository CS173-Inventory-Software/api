from app.baserow_client.user import User
import datetime
from baserowapi import Filter

async def login(async_client, email='root@mail.com'):
    user = User.table.get_rows(
        filters=[Filter("email", email)], 
        return_single=True
    )
    five_minutes_from_now = datetime.datetime.now() + datetime.timedelta(minutes=5)
    user.update({"auth_code": '9999', "auth_expiry": five_minutes_from_now})

    response = await async_client.post("/login/", {
        'email': email,
        'code': '9999'
    })

    token = response.json().get('token')

    return token