from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
from telegram.utils.helpers import escape_markdown

from components import taghints
from rules_bot import article, fuzzy_replacements_markdown
from search import search, WIKI_URL


def hint_article(msg, reply_markup, key):
    return InlineQueryResultArticle(
        id=key,
        title='Send hint on {}'.format(key.capitalize()),
        input_message_content=InputTextMessageContent(
            message_text=msg,
            parse_mode="Markdown",
            disable_web_page_preview=True
        ),
        reply_markup=reply_markup
    )


def inline_query(bot, update, threshold=20):
    query = update.inline_query.query
    results_list = list()

    if len(query) > 0:

        msg, reply_markup, key = taghints.get_hint_data(query)
        if msg is not None:
            results_list.append(hint_article(msg, reply_markup, key))

        modified, replaced = fuzzy_replacements_markdown(query, official_api_links=True)
        if modified:
            results_list.append(article(
                title="Replace links and show official Bot API documentation",
                description=', '.join(modified),
                message_text=replaced))

        modified, replaced = fuzzy_replacements_markdown(query, official_api_links=False)
        if modified:
            results_list.append(article(
                title="Replace links",
                description=', '.join(modified),
                message_text=replaced))

        wiki_pages = search.wiki(query, amount=4, threshold=threshold)
        doc = search.docs(query, threshold=threshold)

        if doc:
            text = f'*{doc.short_name}*\n' \
                   f'_python-telegram-bot_ documentation for this {doc.type}:\n' \
                   f'[{doc.full_name}]({doc.url})'
            if doc.tg_name:
                text += f'\n\nThe official documentation has more info about [{doc.tg_name}]({doc.tg_url}).'

            results_list.append(article(
                title=f'{doc.full_name}',
                description="python-telegram-bot documentation",
                message_text=text,
            ))

        # Limit number of search results to maximum
        wiki_pages = wiki_pages[:50 - len(results_list)]

        if wiki_pages:
            for wiki_page in wiki_pages:
                results_list.append(article(
                    title=f'{wiki_page[0]}',
                    description="Github wiki for python-telegram-bot",
                    message_text=f'Wiki of _python-telegram-bot_\n'
                                 f'[{wiki_page[0]}]({wiki_page[1]})'
                ))

        # "No results" entry
        if len(results_list) == 0:
            results_list.append(article(
                title='❌ No results.',
                description='',
                message_text=f'[GitHub wiki]({WIKI_URL}) of _python-telegram-bot_',
            ))

    else:  # no query input
        # add all wiki pages
        for name, link in search._wiki.items():
            results_list.append(article(
                title=name,
                description='Wiki of python-telegram-bot',
                message_text=f'Wiki of _python-telegram-bot_\n'
                             f'[{escape_markdown(name)}]({link})',
            ))

    bot.answerInlineQuery(update.inline_query.id, results=results_list, switch_pm_text='Help',
                          switch_pm_parameter='inline-help')


def register(dispatcher):
    dispatcher.add_handler(InlineQueryHandler(inline_query))
