# Testing Guide for Django Models

This document serves as a comprehensive guide to help you get started with testing in Django. It outlines how to write tests for your Django models, explains best practices, and provides detailed examples specific to the models in your DataDeck project.

## Table of Contents

1. [Introduction to Testing in Django](#introduction-to-testing-in-django)
2. [Setting Up Testing in Your Django Project](#setting-up-testing-in-your-django-project)
3. [Writing Tests in Django](#writing-tests-in-django)
   - [Understanding TestCase Classes](#understanding-testcase-classes)
   - [Creating Test Data](#creating-test-data)
   - [Running Tests](#running-tests)
4. [Testing Your Models](#testing-your-models)
   - [Session Model Tests](#session-model-tests)
   - [CustomAdmin Model Tests](#customadmin-model-tests)
5. [Best Practices for Testing](#best-practices-for-testing)
6. [Conclusion](#conclusion)

---

## Introduction to Testing in Django

Testing is a crucial part of software development that ensures your code behaves as expected. In Django, testing is made easier with built-in support for unit tests, which helps you validate the functionality of your models, views, forms, and more.

**Why Test?**

- **Catch Bugs Early**: Testing helps identify and fix bugs before they reach production.
- **Ensure Code Quality**: Tests serve as documentation and ensure that your code meets the required standards.
- **Facilitate Refactoring**: With tests in place, you can confidently refactor code, knowing that any issues will be caught.

---

## Setting Up Testing in Your Django Project

Before writing tests, ensure your Django project is correctly set up for testing.

1. **Install Requirements**: Make sure all dependencies are installed. Typically, this includes Django and any other packages used in your project.

   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `tests` Directory**: In each app directory where you want to write tests, create a `tests` directory with an `__init__.py` file.

   ```
   video_app/
       __init__.py
       models.py
       views.py
       tests/
           __init__.py
   ```

3. **Configure the Test Database**: Django uses a separate database for running tests. By default, it uses an in-memory SQLite database, but you can configure it in your `settings.py`:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': ':memory:',
       }
   }
   ```

---

## Writing Tests in Django

### Understanding TestCase Classes

Django provides the `TestCase` class, which is a subclass of Python's `unittest.TestCase`. Use it to write your tests.

- **`django.test.TestCase`**: Resets the database between tests and provides helper methods.
- **`django.test.SimpleTestCase`**: Does not require database access.

### Creating Test Data

You can create test data within your test methods or use the `setUp` method to initialize data for use in multiple tests.

```python
from django.test import TestCase
from .models import Session

class SessionModelTest(TestCase):
    def setUp(self):
        self.session = Session.objects.create(
            name="Test Session",
            section=1,
            created_by=None  # Assuming no admin for simplicity
        )
```

### Running Tests

Run your tests using the `manage.py` command:

```bash
python manage.py test
```

This command searches for tests in `tests` directories and executes them.

---

## Testing Your Models

Below are detailed examples of how to test each of your models.

### Session Model Tests

**File**: `video_app/tests/test_session_model.py`

#### Tests to Write

1. **Session Creation**: Test that a `Session` object can be created and saved.
2. **Session Code Generation**: Ensure that the `session_code` is generated automatically and is unique.
3. **Expiration Logic**: Test the `is_expired` method under different scenarios.
4. **Days Until Deletion**: Verify the `days_until_deletion` method, especially when `is_paused` is `True` or `False`.
5. **String Representation**: Test the `__str__` method.

#### Example Test Cases

```python
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from video_app.models import Session, CustomAdmin

class SessionModelTest(TestCase):
    def setUp(self):
        self.admin = CustomAdmin.objects.create_user(
            username='admin', password='password123', school='Test School', district='Test District'
        )
        self.session = Session.objects.create(
            name="Test Session",
            section=1,
            created_by=self.admin
        )

    def test_session_creation(self):
        self.assertIsInstance(self.session, Session)
        self.assertEqual(self.session.name, "Test Session")
        self.assertEqual(self.session.section, 1)
        self.assertEqual(self.session.created_by, self.admin)

    def test_session_code_generated(self):
        self.assertIsNotNone(self.session.session_code)
        self.assertEqual(len(self.session.session_code), 8)

    def test_session_code_uniqueness(self):
        session2 = Session.objects.create(
            name="Another Session",
            section=2,
            created_by=self.admin
        )
        self.assertNotEqual(self.session.session_code, session2.session_code)

    def test_is_expired_method(self):
        # Test when session is not paused and not expired
        self.assertFalse(self.session.is_expired())

        # Test when session is paused
        self.session.is_paused = True
        self.session.save()
        self.assertFalse(self.session.is_expired())

        # Test when session is expired
        self.session.created_at = timezone.now() - timedelta(days=8)
        self.session.is_paused = False
        self.session.save()
        self.assertTrue(self.session.is_expired())

    def test_days_until_deletion(self):
        # When not paused
        days_left = self.session.days_until_deletion()
        self.assertEqual(days_left, 360)

        # When paused
        self.session.is_paused = True
        self.session.save()
        self.assertEqual(self.session.days_until_deletion(), 'Paused')

    def test_str_method(self):
        self.assertEqual(str(self.session), "Test Session")
```
