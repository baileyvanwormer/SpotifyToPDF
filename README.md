# SpotifyToPDF
Turn Spotify playlists into PDF's to store in case Spotify servers ever remove songs or go down.

**You must update the ngrok forwarding https address in app.py and Spotify.com everytime you restart flash and ngrok since the ngrok address changes everytime on the free plan**

Link to Spotify Dev site: https://developer.spotify.com/dashboard

*Key commands*:
    To start Flask: 
    
    cd into backend -> 
    
    python3 app.py

    To start ngrok (after Flask): New terminal -> 
    
    ngrok http --url=spotifytopdf.ngrok.app 127.0.0.1:5000
