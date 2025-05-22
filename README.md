# SpotifyToPDF
Turn Spotify playlists into PDF's to store in case Spotify servers ever remove songs or go down.

Built using a React.JS frontend and a Python Flask backend.

**ngrok is running on a custom domain https://spotifytopdf.ngrok.app**

Link to Spotify Dev site: https://developer.spotify.com/dashboard

*Key commands to start application for dev testing*:
    To start Flask: 
    
    cd into backend -> 
    
    python3 app.py

    To start ngrok (after Flask): New terminal -> 
    
    ngrok http --url=spotifytopdf.ngrok.app 127.0.0.1:5000

    To start frontend:

    cd into frontend ->

    npm run dev
