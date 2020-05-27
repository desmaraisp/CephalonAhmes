# CephalonAhmes
Heroku-hosted bot used to scrape update notes from the warframe forums and post them to the warframe subreddit

What it does:

- It goes to this website: https://forums.warframe.com/forum/3-pc-update-notes/ and finds the url of the latest update notes post using html navigation.

- To make sure not to post duplicates, it compares said url to a url stored in a text file on an Amazon s3 cloud. That "other" url is the url of the previous last post that the script has reposted

- If the urls differ, we have a new post! And so we open the new post and rip out the text (and the title)

- We translate said text to markdown, and do some additional manipulations to fix a few specific formatting issues, since the translation program isn't perfect.

- We then post the translated text to https://www.reddit.com/r/Warframe/ with the "News" flair while making sure not to forget the post size limit (we may need to break it down in multiple parts if it exceeds 40 000 characters)

- We then do it all over again forever

How to make it work on your machine:

- You'll first need to have a reddit account. From that account, go to here: https://www.reddit.com/prefs/apps/ and create an app. Select the "script" option, put anything in the redirect uri (in my case, http://localhost:8080) and click create. You then need to take note of the secret key, and the client id key, which is just below the app name and "personal use script".

- You then need to set your username, your password, your client id key and your secret id key as environment variables

- Create a text file on your amazon s3 bucket and get the two access keys. Just like previously, set those as environment variables. The file location should be like this: "Bucket_name/file_name.txt", also an env variable

- You need to have chrome installed. The chromedriver (for selenium) is included in the repository, but you might want to update it if needs be to have the same version as your chrome.

How to make it work on your heroku app:

- You have to set all the previous environment variables in you heroku env variables tab (under settings). So that's all 4 reddit authetication variables, 2 aws authentication keys and 1 aws file path.

- You need to make sure all the modules you use are in the requirements file, with the corresponding version. pip freeze might help you get this

- The runtime file has your python version

- The procfile contains your instructions to heroku, as far as I understand it. You just have to list the heroku dyno type you want, your language and the file you want to run.

- You now have to go under settings in your heroku app and add some buildpacks. You need the python buildpack if it's not there already, then you need to add https://github.com/heroku/heroku-buildpack-google-chrome and https://github.com/heroku/heroku-buildpack-chromedriver. These two are here for the selenium browser, if you don't use it, no need to include them.

- Finally, go under resources and toggle your dyno on, but make sure it's set to free hours


Special notes:

- The warframe forum has an odd behavior with refresh, I iitally used request to get the post url, but the website would not refresh the data when refreshed or when responding to a new request. I had to use selenium to do a few manipulations on the site to for it to refresh the data because actual clicking on the website's sorting menu could force the refresh. If whatever you want to scrape doesn't have this sort of behavior, you could totally remove everything selenium-related and just use requests.

- Some of the scraping logic, the posting subreddit and all the html navigation on the forum are hard-coded, so the code needs some manipulations if you want it to apply to another site.

- An easy way to get an amazon s3 cloud with the associated keys if you don't already have an account would be to add the cloud-cube add-on on heroku (under resources), then all you have to do is click on the add-on to see your bucket. The keys are in the settings, top-right corner.
