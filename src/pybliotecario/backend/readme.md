# Pybliotecario Backends

There are some subtleties involved when implementing new backends.
The main thing to take into account is that a new backend will require new API keys
and, often, new ways to communicate with the remote server.

For Telegram the process is quite simple and this program will guide you through the process
of contacting the [botfather](https://t.me/botfather) and getting an API key.
For Facebook instead the process is mre invovled.

## Facebook backend

To start the process one has two create an app in the [facebook's developer page](https://developers.facebook.com/)
it will have to be associated with a Facebook page (one would talk to the bot through the page messenger).

Once both page and app are created, you will want to add the `messenger` product to it and ensure that in your app
subscription both `messaging` and `messaging_postbacks` are set.

TODO: do a more detailed guide with screenshots and everything
