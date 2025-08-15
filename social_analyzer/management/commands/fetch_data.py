from django.core.management.base import BaseCommand
from django.conf import settings
from social_analyzer.models import SocialPost, TrackedKeyword
from social_analyzer.sentiment_analysis import analyze_sentiment, analyze_emotion, get_topic_model
import tweepy

class Command(BaseCommand):
    help = 'Fetches recent tweets and performs sentiment analysis.'

    def handle(self, *args, **options):
        self.stdout.write("Starting to fetch and analyze tweets...")
        SocialPost.objects.all().delete()
        
        keywords = TrackedKeyword.objects.filter(is_active=True).values_list('keyword', flat=True)
        if not keywords:
            self.stdout.write(self.style.WARNING("No active keywords found. Skipping data fetch."))
            return

        query = "DjangoProject -is:retweet lang:en"

        try:
            client = tweepy.Client(settings.TWITTER_BEARER_TOKEN)
            response = client.search_recent_tweets(
                query=query, 
                max_results=5, 
                expansions=['author_id'],
                tweet_fields=['text'],
                user_fields=['username']
            )
            
            tweets = response.data
            users = {user['id']: user for user in response.includes['users']} if response.includes and 'users' in response.includes else {}

            if tweets:
                all_texts = []
                for tweet in tweets:
                    text = tweet.text
                    all_texts.append(text)
                    
                    sentiment_label, sentiment_score = analyze_sentiment(text)
                    emotion_label, emotion_score = analyze_emotion(text)
                    author_username = users.get(tweet.author_id, {}).get('username', 'unknown_user')
                    
                    SocialPost.objects.create(
                        title=f"Tweet by @{author_username}",
                        description=text,
                        platform='Twitter',
                        sentiment_label=sentiment_label,
                        sentiment_score=sentiment_score,
                        emotion_label=emotion_label
                    )
                self.stdout.write(self.style.SUCCESS(f'Successfully fetched and analyzed {len(tweets)} tweets.'))
                
                topics = get_topic_model(all_texts)
                self.stdout.write(self.style.SUCCESS(f'Identified Topics: {topics}'))
            else:
                self.stdout.write(self.style.WARNING('No new tweets found.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))