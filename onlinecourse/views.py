from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import Course, Lesson, Question, Choice, Submission, Enrollment, Instructor, Learner


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        return Course.objects.all()


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, pk=course_id)
        user = request.user
        if user.is_authenticated:
            Enrollment.objects.get_or_create(user=user, course=course)
            return redirect('onlinecourse:course_details', pk=course.id)
        else:
            return redirect('onlinecourse:login')


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    if user.is_authenticated:
        # Convert submitted choice string IDs to integers
        selected_choice_ids = [int(id_str) for id_str in request.POST.getlist('choice')]
        
        # Retrieve or create enrollment record
        enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
        
        # Create submission
        submission = Submission.objects.create(enrollment=enrollment)
        
        # Associate selected choices
        for choice_id in selected_choice_ids:
            choice = get_object_or_404(Choice, pk=choice_id)
            submission.choices.add(choice)
            
        submission.save()
        return redirect('onlinecourse:exam_result', course_id=course.id, submission_id=submission.id)
    else:
        return redirect('onlinecourse:login')


def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    total_score = 0
    selected_choices = submission.choices.all()
    
    for question in course.question_set.all():
        correct_choices = set(question.choice_set.filter(is_correct=True))
        user_choices_for_q = set(selected_choices.filter(question=question))
        
        # Award points if user choices match the correct choice set exactly
        if correct_choices and user_choices_for_q == correct_choices:
            total_score += question.grade

    context['course'] = course
    context['submission'] = submission
    context['choices'] = selected_choices
    context['grade'] = total_score
    
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)


def login_request(request):
    if request.method == "POST":
        username = request.POST['username']
        password =  request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            return render(request, 'onlinecourse/user_login_bootstrap.html', {'error': "Invalid login credentials"})
    return render(request, 'onlinecourse/user_login_bootstrap.html')


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def registration_request(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        try:
            User.objects.get(username=username)
            return render(request, 'onlinecourse/user_registration_bootstrap.html', {'error': "Username already taken"})
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            login(request, user)
            return redirect('onlinecourse:index')
    return render(request, 'onlinecourse/user_registration_bootstrap.html')