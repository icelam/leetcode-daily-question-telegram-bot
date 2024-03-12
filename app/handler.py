"""Lambda function file for sending scheduled message to a connected Telegram chat via Chat ID."""

import os
import requests
import telegram

# AWS Lambda loads handler in a special way so we need to import local modules from 'app'
from app.utils import markdown

LEETCODE_DOMAIN = 'https://leetcode.com'
LEETCODE_ALL_PROBLEM_URL = LEETCODE_DOMAIN + '/problemset/all/'

# Load environment variables
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def get_question_of_today():
    """Fetch today's question from Leetcode's GraphQL API"""

    request = requests.Request(
        'POST',
        LEETCODE_DOMAIN + '/graphql/',
        json={
            'query': """query questionOfToday {
                activeDailyCodingChallengeQuestion {
                    link
                    date
                    question {
                        questionFrontendId
                        title titleSlug
                        content
                        isPaidOnly
                        difficulty
                        topicTags {
                            name
                            slug
                        }
                        stats
                        hints
                    }
                }
            }""",
            'variables': {},
            'operationName': 'questionOfToday',
        },
        headers={
            "authority": "leetcode.com",
        }
    )

    prepped_request = request.prepare()
    session = requests.Session()
    response = session.send(prepped_request)

    try:
        return response.json()
    except ValueError:
        print('Failed to decode JSON, API response:')
        print(response.text)
        raise
    except BaseException as error:
        print(f'Unexpected {error=}, {type(error)=}')
        raise

def send_message(event, context):
    """Lambda function handler to send text message."""

    question_data = get_question_of_today()

    if 'data' in question_data:
        question_info = question_data['data']['activeDailyCodingChallengeQuestion']
        question_id = question_info['question']['questionFrontendId']
        question_title = question_info['question']['title']
        question_url = LEETCODE_DOMAIN + question_info['link']
        question_date = question_info['date']
        question_topic = ', '.join([topic['name'] for topic in question_info['question']['topicTags']])
        question_difficulty = question_info['question']['difficulty']
        question_content = question_info['question']['content']

        message = f'*{question_date}*\n' \
        f'*{question_id}. {question_title}*\n\n' \
        f'*Topic:* {question_topic}\n' \
        f'*Difficulty:* {question_difficulty}\n\n' \
        f'*Problem:*\n{markdown.generate(question_content)}'

        bot = telegram.Bot(token=TOKEN)
        bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            reply_markup=telegram.InlineKeyboardMarkup([
                [telegram.InlineKeyboardButton(text="View on Leetcode", url=question_url)]
            ]),
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    else:
        raise Exception('Invalid API response. No "data" node found in API response.')
