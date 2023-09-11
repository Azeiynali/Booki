import hashlib

def encode_md5(text):
    if text:
        md5_hash = hashlib.md5()
        md5_hash.update(text.encode('utf-8'))
        return md5_hash.hexdigest()
    else:
        return ""