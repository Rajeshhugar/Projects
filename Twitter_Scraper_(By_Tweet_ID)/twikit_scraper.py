from twikit import Client, TooManyRequests
import time
from datetime import datetime
import csv
from configparser import ConfigParser
from random import randint
import asyncio
import os


MINIMUM_TWEETS = 1000  # Set a higher limit or use 0 for unlimited
QUERY = '(from:narendramodi) lang:en until:2025-01-01 since:2024-01-01'


async def get_tweets(tweets, client):
    """Get tweets with proper error handling and delays"""
    if tweets is None:
        print(f'{datetime.now()} - Getting initial tweets...')
        tweets = await client.search_tweet(QUERY, product='Top')
    else:
        wait_time = randint(5, 10)
        print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds...')
        await asyncio.sleep(wait_time)
        tweets = await tweets.next()
    return tweets


async def main():
    try:
        # Login credentials
        config = ConfigParser()
        if not os.path.exists('config.ini'):
            print("Error: config.ini file not found!")
            return
        
        config.read('config.ini')
        
        # Check if config sections exist
        if 'X' not in config:
            print("Error: [X] section not found in config.ini!")
            return
            
        username = config['X']['username']
        email = config['X']['email']
        password = config['X']['password']

        # Create CSV file with headers
        csv_filename = 'tweets.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Tweet_count', 'Username', 'Text', 'Created At', 'Retweets', 'Likes'])

        # Initialize client
        client = Client(language='en-US')
        
        # Authentication handling
        cookies_file = 'cookies.json'
        authenticated = False
        
        # Try to load existing cookies first
        if os.path.exists(cookies_file):
            print(f'{datetime.now()} - Loading existing cookies...')
            try:
                # Handle both sync and async versions of load_cookies
                load_result = client.load_cookies(cookies_file)
                if hasattr(load_result, '__await__'):
                    await load_result
                print(f'{datetime.now()} - Cookies loaded successfully')
                authenticated = True
            except Exception as e:
                print(f'{datetime.now()} - Failed to load cookies: {e}')
                authenticated = False
        
        # If cookies failed to load or don't exist, login
        if not authenticated:
            print(f'{datetime.now()} - Attempting to login...')
            try:
                await client.login(auth_info_1=username, auth_info_2=email, password=password)
                print(f'{datetime.now()} - Login successful')
                
                # Save cookies after successful login
                try:
                    save_result = client.save_cookies(cookies_file)
                    if hasattr(save_result, '__await__'):
                        await save_result
                    print(f'{datetime.now()} - Cookies saved successfully')
                except Exception as e:
                    print(f'{datetime.now()} - Warning: Could not save cookies: {e}')
                    
            except Exception as e:
                print(f'{datetime.now()} - Login failed: {e}')
                return

        tweet_count = 0
        tweets = None
        max_retries = 3
        retry_count = 0
        consecutive_empty_results = 0
        max_empty_results = 3  # Stop if we get 3 consecutive empty results

        while (MINIMUM_TWEETS == 0 or tweet_count < MINIMUM_TWEETS) and retry_count < max_retries and consecutive_empty_results < max_empty_results:
            try:
                tweets = await get_tweets(tweets, client)
                retry_count = 0  # Reset retry count on success
                
            except TooManyRequests as e:
                rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                print(f'{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}')
                wait_time = rate_limit_reset - datetime.now()
                if wait_time.total_seconds() > 0:
                    await asyncio.sleep(wait_time.total_seconds())
                continue
                
            except Exception as e:
                retry_count += 1
                print(f'{datetime.now()} - Error occurred: {e}')
                if retry_count < max_retries:
                    print(f'{datetime.now()} - Retrying... ({retry_count}/{max_retries})')
                    await asyncio.sleep(30)  # Wait 30 seconds before retry
                    continue
                else:
                    print(f'{datetime.now()} - Max retries reached. Exiting...')
                    break

            if not tweets:
                print(f'{datetime.now()} - No more tweets found')
                consecutive_empty_results += 1
                print(f'{datetime.now()} - Empty result count: {consecutive_empty_results}/{max_empty_results}')
                if consecutive_empty_results >= max_empty_results:
                    print(f'{datetime.now()} - Reached maximum empty results, stopping...')
                    break
                continue
                
            # Debug information (remove after testing)
            # print(f'{datetime.now()} - Tweet object type: {type(tweets)}')
            # print(f'{datetime.now()} - Tweet object methods: {[method for method in dir(tweets) if not method.startswith("_")]}')
            
            # Check if tweets has a results attribute or is directly iterable
            tweets_to_process = None
            if hasattr(tweets, 'results'):
                tweets_to_process = tweets.results
                if tweets_to_process:
                    print(f'{datetime.now()} - Using tweets.results, found {len(tweets.results)} tweets')
                    consecutive_empty_results = 0  # Reset empty counter
                else:
                    consecutive_empty_results += 1
                    print(f'{datetime.now()} - Empty tweets.results, count: {consecutive_empty_results}/{max_empty_results}')
            elif hasattr(tweets, '__iter__'):
                tweets_to_process = tweets
                print(f'{datetime.now()} - Using tweets directly for iteration')
                consecutive_empty_results = 0  # Reset empty counter
            else:
                print(f'{datetime.now()} - Cannot determine how to iterate over tweets object')
                consecutive_empty_results += 1
                continue

            # Process tweets
            try:
                tweet_batch = []
                
                # Use the determined tweets object
                batch_tweet_count = 0
                if tweets_to_process:
                    # Try regular iteration (most likely case for twikit)
                    for tweet in tweets_to_process:
                        if MINIMUM_TWEETS > 0 and tweet_count >= MINIMUM_TWEETS:
                            break
                            
                        tweet_count += 1
                        batch_tweet_count += 1
                        
                        # Clean tweet text (remove newlines and extra spaces)
                        clean_text = tweet.text.replace('\n', ' ').replace('\r', ' ').strip()
                        
                        tweet_data = [
                            tweet_count,
                            tweet.user.name,
                            clean_text,
                            tweet.created_at,
                            tweet.retweet_count,
                            tweet.favorite_count
                        ]
                        tweet_batch.append(tweet_data)
                        
                        # Write in batches to improve performance
                        if len(tweet_batch) >= 20:  # Larger batches for efficiency
                            with open(csv_filename, 'a', newline='', encoding='utf-8') as file:
                                writer = csv.writer(file)
                                writer.writerows(tweet_batch)
                            tweet_batch = []
                            print(f'{datetime.now()} - Saved batch. Total tweets: {tweet_count}')
                
                # If no tweets were processed in this batch, increment empty counter
                if batch_tweet_count == 0:
                    consecutive_empty_results += 1
                    print(f'{datetime.now()} - No tweets in this batch. Empty count: {consecutive_empty_results}/{max_empty_results}')
                else:
                    consecutive_empty_results = 0  # Reset counter if we got tweets
                            
                # Write remaining tweets
                if tweet_batch:
                    with open(csv_filename, 'a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerows(tweet_batch)

                print(f'{datetime.now()} - Got {tweet_count} tweets so far (batch: {batch_tweet_count})')
                
                # Add delay between batches to avoid rate limiting
                if tweet_count < MINIMUM_TWEETS or MINIMUM_TWEETS == 0:
                    await asyncio.sleep(randint(10, 20))

            except Exception as e:
                print(f'{datetime.now()} - Error processing tweets: {e}')
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(30)
                    continue
                else:
                    break

        print(f'{datetime.now()} - Finished! Total tweets collected: {tweet_count}')

    except KeyboardInterrupt:
        print(f'\n{datetime.now()} - Script interrupted by user')
    except Exception as e:
        print(f'{datetime.now()} - Unexpected error: {e}')
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())