"""
lexicon.py - word or phrase -> score (-4 to +4).
Tip: add your own words here to make the analyzer smarter!
Words that are NOT listed score 0 (neutral). Zero-score phrases such as
"ok lang" stop the single word "ok" (+1) from matching inside them.
"""

LEXICON = {
    # ---------- POSITIVE (Tagalog) ----------
    "maganda": 2.5, "ganda": 2.5, "mabuti": 2.0, "mabait": 2.2,
    "mahusay": 2.5, "magaling": 2.5, "galing": 2.5, "swak": 2.0,
    "sulit": 2.5, "sulit na sulit": 3.2, "solid": 2.3, "astig": 2.5,
    "bongga": 2.5, "panalo": 2.5, "ayos": 1.8, "maayos": 2.0,
    "mabilis": 1.8, "mura": 1.5, "matibay": 2.2, "tibay": 2.0,
    "malinis": 1.8, "masarap": 2.6, "sarap": 2.5, "masaya": 2.5,
    "saya": 2.3, "nakakatuwa": 2.3, "gusto": 1.8, "nagustuhan": 2.3,
    "gusto ko": 2.3, "mahal ko": 3.0, "mahal na mahal": 3.2,
    "salamat": 1.2, "maraming salamat": 1.6, "maasikaso": 2.3,
    "magalang": 2.0, "kuntento": 2.2, "nakakabilib": 2.5,
    "mapagkakatiwalaan": 2.3, "maaasahan": 2.2, "komportable": 2.0,
    "presko": 1.5, "mabango": 2.0, "maaliwalas": 1.8, "mahal ang quality": 1.0,
    "sakto": 0.8, "pwede na": 0.0, "ok lang": 0.0, "okay lang": 0.0,
    "sakto lang": 0.0, "bait": 2.0, "ulit": 1.7, "responsable": 1.5,
    "well": 0.7, "works well": 1.5, "aesthetic" : 1.5, "very nice": 2.5,
    "stable": 0.45, "outstanding": 2.0, "real": 1.45, "totoo": 1.40,

    # ---------- POSITIVE IDIOMS ("walang masabi" = no complaints, praise) ----------
    "walang masabi": 2.8, "wala akong masabi": 2.8,

    # ---------- POSITIVE (English / Taglish slang) ----------
    "good": 2.4, "great": 3.1, "amazing": 3.2, "awesome": 3.1,
    "excellent": 3.2, "best": 3.2, "nice": 1.8, "perfect": 3.0,
    "love": 3.0, "loved": 3.0, "ok": 1.0, "okay": 1.0,
    "fast": 1.8, "quick": 1.5, "quickly": 1.5, "legit": 2.5, "trusted": 2.0, "recommended": 2.5,
    "recommend": 2.2, "worth it": 2.8, "worth": 2.0,
    "original": 1.5, "helpful": 2.0, "friendly": 2.0, "accommodating": 2.0,
    "satisfied": 2.2, "happy": 2.7, "thank": 1.0, "thanks": 1.2,
    "smooth": 1.8, "durable": 2.2, "affordable": 1.8, "cute": 1.8,
    "beautiful": 2.7, "delicious": 2.8, "yummy": 2.6, "clean": 1.8,
    "comfortable": 2.0, "wow": 2.2, "salute": 2.0, "lodi": 2.0,
    "gumagana": 1.5, "responsive": 1.2, "astetik": 1.5, "relax": 1.2,

    # ---------- "like" alone is NOT praise ("ndi same like sa picture"), only these ----------
    "i like": 1.8, "i liked": 2.0, "like it": 1.8, "like this": 1.8, "liked": 1.8, "will order": 2.0,
    "not order": -2.0, "will buy": 1.8, "not buy": -2.0,

    # ---------- found in real Shopee reviews (clothes + earbuds) ----------
    "goods": 2.0,                       # Filipino "goods" = good ("goods na goods")
    "true color": 1.5, "true size": 1.5, "true to size": 1.5,
    "manipis": -1.5, "nipis": -1.5,     # thin fabric = complaint
    "mainit": -1.2,                     # hot to wear / overheating
    "aberya": -2.0, "disappoint": -2.3, "disappointment": -2.5,
    "malayo sa advertisement": -2.2, "malayo sa picture": -2.2, "iba sa picture": -2.2,
    "not what in the picture": -2.3, "not like the picture": -2.3,
    "not as pictured": -2.3, "not as shown": -2.3,
    "hindi same": -1.8, "not same": -1.8, "hindi pareho": -1.8,
    "not received": -2.5, "did not receive": -2.5, "did not received": -2.5,
    "didn't receive": -2.5, "hindi dumating": -2.5, "di dumating": -2.5,
    "hindi natanggap": -2.5, "isa lang dumating": -2.0, "missing": -2.5,
    "false advertising": -2.5, "nagcha-charge": 2.0,

    # ---------- fit / size / wasted money (watch cases, clothes) ----------
    "unfit": -2.3, "incorrect size": -2.3, "too small": -2.0, "too big": -2.0,
    "too large": -2.0, "too tight": -2.0, "too loose": -2.0, "sikip": -1.0,
    "maliit": -1.5, "ma liit": -1.5, "maiksi": -1.2,
    "not as advertised": -2.3, "misleading": -2.3, "unresponsive": -2.0, "gasgas": -2.0,
    "sinayang": -2.3, "nasayang": -2.3, "wasted": -2.3, "wasted money": -2.8,
    "wasting": -2.0, "waste money": -2.8,
    "kasyang kasya": 2.0, "fits well": 2.0, "fit well": 2.0, "well fit": 2.0,
    "fit me well": 2.2, "fit na fit": 2.0, "bagay": 1.5, "tama": 1.0,
    "magaganda": 2.3, "gaganda": 2.3,
    # same words, other meaning: weather is hot / "galing" = "from" (not "skilled")
    "mainit ang panahon": 0.0, "mainit na panahon": 0.0,
    "galing pang": 0.0, "galing sa": 0.0, "galing china": 0.0, "no manual": -2.0,
    "old stock": -2.5, "rusty": -2.0, "iba dumating": -2.0, "iba pinadala": -2.0,
    "iba yung dumating": -2.0, "iba yung ipinadala": -2.0, 

    # ---------- IDIOMS (look negative, but are praise) ----------
    "cant be this good": 2.8, "can't be this good": 2.8,
    "cannot be this good": 2.8, "cant be this nice": 2.5,
    "can't be this nice": 2.5, "di ako makapaniwala": 1.5,
    "small but terrible": 2.5, "pa budol": 1.67,

    # ---------- NEGATIVE (Tagalog) ----------
    "pangit": -2.8, "panget": -2.8, "bulok": -3.0, "sira": -2.5,
    "nasira": -2.6, "sirang-sira": -3.0, "sira agad": -3.2,
    "masama": -2.5, "basura": -3.2, "peke": -3.0, "walang kwenta": -3.2,
    "walang silbi": -3.0, "sayang": -2.0, "sayang pera": -2.8,
    "mabagal": -2.0, "bagal": -2.0, "matagal": -1.2, "tagal": -1.5,
    "mahal": -1.2, "nakakainis": -2.5, "inis": -2.2, "galit": -2.5,
    "badtrip": -2.8, "bad trip": -2.8, "bwisit": -2.8, "nakakabwisit": -2.8,
    "nakakadismaya": -2.8, "dismayado": -2.8, "kadiri": -2.5,
    "nakakadiri": -2.7, "madumi": -2.0, "marumi": -2.0, "bastos": -2.8,
    "masungit": -2.3, "walang modo": -2.8, "pabaya": -2.3, "palpak": -2.8,
    "sablay": -2.3, "kulang": -1.5, "mali": -1.8, "problema": -1.5,
    "reklamo": -1.8, "basag": -2.3, "nabasag": -2.3, "punit": -1.8,
    "luma": -1.2, "ayoko": -2.0, "manloloko": -3.0, "niloko": -3.0,
    "nakakasuya": -2.3, "hindi gumagana": -2.5, "di gumagana": -2.5,
    "ayaw gumana": -2.0, "hindi sulit": -2.5, "di sulit": -2.5,
    "nakakaawa": -1.5, "nakakadisappoint": -2.7, "mabaho": -2.3,
    "maingay": -1.2, "ordinaryo": -0.2, "lunkot": -1.5, "daya": -1.7,
    "natapon": -2.0, "wala": -1.0, "nadismaya": -2.5, "nakakasama": -1.9,
    "dugyot": -1.8,"indi gumagana": -2.3, "di nagana": -2.3, "tamad": -2.3, "mahina": -2.5,

    # ---------- NEGATIVE (English / Taglish slang) ----------
    "bad": -2.5, "worst": -3.2, "terrible": -3.0, "horrible": -3.0,
    "awful": -3.0, "poor": -2.0, "hate": -3.0, "hated": -3.0,
    "scam": -3.5, "scammer": -3.5, "fake": -3.0, "waste": -2.5,
    "disappointed": -2.7, "disappointing": -2.7, "slow": -2.0,
    "late": -1.5, "delayed": -1.8, "broken": -2.6, "defective": -2.8,
    "damage": -2.5, "overpriced": -2.5, "pricey": -1.5, "rude": -2.8,
    "dirty": -2.2, "useless": -3.0, "trash": -3.0, "sucks": -2.8,
    "scammed": -3.3, "refund": -1.5, "return": -1.5,"complaint": -1.8, "issue": -1.2,
    "cheap quality": -2.2, "lousy": -2.5, "annoying": -2.5, "sad": -1.4, "stress": -1.5,
    "frustrate": -1.7, "liar": -2.2, "high blood": -2.5, "deceive": -1.5, "yupi": -1.0,
    "liit": -1.0, "ugly": -2.0, "deffective" : -2.7,"not charging": -2.5,

    # ---------- DOMAIN PHRASES (same word, different meaning) ----------
    "mabilis maubos": -2.5, "mabilis na maubos": -2.5, "mabilis maubusan": -2.5,
    "mabilis malowbat": -2.5, "mabilis ma-lowbat": -2.5, "mabilis ma-drain": -2.5,
    "mabilis masira": -3.0, "mabilis na masira": -3.0, "madaling masira": -3.0,
    "mabilis mabasag": -2.8, "madaling mabasag": -2.8,
    "mabilis mapunit": -2.6, "madaling mapunit": -2.6,
    "mabilis kumupas": -2.5, "madaling kumupas": -2.5,
    "mabilis uminit": -2.3, "mabilis na uminit": -2.3, "mabilis mag-init": -2.3,
    "mabilis kalawangin": -2.6, "mabilis mapudpod": -2.6, "mabilis madumi": -2.0,
    "mabilis mawala": -2.0, "mabilis ang pagkasira": -2.8, "pagkasira": -2.2,
    "masira agad": -3.0, "agad nasira": -3.0, "agad na nasira": -3.0,
    "ubos agad": -2.0, "uminit": -1.8, "umiinit": -1.8,
    "drains fast": -2.5, "drains quickly": -2.5, "fast drain": -2.5,
    "battery drain": -2.3, "overheat": -2.5, "overheating": -2.5, "heats up": -2.0,
    "mabilis mag-charge": 2.3, "mabilis ma-charge": 2.3, "mabilis mag-load": 2.0,
    "madali": 1.8, "bilis": 1.8, "congrats": 1.5, "congratulations": 1.5,
    "madaling gamitin": 2.2, "user friendly": 2.2, "user-friendly": 2.2,
    "long lasting" : 2.5, "ibang store": -1.2, "expectation vs reality": -1.0,

    # ---------- SLANG (Filipino / Taglish / Gen Z) ----------
    "petmalu": 2.8, "malupit": 2.5, "lupet": 2.5, "werpa": 2.5, "angas": 2.3,
    "bet": 1.8, "bet ko": 2.3, "bet na bet": 3.0, "pasok sa banga": 2.5,
    "pasok sa budget": 2.2, "walang tapon": 2.8, "ang tindi": 2.3,
    "pasabog": 2.5, "swabe": 2.0, "kilig": 2.0, "nakakakilig": 2.3,
    "nakakagana": 2.2, "labyu": 2.5, "pogi": 1.8, "gwapo": 1.8,
    "walang kupas": 2.0, "ayos na ayos": 2.5, "ok na ok": 2.5,
    "tamang tama": 2.2, "worth every peso": 3.0, "worth every penny": 3.0,
    "winner": 2.3, "goated": 2.8, "fire": 2.0, "lit": 1.8, "slaps": 2.3,
    "bussin": 2.5, "slay": 2.3, "dope": 2.3,
    "jeje": -1.5, "pabebe": -1.2, "epal": -2.0, "toxic": -2.5, "yuck": -2.2,
    "eww": -2.2, "ew": -2.0, "cringe": -2.0, "hassle": -2.0,
    "nakakabadtrip": -2.8, "bad vibes": -2.3, "red flag": -2.5, "mid": -1.5,
    "meh": -1.0, "sus": -1.5, "sketchy": -2.0, "scam alert": -3.5,
    "lugi": -2.3, "luge": -2.3, "nalugi": -2.5, "naloko": -2.8, "nauto": -2.5,
    "hay nako": -1.5, "hays": -1.5, "haynaku": -1.5, "haist": -1.5,
    "sakit sa ulo": -2.5, "nakakastress": -2.2, "nakakahiya": -1.8,
    "kakainis": -2.3, "nakakapikon": -2.5, "pikon": -1.5, "kupal": -3.0,
    "walang hiya": -3.0, "walanghiya": -3.0, "buwisit": -2.8, "peste": -2.5,
    "overrated": -2.0, "underwhelming": -2.0, "yikes": -1.5,
    "waste of money": -3.0, "false": 0.5,

    # ---------- "quality" alone is NOT praise: only with a word next to it ----------
    "good quality": 2.3, "great quality": 3.0, "high quality": 2.3,
    "best quality": 3.0, "nice quality": 2.0, "excellent quality": 3.0,
    "poor quality": -2.8, "bad quality": -2.8, "low quality": -2.5,
    "worst quality": -3.2, "mababang quality": -2.5, "pangit na quality": -2.8,
    "short lifespan": -2.5, "expire": -2.5, "work": 1.1,

    # ---------- BATTERY / WORKING (a long battery is praise, a draining one is not) ----------
    "malowbat": -1.5, "lowbat": -1.8, "madrain": -1.8, "ma-drain": -1.8,
    "low batter": -1.8,
    "maubos": -1.5, "maubusan": -1.5, "masira": -2.5, "mabasag": -2.3,
    "mapunit": -1.8, "kumupas": -2.0, "mag-init": -1.8, "mapudpod": -2.0,
    "kalawangin": -2.0, "mawala": -1.5,
    "bilis malowbat": -2.5, "bilis ma-lowbat": -2.5,
    "matagal malowbat": 2.3, "matagal ma-lowbat": 2.3, "matagal din malowbat": 2.3,
    "matagal maubos": 2.3, "matagal masira": 2.3, "tumatagal": 1.8,
    "long battery life": 2.5, "good battery": 2.2, "mahaba ang battery": 2.3,

    # ---------- NOT WORKING / WRONG ITEM ----------
    "not working": -2.6, "doesn't work": -2.6, "doesnt work": -2.6,
    "stopped working": -2.8, "no sound": -2.4, "walang sound": -2.4,
    "walang tunog": -2.4, "sabog": -2.3, "hirap mag connect": -2.0,
    "hirap magconnect": -2.0, "hindi ma connect": -2.3, "di ma connect": -2.3,
    "hindi maconnect": -2.3, "di maconnect": -2.3,
    "wrong item": -2.5, "wrong product": -2.5, "wrong color": -2.3,
    "wrong size": -2.0, "maling item": -2.5, "maling kulay": -2.3,
    "maling size": -2.0, "iba ang dumating": -2.5, "not as described": -2.5,
    "not original": -2.5, "counterfeit": -3.0, "peke": -3.0, "budol" : -3.0,
    "irresponsible": -2.5,

    # for products that has a smell, or fragrance
    "bango": 2.0, "amoy": 0.2, "baho": -2.0, "smell": 0.0, "mabula": 1.2,
    "classy": 1.8, "tapon": 1.6,

    # ---------- PROFANITY / HEAVY INSULTS (negative) ----------
    "tangina": -3.0, "tanginang": -3.0, "putangina": -3.2, "tangina mo": -3.2,
    "gago": -2.8, "gagong": -2.8, "tarantado": -3.0, "ulol": -2.8,
    "leche": -2.5, "bobo": -2.5, "fuck": -2.5,

    # words that has value but no category,
    "order": 1.0, "buying": 1.5,
}

EMOJIS = {
    # ---------- EMOJIS ----------
    "😍": 2.5, "😊": 1.8, "😀": 2.0, "😄": 2.1, "😁": 2.0, "🥰": 2.5,
    "❤": 2.0, "♥️": 2.0, "❤️":2.0,"💚": 2.0, "💖": 2.0, "🫰": 2.0, 
    "👍": 1.5, "👏": 1.7, "🔥": 1.5, "💯": 2.5, "🙏": 0.5, "😚": 1.0,
    "😡": -3.0, "😠": -2.8, "🤬": -2.8, "👎": -2.2, "😞": -2.2, "👌": 1.0,
    "😢": -2.0, "😭": -1.5, "🤮": -3.0, "💩": -2.8, "😒": -1.8, "😕": -0.25,
    "✅": 1.5, "🤗": 2.3, "‼️": -3.0, "😤": -1.9, "✖️": -1.5, "😌": 0.4,
}

# Text emoticons (checked in the raw text)
EMOTICONS = {":)": 2.0, ":D": 2.5, "<3": 2.5, ":(": -2.0, ":'(": -2.2, ">:(": -2.8}
