# Documentation

Running the script will give you an instance of the `GroupChat` class. Its attributes are

Name | Description
--- | ---
`master` | List of all messages in the thread, each one stored as a dict with three keys; 'sndr' (string: message sender), 'text' (string: message body), 'time' (datetime object: message send time).
`size` | Int: number of total messages
`users` | A list of the names of all unique users of the chat, as strings
`users_initials` | The initials of the above, useful for more crowded plots
`max_len` | The max length in chars of any of the participants names + 1
`times` | A np.datetime64 array of all message times, much faster than using lists of datetimes
`sorted_master` | The master list sorted by time
`totals` | The total number of messages for each participant
`convos` | List of conversations within the thread, each entry being another list of message dicts belonging to that conversation

Its methods are

# Calculating/Analysing

#### `GroupChat.user_sort()`

Divides the master list up into lists for each individual user.

__returns__ A list of dicts, one for each user

####  `GroupChat.cluster_find(threshold=30.0)`

Clusters messages into conversations based on gaps. Cluster boundaries are placed where the differenence in time between two sequential messages is larger than the chosed threshold. 30 minutes seems to work pretty well for me but it will vary a lot across different group chats.

__returns__ List of clusters, each cluster being a list of message dicts belonging to that cluster

#### `GroupChat.conversation_matrix()`

Calculates the conversation matrix for the whole group chat as follows:
When a user takes parts in a conversation with another user, the matrix entry between those users receives
a point. When all conversations have been added, each row is divided by that user's total messages and normalised by the sum of all that user's points.

__returns__ N by N np.array of values, N is number of participants

#### `GroupChat.time_bins(times_list, bin_size=1)`
Finds the message per `bin_size` (in days) for a list of message times in `times_list`.
___returns___ np.array of datetime coordinates for the bins, number of messages in the bin

#### `GroupChat.word_find(words)`
Finds all of the occurences of at lease one of the strings listed in `words`
___returns___ np.array of datetimes where the word(s) occurred

#### `GroupChat.all()`
Performs all of the built in analysis in one go:
* Total usage over time plot
* Total usage per individual over time plot
* Conversation matrix plot
* Plot of daily activity for whole group
* Plot of daily activity for individuals
* Plot of group activity over a week
* Distribution of message lengths
* Distribution of word lengths per user

# Printing

#### `GroupChat.random(n=5)`
Prints n random messages from the chat

#### `GroupChat.message_string(msg)`
Prints the msg dict in a readable way.

#### `GroupChat.message_rank()`
Prints a table of participants ordered by their total number of messages.

# Plotting
Running any of these methods will save the resulting plot in `plots/`

#### `GroupChat.time_plot(bin_size=1, window=30)`
Plots the whole group's usage over time, with `bin_size` in days and a moving average of size `window`.

#### `GroupChat.time_plot_user(names, bin_size=1, window_30)`
Same as above but plots the activity of individual users whose names are given in the list `list`.

#### `GroupChat.matrix_plot()`
Plots the conversation matrix

#### `GroupChat.word_plot(words, bin_size=30)`
Plots the usage of individual words by the whole group over time. `words` should 
be a list of lists, each sublist representing one word or phrase. For example, to see the usage of things to do with football compared to things to do with nights out you might do:
```python
>>> words = [['football', 'footy'], ['pub', 'bar', 'drinks']]
>>> groupchat.word_plot(words)
```
#### `GroupChat.daily_plot(names=None)`

Plots the activity of the group over the day. Passing names as None will plot the whole group. Passing names as a list of names will plot the activity of those users only.

#### `GroupChat.weekly_plot(window=60)`

Plots a sort of heatmap for the group's activity over a whole week. Smoothed with a moving average of size `window` (in minutes).

#### `GroupChat.message_length_plot()`

Simply plots the distribution of message lengths over the whole chat

#### `Groupchat.word_length_plot()`

Plots the distribution (just mean and std. dev.) of word length for each user.


