from hamper.interfaces import ChatCommandPlugin, Command
import requests
import os


class WikiBot(ChatCommandPlugin):
    name = 'wikibot'
    api_base_url = 'https://en.wikipedia.org/w/api.php'

    def _api_call(self, **kwargs):
        """Make an API call to Wikipedia, and returned the data returned."""
        params = {
            'format': 'json',
        }
        params.update(kwargs)
        r = requests.get(self.api_base_url, params=params)
        return r.json()

    class WikiSummaryCommand(Command):
        regex = 'wiki (.+)'

        def command(self, bot, comm, groups):
            """
            !wiki <query> -> wiki summary of <query>

            Uses wikipedia api to grab the first 250 or so characters of
            `query` article (or lets you know the query is ambigious) and
            appends a clickable url at the end.
            """
            query = groups[0]

            # Generates list of flags and strips out said flags from input
            query, flag_list = self.flags(query)

            if 'help' in flag_list:
                return self.print_helptext()

            # Generates psuedo-slugified url
            url = 'https://en.wikipedia.org/wiki/' + query.replace(' ', '_')

            # Get the article summary
            summary = self.get_article_summary(query)
            if summary is None:
                bot.reply(comm, "{user}: I couldn't find an article for {query}",
                          kwvars={'query': query})
                return

            # Done!
            bot.reply(comm, '{user}: {summary} :: URL: {url}',
                      kwvars={'summary': summary, 'url': url})

        def get_article_summary(self, query):
            """
            Get the summary of an article.

            Returns `None` if wikipedia returns no page for `query`.
            """
            # Generates list of flags and strips out said flags from input
            query, flag_list = self.flags(query)

            if 'help' in flag_list:
                return self.print_helptext()

            page_data = self.plugin._api_call(
                    action='query',
                    redirects=True,    # Include data about article redirects
                    prop='extracts',   # Return an extract of the page.
                    exintro=True,      # Only include the intro (before the first section)
                    explaintext=True,  # "Ex[tracts] plaintext.
                    exchars=250,       # Maximum of about 250 characters (Sometimes longer)
                    titles=query)

            if page_data.get('redirects', None):
                return self.get_article_summary(page_data['redirects'][0]['to'])

            # Pageid is needed to grab the info of a page, it's an api thing
            pageid = page_data['query']['pages'].keys()[0]
            if pageid == -1:
                return None

            # `extract` is the top content of a given wiki page
            summary = page_data['query']['pages'][pageid]['extract']
            summary = summary.replace(os.linesep, ' ')
            return summary

        def flags(self, query):
            """Returns a modified query and list of flags

            Takes a search query and returns a list of flags as well as the
            query stripped of it's query text.
            """
            flag_list = []

            # add the help flag if it is requested
            if '--help' in query:
                flag_list.append('help')
                query = query.replace('--help', '').replace('-h', '')

            # add longprint flag if requested
            if '-long' in query or '-l' in query:
                flag_list.append('long')
                query = query.replace('--long', '').replace('-l', '')

            return query, flag_list

        def print_helptext(self):
            """Returns Wikibot Docstring"""
            helptext = ("Wikibot Plugin ::`--long` -> prints entire summary of a given article "
                        ":: `--help` -> prints out this help text; overrides query "
                        ":: *Please be kind and do not spam the channel <3*")
            return helptext
