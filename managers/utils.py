from bs4 import element


def recursive_text_content(items, maintain_tag=False):
    data = []

    for item in items:
        if type(item) not in [element.Tag, list]:
            if item:
                data.append(item)
            continue
        elif 'contents' in dir(item):
            next_items = item.contents
        else:
            next_items = item

        if len(next_items):
            data.extend(recursive_text_content(next_items, maintain_tag))
        elif maintain_tag:
            data.append(item)

    return data
