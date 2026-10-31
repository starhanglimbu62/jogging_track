from datetime import date

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import Entry, UserProfile


class JoggingApiTests(APITestCase):
    def setUp(self):
        self.user = self.create_user('runner', 'USER')
        self.other = self.create_user('other', 'USER')
        self.admin = self.create_user('admin', 'ADMIN')

    def create_user(self, username, role):
        user = User.objects.create_user(username=username, password='strong-pass-123')
        UserProfile.objects.create(user=user, role=role)
        return user

    def login(self, user):
        response = self.client.post('/api/auth/login/', {
            'username': user.username,
            'password': 'strong-pass-123',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['token'])

    def test_registration_hashes_password_and_defaults_to_user_role(self):
        response = self.client.post('/api/auth/signup/', {
            'username': 'new-runner',
            'email': 'new@example.com',
            'password': 'strong-pass-123',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        created = User.objects.get(username='new-runner')
        self.assertTrue(created.check_password('strong-pass-123'))
        self.assertEqual(created.profile.role, 'USER')
        self.assertNotIn('password', response.data)

    def test_invalid_login_is_rejected(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'runner',
            'password': 'wrong-password',
        }, format='json')
        self.assertEqual(response.status_code, 401)

    def test_user_can_manage_only_owned_entries(self):
        self.login(self.user)
        create = self.client.post('/api/entry/', {
            'distance': 5,
            'duration': 30,
            'date': '2026-01-05',
        }, format='json')
        self.assertEqual(create.status_code, 201)
        self.assertEqual(create.data['user']['id'], self.user.id)
        entry = Entry.objects.get(pk=create.data['id'])
        self.assertEqual(create.data['average_speed'], 0.17)

        other_entry = Entry.objects.create(user=self.other, distance=9, duration=45, date=date(2026, 1, 6))
        listing = self.client.get('/api/entry/')
        self.assertEqual(listing.status_code, 200)
        self.assertEqual([row['id'] for row in listing.data], [entry.id])
        self.assertEqual(self.client.get('/api/entry/%s/' % other_entry.id).status_code, 404)

    def test_date_range_filter_and_weekly_report(self):
        Entry.objects.create(user=self.user, distance=5, duration=30, date=date(2026, 1, 5))
        Entry.objects.create(user=self.user, distance=7, duration=35, date=date(2026, 1, 8))
        Entry.objects.create(user=self.user, distance=11, duration=55, date=date(2026, 2, 1))
        self.login(self.user)

        response = self.client.get('/api/entry/?from=2026-01-01&to=2026-01-31')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        report = self.client.get('/api/weekly-report/?from=2026-01-01&to=2026-01-31')
        self.assertEqual(report.status_code, 200)
        self.assertEqual(sum(row['total_distance'] for row in report.data), 12)

    def test_admin_can_view_all_entries_and_assign_owner(self):
        Entry.objects.create(user=self.user, distance=5, duration=30, date=date(2026, 1, 5))
        self.login(self.admin)
        self.assertEqual(self.client.get('/api/entry/').data.__len__(), 1)
        response = self.client.post('/api/entry/', {
            'distance': 4,
            'duration': 20,
            'date': '2026-01-07',
            'user_id': self.other.id,
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.other.id)

    def test_only_manager_and_admin_can_manage_users(self):
        self.login(self.user)
        self.assertEqual(self.client.get('/api/user/').status_code, 403)
        self.login(self.admin)
        self.assertEqual(self.client.get('/api/user/').status_code, 200)

    def test_manager_can_create_user_without_assigning_a_privileged_role(self):
        manager = self.create_user('manager', 'MANAGER')
        self.login(manager)
        response = self.client.post('/api/user/', {
            'username': 'managed-user',
            'email': 'managed@example.com',
            'password': 'strong-pass-123',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        created = User.objects.get(username='managed-user')
        self.assertTrue(created.check_password('strong-pass-123'))
        self.assertEqual(created.profile.role, 'USER')
