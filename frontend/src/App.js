import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import SolutionScreen from "./SolutionScreen";
import MainScreen from "./MainScreen";

function App() {
  return (
    <Router>
      <Routes>
        {/* Default route to MainScreen */}
        <Route path="/" element={<Navigate to="/MainScreen" />} />

        <Route path="/MainScreen" element={<MainScreen />} />
        <Route path="/SolutionScreen" element={<SolutionScreen />} />
      </Routes>
    </Router>
  );
}

export default App;