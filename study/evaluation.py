""" Module to consolidate user study results """
import csv

import tasks

from utils import config, plotter
from database import client


def check_uuids():
    """ Opens pre and post questionnaries and look for incosnsistent responses """
    pre_questionnaire = {}
    post_questionnaire = {}

    with open(config.USER_STUDY_QUESTIONNAIRE_PATH.format("pre")) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)  # skip header
        for row in reader:
            uuid = row[1]
            print("PRE UUID", uuid)
            if uuid not in pre_questionnaire:
                pre_questionnaire[uuid] = 0
            pre_questionnaire[uuid] += 1

    with open(config.USER_STUDY_QUESTIONNAIRE_PATH.format("post")) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)  # skip header
        for row in reader:
            uuid = row[1]
            print("POST UUID", uuid)
            if uuid not in post_questionnaire:
                post_questionnaire[uuid] = 0
            post_questionnaire[uuid] += 1

    print("DIFF UUIDS", list(set(pre_questionnaire.keys()) - set(post_questionnaire.keys())))
    print("DIFF UUIDS", list(set(post_questionnaire.keys()) - set(pre_questionnaire.keys())))
    print("REPEATED PRE UUIDS", len([uuid for uuid in pre_questionnaire if pre_questionnaire[uuid] > 1]))
    print("REPEATED POST UUIDS", len([uuid for uuid in post_questionnaire if post_questionnaire[uuid] > 1]))


def check_intents():
    """ Fetches intents from sessions in the user study to analyze them """
    db = client.Database()
    live_sessions = {}
    intents = {}
    confirmed_intents = {}
    tasks_completed_by_session = {}

    with open(config.USER_STUDY_QUESTIONNAIRE_PATH.format("pre")) as csvfile:
        reader = csv.reader(csvfile, delimiter=',',)
        next(reader)  # skip header
        for row in reader:
            uuid = row[1]
            if uuid not in live_sessions:
                live_sessions[uuid] = 0
            live_sessions[uuid] += 1

    with open(config.USER_STUDY_QUESTIONNAIRE_PATH.format("post")) as csvfile:
        reader = csv.reader(csvfile, delimiter=',',)
        next(reader)  # skip header
        for row in reader:
            uuid = row[1]
            if uuid not in live_sessions:
                live_sessions[uuid] = 0
            live_sessions[uuid] += 1

    print("NUM LIVE SESSIONS", len(list(live_sessions)))

    for session, count in live_sessions.items():
        if count == 2:
            session_intents = db.get_intents(session)
            # print(session_intents)
            intents[session] = []
            confirmed_intents[session] = []
            for intent in session_intents:
                intents[session].append(intent)
                if intent['status'] != 'pending':
                    # print(intent['status'])
                    confirmed_intents[session].append(intent)

            print("NUM INTENTS", session, len(intents[session]))
            print("CONFIRMED INTENTS", session, len(confirmed_intents[session]))

            tasks_completed_by_session[session] = 0
            for task in [1, 2, 3, 4, 5]:
                result = tasks.check(session, task)
                # print("TASK #", task, result['done'])
                tasks_completed_by_session[session] += 1 if result['done'] else 0

            print("COMPLETED TASKS", tasks_completed_by_session[session])
    print("TOTAL INTENTS", sum([len(intents) for (uuid, intents) in intents.items()]))


def user_profiles():
    """ Loads data from pre-questionnarie and creates pie charts with  profile """

    sessions_by_job = {}
    sessions_by_region = {}
    sessions_by_exp = {}
    sessions_by_familiarity = {}

    with open(config.USER_STUDY_QUESTIONNAIRE_PATH.format("pre")) as csvfile:
        reader = csv.reader(csvfile, delimiter=',',)
        next(reader)  # skip header
        for row in reader:
            uuid = row[1]
            job = row[3]
            job_class = ""
            if "professor" in job.lower() or "research" in job.lower():
                job_class = "University Faculty"
            elif "network" in job.lower():
                job_class = "Campus Network Operator"
            else:
                job_class = job

            region = row[2]
            experience = config.STUDY_EXPERIENCE_LEVELS[int(row[5]) - 1]
            familiarity = config.STUDY_FAMILIARITY_LEVELS[int(row[8]) - 1]

            if job_class not in sessions_by_job:
                sessions_by_job[job_class] = 0
            if region not in sessions_by_region:
                sessions_by_region[region] = 0
            if experience not in sessions_by_exp:
                sessions_by_exp[experience] = 0
            if familiarity not in sessions_by_familiarity:
                sessions_by_familiarity[familiarity] = 0

            sessions_by_job[job_class] += 1
            sessions_by_region[region] += 1
            sessions_by_exp[experience] += 1
            sessions_by_familiarity[familiarity] += 1

    plotter.plot_pie_chart(sessions_by_job.keys(), sessions_by_job.values(),
                           config.USER_STUDY_PLOTS_PATH.format("job"))
    plotter.plot_pie_chart(sessions_by_region.keys(), sessions_by_region.values(),
                           config.USER_STUDY_PLOTS_PATH.format("region"))

    exp_values = [sessions_by_exp[x] for x in config.STUDY_EXPERIENCE_LEVELS]
    plotter.plot_pie_chart(config.STUDY_EXPERIENCE_LEVELS, exp_values,
                           config.USER_STUDY_PLOTS_PATH.format("exp"))
    familiarity_values = [sessions_by_familiarity[x] for x in config.STUDY_FAMILIARITY_LEVELS]
    plotter.plot_pie_chart(config.STUDY_FAMILIARITY_LEVELS, familiarity_values,
                           config.USER_STUDY_PLOTS_PATH.format("familiarity"))


def tasks_completed():
    """ Loads data from questionnaries and creates pie charts with number of tasks completed by experience"""

    tasks_by_exp = {}
    tasks_nums = []
    with open(config.USER_STUDY_QUESTIONNAIRE_PATH.format("post")) as csvfile:
        reader = csv.reader(csvfile, delimiter=',',)
        next(reader)  # skip header
        for row in reader:
            uuid = row[1]
            tasks_completed = row[6]
            # experience = config.STUDY_EXPERIENCE_LEVELS[int(row[5]) - 1]
            # experience_class = ""
            #
            # if "Novice" in experience or "Beginner" in experience:
            #     experience_class = "Novice or Beginner"
            # elif "Expert" in experience or "Proficient" in experience:
            #     experience_class = "Proficient or Expert"
            # else:
            #     experience_class = experience
            #
            # if experience_class not in tasks_by_exp:
            #     tasks_by_exp[experience_class] = []

            # tasks_completed = 0
            # for task in [1, 2, 3, 4, 5]:
            #     result = tasks.check(uuid, task)
            #     tasks_completed += 1 if result['done'] else 0

            tasks_nums.append(tasks_completed)
            # tasks_by_exp[experience_class].append(tasks_completed)

    # for exp, tasks_count in tasks_by_exp.items():
    num_tasks_sum = {}
    for num_tasks in tasks_nums:
        if str(num_tasks) not in num_tasks_sum:
            num_tasks_sum[str(num_tasks)] = 0
        num_tasks_sum[str(num_tasks)] += 1

    # print(exp)
    plotter.plot_pie_chart(num_tasks_sum.keys(), num_tasks_sum.values(),
                           config.USER_STUDY_PLOTS_PATH.format("tasks"))


def feedback_count():
    """ Count the total number of intents generated, and count the number of feedbacks given """

    db = client.Database()

    num_intents = 0
    num_intents_accepted_right = 0
    num_intents_accepted_wrong = 0
    num_intents_pending = 0
    num_intents_rejected_no_feedback = 0
    num_intents_feedback = 0
    num_intents_feedback_accepted = 0
    with open(config.USER_STUDY_QUESTIONNAIRE_PATH.format("post")) as csvfile:
        reader = csv.reader(csvfile, delimiter=',',)
        next(reader)  # skip header
        for row in reader:
            uuid = row[1]
            session_intents = db.get_intents(uuid)

            for intent in session_intents:
                num_intents += 1
                if intent['status'] == 'declined':
                    if 'missingEntities' in intent:
                        num_intents_feedback += 1
                    else:
                        num_intents_rejected_no_feedback += 1
                elif 'missingEntities' in intent and 'nileFeedback' in intent:
                    num_intents_feedback_accepted += 1
                elif intent['status'] == 'compiled':
                    if tasks.check_intent(intent):
                        num_intents_accepted_right += 1
                    else:
                        num_intents_accepted_wrong += 1
                else:
                    num_intents_pending += 1

    print("NUM INTENTS", num_intents)
    print("CONFIRMED INTENTS RIGHT", num_intents_accepted_right)
    print("CONFIRMED INTENTS WRONG", num_intents_accepted_wrong)
    print("PENDING INTENTS", num_intents_pending)
    # print("REJECTED INTENTS", num_intents_rejected_no_feedback)
    print("FEEDBACK REJECTED INTENTS", num_intents_feedback)
    print("FEEDBACK ACCEPTED INTENTS", num_intents_feedback_accepted)

    plotter.plot_pie_chart(['Confirmed Intents (Right)', 'Confirmed Intents (Wrong)', 'Pending Intents', 'Feedback Accepted', 'Feedback Rejected'],
                           [num_intents_accepted_right, num_intents_accepted_wrong, num_intents_pending,
                               num_intents_feedback_accepted, num_intents_feedback],
                           config.USER_STUDY_PLOTS_PATH.format("feedback"))


def usability():
    """ Computes user reponses on Lumi's usability """
    usability = {}
    comparison = {}
    opinion = {}
    with open(config.USER_STUDY_QUESTIONNAIRE_PATH.format("post")) as csvfile:
        reader = csv.reader(csvfile, delimiter=',',)
        next(reader)  # skip header
        for row in reader:
            uuid = row[1]
            usability_score = config.STUDY_USABILITY_LEVELS[int(row[7]) - 1]
            comparison_score = config.STUDY_COMPARIONS_LEVELS[int(row[8]) - 1]
            opinion_choice = row[9]

            if usability_score not in usability:
                usability[usability_score] = 0
            usability[usability_score] += 1

            if comparison_score not in comparison:
                comparison[comparison_score] = 0
            comparison[comparison_score] += 1

            if opinion_choice not in opinion:
                opinion[opinion_choice] = 0
            opinion[opinion_choice] += 1

    plotter.plot_pie_chart(usability.keys(), usability.values(),
                           config.USER_STUDY_PLOTS_PATH.format("usability"))
    plotter.plot_pie_chart(comparison.keys(), comparison.values(),
                           config.USER_STUDY_PLOTS_PATH.format("comparison"))
    plotter.plot_pie_chart(opinion.keys(), opinion.values(),
                           config.USER_STUDY_PLOTS_PATH.format("opinion"))


def usability_by_profile():
    """ Computer usability responses based on user profiles """
    sessions_by_exp = {}

    usability_by_exp = {}
    comparison_by_exp = {}
    opinion_by_exp = {}

    with open(config.USER_STUDY_QUESTIONNAIRE_PATH.format("pre")) as csvfile:
        reader = csv.reader(csvfile, delimiter=',',)
        next(reader)  # skip header
        for row in reader:
            uuid = row[1]
            experience = config.STUDY_EXPERIENCE_LEVELS[int(row[5]) - 1]
            sessions_by_exp[uuid] = experience

    print(len(sessions_by_exp.values()))
    with open(config.USER_STUDY_QUESTIONNAIRE_PATH.format("post")) as csvfile:
        reader = csv.reader(csvfile, delimiter=',',)
        next(reader)  # skip header
        for row in reader:
            uuid = row[1]

            if uuid in sessions_by_exp:
                experience = sessions_by_exp[uuid]
                usability_score = config.STUDY_USABILITY_LEVELS[int(row[7]) - 1]
                comparison_score = config.STUDY_COMPARIONS_LEVELS[int(row[8]) - 1]
                opinion_choice = row[9]

                exp_class = ""
                if "beginner" == experience.lower() or "novice" == experience.lower():
                    exp_class = "novice-beginner"
                elif "proficient" == experience.lower() or "expert" == experience.lower():
                    exp_class = "proficient-expert"
                else:
                    exp_class = experience.lower()

                if exp_class not in usability_by_exp:
                    usability_by_exp[exp_class] = {}

                if usability_score not in usability_by_exp[exp_class]:
                    usability_by_exp[exp_class][usability_score] = 0

                usability_by_exp[exp_class][usability_score] += 1

                if exp_class not in comparison_by_exp:
                    comparison_by_exp[exp_class] = {}

                if comparison_score not in comparison_by_exp[exp_class]:
                    comparison_by_exp[exp_class][comparison_score] = 0

                comparison_by_exp[exp_class][comparison_score] += 1

                if exp_class not in opinion_by_exp:
                    opinion_by_exp[exp_class] = {}

                if opinion_choice not in opinion_by_exp[exp_class]:
                    opinion_by_exp[exp_class][opinion_choice] = 0

                opinion_by_exp[exp_class][opinion_choice] += 1

    # for exp in opinion_by_exp.keys():
    #     plotter.plot_pie_chart(usability_by_exp[exp].keys(), usability_by_exp[exp].values(),
    #                            config.USER_STUDY_PLOTS_PATH.format("usability-{}".format(exp)))
    #     plotter.plot_pie_chart(comparison_by_exp[exp].keys(), comparison_by_exp[exp].values(),
    #                            config.USER_STUDY_PLOTS_PATH.format("comparison-{}".format(exp)))
    #     plotter.plot_pie_chart(opinion_by_exp[exp].keys(), opinion_by_exp[exp].values(),
    #                            config.USER_STUDY_PLOTS_PATH.format("opinion-{}".format(exp)))


def save_intents_by_tasks():
    """ Fetches intents from all users, divides them by task and save it to a csv  """

    db = client.Database()

    intents_by_task = {
        0: [],
        1: [],
        2: [],
        3: [],
        4: [],
        5: []
    }

    with open(config.USER_STUDY_QUESTIONNAIRE_PATH.format("post")) as csvfile:
        reader = csv.reader(csvfile, delimiter=',',)
        next(reader)  # skip header
        for row in reader:
            uuid = row[1]
            session_intents = db.get_intents(uuid)

            for intent in session_intents:
                task_completed = tasks.check_intent(intent)
                if task_completed > 0:
                    intents_by_task[task_completed].append(intent['text'])

    print("INTENTS", intents_by_task)

    with open(config.USER_STUDY_INTENTS_PATH, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['Task', 'Intent'])
        for (task, intents) in intents_by_task.items():
            for intent in intents:
                writer.writerow([task, intent])


if __name__ == "__main__":
    # check_uuids()
    # check_intents()
    # user_profiles()
    # tasks_completed()
    # feedback_count()
    # usability_by_profile()
    save_intents_by_tasks()
