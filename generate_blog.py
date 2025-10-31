#!/usr/bin/env python3
import os, sys, json, random, requests
from datetime import datetime
from pathlib import Path
from html import escape
import openai

# Configuration
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
REPO_ARTICLES_DIR = Path("articles")
IMAGES_DIR = REPO_ARTICLES_DIR / "images"
POSTS_PER_RUN = 3
TOPICS_POOL = ["weather", "science", "nature", "news", "today weather"]

if not OPENAI_KEY:
    print("ERROR: OPENAI_API_KEY not set. Set it as a GitHub secret named OPENAI_API_KEY.")
    sys.exit(1)

openai.api_key = OPENAI_KEY

def slugify(s):
    s = s.lower().strip()
    for ch in " /\\:;,.!?&\"'()[]{}<>@#%^*+=~`|":
        s = s.replace(ch, "-")
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")

def call_openai(prompt):
    # Uses ChatCompletion to ask the model to return JSON with keys: title, meta, image_keyword, body
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional English content writer. Produce unique, human-like, AdSense-safe blog posts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=900
    )
    return response.choices[0].message.content.strip()

def generate_article(topic):
    # Build a simple prompt. We avoid f-strings here to keep the file safe.
    prompt = (
        "Generate an original English blog article about the topic: '{}'. "
        "Output valid JSON ONLY with these keys: "
        "\"title\": short SEO-friendly natural title (6-12 words), "
        "\"meta\": meta description (max 160 characters), "
        "\"image_keyword\": 2-4 words describing a royalty-free image, "
        "\"body\": the article HTML content (use <p>, <h2>, <ul>/<li> when needed), "
        "approximately between 400 and 750 words. Include a short 'Author: Weather Now' line at the end. "
        "Ensure content is original, suitable for Google AdSense, and do not include raw links in the body."
    ).format(topic)
    out = call_openai(prompt)
    try:
        start = out.index("{")
        end = out.rindex("}") + 1
        jtxt = out[start:end]
        data = json.loads(jtxt)
        return data
    except Exception as e:
        print("OpenAI output parsing error:", e)
        print("Raw output:\n", out)
        raise

def download_image_picsum(seed=None):
    seed = seed or str(random.randint(1000,9999))
    url = "https://picsum.photos/1200/628?random={}".format(seed)
    r = requests.get(url, timeout=30)
    if r.status_code == 200:
        return r.content, "Image courtesy of Picsum Photos"
    return None, ""

def ensure_dirs():
    REPO_ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def build_html(title, meta, img_file, img_credit, body_html):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='en'>")
    html.append("<head>")
    html.append("  <meta charset='UTF-8'>")
    html.append("  <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append("  <title>{}</title>".format(escape(title) + " - Weather Now"))
    html.append("  <meta name='description' content='{}'>".format(escape(meta)))
    html.append("  <link rel='stylesheet' href='/style.css'>")
    html.append("</head>")
    html.append("<body>")
    html.append("  <header><h1><a href='/index.html'>Weather Now</a></h1></header>")
    html.append("  <main><article>")
    html.append("    <h2>{}</h2>".format(escape(title)))
    html.append("    <p>Published: {}</p>".format(now))
    if img_file:
        html.append("    <figure><img src='/articles/images/{}' alt='{}'><figcaption>{}</figcaption></figure>".format(escape(img_file), escape(img_credit), escape(img_credit)))
    html.append(body_html)
    html.append("    <p><em>Author: Weather Now | Contact: darkestweb07@gmail.com</em></p>")
    html.append("  </article></main>")
    html.append("  <footer><p>&copy; 2025 Weather Now</p></footer>")
    html.append("</body></html>")
    return "\n".join(html)

def main():
    ensure_dirs()
    created = []
    for i in range(POSTS_PER_RUN):
        topic = random.choice(TOPICS_POOL)
        print("Generating:", topic)
        try:
            data = generate_article(topic)
        except Exception as e:
            print("Skipping article due to error:", e)
            continue
        title = data.get("title", "{} Update".format(topic.title()))
        meta = data.get("meta", "")
        image_keyword = data.get("image_keyword", topic)
        body = data.get("body", "<p>No content generated.</p>")
        slug = slugify(title)[:80] or "post-{}".format(int(datetime.utcnow().timestamp()))
        img_content, img_credit = download_image_picsum()
        img_filename = slug + ".jpg" if img_content else ""
        if img_content:
            (IMAGES_DIR / img_filename).write_bytes(img_content)
        html = build_html(title, meta, img_filename, img_credit, body)
        out_path = REPO_ARTICLES_DIR / (slug + ".html")
        out_path.write_text(html, encoding="utf-8")
        created.append(str(out_path))
        print("Created:", out_path)
    print("Done. Created files:", created)

if __name__ == '__main__':
    main()
