from hamper.interfaces import ChatCommandPlugin, Command
import requests as re
import json
import os

class WikiBot(ChatCommandPlugin):
    name = 'wikibot'

    class TestCommand(Command):
        regex = 'wiki (.*)'

        def command(self, bot, comm, groups):
            they_said = groups[0]
            bot.reply(comm, (self.first_paragraph(they_said, comm)))

        def first_paragraph(self, query, comm):
            r = re.get('https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles='+query)
            p = json.loads(r.text.encode('ascii','ignore'))
            pageid = p['query']['pages'].keys()[0]
            extract = p['query']['pages'][pageid]['extract']
            url = 'https://en.wikipedia.org/wiki/'+query.replace(' ','_')
            try:
                return (comm['user']+': '+extract[:280].replace(os.linesep,'\ ')+'[...] :: URL: '+url)
            except:
                return (comm['user']+': '+extract.replace(os.linesep,'\ ')+' :: URL: '+url)
