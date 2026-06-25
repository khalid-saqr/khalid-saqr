# Crawler validation checklist

After deployment, validate:

- `https://khalid-saqr.github.io/` loads on desktop, tablet, and mobile.
- View-source contains the canonical identity sentence.
- `data/person.schema.json` is valid JSON-LD.
- Google Rich Results / structured data tools can parse the ProfilePage/Person schema.
- `https://khalid-saqr.github.io/sitemap.xml` returns HTTP 200.
- `https://khalid-saqr.github.io/robots.txt` returns HTTP 200 and references the sitemap.
- `https://khalid-saqr.github.io/llms.txt` returns HTTP 200 and contains canonical identity guidance.
- Search Console URL inspection can fetch the page.
- Bing Webmaster Tools can fetch the sitemap.
- No direct email, phone number, home address, date of birth, or private repo name appears in public files.
