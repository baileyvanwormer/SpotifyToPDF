import LoginButton from "../components/LoginButton";

const LoginPage = () => {
  console.log("login page loaded");
  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h1>ExportMyMusic.com</h1>
      <p>Click below to log in with your Spotify account.</p>
      <LoginButton />
    </div>
  );
};

export default LoginPage;
