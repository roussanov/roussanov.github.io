import requests
import re
import shutil

pages = [
    "https://telegra.ph/Rabota-s-realnostyu-07-02",
    "https://telegra.ph/Najti-luchshie-foto-sluchajnym-oprosom-01-11",
    "https://telegra.ph/Model-i-algoritm-V-chem-raznica-04-11",
    "https://telegra.ph/Binary-search-Cheat-sheet-05-17",
    "https://telegra.ph/Princip-ehnergeticheskoj-sbalansirovannosti-08-06",
    "https://telegra.ph/b-logn-08-08", # index.html
]


def get_filename(page):
    items = re.findall(r"https://telegra.ph/([\w-]+)", page)
    assert(len(items) == 1)
    return items[0] + ".html"


def save_image(url: str):
    assert(url.startswith("/file"))
    r = requests.get("https://telegra.ph" + url, stream=True)
    with open('.' + url, "wb") as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)


def contains_script(line):
    return re.match("\s*<script.*</script>", line)


def get_all_image_paths(line):
    return re.findall("<img src=\"(/file/.+?.)\"", line)


def contains_end_tag(tag, line):
    return ("</"+tag+">") in line


def modify_page_content(text):
    new_lines = []
    more_articles_line_printed = False
    for line in text.splitlines():
        if contains_script(line):
            continue
        for image_path in get_all_image_paths(line):
            save_image(image_path)
        if contains_end_tag('body', line):
            new_lines.append(r'<script defer src="https://roussanov-github-io-commento.herokuapp.com/js/commento.js"></script><div id="commento"></div>')
            new_lines.append(r'<script> window.onload = function(ev){document.getElementById("commento").classList.add("tl_page_wrap");};</script>')
        if contains_end_tag('address', line) and not more_articles_line_printed:
            new_lines.append(r'<a rel="" href="https://roussanov.github.io/" target="">| More articles</a>')
            more_articles_line_printed = True
        if contains_end_tag('head', line):
            new_lines.append(r'<link href="/css/extra.css" rel="stylesheet">')
        new_lines.append(line)
    return "\n".join(new_lines)


for page in pages:
    r = requests.get(page)
    assert(r.status_code == 200)
    with open(get_filename(page), "w") as fd:
        fd.write(modify_page_content(r.text))
