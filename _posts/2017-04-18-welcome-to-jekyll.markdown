---
layout: post
title:  "Parsing the HTML"
date:   2017-04-18 21:43:23 +0100
categories: html parsing text rawdata
---

The first stage in anything like this is to actually get hold of the data in a way you can use it.

A user's Facebook messages can be accessed through the Graph API and initially I tried some software that did this. Unfortuneately, the system struggled with requests for messages > 5,000 at a time. With over 80,000 messages in the chat I'm interested in this wasn't going to be an option.

Instead I took the long way round and downloaded my [Facebook archive](). After some tinkering with BeautifulSoup, this turned out to provide easy enough access to the messages themselves.
