const LoginButton = () => {
    const handleLogin = () => {
      // Redirects to your Flask backend to start Spotify OAuth
      window.location.href = "https://backend-production-4f70.up.railway.app/login"; // or your ngrok URL
    };
  
    return <button onClick={handleLogin}>Log in with Spotify</button>;
  };
  
  export default LoginButton;
  