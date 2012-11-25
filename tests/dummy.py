#: Module purely exists to test patching things.
thing = True
it = lambda: False


def get_thing():
    global thing
    return thing

def get_it():
    global it
    return it
