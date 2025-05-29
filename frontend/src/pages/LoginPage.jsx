import LoginButton from "../components/LoginButton";

const LoginPage = () => {
  console.log("login page loaded");
  return (
    <div class="login-header" style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h1>Connect Music Services</h1>
      <p>Log in to your Spotify account to begin exporting your playlists.</p>
      <LoginButton />
    </div>
  );
};

export default LoginPage;
