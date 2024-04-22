import random


def generate_randome_tripartite_name():
    word_list = [
        "flux",
        "fract",
        "quant",
        "neur",
        "tensor",
        "vortex",
        "chaos",
        "laser",
        "glyph",
        "glitch",
        "warp",
        "phase",
        "lens",
        "shade",
        "sync",
        "delta",
        "echo",
        "sonic",
        "blend",
        "spark",
        "pixel",
        "latch",
        "gamma",
        "nova",
        "hyper",
        "orbit",
        "omega",
        "polar",
        "radar",
        "quark",
        "cosmo",
        "quasar",
        "sigma",
        "theta",
        "unity",
        "vector",
        "mecha",
        "flame",
        "chrono",
        "solar",
        "plasma",
        "radar",
        "pulse",
        "comet",
        "nebula",
        "vertex",
        "photon",
        "magma",
        "atom",
        "quanta",
        "fusion",
        "prism",
        "specter",
        "relic",
        "cipher",
        "vortex",
        "aura",
        "nexus",
        "genesis",
        "zenith",
        "nadir",
        "echo",
        "mirage",
        "enigma",
        "karma",
        "mantra",
        "stigma",
        "igma",
        "alpha",
        "beta",
        "zeta",
        "eta",
        "iota",
        "kappa",
        "lambda",
        "mu",
        "nu",
        "xi",
        "omicron",
        "pi",
        "rho",
        "tau",
        "upsilon",
        "phi",
        "chi",
        "psi",
        "omega",
    ]

    normal_adjectives_list = [
        "happy",
        "calm",
        "confident",
        "curious",
        "eager",
        "excited",
        "grateful",
        "hopeful",
        "joyful",
        "optimistic",
        "proud",
        "satisfied",
        "ambitious",
        "caring",
        "cautious",
        "determined",
        "friendly",
        "generous",
        "helpful",
        "honest",
        "humble",
        "kind",
        "loyal",
        "modest",
        "polite",
        "positive",
        "reliable",
        "responsible",
        "sensitive",
        "thoughtful",
        "trustworthy",
        "warm",
        "wise",
        "absurd",
        "charming",
        "classic",
        "comic",
        "dramatic",
        "elegant",
        "entertaining",
        "epic",
        "fabulous",
        "fantastic",
        "glamorous",
        "grand",
        "humorous",
        "majestic",
        "magical",
        "magnificent",
        "nostalgic",
        "picturesque",
        "romantic",
        "sensational",
        "spectacular",
        "stunning",
        "thrilling",
        "witty",
        "adventurous",
        "brave",
        "daring",
        "fearless",
        "heroic",
        "powerful",
        "strong",
        "tough",
        "valiant",
        "creative",
        "imaginative",
        "innovative",
        "intelligent",
        "logical",
        "rational",
        "resourceful",
        "smart",
        "accurate",
        "efficient",
        "productive",
        "reliable",
        "skillful",
        "affectionate",
        "loving",
        "passionate",
        "warm",
        "cheerful",
        "enthusiastic",
        "extroverted",
        "outgoing",
        "optimistic",
        "calm",
        "composed",
        "patient",
        "relaxed",
        "content",
    ]

    # Select three random words from the word list
    word1 = random.choice(word_list)

    # Select two random adjectives from the adjective list
    adjective1 = random.choice(normal_adjectives_list)
    adjective2 = random.choice(normal_adjectives_list)

    # Join the selected words to form the session name
    session_name = f"{adjective1}-{adjective2}-{word1}"
    return session_name