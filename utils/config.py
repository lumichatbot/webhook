""" Configurations and constansts for webhook module """

from pathlib import Path


def get_project_root():
    """Returns project root folder."""
    return str(Path(__file__).parent.parent)


########## DEPLOYER ##########
DEPLOY_URL = "http://localhost:5000/deploy"


########## PATH ###########
ROOT = get_project_root()

MODEL_WEIGHTS_PATH = ROOT + "/res/weights/{}_{}.joblib"

TOPOLOGY_PATH = ROOT + "/res/topology/user_study.json"
TOPOLOGY_CAMPUS_PATH = ROOT + "/res/topology/campus.json"
TOPOLOGY_CAMPUS_DOT_PATH = ROOT + "/res/topology/campus.dot"
LEARNING_CURVE_PATH = ROOT + "/res/results/learning/learning_{}_{}.csv"

EXTRACTION_DATASET_PATH = ROOT + "/res/dataset/extraction_{}.json"
EXTRACTION_RESULTS_PATH = ROOT + "/res/results/extraction/extraction_{}_{}.csv"

CONFLICTS_DATASET_PATH = ROOT + "/res/dataset/conflicts_{}.json"
CONFLICTS_CAMPI_DATASET_PATH = ROOT + "/res/dataset/conflicts_{}_{}.json"
CONFLICTS_RESULTS_PATH = ROOT + "/res/results/conflicts/conflicts_{}_{}.csv"

COMPILATION_DATASET_PATH = ROOT + "/res/dataset/compilation.json"

USER_STUDY_PLOTS_PATH = ROOT + "/res/results/study/study-{}.pdf"
USER_STUDY_INTENTS_PATH = ROOT + "/res/results/study/intents_by_task.csv"
USER_STUDY_QUESTIONNAIRE_PATH = ROOT + "/res/results/study/{}_questionnaire.csv"


######### USER STUDY ########

STUDY_USABILITY_LEVELS = ["Very Hard", "Hard", "Neutral", "Easy", "Very Easy"]
STUDY_COMPARIONS_LEVELS = ["Much Worse", "Worse", "Neutral", "Better", "Much Better"]
STUDY_EXPERIENCE_LEVELS = ["Novice", "Beginner", "Competent", "Proficient", "Expert"]
STUDY_FAMILIARITY_LEVELS = ["Unfamiliar", "Slightly Familiar",
                            "Moderately Familiar", "Very Familiar", "Extremely Familiar"]

######### DATASET ########

DATASET_SIZES = [100, 1000, 2500, 5000, 10000]
DATASET_ACTIONS_MBS = ["add", "remove"]
DATASET_ACTIONS_ACL = ["allow", "block"]
DATASET_ACTIONS_QOS = ["set", "unset"]
DATASET_GROUPS = ["network", "students", "dorms", "guests"]
DATASET_MIDDLEBOXES = ["copyright monitoring", "traffics monitor", "firewall", "dpi",
                       "ids", "ips", "network border system", "unit firewall",
                       "load balancer", "parental control", "overuse notification"]
DATASET_SERVICES = ["netflix", "youtube", "facebook", "vimeo",
                    "CounterStrike", "Battlenet", "AIM chat", "listserver", "Everquest",
                    "MSN audio", "MSN video", "MSN chat", "MSN application sharing",
                    "Net2Phone", "PC Telephone", "Sony Playstation 2", "NETBIOS",
                    "Sorenson Videophone 200", "file transfer", "amazon prime video",
                    "instagram", "popcorn time", "stremio", "bittorrent", "email", "irc"]
DATASET_TRAFFIC = ["peer2peer", "torrent", "streaming", "social media", "H323 video conferencing",
                   "email", "video conference", "voip", "file sharing", "gaming", "any"]
DATASET_PROTOCOLS = ["udp", "tcp", "https", "http", "smtp", "icmp", "dns",
                     "IMAP", "secure IMAP", "nat",  "POP3", "secure POP",
                     "telnet", "snmp", "sftp", "ftp", "quic", "scp", "ssh"]
DATASET_QOS_METRICS = [("bandwidth", "mbps"), ("quota", "gb/wk")]
DATASET_BW_CONSTRAINTS = ["min", "max"]
DATASET_QUOTA_CONSTRAINTS = ["download", "upload", "any"]


DATASET_SERVICE_ASSOCIATIONS = {
    "netflix": {
        "protocols": ["tcp", "https"],
        "traffics": ["streaming"]
    },
    "youtube": {
        "protocols": ["udp", "https", "quic"],
        "traffics": ["streaming"]
    },
    "facebook": {
        "protocols": ["tcp", "https"],
        "traffics": ["streaming", "social media"]
    },
    "AIM chat": {
        "protocols": ["tcp", "https", "http"],
        "traffics": ["social media"]
    },
    "instagram": {
        "protocols": ["tcp", "https"],
        "traffics": ["social media"]
    },
    "vimeo": {
        "protocols": ["tcp", "https"],
        "traffics": ["streaming"]
    },
    "amazon prime video": {
        "protocols": ["tcp", "https"],
        "traffics": ["streaming"]
    },
    "popcorn time": {
        "protocols": ["udp"],
        "traffics": ["peer2peer", "torrent"]
    },
    "stremio": {
        "protocols": ["udp"],
        "traffics": ["peer2peer", "torrent"]
    },
    "bittorrent": {
        "protocols": ["udp"],
        "traffics": ["peer2peer", "torrent"]
    },
    "utorrent": {
        "protocols": ["udp"],
        "traffics": ["peer2peer", "torrent"]
    },
    "CounterStrike": {
        "protocols": ["tcp"],
        "traffics": ["gaming"]
    },
    "Battlenet": {
        "protocols": ["tcp"],
        "traffics": ["gaming"]
    },
    "listserver": {
        "protocols": ["tcp", "smtp"],
        "traffics": ["email"]
    },
    "Everquest": {
        "protocols": ["tcp"],
        "traffics": ["gaming"]
    },
    "MSN audio": {
        "protocols": ["tcp", "http", "https"],
        "traffics": ["social media" "video conference", "voip", "H323 video conferencing"]
    },
    "MSN video": {
        "protocols": ["tcp", "http", "https"],
        "traffics": ["social media", "video conference", "voip", "H323 video conferencing"]
    },
    "MSN chat": {
        "protocols": ["tcp", "http", "https"],
        "traffics": ["social media"]
    },
    "MSN application sharing": {
        "protocols": ["tcp", "http", "https"],
        "traffics": ["social media"]
    },
    "Net2Phone": {
        "protocols": ["tcp", "http", "https"],
        "traffics": ["social media", "video conference", "voip", "H323 video conferencing"]
    },
    "PC Telephone": {
        "protocols": ["tcp", "http", "https"],
        "traffics": ["social media", "video conference", "voip", "H323 video conferencing"]
    },
    "email": {
        "protocols": ["tcp", "snmp", "POP3", "secure POP", "IMAP", "secure IMAP"],
        "traffics": ["email"]
    },
    "Sony Playstation 2": {
        "protocols": ["tcp"],
        "traffics": ["gaming"]
    },
    "Sorenson Videophone 200": {
        "protocols": ["tcp", "http", "https"],
        "traffics": ["social media", "video conference", "voip", "H323 video conferencing"]
    },
    "file transfer": {
        "protocols": ["scp", "sftp", "ftp", "ssh"],
        "traffics": ["file sharing"]
    },
    "irc": {
        "protocols": ["tcp", "http", "https"],
        "traffics": ["social media"]
    },
    "NETBIOS": {
        "protocols": ["tcp"],
        "traffics": []
    }
}

DATASET_TRAFFIC_ASSOCIATIONS = {
    "streaming": {
        "protocols": ["tcp", "https", "quic", "udp"],
        "services": ["netflix", "youtube", "vimeo", "amazon prime video", "facebook"]
    },
    "social media": {
        "protocols": ["tcp", "https"],
        "services": ["facebook", "instagram", "AIM chat", "irc",
                     "MSN audio", "MSN video", "MSN chat",
                     "MSN application sharing", "Net2Phone",
                     "PC Telephone", "Sorenson Videophone 200"]
    },
    "peer2peer": {
        "protocols": ["udp"],
        "services": ["bittorrent", "utorrent", "stremio", "popcorn time"]
    },
    "torrent": {
        "protocols": ["udp"],
        "services": ["bittorrent", "utorrent", "stremio", "popcorn time"]
    },
    "gaming": {
        "protocols": ["tcp"],
        "services": ["CounterStrike",
                     "Battlenet",
                     "Everquest",
                     "Sony Playstation 2"]
    },
    "email": {
        "protocols": ["tcp", "snmp", "POP3", "secure POP", "IMAP", "secure IMAP"],
        "services": ["listserver", "email"]
    },
    "video conference": {
        "protocols": ["tcp", "http", "https"],
        "services": [
            "MSN audio",
            "MSN video",
            "Net2Phone",
            "PC Telephone",
            "Sorenson Videophone 200"
        ]
    },
    "voip": {
        "protocols": ["tcp", "http"],
        "services": [
            "MSN audio",
            "MSN video",
            "Net2Phone",
            "PC Telephone",
            "Sorenson Videophone 200"
        ]
    },
    "H323 video conferencing": {
        "protocols": ["tcp", "http"],
        "services": [
            "MSN audio",
            "MSN video",
            "Net2Phone",
            "PC Telephone",
            "Sorenson Videophone 200"
        ]
    },
    "file sharing": {
        "protocols": ["scp", "ssh", "ftp", "sftp"],
        "services": ["file transfer"]
    },
    "any": {
        "protocols": DATASET_PROTOCOLS,
        "services": DATASET_SERVICES
    }
}

DATASET_SYNONYMS = {
    "dorms": ["dormitory", "hall", "dorm", "residence hall", "student residence"],
    "professors": ["professor", "prof", "faculty", "staff"],
    "students": ["student", "pupil", "educatee", "scholar", "scholarly person", "bookman"],
    "labs": ["dmz", "laboratories", "research labs", "research laboratories"],
    "servers": ["server racks", "racks"],
    "guests": ["guest networks", "guest users", "guest", "visitors", "non registered users"],
    "network": ["gateway", "internet", "university", "wireless", "campus"]
}

NILE_ACTIONS_NEGATION = {
    " add ": " remove ",
    " allow ": " block ",
    " set ": " unset "
}

NILE_OPERATIONS = ['add', 'remove', 'from', 'to', 'set', 'unset', 'allow', 'block', 'start', 'end', 'for']
