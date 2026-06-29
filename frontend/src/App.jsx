import { Routes, Route } from "react-router-dom";
import SearchPage from "./pages/SearchPage";
import DisambiguationPage from "./pages/DisambiguationPage";
import ArtistPage from "./pages/ArtistPage";
import ReleasePage from "./pages/ReleasePage";
import "./App.css";

function App() {
  return (
    <Routes>
      <Route path="/" element={<SearchPage />} />
      <Route path="/search" element={<DisambiguationPage />} />
      <Route path="/artist/:artistSlug" element={<ArtistPage />} />
      <Route path="/release/:mbid" element={<ReleasePage />} />
    </Routes>
  );
}

export default App;
