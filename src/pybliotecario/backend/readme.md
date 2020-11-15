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

Now we need a webhook to comunicate with our app.
For the purposes of this tutorial we will use ngrok so write here something along the lines of `https://123f2134t5.ngrok.io/webhook`.
If you have your own server (with https!) you can use that instead.

To start the process one has to create an app in the [facebook's developer page](https://developers.facebook.com/)
it will have to be associated with a Facebook page (one would talk to the bot through the page messenger).

Once both page and app are created, you will want to add the `messenger` product to it and ensure that in your app
subscription both `messaging` and `messaging_postbacks` are set.

TODO: do a more detailed guide with screenshots and everything
