import { Routes, Route, BrowserRouter } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";

function App() {
  console.log("App loaded");
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/dash" element={<DashboardPage />} />
    </Routes>
  );
}

export default App;