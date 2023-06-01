import markdown

with open('pointstore_api.md', 'r') as f:
    text = f.read()
    html = markdown.markdown(text)

with open('pointstore_api.html', 'w') as f:
    f.write(html)
