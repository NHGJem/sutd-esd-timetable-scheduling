#!/usr/bin/env python3

import gurobipy as gp
from gurobipy import GRB

try:
    # Create a new model
    m = gp.Model("sutd_esd_timetable_scheduling")

    jobs, proc_time, venue = gp.multidict(
        {
            "J01": [4, "2404"],
            "J02": [4, "2404"],
            "J03": [4, "2503"],
            "J04": [4, "2503"],
            "J05": [4, "2505"],
            "J06": [4, "2404"],
            "J07": [4, "2404"],
            "J08": [4, "2505"],
            "J09": [4, "2505"],
            "J10": [4, "2503"],
            "J11": [4, "2503"],
            "J12": [4, "2503"],
            "J13": [4, "2503"],
            "J14": [2, "1203"],
            "J15": [4, "2503"],
            "J16": [4, "2503"],
            "J17": [4, "1415"],
            "J18": [4, "1415"],
            "J19": [4, "2308"],
            "J20": [4, "2308"],
            "J21": [2, "1610"],
            "J22": [4, "2304"],
            "J23": [4, "2304"],
            "J24": [4, "1610"],
            "J25": [4, "1610"],
            "J26": [4, "2304"],
            "J27": [4, "2304"],
            "J28": [2, "2404"],
            "J29": [2, "2404"],
            "J30": [4, "2404"],
            "J31": [3, "2404"],
            "J32": [3, "2404"],
            "J33": [4, "2404"],
            "J34": [4, "2404"],
            "J35": [4, "2404"],
            "J36": [3, "1203"],
            "J37": [3, "1203"],
            "J38": [4, "1203"],
        }
    )

    weight = [
        2,
        1,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        4,
        4,
        4,
        4,
        4,
        4,
        4,
    ]

    T = 23  # 0.5h blocks per day 8.30 and 19.30
    Days = 5  # monday to friday

    # never use the values of this dictionary, just keys
    start_time = {
        (j, t, d): weight[t] for j in jobs for t in range(T) for d in range(Days)
    }

    # Create decision variables Xjtd
    X = m.addVars(start_time.keys(), vtype=GRB.BINARY, name="X")

    # Add variable for occupied slot
    taken = {(j, t, d): 0 for j in jobs for t in range(T) for d in range(Days)}
    for j in jobs:
        for t in range(T):
            minT = max(0, t + 1 - proc_time[j])
            maxT = t
            for d in range(Days):
                for s in range(minT, maxT + 1):
                    taken[j, t, d] += X[j, s, d]

    # Set objective function
    obj_func = gp.quicksum(
        weight[t] * X[j, t, d] for j in jobs for t in range(T) for d in range(Days)
    )

    m.setObjective(obj_func, GRB.MINIMIZE)

    # Hardcode non ESD classes
    m.addConstr(X["J28", 1, 3] == 1)
    m.addConstr(X["J29", 4, 0] == 1)
    m.addConstr(X["J30", 11, 0] == 1)
    # m.addConstr(X["J31", 6, 0] == 1)
    m.addConstr(X["J32", 16, 1] == 1)
    m.addConstr(X["J33", 15, 0] == 1)
    m.addConstr(X["J34", 0, 4] == 1)
    m.addConstr(X["J35", 7, 0] == 1)
    m.addConstr(X["J36", 1, 0] == 1)
    m.addConstr(X["J37", 13, 1] == 1)
    m.addConstr(X["J38", 9, 1] == 1)

    locations = [
        ["J14", "J36", "J37", "J38"],
        ["J17", "J18"],
        ["J21", "J24", "J25"],
        ["J22", "J23", "J26", "J27"],
        ["J19", "J20"],
        [
            "J01",
            "J02",
            "J06",
            "J07",
            "J28",
            "J29",
            "J30",
            "J31",
            "J32",
            "J33",
            "J34",
            "J35",
        ],
        ["J03", "J04", "J10", "J11", "J12", "J13", "J15", "J16"],
        ["J05", "J08", "J09"],
    ]

    # FIXME
    # Jobs from a set of eclusive jobs J due to being the same location cannot be started on the same day at same time
    # for location in locations:
    #     for d in range(Days):
    #         for t in range(T):
    #             for l in location:
    #                 same_day_time_location = 0
    #                 minT = max(0, t + 1 - proc_time[l])
    #                 maxT = t
    #                 for s in range(minT, maxT + 1):
    #                     same_day_time_location += X[l, s, d]
    #         m.addConstr(same_day_time_location <= 1)

    for location in locations:
        for d in range(Days):
            for t in range(T):
                same_day_time_location = 0
                for l in location:
                    same_day_time_location += taken[l, t, d]
                m.addConstr(same_day_time_location <= 1)

    professors = [
        ["J01", "J02", "J03", "J04"],
        ["J05", "J06", "J07", "J08", "J09"],
        ["J10", "J11", "J12", "J13"],
        ["J14", "J15", "J16", "J17", "J18"],
        ["J19", "J20"],
        ["J21", "J22", "J23"],
        ["J24", "J25"],
        ["J26", "J27"],
    ]

    # FIXME
    # Jobs from a set of eclusive jobs J due to being the same professor cannot be started on the same day at the same time
    # for professor in professors:
    #     for d in range(Days):
    #         for t in range(T):
    #             for p in professor:
    #                 same_day_time_professor = 0
    #                 minT = max(0, t + 1 - proc_time[p])
    #                 maxT = t
    #                 for s in range(minT, maxT + 1):
    #                     same_day_time_professor += X[p, t, d]
    #         m.addConstr(same_day_time_professor <= 1)

    for professor in professors:
        for d in range(Days):
            for t in range(T):
                same_day_time_prof = 0
                for p in professor:
                    same_day_time_prof += taken[p, t, d]
                m.addConstr(same_day_time_prof <= 1)

    class_subjects = [
        ["J01", "J02", "J05", "J06", "J07", "J10", "J11"],
        ["J03", "J04", "J05", "J08", "J09", "J12", "J13"],
        # Tracks?
        ["J19", "J20", "J26", "J27"],
        ["J14", "J15", "J16", "J17", "J18", "J21", "J22", "J23"],
    ]

    # Jobs from a set of exclusive jobs J due to being for the same class, cannot be started on the same day at the same time
    for c_subject in class_subjects:
        for d in range(Days):
            for t in range(T):
                same_day_time_class = 0
                for c in c_subject:
                    same_day_time_class += taken[c, t, d]
                m.addConstr(same_day_time_class <= 1)

    # Each job j starts at exactly one time instant
    for j in jobs:
        job_start_once = 0
        for t in range(T):
            for d in range(Days):
                job_start_once += X[j, t, d]
        m.addConstr(job_start_once == 1)

    # All jobs cannot be processed at time instants corresponding to Wed/Fri afternoons
    job_on_wed_fri = 0
    for j in jobs:
        for d in [2, 4]:
            for t in range(9, T):
                minT = max(0, t + 1 - proc_time[j])
                maxT = t
                for s in range(minT, maxT + 1):
                    job_on_wed_fri += X[j, s, d]
    m.addConstr(job_on_wed_fri == 0)

    ESD_jobs = [
        "J01",
        "J02",
        "J03",
        "J04",
        "J05",
        "J06",
        "J07",
        "J08",
        "J09",
        "J10",
        "J11",
        "J12",
        "J13",
        "J14",
        "J15",
        "J16",
        "J17",
        "J18",
        "J19",
        "J20",
        "J21",
        "J22",
        "J23",
        "J24",
        "J25",
        "J26",
        "J27",
    ]

    def time_instant_constraint(start, end, day):
        time_instant_sum = 0
        for j in ESD_jobs:
            for d in [day]:
                for t in range(start, end):  # could use refinement
                    minT = max(0, t + 1 - proc_time[j])
                    maxT = t
                    for s in range(minT, maxT + 1):
                        time_instant_sum += X[j, s, d]
        m.addConstr(time_instant_sum == 0)

    # All jobs cannot be processed at time instants corresponding to HASS/TAE blocks
    time_instant_constraint(13, 19, 0)
    time_instant_constraint(0, 9, 1)
    time_instant_constraint(13, 19, 3)
    time_instant_constraint(1, 5, 3)
    time_instant_constraint(4, 10, 4)

    subjects = [
        ["J01", "J02"],
        ["J03", "J04"],
        ["J05", "J06", "J07"],
        ["J05", "J08", "J09"],
        ["J10", "J11"],
        ["J12", "J13"],
        ["J14", "J15", "J16"],
        ["J14", "J17", "J18"],
        ["J19", "J20"],
        ["J21", "J22", "J23"],
        ["J24", "J25"],
        ["J26", "J27"],
    ]

    # Jobs from a set of eclusive jobs J due to being the same subject cannot be started on the same day
    for subject in subjects:
        for d in range(Days):
            same_day_subject = 0
            for s in subject:
                for t in range(T):
                    same_day_subject += X[s, t, d]
            m.addConstr(same_day_subject <= 1)

    m.optimize()

    # Format data to human-friendly output
    job_to_class = {
        "J01": "40.004 Statistics CS01 Period 1",
        "J02": "40.004 Statistics CS01 Period 2",
        "J03": "40.004 Statistics CS02 Period 1",
        "J04": "40.004 Statistics CS02 Period 2",
        "J05": "40.012 Manufacturing and Service Operations LS01",
        "J06": "40.012 Manufacturing and Service Operations CS01 Period 1",
        "J07": "40.012 Manufacturing and Service Operations CS01 Period 2",
        "J08": "40.012 Manufacturing and Service Operations CS02 Period 1",
        "J09": "40.012 Manufacturing and Service Operations CS02 Period 2",
        "J10": "40.014 Engineering Systems Architecture CS01 Period 1",
        "J11": "40.014 Engineering Systems Architecture CS01 Period 2",
        "J12": "40.014 Engineering Systems Architecture CS02 Period 1",
        "J13": "40.014 Engineering Systems Architecture CS02 Period 2",
        "J14": "40.319 Statistical and Machine Learning LS01 (Lecture)",
        "J15": "40.319 Statistical and Machine Learning CS01 Period 1",
        "J16": "40.319 Statistical and Machine Learning CS01 Period 2",
        "J17": "40.319 Statistical and Machine Learning CS02 Period 1",
        "J18": "40.319 Statistical and Machine Learning CS02 Period 2",
        "J19": "40.242 Derivative Pricing and Risk Management Period 1",
        "J20": "40.242 Derivative Pricing and Risk Management Period 2",
        "J21": "40.302 Advanced Topics in Optimisation#/40.305 Advanced Topics in Stochastic Modelling# Lesson 1",
        "J22": "40.302 Advanced Topics in Optimisation#/40.305 Advanced Topics in Stochastic Modelling# Lesson 2",
        "J23": "40.302 Advanced Topics in Optimisation#/40.305 Advanced Topics in Stochastic Modelling# Lesson 3",
        "J24": "40.321 Airport Systems Modelling and Simulation Period 1",
        "J25": "40.321 Airport Systems Modelling and Simulation Period 2",
        "J26": "40.323 Equity Valuation Period 1",
        "J27": "40.323 Equity Valuation Period 2",
        "J28": "",
        "J29": "",
        "J30": "",
        "J31": "",
        "J32": "",
        "J33": "",
        "J34": "",
        "J35": "",
        "J36": "",
        "J37": "",
        "J38": "",
    }

    index_to_time = {
        "0": "0830",
        "1": "0900",
        "2": "0930",
        "3": "1000",
        "4": "1030",
        "5": "1100",
        "6": "1130",
        "7": "1200",
        "8": "1230",
        "9": "1300",
        "10": "1330",
        "11": "1400",
        "12": "1430",
        "13": "1500",
        "14": "1530",
        "15": "1600",
        "16": "1630",
        "17": "1700",
        "18": "1730",
        "19": "1800",
        "20": "1830",
        "21": "1900",
        "22": "1930",
    }

    index_to_day = {
        "0": "Mon",
        "1": "Tue",
        "2": "Wed",
        "3": "Thu",
        "4": "Fri",
    }

    for x in X.values():
        if x.x > 0.5:
            day_index = x.varName[-2]
            start_time_index = (x.varName[6] + x.varName[7]).replace(",", "")
            subject_index = x.varName[2] + x.varName[3] + x.varName[4]
            print(
                "%s | %s | %s | %s"
                % (
                    index_to_day[day_index],
                    index_to_time[start_time_index],
                    index_to_time[
                        str(int(start_time_index) + proc_time[subject_index])
                    ],
                    job_to_class[subject_index],
                )
            )
    print("Obj: %g" % m.objVal)

except gp.GurobiError as e:
    print("Error code " + str(e.errno) + ": " + str(e))

except AttributeError:
    print("Encountered an attribute error")
