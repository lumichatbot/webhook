""" Module to control task progression in user study """

from database import client


def check_task(intents, keywords):
    """ Given intents and keywords, checks if one intent contains all given keyword """
    task_done = False
    most_matches = []
    for intent in intents:
        nile = intent["nileFeedback"] if "nileFeedback" in intent else intent['nile']
        if all(keyword in nile for keyword in keywords):
            task_done = True
            most_matches = keywords
            break
        else:
            matches = [keyword for keyword in keywords if keyword in nile]
            most_matches = matches if len(matches) > len(most_matches) else most_matches

    return {'done': task_done, 'matches': most_matches, 'missing': list(set(keywords) - set(most_matches))}


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
    keywords = ["labs", "add", "dpi"]
    return check_task(intents, keywords)


def check_task_two(intents):
    """
        Given intents in the session, check if user has completed task two.

        Task: limit to 100 Mbps the bandwidth torrent traffic can consume.

        Answer:
            define intent answer:
                for traffic('torrent')
                set bandwidth('max', '100', 'mbps')
    """
    keywords = ["torrent", "set", "bandwidth", "max", "100", "mbps"]
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
    keywords = ["dorms", "quota", "10", "gb/wk"]
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
    keywords = ["server", "bandwidth", "5", "gbps", "start", "16:00", "end", "19:00"]
    return check_task(intents, keywords)


def check_intent(intent):
    """ Given intent, check if it complete any of the five tasks """
    task_completed = False
    checker = {
        1: check_task_one,
        2: check_task_two,
        3: check_task_three,
        4: check_task_four,
        5: check_task_five
    }

    for task in [1, 2, 3, 4, 5]:
        task_completed += task if checker[task]([intent])['done'] else 0

    return task_completed


def check(session, task):
    """Given Session UUID and Task number, check if user has completed it."""
    db = client.Database()
    intents = db.get_intents(session)
    checker = {
        1: check_task_one,
        2: check_task_two,
        3: check_task_three,
        4: check_task_four,
        5: check_task_five
    }

    return checker[task](intents) if task in checker else False
