from django.test import TestCase
from django.contrib.auth.models import User
from onlinecourse.models import Course, Question, Choice, Enrollment, Submission

class ExamTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        # Create test course
        self.course = Course.objects.create(name='Learning Django', description='Django Basics')
        
        # Create test question & choices
        self.question = Question.objects.create(
            course=self.course,
            content='Is Django a Python framework?',
            grade=100
        )
        self.choice_yes = Choice.objects.create(question=self.question, content='Yes', is_correct=True)
        self.choice_no = Choice.objects.create(question=self.question, content='No', is_correct=False)
        
        # Enroll user
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course, mode='honor')

    def test_exam_submission_pass(self):
        # Log in
        self.client.login(username='testuser', password='password123')
        
        # Submit correct answer
        response = self.client.post(
            f'/onlinecourse/{self.course.id}/submit/',
            {'choice': [str(self.choice_yes.id)]}
        )
        
        # Verify submission creation and redirection
        self.assertEqual(response.status_code, 302)
        submission = Submission.objects.get(enrollment=self.enrollment)
        self.assertIn(self.choice_yes, submission.choices.all())