""" Module to control task progression in user study """

from database import client


def check_task(intents, keywords):
    """ Given intents and keywords, checks if one intent contains all given keyword """
    task_done = False
    for intent in intents:
        nile = intent["nile"]
        if all(keyword in nile for keyword in keywords):
            task_done = True
            break

    return task_done


def check_task_one(intents):
    """
        Given intents in the session, check if user has completed task one.

        Task: ensure that all traffic from the Internet to the labs is carefully
        inspected by the Deep Packet Inspection (DPI) middlebox.

        Answer:
            define intent answer:
                for endpoint('labs')
                add middlebox('deep inspection')
    """
    keywords = ["labs", "add", "deep inspection"]
    return check_task(intents, keywords)


def check_task_two(intents):
    """
        Given intents in the session, check if user has completed task two.

        Task: limit to 100 Mbps the bandwidth torrent traffic can consume.

        Answer:
            define intent answer:
                for traffic('peer2peer')
                set bandwidth('max', '100', 'mbps')
    """
    keywords = ["peer2peer", "set", "bandwidth", "max", "100", "mbps"]
    return check_task(intents, keywords)


def check_task_three(intents):
    """
        Given intents in the session, check if user has completed task three.

        Task: set a 10 GB per week download quota for students in dorms.

        Answer:
            define intent answer:
                for endpoint('dorms')
                set quota('download', '10', 'gb/wk')
    """
    keywords = ["dorms", "set", "quota", "10", "gb/wk"]
    return check_task(intents, keywords)


def check_task_four(intents):
    """
        Given intents in the session, check if user has completed task four.

        Task: block F2movies traffic for students in the labs.

        Answer:
            define intent answer:
                from endpoint('gateway')
                to endpoint('labs')
                for group('students')
                block service('F2movies')
    """
    keywords = ["labs", "students", "block", "F2movies"]
    return check_task(intents, keywords)


def check_task_five(intents):
    """
        Given intents in the session, check if user has completed task five.

        Task: set a 5 Gbps bandwidth limit for the server racks from 4PM to 7PM.

        Answer:
            define intent answer:
                for endpoint('servers')
                set bandwidth('max', '5', 'gpbs')
                start hour('16:00')
                end hour('19:00')
    """
    keywords = ["server", "set", "bandwidth", "max", "5", "gbps", "start", "16:00", "end", "19:00"]
    return check_task(intents, keywords)


def check(session, task):
    """Given Session UUID and Task number, check if user has completed it."""
    db = client.Database()
    intents = db.get_confirmed_intents(session)
    checker = {
        1: check_task_one,
        2: check_task_two,
        3: check_task_three,
        4: check_task_four,
        5: check_task_five
    }

    return checker[task](intents) if task in checker else False
