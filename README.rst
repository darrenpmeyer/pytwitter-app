pytwitter-app
=============

A Twitter library for accessing Twitter API endpoints that use Application-Only authentication

About
-----

Certain Twitter endpoints--such as search--permit Twitter clients to authenticate in "Application-Only mode". In this
mode, clients are not associated with a particular user (which means you don't have to deal with the OAuth handshake!)
and rate limits are increasted.

See https://dev.twitter.com/oauth/application-only for details.

.. code-block:: python

    client = TwitterConnection(consumer_key=twitter_consumer_key, consumer_secret=twitter_consumer_secret)

    try:
        client.bearer_token()

        results = client.search('Python', result_type='recent')
        for tweet in results['statuses']:
            print("{}: {}".format(tweet['user']['screen_name'], tweet['text']))
    except TwitterAuthException as e:
        print("Unable to authenticate to Twitter. Details: {}".format(e))
    except TwitterSearchException as e:
        print("Search failed. Details: {}".format(e))


**Alpha status:** currently only the Search endpoint is supported in this mode