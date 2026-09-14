# FRAME — Django trailer platform

A responsive cinema catalog with movie details, trailer playback, genres, search, accounts, personal watchlists, community ratings, and a publishing studio inside your personal account.

## Run locally on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py seed_demo
.\.venv\Scripts\python manage.py createsuperuser
.\.venv\Scripts\python manage.py runserver 127.0.0.1:8011
```

Open http://127.0.0.1:8011/. Sign in with your administrator account and choose **My account → Open studio**. The studio is at `/account/studio/`.

## Publish from your account

Create genres, then add movies with synopsis, year, runtime, age rating, director, cast, country, and language. Upload posters/backdrops or enter image URLs. Paste a **full YouTube watch/share link**, or upload a trailer (MP4/WebM, maximum 200 MB). YouTube short links, watch links, Shorts, live, and embed links are accepted. Invalid and non-YouTube links are rejected. Existing trailer IDs are migrated to full links without removing movies.

An uploaded trailer takes priority over a YouTube link. Select **Clear** beside the current trailer upload to switch to YouTube. Mark a movie featured for the homepage, or turn off Published to keep a draft hidden. Movie and genre deletion asks for confirmation; deleting a movie also deletes its ratings and watchlist entries.

The studio supports movie and genre management, rating moderation, and owner-controlled editor roles under Members. Only owners (superusers) can grant editor access. Ordinary registration creates viewer accounts. Existing staff accounts retain their Django model permissions; the owner can assign the Editor role to provide catalog permissions. Django admin remains available at `/admin/` for advanced account and permission administration.

## Verification

```powershell
.\.venv\Scripts\python manage.py test
.\.venv\Scripts\python manage.py check
```

## Scope and deployment

This is a local trailer platform, not a production streaming service. Extension and size checks do not prove that a video is a trailer; editors must upload trailers only. Automated duration inspection, transcoding, subscriptions, text reviews, email verification, and configured password-reset email delivery are not included.

The optional demo seed creates sample metadata using remote TMDB artwork and YouTube embeds. It preserves existing movies and creates no users or ratings. External images, fonts and videos need internet access; YouTube playback depends on provider and regional availability. Use authorized artwork and trailers for your catalog.

For production, set `DJANGO_DEBUG=0`, a random `DJANGO_SECRET_KEY`, and `DJANGO_ALLOWED_HOSTS`. Configure HTTPS, a production WSGI server, static collection, database backups, rate limiting, separate-origin media storage, and reverse-proxy upload limits. See https://docs.djangoproject.com/en/5.2/topics/security/#user-uploaded-content.
# frame
