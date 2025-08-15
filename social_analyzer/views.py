from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from social_analyzer.models import SocialPost
from collections import defaultdict
import datetime

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


