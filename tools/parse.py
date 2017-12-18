from sys import argv
from bs4 import BeautifulSoup
from datetime import datetime as dt
from pickle import dump


class Thread:
    """
    Parses and organises data per thread
    """

    def __init__(self, s, ns, ids):

        # Get participants of this thread
        self.users = s.contents[0].split(', ')

        # Get message senders
        self.sndrs = [m.text for m in s.findAll('span', {'class', 'user'})]

        # Replace the FBID with the name
        for i, sender in enumerate(self.sndrs):
            if sender.split('@')[0] in ids:
                self.sndrs[i] = ns[ids.index(sender.split('@')[0])]

        # Same again for the participants
        for i, partic in enumerate(self.users):
            if partic.split('@')[0] in ids:
                self.users[i] = ns[ids.index(partic.split('@')[0])]

        # Get message times
        self.times = [date(d.text) for d in s.findAll('span', {'class', 'meta'})]

        # Get message bodies
        self.texts = [t.text for t in s.findAll('p')]


def date(x):
    """
    Converts Facebook date strings to datetime objects
    """
    return dt.strptime(x.split(' UTC')[0], '%A, %B %d, %Y at %I:%M%p %Z')


def thread_parse(file_path):
    """
    Parses message data from a HTML file containing one thread.
    """

    # Open and import file
    with open(file_path) as f:
        print 'Found file %s' % file_path.split('/')[-1]
        html = f.read()

    # Create a BS object
    print 'Parsing HTML (may take a while)...'
    soup = BeautifulSoup(html, 'lxml')

    # Collect the thread object from the HTML
    thread = soup.findAll('div', {'class': 'thread'})[0]

    # Collect all the paragraph text, these are the message bodies
    texts = [m.text for m in thread.findAll('p')]

    print 'Found %d messages in this thread' % len(texts)

    # Collect the message objects from the thread
    messages = thread.findAll('div', {'class': 'message'})

    # Get the message headers
    headers = [m.findNext('div', {'class': 'message_header'}) for m in messages]

    # Get the sender from the message headers
    users = [h.findNext('span', {'class': 'user'}).text for h in headers]

    # Get the times from the message headers and conver to datetime
    times = [date(h.findNext('span', {'class': 'meta'}).text) for h in headers]

    # Create a list of dicts for all messages
    print 'Saving pickled list of messages at /input/messages.pkl'
    master = [{'sndr': users[i],
               'time': times[i],
               'text': texts[i]}
              for i in range(len(texts))]

    # Pickle the messages
    with open('./input/group_chat.pkl', 'w') as f:
        dump(master, f)

    return master


if __name__ == '__main__':

    # If ran independently, takes the HTML file path as input
    thread_parse(argv[1])
