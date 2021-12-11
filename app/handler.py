"""Lambda function file for sending scheduled message to a connected Telegram chat via Chat ID."""

import os
import re
import requests
import telegram
from markdownify import markdownify as md

LEETCODE_DOMAIN = 'https://leetcode.com'
LEETCODE_ALL_PROBLEM_URL = LEETCODE_DOMAIN + '/problemset/all/'

# Load environment variables
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def get_question_of_today():
    """Fetch today's question from Leetcode's GraphQL API"""

    client = requests.session()

    # Visit leetcode webpage to retrieve a CSRF token first
    client.get(LEETCODE_ALL_PROBLEM_URL)

    if 'csrftoken' in client.cookies:
        csrftoken = client.cookies['csrftoken']
    else:
        csrftoken = ''

    response = client.post(
        LEETCODE_DOMAIN + '/graphql/',
        data={
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
            'csrfmiddlewaretoken': csrftoken
        },
        headers={
            'referer': LEETCODE_ALL_PROBLEM_URL
        }
    )

    try:
        return response.json()
    except ValueError:
        print("Failed to decode JSON, API response:")
        print(response.text)
        raise
    except BaseException as error:
        print(f"Unexpected {error=}, {type(error)=}")
        raise

def generate_telegram_markdown(content):
    """Convert HTML to Telegram Markdown syntax"""

    formatted_content = content
    # Special handling for superscript and subscript since standard markdown does not support them
    formatted_content = re.sub('<sup>', '<sup>^', formatted_content)
    formatted_content = re.sub('<sub>', '<sub>_', formatted_content)
    # Convert allowed tags to markdown
    # Note that supported markdown syntax is different in Telegram
    # https://core.telegram.org/bots/api#formatting-options
    formatted_content = md(formatted_content, convert=['p', 'img', 'code', 'pre'])
    # Replace multiple empty lines
    formatted_content = re.sub('(\s+)?\n{2,}', '\n\n', formatted_content)
    # Special handling for images
    formatted_content = re.sub('\!\[(.+)?\]\((.+)\)', r'image: \2', formatted_content)

    return formatted_content.strip()

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


        message = f"*{question_date}*\n" \
        f"*{question_id}. {question_title}*\n\n" \
        f"*Topic:* {question_topic}\n" \
        f"*Difficulty:* {question_difficulty}\n\n" \
        f"*Problem:*\n{generate_telegram_markdown(question_content)}"

        bot = telegram.Bot(token=TOKEN)
        bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            reply_markup=telegram.InlineKeyboardMarkup([
                [telegram.InlineKeyboardButton(text="View on Leetcode", url=question_url)]
            ]),
            parse_mode='Markdown'
        )
    else:
        raise Exception('Invalid API response. No "data" node found in API response.')
