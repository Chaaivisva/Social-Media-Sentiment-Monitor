from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count
from social_analyzer.models import SocialPost, TrackedKeyword, SavedReport, AlertSettings
from collections import defaultdict
import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def dashboard(request):
    posts = SocialPost.objects.all().order_by('-timestamp')
    sentiment_filter = request.GET.get('sentiment')
    search_query = request.GET.get('q')
    emotion_filter = request.GET.get('emotion')

    if sentiment_filter:
        posts = posts.filter(sentiment_label=sentiment_filter)
    
    if search_query:
        posts = posts.filter(description__icontains=search_query)

    if emotion_filter:
        posts = posts.filter(emotion_label=emotion_filter)

    context = {
        'posts': posts,
        'selected_sentiment': sentiment_filter or '',
        'selected_emotion': emotion_filter or '',
        'search_query': search_query or '',
        'emotions': SocialPost.objects.values_list('emotion_label', flat=True).distinct(),
    }
    return render(request, 'social_analyzer/dashboard.html', context)


def get_sentiment_data(request):
    labels_order = ['positive', 'negative', 'neutral']
    sentiment_counts = SocialPost.objects.values('sentiment_label').annotate(count=Count('id'))
    sentiment_data = {label: 0 for label in labels_order}
    for item in sentiment_counts:
        label = item['sentiment_label']
        if label in sentiment_data:
            sentiment_data[label] = item['count']
    chart_labels = [label.capitalize() for label in labels_order]
    chart_data = [sentiment_data[label] for label in labels_order]
    
    return JsonResponse({
        'sentiment_pie_chart': {'labels': chart_labels, 'data': chart_data},
        'sentiment_bar_chart': {'labels': chart_labels, 'data': chart_data}
    })


@login_required
@require_POST
def save_report(request):
    sentiment_filter = request.GET.get('sentiment')
    search_query = request.GET.get('q')
    emotion_filter = request.GET.get('emotion')

    posts_to_save = SocialPost.objects.all().order_by('-timestamp')
    if sentiment_filter:
        posts_to_save = posts_to_save.filter(sentiment_label=sentiment_filter)
    if search_query:
        posts_to_save = posts_to_save.filter(description__icontains=search_query)
    if emotion_filter:
        posts_to_save = posts_to_save.filter(emotion_label=emotion_filter)

    report_name = request.POST.get('report_name', f'Report from {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    serialized_posts = []
    for post in posts_to_save.values():
        post['timestamp'] = post['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        serialized_posts.append(post)

    report_data = {
        'filters': request.GET.dict(),
        'posts': serialized_posts
    }
    
    SavedReport.objects.create(
        user=request.user,
        name=report_name,
        report_data=json.dumps(report_data)
    )
    messages.success(request, f'Report "{report_name}" saved successfully!')
    return redirect('dashboard')

@login_required
def view_reports(request):
    reports = SavedReport.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'social_analyzer/view_reports.html', {'reports': reports})

@login_required
def load_report(request, report_id):
    report = get_object_or_404(SavedReport, id = report_id, user = request.user)
    report_data = json.loads(report.report_data)

    context = {
        'posts': report_data['posts'],
        'report_name': report.name,
        'filters': report_data['filters']
    }
    return render(request, 'social_analyzer/loaded_report.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'social_analyzer/register.html', {'form': form})

