def wrapper(func):
    def inner():
        try:
            func()
        except Exception:
            print("Exception handled")
    return inner


@wrapper
def test():
    print("I am called")
    raise Exception("Test exception called")

test()