import unittest
from app import app, db, Todo

class TodoTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for isolation during testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = app.test_client()
        
        # Instantiate tables within the memory db context
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Tear down db session and clean up memory database
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_empty_list(self):
        """Verify the homepage displays the empty state when no tasks exist."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No tasks yet', response.data)

    def test_add_task(self):
        """Verify submitting the task creation form adds a new Todo record."""
        response = self.client.post('/', data={'content': 'Test Task'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Task', response.data)
        self.assertNotIn(b'No tasks yet', response.data)

    def test_delete_task(self):
        """Verify the delete route deletes a task by ID."""
        with app.app_context():
            task = Todo(content='Delete Me')
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        # Perform deletion
        response = self.client.get(f'/delete/{task_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Delete Me', response.data)
        self.assertIn(b'No tasks yet', response.data)

    def test_update_task(self):
        """Verify the edit form is served correctly, and updates commit successfully."""
        with app.app_context():
            task = Todo(content='Original Task')
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        # Verify update page loads current data
        response = self.client.get(f'/update/{task_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Original Task', response.data)

        # Perform the update action
        response = self.client.post(f'/update/{task_id}', data={'content': 'Updated Task'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Updated Task', response.data)
        self.assertNotIn(b'Original Task', response.data)

if __name__ == '__main__':
    unittest.main()
