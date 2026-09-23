import { Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Play from "./pages/Play";
import Board from "./pages/Board";
import AdminLogin from "./pages/AdminLogin";
import AdminLayout from "./pages/AdminLayout";
import AdminEvents from "./pages/AdminEvents";
import AdminAvatars from "./pages/AdminAvatars";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/jugar" element={<Play />} />
      <Route path="/tablero/:code" element={<Board />} />
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<AdminEvents />} />
        <Route path="avatares" element={<AdminAvatars />} />
      </Route>
    </Routes>
  );
}
