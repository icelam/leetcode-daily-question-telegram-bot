"""Convert HTML to Telegram markdown syntax"""

import re
from markdownify import MarkdownConverter, BACKSLASH

class TelegramMarkdownConverter(MarkdownConverter):
    """Create a custom MarkdownConverter that fits Telegram markdown format"""

    def convert_img(self, el, text, convert_as_inline):
        src = el.attrs.get('src', None) or ''

        if convert_as_inline:
            return f'(Image: [{src}]({src}))'

        return f'\nImage: [{src}]({src})\n'

    def convert_br(self, el, text, convert_as_inline):
        if convert_as_inline:
            return ""

        if self.options['newline_style'].lower() == BACKSLASH:
            return '\\\n'

        return '\n'

    def convert_p(self, el, text, convert_as_inline):
        if convert_as_inline:
            return text
        return f'{text}\n\n' if text.strip() else ''

    def convert_pre(self, el, text, convert_as_inline):
        if not text:
            return ''
        after_paragraph = False

        if el.previous_sibling and el.previous_sibling.name in ['p']:
            after_paragraph = True

        return ('\n' if not after_paragraph else '') + f"```{self.options['code_language']}\n{text.strip()}\n```\n\n"

    def convert_sub(self, el, text, convert_as_inline):
        return f'_{text}'

    def convert_sup(self, el, text, convert_as_inline):
        return f'^{text}'

def generate(html, **options):
    """Convert function with options predefined"""

    result = TelegramMarkdownConverter(
        **options,
        convert=['br', 'p', 'img', 'code', 'pre', 'ul', 'ol', 'li', 'a', 'sup', 'sub'],
        bullets='•••'
    ).convert(html).strip()

    result = re.sub('\n{2,}', '\n\n', result)

    return result
