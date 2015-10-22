""" helper functions to make travis/coveralls tests pass 100%
"""

import os

def file_range(filename, expected_size, ok_range=50):
    """ Files are slightly different sizes on travis build then on local
    machine. For tests that include building an image using Pillow. I'm
    guessing this is due to slightly different pillow versions. This
    also seems like a bad idea, as your CI environment is now different
    from your dev. Trying to match the pillow version on your fedora 22
    core system seems like a bad idea too. This seems to be a 0.003%
    difference in file size.
    """
    if not os.path.exists(filename):
        #print "\n\n### FILE DOES NOT EXIST: %s ###\n\n" % filename
        return False

    actual_size = os.path.getsize(filename)

    return size_range(actual_size, expected_size, ok_range)

def size_range(actual_size, expected_size, ok_range=50):
    """ Simple comparison of two size ranges.
    """
    min_size = expected_size - ok_range
    max_size = expected_size + ok_range

    if actual_size < min_size:
        return False

    if actual_size > max_size:
        return False

    return True

    
