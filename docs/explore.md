# گشت و گذار

## ویژگی ها
این صفحه کاربران را به شما نمایش خواهد داد، آن ها بر اساس "میزان شباهت بیوگرافی شما به بیوگرافی آنها" مرتب شده اند، این مرتب سازی توسط هوش مصنوعی و با استفاده از کتابخانه scikit-learn نوشته شده است، همچنین در این صفحه جنسیت و تعداد دنبال کنندگان هر کاربر نوشته شده، تا میزان ارتباط گیری کاربران بیشتر شود

## هوش مصنوعی
بخشی از کد مربوط به فهمیدن شباهت دو تا biography:

``` python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def text_similarity(text1, text2):
    vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    csim = cosine_similarity(vectors)
    return csim[0][1]
```