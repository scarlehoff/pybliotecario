# Pybliotecario Backends

Using different backend requires usually two things: API Keys and an API.

## Telegram backend
For Telegram the process is quite simple, `pybliotecario` will guide you through the process
of contacting the [botfather](https://t.me/botfather) and getting an API key.
The `--init` option will start the guide.

```
pybliotecario --init
```

## Facebook backend
The facebook backend configuration is a bit more involved, since we need to set up a server that will be communicating with facebook.
This is done in the pybliotecario with `flask`.

The first step is to create an app in the [facebook's developer page](https://developers.facebook.com/).
The process has changed several times in the past, the guide below has been last updated the 6th of April 2022.

There's also a guide on how to [set up a facebook app](https://developers.facebook.com/docs/messenger-platform/getting-started/app-setup)
to use the messenger platform (for which it is necessary also to create a [facebook page](https://www.facebook.com/pages/create)).

The main steps are summarized here in case the guides change address in the future:

1. Find `PRODUCTS` in the app settings and add a new one for `messenger`.
2. Then you need to associate the app you just created with the page. The idea is that this bot will be the bot of the created page.
3. In the `messenger` settings, add the callback URL of the weebhook and enter the verification token. Ensure that the webhook has `messages` and `messaging_postbacks` active as `subscription fields`.

If everything has been done correctly, try to open a conversation with the page you just created!
You should receive the messages in the terminal you opened the pybliotecario before (that's why we used the --debug option!).

#### Adding a chat id
One of the nice features of the pybliotecario is to set up automatic communications with your telegram account.
For telegram there was an automatic fill in for the user id.
Eventually I will do the same for facebook, but since this is a bit more of a niche user, for now it has to be done manually.
Luckily it is quite easy to do, just send a message from the user you want to set as default.
Among the many different fields, there will be the `chat_id` field, which will be a long number.

```config
[FACEBOOK]
app_token = <your token>
verify = SuzumiyaHaruhi
chat_id = <long number you just copied>
```

And you are ready to go!

In order to verify the callback URL we need to have a server active.
`pybliotecario` offers a facility for that, in our `pybliotecario.ini` we can start filling up the `facebook` section with the verification key:

```ini
[FACEBOOK]
verify = SuzumiyaHaruhi
```

And then we can start the facebook backend: `pybliotecario --debug -d -b facebook`.
Now we can add a callback URL. Since facebook requires SSL a very easy option is to use ngrok.io, which will basically create a reverse proxy.
For instance if we are using port 3000 (the default for flask in `pybliotecario`) we can do:

```bash
sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT # or the equivalent in your router
ngrok http <my ip or server>:3000
```

This is already enough to receive messages but at the moment the bot cannot interact with anyone.

4. Create a token (`Generate token`) and copy it to `pybliotecario.ini`

```ini
[FACEBOOK]
app_token = <my very long token>
```

5. In order to interact with people you need to be approved by Facebook. Since the `pybliotecario` is intended for personal usage (and I didn't want to bother with Facebook approval) we just add the users that we want to use the App in `Roles`. To check what our user ID is the easiest thing is to simply send a message to the `pybliotecario --debug` (i.e., with our user in facebook to the message box in the page we created), in the console we should see a field called `chat_id` with a very long number in it. We can copy it and add it to the `.ini` file:

```ini
[FACEBOOK]
app_token = <my very long token>
user_id = 1919191919191919
```

Great! Now we have everything we need.
Test that the messages that you send using the `facebook` backend are indeed arriving to your user in facebook.

```bash
pybliotecario --backend facebook "Hello, again, friend of a friend"
```
