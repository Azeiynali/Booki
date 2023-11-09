import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

def encode_md5(text):
    if text:
        md5_hash = hashlib.md5()
        md5_hash.update(text.encode('utf-8'))
        return md5_hash.hexdigest()
    else:
        return ""

def text_similarity(text1, text2):
    vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    csim = cosine_similarity(vectors)
    return csim[0][1]

def format_age(date):
    now = datetime.now()
    age = now - date

    if age.days < 0:
        return "تازه تولد شده"
    elif age.days == 0:
        if age.seconds < 60:
            return "به تازگی"
        elif age.seconds < 3600:
            minutes = age.seconds // 60
            return f"{minutes} دقیقه پیش"
        else:
            hours = age.seconds // 3600
            return f"{hours} ساعت پیش"
    elif age.days == 1:
        return "دیروز"
    elif age.days < 30:
        return f"{age.days} روز پیش"
    elif age.days < 365:
        months = age.days // 30
        days = age.days % 30
        return f"{months} ماه و {days} روز پیش"
    else:
        years = age.days // 365
        return f"{years} سال پیش"

def normalize(text):
    normalized = text
    cleaned_string = (str(cleaned_string).replace(b'\xdb\x96'.decode("utf-8"), ''))
    cleaned_string = re.sub("ي", "ی", cleaned_string)
    cleaned_string = re.sub("أ", "ا", cleaned_string)
    cleaned_string = re.sub("إ", "ا", cleaned_string)
    cleaned_string = re.sub("ة", "ه", cleaned_string)
    cleaned_string = (cleaned_string.replace(b'\xdb\x97'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xdb\x98'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xdb\x99'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xdb\x9a'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xdb\x9b'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xdb\x9c'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xdb\x9d'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xdb\x9e'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xd9\x8f'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xd9\x92'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xd9\x90'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xd9\x8e'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xd9\x91'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xd9\x8d'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xd9\x8c'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xd9\x8b'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xd9\xb0'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace(b'\xd9\xb0'.decode("utf-8"), ''))
    cleaned_string = (cleaned_string.replace('\n', ' '))
    normalized = re.sub("،", "", normalized)
    normalized = re.sub(".", "", normalized)
    normalized = re.sub(",", "", normalized)
    normalized = re.sub("\"", "", normalized)
    normalized = re.sub("'", "", normalized)
    normalized = re.sub("-", "", normalized)
    normalized = re.sub("+", "", normalized)
    normalized = re.sub(")", "", normalized)
    normalized = re.sub("(", "", normalized)
    normalized = re.sub("<.*>?.*<\/.*>?", "", normalized)
    normalized = re.sub("&", "", normalized)
    normalized = re.sub("\*", "", normalized)


def search(content, search_value):
    score = 0

    content_normalized = normalize(content)

    for token in normalize(search_value).split(" "):
        score += content_normalized.count(token)
    
    for token in normalize(content_normalized).split(" "):
        for search_token in normalize(search_value).split(" "):
            if text_similarity(token, search_token):
                score += .01

    return score