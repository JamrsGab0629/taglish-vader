"""
normalizer.py - spelling normalizer (texting shortcuts / common typos -> real word).
One word -> one word. Add your own!
"""

NORMALIZE = {
    # negation shortcuts
    "d": "hindi", "ndi": "hindi", "nde": "hindi", "hnd": "hindi", "hndi": "hindi",
    "wla": "wala", "wlang": "walang", "wlng": "walang",
    # negative words
    "pngit": "pangit", "pangt": "pangit", "pngt": "pangit", "pnget": "panget",
    "msama": "masama", "mbagal": "mabagal", "nkakainis": "nakakainis",
    "nkakabwisit": "nakakabwisit", "nkakadismaya": "nakakadismaya",
    "dismayd": "dismayado", "dissapointed": "disappointed",
    "disapointed": "disappointed", "disappointd": "disappointed",
    # positive words
    "gnda": "ganda", "mganda": "maganda", "mgnda": "maganda", "magnda": "maganda",
    "mbait": "mabait", "msarap": "masarap", "mhusay": "mahusay",
    "mbilis": "mabilis", "slit": "sulit", "sult": "sulit", "lgit": "legit",
    "recomended": "recommended", "reccomended": "recommended",
    "rcmmnded": "recommended", "recommnded": "recommended",
    # intensifiers
    "sbrang": "sobrang", "sobrng": "sobrang", "sbra": "sobra",
    "grbe": "grabe", "grabeh": "grabe",
    # thanks
    "salmat": "salamat", "slmat": "salamat", "tnx": "thanks", "tnks": "thanks",
    "thx": "thanks", "ty": "thanks", "tysm": "thanks",
    # English shortcuts
    "gud": "good", "gd": "good", "nc": "nice", "gr8": "great", "amazin": "amazing",
    "okie": "ok", "okey": "okay", "oks": "ok", "okz": "ok",
    # slang spellings
    "waley": "wala", "wrpa": "werpa",
    # typos seen in real Shopee reviews
    "nman": "naman", "sna": "sana", "dismiya": "dismaya", "dismay": "dismaya",
    "nakakadismiya": "nakakadismaya", "nakakadismay": "nakakadismaya",
    # battery
    "lobat": "lowbat", "lowbatt": "lowbat", "malobat": "malowbat",
    "malowbatt": "malowbat", "ma-lowbat": "malowbat", "ma-lobat": "malowbat",
    "palowbat": "malowbat",
    # connect / working
    "ma-connect": "maconnect", "connected": "connect", "connecting": "connect",
}
