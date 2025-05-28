import { Routes, Route, BrowserRouter } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import Callback from "./pages/Callback"; // Adjust this path to match your structure

function App() {
  console.log("App loaded");
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/dash" element={<DashboardPage />} />
      <Route path="/callback" element={<Callback />} />
    </Routes>
  );
}

export default App;