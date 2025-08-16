# social_analyzer/management/commands/fetch_data.py

from django.core.management.base import BaseCommand
from django.conf import settings
from social_analyzer.models import SocialPost, TrackedKeyword
from social_analyzer.sentiment_analysis import analyze_sentiment, analyze_emotion, get_topic_model
import tweepy
import praw 
import time 
from langdetect import detect, LangDetectException

class Command(BaseCommand):
    help = 'Fetches recent tweets and performs sentiment analysis.'

    def handle(self, *args, **options):
        self.stdout.write("Starting to fetch and analyze posts...")
        
        SocialPost.objects.all().delete()
        
        keywords = list(TrackedKeyword.objects.filter(is_active=True).values_list('keyword', flat=True))
        print(keywords)
        if not keywords:
            self.stdout.write(self.style.WARNING("No active keywords found. Skipping data fetch."))
            return

        mid_point = len(keywords) // 2
        group1 = keywords[:mid_point]
        group2 = keywords[mid_point:]
        
        query = ""
        if group1 and group2:
            query_part1 = " OR ".join(group1)
            query_part2 = " OR ".join(group2)
            query = f'({query_part1}) ({query_part2})'
        elif keywords:
            query = " OR ".join(keywords)

        query_x = query + " -is:retweet lang:en"

        try:
            client_x = tweepy.Client(settings.TWITTER_BEARER_TOKEN)

            client_reddit = praw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent=settings.REDDIT_USER_AGENT
            )

            all_posts_data = []

            response_x = client_x.search_recent_tweets(
                query=query_x,
                max_results=10,
                expansions=['author_id'],
                tweet_fields=['text'],
                user_fields=['username'],
            )
            
            tweets = response_x.data
            users = {user['id']: user for user in response_x.includes['users']} if response_x.includes and 'users' in response_x.includes else {}
            if tweets:
                for tweet in tweets:
                    author_username = users.get(tweet.author_id, {}).get('username', 'unknown_user')
                    all_posts_data.append({
                        'title': f"Tweet by @{author_username}",
                        'description': tweet.text,
                        'platform': 'Twitter',
                    })

            for keyword in keywords:
                for submission in client_reddit.subreddit('all').search(keyword, limit=2):
                    try:
                        text = (submission.title or "") + " " + (submission.selftext or "")
                        if not text.strip():
                            continue
                        if detect(text) == "en":
                            all_posts_data.append({
                                'title': submission.title,
                                'description': submission.selftext,
                                'platform': 'Reddit',
                            })
                    except LangDetectException:
                        continue

            
            if all_posts_data:
                all_texts = [d['description'] for d in all_posts_data]
                topics = get_topic_model(all_texts)
                self.stdout.write(self.style.SUCCESS(f'Identified Topics: {topics}'))

                for post_data in all_posts_data:
                    sentiment_label, sentiment_score = analyze_sentiment(post_data['description'])
                    emotion_label, emotion_score = analyze_emotion(post_data['description'])

                    SocialPost.objects.create(
                        title=post_data['title'],
                        description=post_data['description'],
                        platform=post_data['platform'],
                        sentiment_label=sentiment_label,
                        sentiment_score=sentiment_score,
                        emotion_label=emotion_label,
                    )

                self.stdout.write(self.style.SUCCESS(f'Successfully fetched and analyzed {len(all_posts_data)} posts.'))
            else:
                self.stdout.write(self.style.WARNING('No new posts found for any active keywords.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
