WeatherNow AutoBlog - Setup Guide
---------------------------------
This package will auto-generate 3 blog posts per day and save them to /articles/.
Steps to install:

1) Copy all files to your GitHub Pages repository root.
   - scripts/generate_blog.py
   - scripts/requirements.txt
   - .github/workflows/auto_blog.yml
   - (Leave your existing site files like index.html, style.css as-is)

2) Add GitHub Action secret:
   - In your repo: Settings -> Secrets & variables -> Actions -> New repository secret
   - Name: OPENAI_API_KEY
   - Value: (your OpenAI API key)

3) Commit and push to GitHub. Open Actions tab and run the workflow manually the first time using 'Run workflow' -> this will generate articles/ folder.

4) Check the 'articles' folder in the repository after the workflow runs: you should see 3 new HTML files and /articles/images/*.jpg.

Notes & tips:
- The script uses the OpenAI ChatCompletion API. If your account/model differs, adjust the model name in scripts/generate_blog.py.
- For higher quality images or photographer credit, you can add UNSPLASH integration (requires UNSPLASH_ACCESS_KEY).
- The posts are generated to /articles/ to keep the site structure simple and AdSense-friendly.
- Monitor the generated content for quality and compliance especially during initial approval for AdSense.
