from threading import Thread


def nonblocking(fn, daemon=True):
    def wrapped(*args, **kwargs):
        Thread(target=fn, args=args, kwargs=kwargs, daemon=daemon).start()

    return wrapped

