# CephalonAhmes
Heroku-hosted bot used to scrape update notes from the warframe forums and post them to the warframe subreddit

What it does:

- It goes to this website: https://forums.warframe.com/forum/3-pc-update-notes/ and finds the url of the latest update notes post using html navigation.

- To make sure not to post duplicates, it compares said url to a url stored in a text file on an Amazon s3 cloud. That "other" url is the url of the previous last post that the script has reposted

- If the urls differ, we have a new post! And so we open the new post and rip out the text (and the title)

- We translate said text to markdown, and do some additional manipulations to fix a few specific formatting issues, since the translation program isn't perfect.

- We then post the translated text to https://www.reddit.com/r/Warframe/ with the "News" flair while making sure not to forget the post size limit (we may need to break it down in multiple parts if it exceeds 40 000 characters)

- We then do it all over again forever
