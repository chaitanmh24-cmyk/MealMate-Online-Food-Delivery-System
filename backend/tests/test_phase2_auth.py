import pytest
from django.urls import reverse
from accounts.models import User

@pytest.mark.django_db
def test_signup_successful(client):
    url = reverse('accounts:signup')
    response = client.post(url, {
        'first_name': 'Amit',
        'last_name': 'Verma',
        'email': 'amit.verma@example.com',
        'mobile_number': '9876543210',
        'gender': 'M',
        'address': 'Koramangala 5th Block',
        'city': 'Bengaluru',
        'password': 'StrongPassword123!',
        'confirm_password': 'StrongPassword123!'
    })
    assert response.status_code == 302
    assert response.url == '/'
    user = User.objects.filter(email='amit.verma@example.com').first()
    assert user is not None
    assert user.first_name == 'Amit'
    assert user.mobile_number == '9876543210'

@pytest.mark.django_db
def test_signup_invalid_mobile_fails(client):
    url = reverse('accounts:signup')
    response = client.post(url, {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'mobile_number': '12345',  # Invalid!
        'gender': 'M',
        'password': 'StrongPassword123!',
        'confirm_password': 'StrongPassword123!'
    })
    assert response.status_code == 200
    assert 'Enter a valid 10-digit Indian mobile number' in response.content.decode()

@pytest.mark.django_db
def test_login_successful_with_email(client):
    User.objects.create_user(
        username='priya_sharma',
        email='priya@example.com',
        password='MyPassword123!',
        mobile_number='9876543222'
    )
    url = reverse('accounts:login')
    response = client.post(url, {
        'username_or_email': 'priya@example.com',
        'password': 'MyPassword123!'
    })
    assert response.status_code == 302
    assert response.url == '/'

@pytest.mark.django_db
def test_profile_update(client):
    user = User.objects.create_user(
        username='karthik',
        email='karthik@example.com',
        password='Password123!',
        mobile_number='9876543233',
        first_name='Karthik',
        last_name='Rao'
    )
    client.force_login(user)

    url = reverse('accounts:profile')
    response = client.post(url, {
        'first_name': 'Karthik',
        'last_name': 'Kumar',
        'email': 'karthik@example.com',
        'mobile_number': '9876543233',
        'gender': 'M',
        'city': 'Bengaluru',
        'address': 'Indiranagar 100ft Road'
    })
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.last_name == 'Kumar'
    assert user.address == 'Indiranagar 100ft Road'
