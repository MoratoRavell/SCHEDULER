const API_BASE = "http://localhost:8000"; // Use .env for production

const fetchWithHandling = async (url, options = {}) => {
  const response = await fetch(url, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`HTTP ${response.status}: ${text}`);
  }
  return response;
};

export const runModel = (userId, inputData, signal) => {
  return fetchWithHandling(`${API_BASE}/run-model`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      data: inputData,  // This is the full input JSON
    }),
    signal,
  });
};

export const stopModel = () => {
  return fetchWithHandling(`${API_BASE}/stop-model`, { method: "POST" });
};

export const validateSolution = (userId, solutionId) => {
  return fetchWithHandling(`${API_BASE}/validate-solution`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, solution_id: solutionId }),
  });
};

export const fetchSolutionCSV = (solutionId) => {
  return fetchWithHandling(`${API_BASE}/get-solution`, {
    method: "POST",
    headers: {
      "Content-Type": "text/plain",
    },
    body: solutionId,
  });
};

export const customFetchSolutionCSV = (userId, solutionId) => {
  return fetchWithHandling(`${API_BASE}/custom-get-solution`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, solution_id: solutionId }),
  });
};

export const fetchInsightsCSV = () => {
  return fetchWithHandling(`${API_BASE}/get-insights?t=${Date.now()}`);
};

export const customFetchInsightsCSV = (userId, solutionId) => {
  return fetchWithHandling(`${API_BASE}/custom-get-insights`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, solution_id: solutionId }),
  });
};

export const fetchStudentCountData = () => {
  return fetchWithHandling(`${API_BASE}/get-student-count`);
};

export const customFetchStudentCountData = (userId, solutionId) => {
  return fetchWithHandling(`${API_BASE}/custom-get-student-count`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, solution_id: solutionId }),
  });
};

export const fetchNameMapping = (endpoint) => {
  return fetchWithHandling(`${API_BASE}/${endpoint}?t=${Date.now()}`);
};

export const customFetchNameMapping = (modifiedEndpoint, userId, solutionId) => {
  const url = `${API_BASE}/${modifiedEndpoint}?t=${Date.now()}`;

  return fetchWithHandling(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: userId,
      solution_id: solutionId,
    }),
  });
};

export const saveSolution = (userId, solutionId) => {
  return fetchWithHandling(`${API_BASE}/save-solution`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json", // Changed from text/plain
    },
    body: JSON.stringify({ user_id: userId, solution_id: solutionId }),
  });
};

export const fetchSolutionsList = (userId) => {
  return fetchWithHandling(`${API_BASE}/get-solutions-list?user_id=${encodeURIComponent(userId)}`);
};

export const deleteSolution = (userId, solutionId) => {
  return fetchWithHandling(`${API_BASE}/delete-solution`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, solution_id: solutionId }),
  });
};
