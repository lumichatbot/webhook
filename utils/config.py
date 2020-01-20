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

TOPOLOGY_PATH = ROOT + "/res/topology.json"
TOPOLOGY_DOT_PATH = ROOT + "/res/topology.dot"
LEARNING_CURVE_PATH = ROOT + "/res/results/learning_curve_{}_{}.csv"

COMPILATION_DATASET_PATH = ROOT + "/res/dataset/compilation.json"
COMPILATION_RESULTS_PATH = ROOT + "/res/dataset/compilation.csv"

EXTRACTION_DATASET_PATH = ROOT + "/res/dataset/extraction_{}.json"
EXTRACTION_RESULTS_PATH = ROOT + "/res/results/extraction_{}.csv"

CONTRADICTIONS_DATASET_PATH = ROOT + "/res/dataset/contradictions_{}.json"
CONTRADICTIONS_RESULTS_PATH = ROOT + "/res/results/contradictions_{}_{}.csv"


######### DATASET ########

DATASET_SIZES = [100, 500, 1000, 2500, 5000, 10000]
DATASET_ACTIONS_MBS = ['add', 'remove']
DATASET_ACTIONS_ACL = ['allow', 'block']
DATASET_ACTIONS_QOS = ['set', 'unset']
DATASET_GROUPS = ['students', 'professors', 'servers', 'guests', 'dorms', 'labs']
DATASET_MIDDLEBOXES = ['firewall', 'dpi', 'ids', 'load-balancer', 'parental-control']
DATASET_SERVICES = ['netflix', 'youtube', 'facebook', 'vimeo',
                    'amazon-prime', 'instagram', 'popcorn-time', 'stremio', 'bittorrent']
DATASET_TRAFFIC = ['peer2peer', 'torrent', 'streaming', 'social-media']
DATASET_PROTOCOLS = ['udp', 'tcp', 'https', 'http', 'smtp', 'icmp', 'telnet', 'snmp', 'sftp', 'ftp', 'quic']
DATASET_QOS_METRICS = [('bandwidth', 'mbps'), ('quota', 'gb/wk')]
DATASET_QOS_CONSTRAINTS = ['min', 'max']

DATASET_SERVICE_ASSOCIATIONS = {
    "netflix": {
        "protocol": ['tcp', 'https'],
        "traffic": ['streaming']
    },
    "youtube": {
        "protocol": ['udp', 'https', 'quic'],
        "traffic": ['streaming']
    },
    "facebook": {
        "protocol": ['tcp', 'https'],
        "traffic": ['streaming', 'social-media']
    },
    "instagram": {
        "protocol": ['tcp', 'https'],
        "traffic": ['social-media']
    },
    "vimeo": {
        "protocol": ['tcp', 'https'],
        "traffic": ['streaming']
    },
    "amazon-prime": {
        "protocol": ['tcp', 'https'],
        "traffic": ['streaming']
    },
    'popcorn-time': {
        "protocol": ['udp'],
        "traffic": ['peer2peer', 'torrent']
    },
    'stremio': {
        "protocol": ['udp'],
        "traffic": ['peer2peer', 'torrent']
    },
    'bittorrent': {
        "protocol": ['udp'],
        "traffic": ['peer2peer', 'torrent']
    }
}

DATASET_TRAFFIC_ASSOCIATIONS = {
    "streaming": {
        "protocol": ['tcp', 'https', 'quic', 'udp'],
        "service": ['netflix', 'youtube', 'vimeo', 'amazon-prime', 'facebook']
    },
    "social-media": {
        "protocol": ['tcp', 'https'],
        "service": ['facebook', 'instagram']
    },
    "peer2peer": {
        "protocol": ['udp'],
        "service": ['bittorrent', 'utorrent', 'stremio', 'popcorn-time']
    },
    "torrent": {
        "protocol": ['udp'],
        "service": ['bittorrent', 'utorrent', 'stremio', 'popcorn-time']
    }
}

DATASET_SYNONYMS = {
    "dorms": ["dormitory", "hall", "dorm", "residence_hall", "student_residence"],
    "professors": ["professor", "prof"],
    "staff": ["faculty"],
    "students": ["student", "pupil", "educatee", "scholar", "scholarly_person", "bookman"],
    "labs": ["dmz", "laboratories", "research labs", "research laboratories"]
}

NILE_ACTIONS_NEGATION = {
    "add": "remove",
    "allow": "block",
    "set": "unset"
}
