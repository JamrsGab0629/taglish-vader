"""
normalizer.py - spelling normalizer (texting shortcuts / common typos -> real word).
One word -> one word. Add your own!
"""

NORMALIZE = {
    # negation shortcuts
    "d": "hindi", "ndi": "hindi", "nde": "hindi", "hnd": "hindi", "hndi": "hindi",
    "wla": "wala", "wlang": "walang", "wlng": "walang", "hwag": "huwag", 
    # negative words
    "pngit": "pangit", "pangt": "pangit", "pngt": "pangit", "pnget": "panget",
    "msama": "masama", "mbagal": "mabagal", "nkakainis": "nakakainis",
    "nkakabwisit": "nakakabwisit", "nkakadismaya": "nakakadismaya",
    "dismayd": "dismayado", "dissapointed": "disappointed",
    "disapointed": "disappointed", "disappointd": "disappointed",
    "lier": "liar", "lie": "liar", "lying": "lie", "maling": "mali",
    # positive words
    "gnda": "ganda", "mganda": "maganda", "mgnda": "maganda", "magnda": "maganda",
    "mbait": "mabait", "msarap": "masarap", "mhusay": "mahusay",
    "mbilis": "mabilis", "slit": "sulit", "sult": "sulit", "lgit": "legit",
    "recomended": "recommended", "reccomended": "recommended",
    "rcmmnded": "recommended", "recommnded": "recommended",
    # intensifiers
    "sbrang": "sobrang", "sobrng": "sobrang", "sbra": "sobra", "subrang": "sobrang", "skbrang": "sobrang",
    "grbe": "grabe", "grabeh": "grabe",
    # thanks
    "salmat": "salamat", "slmat": "salamat", "tnx": "thanks", "tnks": "thanks",
    "thx": "thanks", "ty": "thanks", "tysm": "thanks", "thankyou": "thank you",
    # English shortcuts
    "gud": "good", "gd": "good", "nc": "nice", "gr8": "great", "amazin": "amazing",
    "okie": "ok", "okey": "okay", "oks": "ok", "okz": "ok",
    # slang spellings
    "waley": "wala", "wrpa": "werpa", "liget": "legit",
    # typos seen in real Shopee reviews
    "nman": "naman", "sna": "sana", "dismiya": "dismaya", "dismay": "dismaya",
    "nakakadismiya": "nakakadismaya", "nakakadismay": "nakakadismaya",
    # battery
    "lobat": "lowbat", "lowbatt": "lowbat", "malobat": "malowbat",
    "malowbatt": "malowbat", "ma-lowbat": "malowbat", "ma-lobat": "malowbat",
    "palowbat": "malowbat",
    # more typos seen in real Shopee reviews
    "ayuss": "ayos", "ayus": "ayos", "ayuz": "ayos", "nagustahan": "nagustuhan",
    "kpanget": "panget", "kpangit": "pangit", "lng": "lang", "oka": "okay", "okiee": "ok",
    "peru": "pero", 
    # typos + Cebuano seen in the watch-case / phone / shorts reviews
    "nuce": "nice", "medo": "medyo", "ayw": "ayaw", "mgkasya": "magkasya",
    "sayng": "sayang", "waisting": "wasting", "good's": "goods", "goodss": "goods",
    "makadissapoint": "nakakadisappoint", "makadisappoint": "nakakadisappoint",
    "nakakalungkot": "lungkot", "sadly": "sad", 
    "dissapoint": "disappoint", "dili": "hindi", "dli": "hindi", "dna": "hindi",
    "madaya": "daya", "ntapon": "natapon",
    # connect / working
    "ma-connect": "maconnect", "connected": "connect", "connecting": "connect",

    #new added
    "i wish" : "i wished", "akala": "kala", "mabango": "bango", "mabaho": "baho",
    "natapon": "tapon", "binudol": "budol", "bdol": "budol", "dyos" : "diyos ko",
    "jusko": "diyos ko", "jsko": "diyos ko", "expired" : "expire", "xpire": "expire",
    "frustrating": "frustrate", "frustration": "frustrate", "non-responsive": "unresponsive",
    "non responsive": "unresponsive", "nonresponsive": "unresponsive", "irresponsable": "irresponsible",
    "false advertisement": "false advertising", "false adverticement": "false advertising",
    "ibng store": "ibang store", "other store": "ibang store", "decieving": "deceive", "decieve": "deveive",
    "deceiving": "deceive", "fck": "fuck", "f*ck": "fuck", "maliit": "liit", "work well": "works well",
    "aestheticly" : "aesthetic", "aestetically": "aesthetic", "estetik": "astetik", "verygood": "very good",
    "working": "work", "damages": "damage", "damaged": "damage", "22o": "totoo", "tooto": "totoo", "toto": "totoo",
    "old stocks": "old, stock", "nagcharge": "nagcha-charge", "nachacharge": "nagcha-charge", "defected": "defect", 
    "deffect": "defect","scratches" :"scratch","mukha":"muka","kpangit" :"pangit","sanaall" :"sana all", 
    "nagana": "ayaw gumana","nman":"naman", "rhank": "thank", "rhanks": "thanks","functionable" : "function",
    "functionaly" : "function","sofer" : "super","prety" : "pretty", "subrang" : "sobrang","worst" : "worse",
    "magtagal": "mag tagal", "ang tagal": "matagal","nicee" : "nice","niceeee" : "nice" ,"bumili ulet" :"bumili ulit" ,
    "bibili ulit" :"bumili ulit","bumili uli" : "bumili ulit" , "bumile ulet" : "bumili ulit","bumile ulit" : "bumili ulit",
    "bumile ulet" : "bumili ulit","bumile ule" : "bumili ulit", "cutesy" : "cute", "cutesie" : "cute" 
    }
