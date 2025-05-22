const LoginButton = () => {
    const handleLogin = () => {
      // Redirects to your Flask backend to start Spotify OAuth
      window.location.href = "https://spotifytopdf.ngrok.app/login"; // or your ngrok URL
    };
  
    return <button onClick={handleLogin}>Log in with Spotify</button>;
  };
  
  export default LoginButton;
  