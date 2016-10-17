class TwitterException(Exception):
    pass


class TwitterAuthExecption(TwitterException):
    pass


class TwitterAPIException(TwitterException):
    pass


class TwitterSearchException(TwitterAPIException):
    pass
