from ast import Raise


def increment_likes(like):
    if type(like) in [int]:
        if like < 0:
            raise ValueError("likes cannot be negative")
        return like + 1
    raise TypeError("this is not an intenger")

