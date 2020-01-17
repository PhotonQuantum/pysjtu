import collections
from math import inf


def replace_keys(data, pairs):
    for from_key, to_key in pairs:
        if from_key in data:
            data[to_key] = data.pop(from_key)
    return data


def schema_post_loader(schema_ref, data):
    if isinstance(data, list):
        return schema_ref(many=True).load(data)
    elif isinstance(data, dict):
        return schema_ref().load(data)
    else:
        raise ValueError


def range_list_to_str(range_list):
    return "或".join((str(x) for x in flatten(range_list)))


def recognize_captcha(captcha_img):
    from io import BytesIO
    from PIL import Image
    import pytesseract
    raw_png = BytesIO(captcha_img)
    img = Image.open(raw_png)
    img = img.convert("L")
    table = [0] * 128 + [1] * 128
    img = img.point(table, '1')
    return pytesseract.image_to_string(img, config="-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz --psm 7")


def range_in_set(set_in):
    if len(set_in) == 0:
        return set()
    else:
        last_elem = -inf
        start = None
        for elem in set_in:
            if elem != last_elem + 1:
                if start:
                    yield range(start, last_elem + 1)
                start = elem
            last_elem = elem
        yield range(start, last_elem + 1)


def overlap(list1, list2):
    if not isinstance(list1, list): list1 = [list1]
    if not isinstance(list2, list): list2 = [list2]
    flatten1 = flatten(list1)
    flatten2 = flatten(list2)
    set1 = set(flatten1)
    return set1.intersection(flatten2)


def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el
