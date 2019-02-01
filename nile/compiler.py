
from parser import parse


def compile(nile, target="Merlin"):
    """ Compiles Nile intent into target language. By default, the target language is Merlin. """
    if target != "Merlin":
        raise ValueError("Target language not yet support. Please contact the repo admin.")
    return parse(nile)


if __name__ == "__main__":
    compile("define intent uniIntent: for group('students') add middlebox('firewall'), middlebox('dpi')")
