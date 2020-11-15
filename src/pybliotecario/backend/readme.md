# Pybliotecario Backends

There are some subtleties involved when implementing new backends.
The main thing to take into account is that a new backend will require new API keys
and, often, new ways to communicate with the remote server.

## Telegram backend
For Telegram the process is quite simple and this program will guide you through the process
of contacting the [botfather](https://t.me/botfather) and getting an API key.
For Facebook instead the process is mre invovled.

## Facebook backend
The first step is to create an app in the [facebook's developer page](https://developers.facebook.com/),
for this example we can create an app called `pybliotec_libro`.
At the time of writting (13/11/2020) one has to log in, go to `My Apps` and click on `Create App`.
Choose `Manage Business integration` (it includes the messaging API) and fill in the details.

In the dashboard of the app you just cread, you need to set up the messenger API.
And here's where things start to get fun.
First you will need to either create a Facebook Page to associate the bot with or associate one you already created.
Once this association is performed you will have to create a Token and add a callback URL for your App.
For the Token just generate it and make sure you copy it somewhere safe. We will use this later.

Before continuing we need to set up the server for our app (since we need to verify the callback URL when we set it up).
Since the server needs to communicate with Facebook through a SSL-secured connection, a good option for this is [ngrok](https://ngrok.com/).
Since the default pybliotecario setup for facebook is set up to the port 3000, ensure it is accessible from outside
(for instance `iptables -A INPUT -p tcp --dport 3000  -j ACCEPT`) and then fire up `ngrok` and the pybliotecario.

```bash
ngrok http <my ip or server>:3000
pybliotecario --debug -d -b facebook
```

Now paste the app TOKEN you generated previously in the `pybliotecario.ini` and make up a verification token (I'll use `SuzumiyaHaruhi`):
```config
[FACEBOOK]
app_token = <your token>
verify = SuzumiyaHaruhi
```

Now go back to the the point we were in the Facebook Developer page and add a new callback url, `Add Callback URL`.
You will need to fill in two fields, `Callback URL` should be the https address provided by ngrok followed by webhook:
for instance `https://123f2134t5.ngrok.io/webhook`.
`Verify Token` should be `SuzumiyaHaruhi`.

If everything is done correctly, the webhook should now be validated.
Only one step is left to start using it.
In the webhook you just created, now there is the `Add Subscriptions` buttons,
ensure that both `messages` and `messaging_postbacks` are ticked.

If everything has been done correctoy, try to open a conversation with the page you just created!
You should receive the messages in the terminal you opened the pybliotecario before (that's why we used the --debug option!).

#### Adding a chat id
One of the nice features of the pybliotecario is to set up automatic communications with your telegram account.
For telegram there was an automatic fill in for the user id.
Eventually I will do the same for facebook, but since this is a bit more of a niche user, for now it has to be done manually.
Luckily it quite easy to do, just send a message from the user you want to set as default.
Among the many different fields, there will be the `chat_id` field, which will be a long number.

```config
[FACEBOOK]
app_token = <your token>
verify = SuzumiyaHaruhi
chat_id = <long number you just copied>
```

And you are ready to go!
