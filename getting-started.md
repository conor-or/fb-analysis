---
layout: default
title: Getting Started
---

With minimal use of the command line you can use all of the features of this code.
This page will briefly explain how to get the data from Facebook, parse it, analyse it, and produce some of
the example plots on the previous page.

For more information on any part, please check out the [documentation](documentation).

___

### 1. Getting Your Data from Facebook

On Facebook, go to your [settings](https://www.facebook.com/settings) and you should
see an option to __"Download a copy of your Facebook data"__. Follow this and click __"Download Archive"__.

Facebook will put together a .zip archive of all your data and email it to you, it can take a little while so check back after 20-30 mins.

In the meantime go back to the Facebook front page and click Messenger on the left hand side. 

![messages](https://github.com/conor-or/fb-analysis/blob/gh-pages/assets/messages.png?raw=true)

Click on the group chat you're interested in and copy the number at the end of the URL.

![url](https://github.com/conor-or/fb-analysis/blob/gh-pages/assets/url.png?raw=true)

You'll need this later to find the group chat within your Facebook data download.

### 2. Getting the Code

__If you have Git installed__ you can run

```bash
$ git clone https://github.com/conor-or/fb-analysis
```

or __if you don't have Git__ you can [click this link](https://github.com/conor-or/fb-analysis/archive/master.zip) to download all the stuff you need.

### 3. Parsing the HTML

The first time you run the code you need to pass it the HTML file to parse. The file you want will be in the `/messages` folder within your Facebook archive. It's named `xxxxxxxxxxxx.html` with the ID number you found earlier. From within the fb-analysis directory run

```bash
$ python main.py /path/to/html/file.html
```
Once this is done a `group_chat.pkl` file is saved in the `input/` directory. This contains only the thread you're interested in and is formatted as a list of dicts, each dict representing a single message. For example it might look like this:
```python
[
  {
   'text': u'What about Saturday night?',
   'sndr': u'Linwood Zook',
   'time': datetime.datetime(2013, 12, 29, 21, 48)
  },
  {
   'text': u"Can't make it lad",
   'sndr': u'Harold Culligan',
   'time': datetime.datetime(2013, 12, 29, 21, 50)
  }
]
```
### 5. Running the Analysis

After this, it's really up to you how you want to analyse your group chat. Once the `.pkl` file is created the program will always read from this by default so to interact with the group chat you can run:
```bash
$ python -i main.py
```
To return the list of dicts of all messages:
```
>>> groupchat.master
```
To print $n$ random messages from the chat:
```
>>> groupchat.random(n)
12/06/16 15:49 Genaro Eggleston   What a shambles
09/11/16 04:15 Diedra Devane      Needs to chill.
26/08/15 11:54 Melissia Dubiel    Is it Euston?
11/12/16 00:39 Mitchell Ashworth  Thought it would be better
04/04/16 21:10 Genaro Eggleston   Yeah in a suit
```
To print the ranking of all participants by message count:
```
>>> groupchat.message_rank()
Linwood Zook       21610  26.00%
Mitchell Ashworth  17929  21.57%
Diedra Devane      13538  16.29%
Genaro Eggleston   10650  12.81%
Erna Claypool      6162   7.41%
Harold Culligan    3914   4.71%
Lester Sneed       3739   4.50%
Melissia Dubiel    2478   2.98%
Wilburn Malbon     1213   1.46%
Maryann Peguero    942    1.13%
Ashanti Sankey     486    0.58%
Evelin Boden       420    0.51%
Hai Cruzan         24     0.03%
Irwin Alm          8      0.01%
```
To run all available plotting features simply do
```
>>> groupchat.all()
```
or run the script initially with
```bash 
$ python -i main.py -all
```
If you're more a fan of doing things through Jupyter/iPython you can run the included notebook to access everything interactively.
```bash
$ jupyter notebook notebook.ipynb
```
___
__For the full list of all features please [check out the documentation](documentation). Enjoy!__
