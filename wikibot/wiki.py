from hamper.interfaces import ChatCommandPlugin, Command
import requests as re
import json
import os

class WikiBot(ChatCommandPlugin):
    name = 'wikibot'

    class TestCommand(Command):
        regex = 'wiki (.+)'

        def command(self, bot, comm, groups):
            """
            !wiki <query> -> wiki summary of <query>
            """
            query = groups[0]
            bot.reply(comm, (self.summary(query, comm)))


        def summary(self, query, comm):
            """Returns wikipedia summary of <query>

            Uses wikipedia api to grab the first <280 characters of <query>
            article (or lets you know the query is ambigious) and appends a
            clickable url at the end.
            """
            # Generates list of flags and strips out said flags from input
            query, flag_list = self.flags(query)

            if 'help' in flag_list:
                return self.print_helptext()

            # Makes the api call
            r = re.get('https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles='+query)

            # Loads r.text into an object
            p = json.loads(r.text)

            # Pageid is needed to grab the info of a page, it's an api thing
            pageid = p['query']['pages'].keys()[0]
            if pageid == '-1':
                return (comm['user']+": I couldn't find an article for "+query)

            # Extract is the top content of a given wiki page
            extract = p['query']['pages'][pageid]['extract']

            # Generates psuedo-slugified url
            url = 'https://en.wikipedia.org/wiki/'+query.replace(' ','_')

            # If the article introduction is longer than 280 charcters it
            # shortens it so you don't get wikibot spam
            if 'long' in flag_list:
                return (comm['user']+': '+extract.replace(os.linesep,'\ ')+'[...] :: URL: '+url)
            else:
                return (comm['user']+': '+extract[:280].replace(os.linesep,'\ ')+'[...] :: URL: '+url)


        def flags(self, query):
            """Returns a modified query and list of flags

            Takes a search query and returns a list of flags as well as the
            query stripped of it's query text.
            """
            flag_list = []

            # add the help flag if it is requested
            if '--help' in query :
                flag_list.append('help')
                query = query.replace('--help','').replace('-h','')
                
            # add longprint flag if requested
            if '-long' in query or '-l' in query:
                flag_list.append('long')
                query = query.replace('--long','').replace('-l','')

            return query, flag_list


        def print_helptext(self):
            """Reutrns Wikibot Docstring"""
            helptext = "Wikibot Plugin ::`--long` -> prints entire summary of a given article :: `--help` -> prints out this help text; overrides query :: *Please be kind and do not spam the channel <3*"
            return helptext
