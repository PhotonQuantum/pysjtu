import collections


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
