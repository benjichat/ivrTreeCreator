import requests
import string
import random

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def start(test_number, message):
    response = requests.post(
    'https://api.46elks.com/a1/conversations',
    auth = ('u842f2a9cfb50a0f7335f4dec9997f5bc', 'A9D615832085584F3BEF5C4F8ED84326'),
    data = {
            "to": test_number,
            "message": message,
            "token":"new",
            "reply_url": "https://dca8234f.ngrok.io/test_response"
            },
    )

    print(response)
