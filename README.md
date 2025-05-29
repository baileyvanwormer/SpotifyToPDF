# ExportMyMusic.com
Turn Spotify Liked Songs and playlists into .pdf and .xlsx files to store in case Spotify servers ever remove songs or go down.

Link to website: https://www.exportmymusic.com

Built using a React.JS frontend and a Python Flask backend. Using Redis and Celery for async background processes. Deployed on Vercel (frontend) and Railway (backend). Using Amazon s3 storage to save .xlsx and .pdf for download to manage traffic.

Link to Spotify Dev site: https://developer.spotify.com/dashboard

*Key commands to start application for dev testing*:
    To start Redis:

    cd into backend ->

    brew services start redis ->

    redis-cli ping (To ensure Redis is running properly)
    
    To start Flask: 
    
    cd into backend -> 
    
    python3 app.py

    To start Celery (must be after redis) ->

    celery -A celery_worker.celery_app worker --loglevel=info

    To start ngrok (must be after Flask): New terminal -> 
    
    ngrok http --url=spotifytopdf.ngrok.app 127.0.0.1:5000

    To start frontend:

    cd into frontend ->

    npm run dev

Using Postman for backend testing.

User Spotify access token is stored as a cookie rather than in URL query for security, see Postman. Want to reflect this in front end code for MVP.
