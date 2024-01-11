# صفحه ثبت نام

## ویژگی ها

این صفحه با نام کاربری شروع می کند و رمز عبور، بیوگرافی، جنسیت، عکس پروفایل و شهر و کشور را می پرسد همچنین این صفحه در پایین یک لینک برای ورود به شما ارائه می کند تا کار راحت تر شود<br />
هنگام بررسی نام کاربری، آن را به سرور می فرستد و بررسی می کند که آیا آن از قبل وجود دارد یا نه، محدودیت ارسال نام کاربری، 4 بار در دقیقه است که در صورت بیشتر شدن، پیغام مناسبی را نمایش می دهد.<br />
همچنین هر کاربر مجاز به ساخت فقط یک کاربر در وب سایت در هر دقیقه می باشد<br />
رمز های عبور نیز با روش sha256 هش می شوند و با salt شان، در database ذخیره می شوند.<br />
نحوه هش کردن پسورد:

```python
import hashlib

def sha256_hash(password, salt):

    # sha256 object
    hash_object = hashlib.sha256()
    # encoding the password
    hash_object.update(password.encode())
    hashed_text = hash_object.hexdigest()
    # salt adding
    hashed_text = hashed_text + salt
    return hashed_text
```

این کد از کتابخانه hashlib که در پایتون هست و نیاز به نصب استفاده می کند

## هوش مصنوعی
در هنگام ثبت نام، ما برای استفاده بعدا، کلمات کلیدی مهم بیوگرافی شما را پیدا می کنیم، این کار توسط هوش مصنوعی و کتابخانه scikit-learn انجام می گیرد.<br />
کد پیدا کردن کلمات کلیدی یک متن:
``` python
from sklearn.feature_extraction.text import TfidfVectorizer

def find_keywords(text):
    '''Finding keywords in a text'''
    vectorizer = TfidfVectorizer()
    vectorizer.fit_transform([text])

    words = vectorizer.get_feature_names_out()

    return words[:25]
```

برای گرفتن بهترین نتیجه ما فقط 25 تا از کلیدی ترین کلمات را انتخاب می کنیم.