# ExportMyMusic.com
Turn Spotify Liked Songs and playlists into .xlsx and .pdf files to store in case Spotify servers ever remove songs or go down. Planning to add functionality for other music streaming services in future versions.

Link to website: https://www.exportmymusic.com

Built using a React.JS frontend and a Python Flask backend. Using Redis and Celery for async background processes. Deployed on Vercel (frontend) and Railway (backend). Using Amazon s3 storage to save .xlsx and .pdf for download to manage traffic.

Future Feature Ideas Include: 
    - Add more streaming services to .xlsx and .pdf export
    - Add a way for streaming service users to create a playlist on their service, thru my site convert it into a playlist on a different site, then share it with a friend
    - Make the previously mentioned features available on Spotify, Apple Music, Amazon Music, Tidal, etc.
    - Cool listening statistics for users for every streaming service

Link to Spotify Dev site: https://developer.spotify.com/dashboard

*Key commands to start application for dev testing*:
    To start Redis:

    'cd backend -> brew services start redis -> redis-cli ping' (To ensure Redis is running properly)
    
    To start Flask: 
    
    'cd backend -> python3 app.py'

    To start Celery (must be after redis) ->

    'celery -A celery_worker.celery_app worker --loglevel=info'

    To start ngrok (must be after Flask): New terminal -> 'ngrok http --url=spotifytopdf.ngrok.app 127.0.0.1:5000'

    To start frontend:

    'cd frontend -> 'npm run build' -> npm run dev'

Using Postman for backend testing.

User Spotify access token is stored as a cookie rather than in URL query for security, see Postman. Want to reflect this in front end code for MVP.
