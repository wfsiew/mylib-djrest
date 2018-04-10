from django.test import TestCase
import requests, os

# Create your tests here.

def create_user():
    picdir = os.path.dirname(os.path.realpath(__file__))
    headers = {
        'Authorization': 'Bearer TK7uZMS3Rze5sMeRxYc7IyM02AtDlh'
    }
    link = 'http://localhost:8000/app/users/'
    o = {
        'userid': 5,
        'username': 'andy.hui',
        'password': 'andy.hui',
        'email': 'andy.hui@gmail.com',
        'usertype': 3,
        'mobile': '01268655433',
        'firstname': 'Andy',
        'lastname': 'Hui'
    }
    path = os.path.join(picdir, 'pic/profile2.jpg')
    p = open(path, 'rb')
    pd = {
        'picture': ('profile2.jpg', p, 'application/octet-stream', { 'Expires': '0' })
    }
    k = requests.post(link, data=o, files=pd, headers=headers)

if __name__ == '__main__':
    create_user()