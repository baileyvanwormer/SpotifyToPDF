const LoginButton = () => {
    const handleLogin = () => {
      // Redirects to your Flask backend to start Spotify OAuth
      window.location.href = "https://api.exportmymusic.com/login"; // or your ngrok URL
    };
  
    return <button onClick={handleLogin}>Log in with Spotify</button>;
  };
  
  export default LoginButton;
  