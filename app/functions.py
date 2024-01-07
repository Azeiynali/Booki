import re
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
    ageY = now.year - date.year
    ageM = now.month - date.month
    ageD = now.day - date.day
    ageH = now.hour - date.hour
    ageMI = now.minute - date.minute

    if not ageY and not ageM and not ageD and not ageH and ageMI < 10:
        return "به تازگی"
    elif not ageY and not ageM and not ageD and not ageH:
        return f"{ageMI} دقیقه پیش"
    elif not ageY and not ageM and not ageD:
        return f"{ageH} ساعت پیش"
    elif not ageY and not ageM and ageD == 1:
        return "دیروز"
    elif not ageY and not ageM:
        return f"{ageD} روز پیش"
    elif not ageY and not ageM == 1 and ageD > 2:
        return "ماه قبل"
    elif not ageY:
        if ageD > 2:
            return f"{ageM} ماه و {ageD} روز پیش"
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
            return f"{ageM} ماه"
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
        return f"{ageY} سال پیش"
        years = age.days // 365
        return f"{years} سال پیش"

def normalize(text):
    cleaned_string = text
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
    cleaned_string = re.sub(r"،", "", cleaned_string)
    cleaned_string = re.sub(r"\.", "", cleaned_string)
    cleaned_string = re.sub(r",", "", cleaned_string)
    cleaned_string = re.sub(r"\"", "", cleaned_string)
    cleaned_string = re.sub(r"'", "", cleaned_string)
    cleaned_string = re.sub(r"-", "", cleaned_string)
    cleaned_string = re.sub(r"\+", "", cleaned_string)
    cleaned_string = re.sub(r"\)", "", cleaned_string)
    cleaned_string = re.sub(r"\(", "", cleaned_string)
    cleaned_string = re.sub(r"\s\s", " ", cleaned_string)
    cleaned_string = re.sub(r"<.*>?.*<\/.*>?", "", cleaned_string)
    cleaned_string = re.sub(r"&", "", cleaned_string)
    cleaned_string = re.sub(r"\*", "", cleaned_string)

    return cleaned_string

def search_score(tags, content, search_value):
    score = 0

    content_normalized = normalize(content)

    for token in normalize(search_value).split(" "):
        score += content_normalized.count(token)
    
    for token in normalize(content_normalized).split(" "):
        if token:
            for search_token in normalize(search_value).split(" "):
                if search_token:
                    score += text_similarity(token, search_token) * 1.5
                    if search_token in tags:
                        score += 1


    return score

def find_keywords(text):
    vectorizer = TfidfVectorizer()
    vectorizer.fit_transform([text])

    words = vectorizer.get_feature_names_out()

    return words[:25]