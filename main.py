import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.dates import date2num
from datetime import datetime
from tools.parse import thread_parse
from pickle import load
from random import randint
from itertools import permutations
from mpl_toolkits.axes_grid1 import make_axes_locatable
plt.style.use('ggplot')
rcParams['figure.figsize'] = (13, 8)
rcParams['font.family'] = 'monospace'


class GroupChat:

    def __init__(self, master_list):

        # Holds the master list of messages
        self.master = master_list
        self.size = len(master_list)

        # Get the unique users in this groupchat
        self.users = list(set([m['sndr'] for m in master_list]))

        # Get their initials
        self.users_initials = [''.join(map(lambda x: x[0],
                               u.split(' '))) for u in self.users]

        # Sort messages per user
        self.user_bins = self.user_sort()

        # Find max length of user names
        self.max_len = max(len(p) for p in self.users) + 1

        # np.array of message times for easier manipulation
        self.times = np.array([m['time'] for m in self.master],
                              dtype='datetime64[m]')

        # Sort the master list
        self.sorted_master = self.message_sort(self.master)

        # Get total messages of each user
        self.totals = [float(len(self.user_bins[i]['msgs']))
                       for i in range(len(self.users))]

        # Cluster into conversations
        self.convos = self.cluster_find()

    def user_sort(self):
        """
        Sorts the master lists into individual lists
        for each user
        """

        usr_bins = [
            {'Name': n, 'msgs': [], 'texts': [],
             'dates': [], 'bins': []} for n in self.users
        ]

        for m in self.master:
            for u in usr_bins:
                if m['sndr'] == u['Name']:
                    u['msgs'].append(m)
                    u['texts'].append(m['text'])
                    u['dates'].append(m['time'])

        return usr_bins

    def cluster_find(self, threshold=30.0):
        """
        Clusters messages into conversations based on gaps.
        Cluster boundaries are placed where the differenence
        in time between two sequential messages is larger than
        the chosed threshold. 30 minutes seems to work pretty well
        but it vary in more extreme group chats.
        """
        cluster_ix, j = [0], 0

        # Loop over messages
        for i in range(1, len(self.sorted_master)):

            # If time since last message is greater than
            # the threshold, start a new cluster
            td = (self.sorted_master[i]['time'] -
                  self.sorted_master[i - 1]['time'])

            if td.total_seconds() / 60.0 > threshold:
                j += 1
            cluster_ix.append(j)

        # Store each cluster's messages in a dict
        clusters = [{'msgs': []} for i in range(max(cluster_ix) + 1)]
        for i, m in enumerate(self.sorted_master):
            clusters[cluster_ix[i]]['msgs'].append(m)

        return clusters

    def conversation_matrix(self):
        """
        Calculates the conversation matrix for the whole
        group chat as follows:
        When a user takes parts in a conversation with
        another user, the matrix entry between those users receives
        a point. When all conversations have been added, each row is divided
        by that user's total messages and normalised by the sum of all
        that user's points.
        """

        # Storage
        convo_matrix = np.zeros(shape=(len(self.users),
                                       len(self.users)))

        # Loop over conversations
        for convo in self.convos:

            # Get the indices of all convo. members
            members = list(set([c['sndr'] for c in convo['msgs']]))
            ids = [self.users.index(m) for m in members]

            # Get all the permutations of users in the convo.
            if len(ids) > 1:
                perms = np.array(list(permutations(ids, 2)))

                # Add points to those permutations
                convo_matrix[perms[:, 0], perms[:, 1]] += 1.0

        # Normalise
        for i in range(len(self.users)):
            convo_matrix[i, :] /= (self.totals[i])
            convo_matrix[i, :] /= (convo_matrix[i, :].sum()) / 100.0

        return convo_matrix

    @staticmethod
    def message_sort(msgs, reverse=False):
        """
        Sorts a list of messages by time (oldest first)
        """
        mtimes = np.array([m['time'] for m in msgs],
                          dtype='datetime64[m]')

        return [y for (x, y) in sorted(zip(mtimes, msgs),
                                       reverse=reverse)]

    def random(self, n=5):
        """
        Prints five random messages from the group chat 
        """
        ix = [randint(0, len(self.master)) for _ in range(n)]
        for i in ix:
            print self.message_string(self.master[i])

    def message_string(self, msg):
        return (
            '{date} {name:{width}} {text}'.format(
                name=msg['sndr'], width=self.max_len,
                date=msg['time'].strftime('%d/%m/%y %H:%M'),
                text=msg['text'].encode('utf-8'))
        )

    def message_rank(self):
        """
        Prints the total message counts for each user
        """
        counts = [len(u['msgs']) for u in self.user_bins]
        ranked_users = sorted(self.users, key=dict(zip(self.users, counts)).get, reverse=True)
        ranked_counts = sorted(counts, reverse=True)
        percentiles = map(lambda x: 100.0 * x / len(self.master), ranked_counts)

        for x, y, p in zip(ranked_users, ranked_counts, percentiles):
            print '{name:{width}} {counts:<6} {perc:.2f}%'.format(
                name=x, width=self.max_len, counts=y, perc=p)

    def time_bins(self, times_list, bin_size=1):
        """
        Finds the messages per bin_size (in days) over
        the whole group chat
        """

        all_days = np.array(self.times - self.times.min(), dtype='timedelta64[D]').astype('int')
        days = (times_list - self.times.min()).astype('timedelta64[D]').astype('int')
        bins = np.histogram(days, range(1, all_days.max() + 3, bin_size))[0]
        time = np.arange(self.times.min(), self.times.max(),
                         bin_size, dtype='datetime64[D]')

        if len(time) != len(bins):
            return time, bins[:len(time)]
        else:
            return time, bins

    def time_plot(self, bin_size=1, window=30):

        print 'Plotting total group activity with time'
        timex, timey = self.time_bins(self.times, bin_size)

        # Create moving average
        avg = np.convolve(timey, np.ones((window,)) / float(window), mode='same')

        # Plot
        fig, ax = plt.subplots()
        ax.plot(timex.astype(datetime), timey[:len(timex)] / bin_size, color='C0', alpha=0.1)
        ax.plot(timex.astype(datetime), avg / bin_size, color='C0')
        ax.set_xlabel('Date')
        ax.set_ylabel('Avg. Messages per Day')
        ax.set_ylim([0, np.max(avg / bin_size) * 1.1])

        fig.tight_layout()
        fig = self.fig_watermark(fig, 'All-User Lifetime Activity')
        fig.savefig('./plots/all-user_lifetime_activity.png')

    def time_plot_user(self, names, bin_size=1, window=30):

        print 'Plotting individual activity with time'
        data = []
        # Get data to be plotted
        for name in names:
            for user in self.user_bins:
                if user['Name'] == name:
                    data.append(self.time_bins(
                        np.array(user['dates'], dtype='datetime64[m]')
                    ))

        # Plot
        fig, ax = plt.subplots()
        for i in range(len(names)):
            avg = np.convolve(data[i][1], np.ones((window,)) / window, mode='same')
            ax.plot(data[i][0].astype(datetime), avg / bin_size, label=names[i])
        ax.legend()
        ax.set_xlabel('Date')
        ax.set_ylabel('Avg. Messages per Day')

        fig.tight_layout()
        fig = self.fig_watermark(fig, '%d User Lifetime Activity' % len(names))
        file_string = '_'.join(map(lambda x: x.replace(' ', '_'), names))
        fig.savefig('./plots/%s_lifetime_activity.png' % file_string)

    def matrix_plot(self):

        print 'Plotting conversation matrix'
        convo_matrix = self.conversation_matrix()

        fig, ax = plt.subplots()
        imax = ax.imshow(convo_matrix, interpolation='none')
        ax.grid(False)
        ax.set_xticks(range(0, 14))
        ax.set_xticklabels(self.users_initials, rotation=90.0)
        ax.set_yticks(range(0, 14))
        ax.set_yticklabels(self.users_initials)
        ax.set_xlabel('Person $X$')
        ax.set_ylabel('Person $Y$')
        for i in range(len(self.users)):
            for j in range(len(self.users)):
                ax.text(i, j, '%.0f' % convo_matrix[j, i],
                        color='w', va='center', ha='center')
        divider = make_axes_locatable(ax)
        cax1 = divider.append_axes("right", size="3%", pad=0.5)
        cbar = plt.colorbar(imax, cax=cax1)
        cbar.set_label("Amount of $Y$'s Conversation Which is Shared With $X$ (%)",
                       labelpad=10.0)
        fig.set_size_inches(10, 10)
        fig.tight_layout()
        fig = self.fig_watermark(fig, 'Conversation Matrix')
        fig.savefig('./plots/Conversation_Matrix_All_User.png')

    def word_print(self, words):
        """
        Prints all the occurences of the words in
        [words] from the chat
        """
        for msg in self.master:
            if any(x in msg['text'] for x in words):
                print self.message_string(msg)

    def word_find(self, words):
        """
        Finds all the occurences in time of the words in [words]
        """
        times = []
        for msg in self.master:
            if any(x in msg['text'] for x in words):
                times.append(msg['time'])
        return np.array(times, dtype='datetime64[m]')

    def word_plot(self, words, bin_size=30):
        """
        Plots the occurrence rate of words over time, given as a list of lists
        where each sublist is all the possible spellings of that word.
        Or use for general categories grouped together. Each sublist
        is used as one line in the plot.
        """

        fig, ax = plt.subplots()
        full_string = ','.join([','.join(w) for w in words]).replace(' ', '')

        # Loop over groups of words
        for w in words:
            tl = self.word_find(w)
            tb = self.time_bins(tl, bin_size=bin_size)
            t0 = self.time_bins(self.times, bin_size=bin_size)
            ax.plot(tb[0].astype(datetime), 100.0 * tb[1].astype(float) / t0[1].astype(float),
                    label=','.join(w).replace(' ', ''))

        ax.legend()
        ax.set_xlabel('Date')
        ax.set_ylabel('Occurrence Rate per %d Days (%%)' % bin_size)

        fig.tight_layout()
        fig = self.fig_watermark(fig, 'Usage for %s' % full_string)
        fig.savefig('./plots/Word_Usage_%s.png' % full_string)

    def daily_plot(self, names=None, window=60):
        """
        Plots activity per-user or per-whole group over 1 min bins
        across the whole day, uses a moving average of size window
        """

        print 'Plotting group daily activity'

        fig, ax = plt.subplots()
        x = np.linspace(0.0, 24.0, 1440)

        # If names are given, plot the individuals, otherwise
        # plot the whole group
        if names:
            data = []

            # Get data to be plotted
            for name in names:
                for user in self.user_bins:
                    if user['Name'] == name:
                        data.append(np.array(user['dates'],
                                             dtype='datetime64[m]'))
            for i, name in enumerate(names):
                d = self.daily_bins(data[i])
                ax.plot(x, moving_average(d, window), label=name, )
                ax.legend()
            title = '%d-User Daily Activity' % len(names)
        else:
            ax.plot(x, self.daily_bins(self.times), color='k', alpha=0.1)
            ax.plot(x, moving_average(self.daily_bins(self.times), window))
            title = 'All-User Daily Activity'

        ax.set_ylabel('Messages per minute')
        ax.set_xticks(np.linspace(0.0, 24.0, 25))
        ax.set_xlabel('Hour of Day')

        fig.tight_layout()
        fig = self.fig_watermark(fig, title)
        fig.savefig('./plots/%s.png' % title)

    def weekly_plot(self, window=60):
        """
        Plots the activity over the whole over the week
        with a moving average of size window
        """

        print 'Plotting weekly activity'

        d = self.daily_bins(self.times, weekday=True)
        avg = []
        for i in range(7):
            avg.append(moving_average(d[i, :], 60))
        avg = np.array(avg)

        fig, ax = plt.subplots()
        imax = ax.imshow(avg, extent=[0, 24, 0, 0.6 * 24], origin='lower')

        ax.set_yticks(np.linspace(1.0, 0.6 * 24 - 1.0, 7))
        ax.set_xticks(np.linspace(0.0, 24.0, 25))

        ax.set_ylabel('Day of Week')
        ax.set_xlabel('Hour of Day')
        ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])

        ax.grid(False)
        divider = make_axes_locatable(ax)
        cax1 = divider.append_axes("right", size="3%", pad=0.5)
        cbar = plt.colorbar(imax, cax=cax1)

        cbar.set_label("Messages per Minute",
                       labelpad=10.0)
        fig.tight_layout()
        fig = self.fig_watermark(fig, 'Weekly Activity')
        fig.savefig('./plots/Group_Daily_Weekly_Activity.png')

    def message_length_plot(self):

        print 'Plotting Message Lengths'

        fig, ax = plt.subplots()

        length_dist = np.array([len(msg['text'].split(' ')) for msg in self.master])
        dist = ax.hist(length_dist, bins=np.linspace(1, 50, 50))
        ax.text(50, dist[0].max() * 0.9, 'Mean Length = %.2f Words' % length_dist.mean(),
                size=20, ha='right')
        ax.set_xlabel('Message Length (Words)')
        ax.set_ylabel('Frequency')
        fig.tight_layout()
        fig = groupchat.fig_watermark(fig, 'Message Length')
        fig.savefig('./plots/Message_Length')

    def word_length_plot(self):
        """
        Plots the distribution of word lengths for all users
        """

        print 'Plotting Word Length Distributions'

        char_dist = []

        for i in range(len(self.users)):
            c = [[len(w) for w in msg.split(' ')] for msg in self.user_bins[i]['texts']]
            char_dist.append(np.array([x for y in c for x in y]))
        means = np.array([c.mean() for c in char_dist])
        percs = np.array([c.std() for c in char_dist])

        c = [[len(w) for w in msg['text'].split(' ')] for msg in self.master]
        c = np.array([x for y in c for x in y])

        fig, ax = plt.subplots()
        ax.axvline(c.mean(), linestyle='--', color='k', alpha=0.5)
        ax.errorbar(means, range(1, len(groupchat.users) + 1), xerr=percs, marker='o', linestyle='none',
                    capsize=5.0)
        ax.set_xlim([-1, 10])
        ax.set_yticks(range(1, len(groupchat.users) + 1))
        ax.set_yticklabels(groupchat.users)
        ax.set_xlim([0.0, 15])
        ax.set_xlabel('Word Length (chars)')
        fig.tight_layout()
        fig = groupchat.fig_watermark(fig, 'User Word Length Distribution')
        fig.savefig('./plots/All_User_Word_Length_Distribution.png')

    def all(self):
        """
        The interactive equivalent of running the script with the
        -all flag.
        """
        print 'Performing all analysis...'
        self.time_plot()
        self.time_plot_user(groupchat.users)
        self.matrix_plot()
        self.daily_plot()
        self.daily_plot(names=groupchat.users)
        self.weekly_plot()
        self.message_length_plot()
        self.word_length_plot()

    @staticmethod
    def daily_bins(times, weekday=False):
        """
        Bins a list of messages over the day/week in 1 minute bins.
        """

        if weekday:
            bins = np.zeros((7, 1440))
            for t in times:
                ix = (t.astype(datetime).hour * 60) + t.astype(datetime).minute
                bins[t.astype(datetime).weekday(), ix] += 1
        else:
            bins = np.zeros(1440)
            for t in times:
                ix = (t.astype(datetime).hour * 60) + t.astype(datetime).minute
                bins[ix] += 1
        return bins / (1440.0)

    @staticmethod
    def fig_watermark(fig, title):
        """
        Adds a watermark and title to every plot
        """
        fig.subplots_adjust(top=0.9)
        x = fig.axes[0].get_position().x0
        w = fig.axes[0].get_position().width
        y = 0.92
        fig.text(x, y, title, family='serif', size=18)
        fig.text(x + w, y, "github.com/conor-or/fb-analysis\nConor O'Riordan 2017",
                 family='serif', size=10, ha='right', alpha=0.4)
        return fig

    @staticmethod
    def help():
        print """
    The messages and all the analysis tools are handled
    by the groupchat object. The full list of
    messages is in groupchat.master.
    
    Each message in the master list is a dict with three
    keys:
    ['sndr']    A string with the sender's name
    ['time']    A datetime object for the message's sent time
    ['text']    The actual message body
    
    Below are most of the included methods which you can use
    to analyse the chat. All outputs are saved in ./plots/

    * groupchat.random(n=5)
        Prints n randomly chosen messages from the chat
        
    * groupchat.message_rank()
        Prints every user's total message count in order
         
    * groupchat.time_plot_user(names)
        Same as above but plots individual activity for
        any of the names passed in {names} (must be a list)
        
    * groupchat.word_use([words])
        Plots the use of specific words in the provided
        list over time.
    """


def messages_load():
    """
    Loads the messages file or calls the parsing function
    to create it
    """

    # Check to see if pickled messages are already there
    if not os.path.exists('./input/group_chat.pkl') \
            or '-force' in sys.argv:
        # Create it if not
        print 'No pkl file found, parsing HTML...'
        thread_parse(sys.argv[1])

    else:
        print 'File found, loading messages...'

    # Load messages dicts
    with open('./input/group_chat.pkl', 'r') as f:
        return GroupChat(load(f))


def moving_average(data, window):
    """
    Simple circular moving average
    """

    dd = np.concatenate((data, data))

    return np.convolve(np.ones(window) / float(window), dd)[window: len(data) + window]


if __name__ == '__main__':
    print """
    Facebook Group Chat Analysis
    Conor O'Riordan
    Apr 2017
    
    Check the README at github.com/conor-or/fb-analysis or
    type groupchat.help() to see what you can do.
    """

    groupchat = messages_load()

    if '-all' in sys.argv:
        print 'Performing all analysis...'
        groupchat.time_plot()
        groupchat.time_plot_user(groupchat.users)
        groupchat.matrix_plot()
        groupchat.daily_plot()
        groupchat.daily_plot(names=groupchat.users)
        groupchat.weekly_plot()
        groupchat.message_length_plot()
        groupchat.word_length_plot()
