# social_analyzer/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count
from social_analyzer.models import SocialPost, TrackedKeyword, SavedReport
from collections import defaultdict
import datetime
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def dashboard(request):
    posts = SocialPost.objects.all().order_by('timestamp')

    keyword_filter = request.GET.get('keyword')
    compare_keyword1 = request.GET.get('compare1')
    compare_keyword2 = request.GET.get('compare2')
    platform_filter = request.GET.get('platform')

    if compare_keyword1 and compare_keyword2:
        posts_comp1 = posts.filter(description__icontains=compare_keyword1)
        posts_comp2 = posts.filter(description__icontains=compare_keyword2)
        
        if platform_filter:
            posts_comp1 = posts_comp1.filter(platform=platform_filter)
            posts_comp2 = posts_comp2.filter(platform=platform_filter)

        context = {
            'compare_mode': True,
            'posts_comp1': posts_comp1,
            'posts_comp2': posts_comp2,
            'compare_keyword1': compare_keyword1,
            'compare_keyword2': compare_keyword2,
            'keywords': TrackedKeyword.objects.filter(is_active=True),
            'platforms': SocialPost.objects.values_list('platform', flat=True).distinct()
        }
        return render(request, 'social_analyzer/dashboard.html', context)
    
    elif keyword_filter:
        posts = posts.filter(description__icontains=keyword_filter)

    if platform_filter:
        posts = posts.filter(platform=platform_filter)

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
        'selected_keyword': keyword_filter or '',
        'selected_platform': platform_filter or '',
        'search_query': search_query or '',
        'emotions': SocialPost.objects.values_list('emotion_label', flat=True).distinct(),
        'keywords': TrackedKeyword.objects.filter(is_active=True),
        'platforms': SocialPost.objects.values_list('platform', flat=True).distinct(),
    }
    return render(request, 'social_analyzer/dashboard.html', context)

def get_sentiment_data(request):
    keyword_filter = request.GET.get('keyword')
    compare_keyword1 = request.GET.get('compare1')
    compare_keyword2 = request.GET.get('compare2')
    platform_filter = request.GET.get('platform')

    labels_order = ['positive', 'negative', 'neutral']
    
    def get_sentiment_data_for_keyword(keyword, platform=None):
        posts_for_keyword = SocialPost.objects.filter(description__icontains=keyword) if keyword else SocialPost.objects.all()
        if platform:
            posts_for_keyword = posts_for_keyword.filter(platform=platform)
            
        sentiment_counts = posts_for_keyword.values('sentiment_label').annotate(count=Count('id'))
        
        sentiment_data = {label: 0 for label in labels_order}
        for item in sentiment_counts:
            label = item['sentiment_label']
            if label in sentiment_data:
                sentiment_data[label] = item['count']
        
        return {
            'labels': [label.capitalize() for label in labels_order],
            'data': [sentiment_data[label] for label in labels_order]
        }

    if compare_keyword1 and compare_keyword2:
        data_comp1 = get_sentiment_data_for_keyword(compare_keyword1, platform_filter)
        data_comp2 = get_sentiment_data_for_keyword(compare_keyword2, platform_filter)
        return JsonResponse({
            'compare1_charts': data_comp1,
            'compare2_charts': data_comp2,
        })
    else:
        chart_data = get_sentiment_data_for_keyword(keyword_filter, platform_filter)
        return JsonResponse({
            'sentiment_pie_chart': chart_data,
            'sentiment_bar_chart': chart_data,
        })

@login_required
@require_POST
def save_report(request):
    sentiment_filter = request.GET.get('sentiment')
    search_query = request.GET.get('q')
    emotion_filter = request.GET.get('emotion')
    keyword_filter = request.GET.get('keyword')
    compare_keyword1 = request.GET.get('compare1')
    compare_keyword2 = request.GET.get('compare2')
    platform_filter = request.GET.get('platform')

    posts_to_save = SocialPost.objects.all().order_by('-timestamp')
    if sentiment_filter:
        posts_to_save = posts_to_save.filter(sentiment_label=sentiment_filter)
    if search_query:
        posts_to_save = posts_to_save.filter(description__icontains=search_query)
    if emotion_filter:
        posts_to_save = posts_to_save.filter(emotion_label=emotion_filter)
    if keyword_filter:
        posts_to_save = posts_to_save.filter(description__icontains=keyword_filter)
    if compare_keyword1:
        posts_to_save = posts_to_save.filter(description__icontains=compare_keyword1)
    if compare_keyword2:
        posts_to_save = posts_to_save.filter(description__icontains=compare_keyword2)
    if platform_filter:
        posts_to_save = posts_to_save.filter(platform=platform_filter)

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
    report = get_object_or_404(SavedReport, id=report_id, user=request.user)
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
