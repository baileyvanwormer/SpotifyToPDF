import LoginButton from "../components/LoginButton";

const LoginPage = () => {
  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h1>Spotify to PDF</h1>
      <p>Click below to log in with your Spotify account.</p>
      <LoginButton />
    </div>
  );
};

export default LoginPage;
