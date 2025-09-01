import { useState, useEffect, useRef } from "react";

// COMPONENTS
import SolutionScreen from "./SolutionScreen";
import SolutionListModal from "./SolutionListModal";
import FileUploader from './FileUploader';
import TopBar from './TopBar';

// API CALLS
import {
  runModel,
  stopModel,
  validateSolution,
  customFetchSolutionCSV,
  customFetchInsightsCSV,
  customFetchStudentCountData,
  customFetchNameMapping,
} from './APIcalls';

// CSS
import './App.css';

class SolutionEntry {
    // Solution instance
    constructor(row) {
        this.class = row[0] || "Unknown";
        this.startTime = row[1] || "Unknown";
        this.endTime = row[2] || "Unknown";
        this.room = row[3] || "Unknown";
        this.maxCapacity = row[4] || "Unknown";
        this.currentCapacity = row[5] || "Unknown";
        this.teacher = row[6] || "Unknown";
        this.contract = row[7] || "Unknown";
        this.load = row[8] || "Unknown";
        this.student = row[9] || "Unknown";
        this.instrumentPenalty = row[10] || "Unknown";
        this.antiquityDayPenalty = row[11] || "Unknown";
        this.antiquityDeviationPenalty = row[12] || "Unknown";
        this.siblingMismatchPenalty = row[13] || "Unknown";
    }
}

function MainScreen() {
    const [output, setOutput] = useState("");
    const [solutionData, setSolutionData] = useState(null);
    const [insightsData, setInsightsData] = useState(null);
    const [studentCount, setStudentCountData] = useState(null);
    const [studentNames, setStudentNames] = useState([]);
    const [teacherNames, setTeacherNames] = useState([]);
    const [roomNames, setRoomNames] = useState([]);
    const [courseNames, setCourseNames] = useState([]);
    const [instrumentNames, setInstrumentNames] = useState([]);
    const [isRunning, setIsRunning] = useState(false);
    const [isHoveredRun, setIsHoveredRun] = useState(false);
    const [isHoveredLoad, setIsHoveredLoad] = useState(false);
    const [isContainerClickable, setIsContainerClickable] = useState(false);
    const [showSolution, setShowSolution] = useState(false);
    const [showConfirmModal, setShowConfirmModal] = useState(false);
    const [modalOpen, setModalOpen] = useState(false);
    const [showLoginAlertRun, setShowLoginAlertRun] = useState(false);
    const [showLoginAlertLoad, setShowLoginAlertLoad] = useState(false);
    const [showMissingInputAlertRun, setShowMissingInputAlertRun] = useState(false);
    const [resetUploader, setResetUploader] = useState(false);
    const [loadedFiles, setLoadedFiles] = useState([]);
    const [allLoaded, setAllLoaded] = useState(false);
    const [loadedSolution, setLoadedSolution] = useState(false);
    const [modelFinishedRunning, setModelFinishedRunning] = useState(false);

    const [loggedInUserId, setLoggedInUserId] = useState(() => {
        return sessionStorage.getItem("user_id") || null;
    });

    const outputRef = useRef(null);
    const controllerRef = useRef(null);
    const modalRef = useRef(null);
    const loginAlertRunRef = useRef(null);
    const MissingInputAlertRunRef = useRef(null);
    const loginAlertLoadRef = useRef(null);
    const confirmModalRef = useRef(null);

    const handleAuthSuccess = (user_id) => {
        setLoggedInUserId(user_id);
        // Keep users logged in wihle the tab is open, even after realoads
        sessionStorage.setItem("user_id", user_id);
    };

        const handleFilesLoaded = (files, allSuccessfullyLoaded) => {
            setLoadedFiles(files);
            setAllLoaded(allSuccessfullyLoaded);
    };

    useEffect(() => {
        // Retrieve user_id after reloads
        const savedUserId = sessionStorage.getItem("user_id");
        if (savedUserId) {
            setLoggedInUserId(savedUserId);
        }
    }, []);

    // Avoid reloads either when the model is running or when it has finished running
    useEffect(() => {
        const handleBeforeUnload = (e) => {
            if (isRunning || modelFinishedRunning) {
                e.preventDefault();
                e.returnValue = "";
            }
        };
        window.addEventListener("beforeunload", handleBeforeUnload);
        return () => {
            window.removeEventListener("beforeunload", handleBeforeUnload);
        };
    }, [isRunning, modelFinishedRunning]);

    // Autoscrolling of the model log
    useEffect(() => {
        if (outputRef.current) {
        outputRef.current.scrollTop = outputRef.current.scrollHeight;
        }
    }, [output]);

    // Allow outside click, Escape and Enter actions on modals
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.key === "Escape") {
                setShowConfirmModal(false);
                setModalOpen(false);
                setShowLoginAlertRun(false);
                setShowLoginAlertLoad(false);
            }

            if (e.key === "Enter") {
                if (showConfirmModal) {
                    setShowConfirmModal(false);
                    runModelWithState();
                }
            }
        };

        const handleClickOutside = (e) => {
            if (showConfirmModal) {
                if (
                    modalRef.current &&
                    !modalRef.current.contains(e.target)
                ) {
                    setShowConfirmModal(false);
                    return;
                }
            }

            if (showLoginAlertRun) {
                if (
                    loginAlertRunRef.current &&
                    !loginAlertRunRef.current.contains(e.target)
                ) {
                    setShowLoginAlertRun(false);
                    return;
                }
            }

            if (showLoginAlertLoad) {
                if (
                    loginAlertLoadRef.current &&
                    !loginAlertLoadRef.current.contains(e.target)
                ) {
                    setShowLoginAlertLoad(false);
                    return;
                }
            }

            if (modalOpen) {
                if (modalRef.current && !modalRef.current.contains(e.target)) {
                    setModalOpen(false);
                }
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        document.addEventListener("keydown", handleKeyDown);

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
            document.removeEventListener("keydown", handleKeyDown);
        };
    }, [showConfirmModal, showLoginAlertRun, showLoginAlertLoad, modalOpen]);

    // Called when a solution is selected from the saved solutions list
    const handleLoadSolution  = async (solutionId) => {
        try {
            // API Call
            const res = await validateSolution(loggedInUserId, solutionId);

            if (!res.ok) {
                throw new Error(`HTTP ${res.status}: ${await res.text()}`);
            }

            const data = await res.json();

            if (data.valid === true) {
                await Promise.all([
                    fetchSolutionData('True', solutionId),
                    fetchInsightsData('True', solutionId),
                    fetchStudentCount('True', solutionId),
                    fetchData('True', solutionId)
                ]);
            
            setLoadedSolution(true);

            } else {
                alert("Invalid solution folder: it does not exist or is incomplete.");
            }
        } catch (err) {
            console.error("Validation error:", err);
            alert("Failed to validate selected solution folder.");
        }
    };

    const filesDict = Object.fromEntries(
        loadedFiles.map(f => [f.file.name.replace('.json', ''), f.content])
    );

    // Called from handleRunModel
    const runModelWithState = async () => {
        try {
            setOutput("");
            setIsRunning(true);
            setIsHoveredRun(false);
            setIsContainerClickable(false);
        
            // STOP button functionality
            controllerRef.current = new AbortController();

            // API Call
            const response = await runModel(loggedInUserId, filesDict, controllerRef.current.signal);
        
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let done = false;
        
            while (!done) {
                const { value, done: doneReading } = await reader.read();
                setOutput((prevOutput) => prevOutput + decoder.decode(value, { stream: true }));
                done = doneReading;
            }

            if (!controllerRef.current.signal.aborted) {
                setModelFinishedRunning(true);
                setIsContainerClickable(true);
            }

        } catch (error) {
            if (error.name === "AbortError") {
                setOutput((prevOutput) => prevOutput + "\nProcess stopped by user.");
            } else {
                setOutput(`Error running the model: ${error.message || error}`);
            }
        } finally {
            setIsRunning(false);
        }
    };

    // Call when the run model button is pressed
    const handleRunModel = () => {
        if (isContainerClickable) {
            // A previous run has finished, and the user is attempting to run the model again
            // Re-running the modal will overwritte the previous run's generated solution
            setShowConfirmModal(true);
        } else {
            runModelWithState();
        }
    };
  
    // Called when the X icon on the run model bubtton is pressed
    const handleStopModel = async () => {
        try {
            // Stop the model and recieve confirmation
            // API Call
            const response = await stopModel();
            const data = await response.json();
            // Show stopping confirmation
            setOutput((prevOutput) => prevOutput + `\n${data.message}`);
        } catch (error) {
            setOutput((prevOutput) => prevOutput + `\nError stopping model: ${error.message || error}`);
        } finally {
            setIsContainerClickable(false);
        }
    };

    // Called from handleContainerClick
    const fetchData = async (customval, selection) => {
        // Extract label names
        try {
            await Promise.all([
                processNameMapping("get-student-names", setStudentNames, customval, selection),
                processNameMapping("get-teacher-names", setTeacherNames, customval, selection),
                processNameMapping("get-room-names", setRoomNames, customval, selection),
                processNameMapping("get-course-names", setCourseNames, customval, selection),
                processNameMapping("get-instrument-names", setInstrumentNames, customval, selection),
            ]);
            console.log("successfully fetched labels")
        } catch (error) {
            console.error("Error fetching name mappings:", error);
        }
    };

    // Called from handleContainerClick
    const fetchAndParseCSV = async (fetchFunc, ...args) => {
        // Helper function to extract data from CSV files and return rows
        try {
            // API Call
            const response = await fetchFunc(...args);
            if (!response.ok) throw new Error("Failed to fetch CSV");

            const text = await response.text();
            const rows = text.trim().split("\n").filter(row => row.trim() !== "");

            return rows;
        } catch (error) {
            console.error("Error fetching and parsing CSV:", error);
            throw error;
        }
    };

    // Called from handleContainerClick
    const fetchSolutionData = async (customval, selection) => {
        // Format Solution data 
        try {
            let rows;
            if (customval === 'True') {
                // API Call
                rows = await fetchAndParseCSV(() => customFetchSolutionCSV(loggedInUserId, selection));
            } else {
                // API Call
                selection = 'temp_sol';
                rows = await fetchAndParseCSV(() => customFetchSolutionCSV(loggedInUserId, selection));
            };
            const [header, ...dataRows] = rows.map(row => row.split(","));

            console.log(rows);

            // Each SolutionEntry object is a solution instance
            const formattedData = dataRows.map(row => new SolutionEntry(row));
            setSolutionData({
                chartLabels: header,
                chartData: dataRows.length,
                tableData: formattedData,
            });
            console.log('successfully formatted data');
            console.log(formattedData);

            setShowSolution(true);
        } catch (error) {
            console.error("Error fetching solution data:", error);
        }
    };

    // Called from handleContainerClick
    const fetchInsightsData = async (customval, selection) => {
        // Format Insights data
        try {
            let rows;
            if (customval === 'True') {
                // API Call
                rows = await fetchAndParseCSV(() => customFetchInsightsCSV(loggedInUserId, selection));
            } else {
                // API Call
                selection = 'temp_sol';
                rows = await fetchAndParseCSV(() => customFetchInsightsCSV(loggedInUserId, selection));
            };

            console.log(rows);

            const header = rows[0].split(",");
            const dataRow = rows[1].match(/(".*?"|[^",]+)(?=\s*,|\s*$)/g);

            const parseDict = (value) => {
                try {
                    if (typeof value === "string" && value.startsWith("\"{") && value.endsWith("}\"")) {
                        value = value.slice(1, -1).replace(/""/g, '"');
                    }
                    return value.startsWith("{") ? JSON.parse(value) : parseFloat(value);
                } catch (error) {
                    console.warn("Failed to parse dictionary:", value);
                    return {};
                }
            };

            const parseList = (value) => {
                try {
                    if (typeof value === "string" && value.startsWith("\"[") && value.endsWith("]\"")) {
                        value = value.slice(1, -1).replace(/""/g, '"');
                    }
                    return value.startsWith("[") ? JSON.parse(value) : [];
                } catch (error) {
                    console.warn("Failed to parse list:", value);
                    return [];
                }
            };

            const insightsData = {
                workloadBalanceIndex: parseFloat(dataRow[0]),
                dailyWorkloadDeviation: parseDict(dataRow[1]),
                underutilizedTeachers: parseDict(dataRow[2]),
                overloadedTeachers: parseDict(dataRow[3]),
                studentDistributionScore: parseFloat(dataRow[4]),
                roomUtilizationRate: parseFloat(dataRow[5]),
                peakHourCongestion: parseDict(dataRow[6]),
                roomUnderuse: parseDict(dataRow[7]),
                missingCourseStudents: parseList(dataRow[8]),
                missingInstrumentStudents: parseList(dataRow[9]),
                antiquityPenalties: parseDict(dataRow[10]),
                siblingPenalties: parseDict(dataRow[11]),
            };

            setInsightsData(insightsData);
        } catch (error) {
            console.error("Error fetching insights data:", error);
        }
    };

    // Called from fetchData, which is called from handleContainerClick
    const processNameMapping = async (endpoint, setDataFunction, customval, selection) => {
        // Extracts indexed name mappings for use in displaying labeled entities
        try {
            let rows;
            if (customval === 'True') {
                // API Call
                const modifiedEndpoint = `custom-${endpoint}`;
                rows = await fetchAndParseCSV(() => customFetchNameMapping(modifiedEndpoint, loggedInUserId, selection), modifiedEndpoint);
            } else {
                // API Call
                const modifiedEndpoint = `custom-${endpoint}`;
                selection = 'temp_sol';
                rows = await fetchAndParseCSV(() => customFetchNameMapping(modifiedEndpoint, loggedInUserId, selection), modifiedEndpoint);
            };

            if (!rows) return;

            const header = rows[0].split(",");
            const dataRows = rows.slice(1).map(row => row.split(","));

            const parsedData = dataRows.map(row => ({
                index: parseInt(row[0], 10),
                id: row[1],
                name: row[2]
            }));

            setDataFunction(parsedData);
        } catch (error) {
            // Already logged by fetchAndParseCSV
        }
    };

    // Called from handleContainerClick
    const fetchStudentCount = async (customval, selection) => {
        // Extracts sudent count per time slot for statistical purposes
        try {
            let rows;
            if (customval === 'True') {
                // API Call
                rows = await fetchAndParseCSV(() => customFetchStudentCountData(loggedInUserId, selection));
            } else {
                // API Call
                selection = 'temp_sol';
                rows = await fetchAndParseCSV(() => customFetchStudentCountData(loggedInUserId, selection));
            };

            if (!rows) return;

            const [header, ...dataRows] = rows.map(row => row.split(","));

            const studentCount = dataRows.map(row => ({
                timeSlot: row[0] || "Unknown",
                numStudents: row[1] || "Unknown",
            }));

            setStudentCountData(studentCount);
            setShowSolution(true);
        } catch (error) {
            // Already logged by fetchAndParseCSV
        }
    };

    // Called when the user wants to access the solution screen
    const handleContainerClick = () => {
        // Fetch model solution data upon accessing the solution screen
        if (!isContainerClickable) return;
        fetchSolutionData('False', '');
        fetchInsightsData('False', '');
        fetchStudentCount('False', '');
        fetchData('False', '');
    };

    // Triggered when the user wants to access the solution screen and all data has been successfully loaded
    if (showSolution && solutionData && insightsData && studentCount && loggedInUserId) {
        // Takes the user to the solution screen
        return <SolutionScreen 
        solutionData={solutionData} 
        insightsData={insightsData}
        studentCount={studentCount} 
        studentNames={studentNames}
        teacherNames={teacherNames}
        courseNames={courseNames}
        instrumentNames={instrumentNames}
        roomNames={roomNames}
        userID={loggedInUserId}
        loadedSolution={loadedSolution}
        />;
    }

    return (
        <div className="top-bar" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
            <div style={{ textAlign: "center", paddingTop: "60px", position: "relative" }}>
                <TopBar
                onLoginSuccess={handleAuthSuccess}
                onLogout={() => {}}
                isRunning={isRunning}
                handleStopModel={handleStopModel}
                setOutput={setOutput}
                setIsContainerClickable={setIsContainerClickable}
                setResetUploader={setResetUploader}
                showHeaderAsClickable={false}
            />
        </div>
        
        {/* Run / Stop Model */}
        <div className="main-content">
            <div
                className={!isRunning && !isContainerClickable ? "animatedRunContainer" : ""}
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    borderRadius: "20px",
                    border: "1px solid #ccc",
                    overflow: "hidden",
                    width: "fit-content",
                    margin: "auto",
                    backgroundColor: isRunning || isContainerClickable ? "#FFFFFF" : "transparent",
                    transition: "background 0.3s ease-in-out",
                }}
                >
                <button
                    onClick={() => {
                        if (!loggedInUserId) {
                            setShowLoginAlertRun(true);
                            return;
                        }

                        if (!allLoaded) {
                            setShowMissingInputAlertRun(true);
                            return;
                        }

                        handleRunModel();
                    }}
                    disabled={isRunning}
                    onMouseEnter={() => !isRunning && setIsHoveredRun(true)}
                    onMouseLeave={() => setIsHoveredRun(false)}
                    style={{
                    padding: "10px 20px",
                    fontSize: "18px",
                    fontWeight: "bold",
                    fontFamily: "Segoe UI, Roboto, sans-serif",
                    backgroundColor: isRunning ? "white" : "transparent",
                    border: "none",
                    cursor: isRunning ? "not-allowed" : "pointer",
                    flex: 1,
                    opacity: isRunning ? 0.5 : 1,
                    color: isHoveredRun && !isRunning ? "#555" : "black",
                    transition: "color 0.2s, transform 0.2s, background 0.3s",
                    }}
                >
                    RUN MODEL
                </button>

                <div style={{ width: "1px", backgroundColor: "#ccc", height: "100%" }}></div>

                <button
                    onClick={handleStopModel}
                    disabled={!isRunning}
                    onMouseEnter={(e) => isRunning && (e.target.style.color = "red")}
                    onMouseLeave={(e) => (e.target.style.color = isRunning ? "black" : "#ccc")}
                    style={{
                    padding: "10px 20px",
                    fontSize: "16px",
                    backgroundColor: "transparent",
                    border: "none",
                    cursor: isRunning ? "pointer" : "not-allowed",
                    opacity: isRunning ? 1 : 0.5,
                    color: isRunning ? "black" : "#ccc",
                    transition: "color 0.2s ease-in-out",
                    }}
                >
                    X
                </button>
                </div>

                {showLoginAlertRun && (
                <div 
                    style={{
                    position: "fixed",
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: "rgba(0,0,0,0.5)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    zIndex: 1000,
                    }}
                >
                    <div 
                    ref={loginAlertRunRef}
                    style={{
                            background: "#fff",
                            padding: "20px 30px",
                            borderRadius: "10px",
                            textAlign: "center",
                            boxShadow: "0 0 10px rgba(0,0,0,0.3)",
                            width: "90%",
                            maxWidth: "410px",
                            height: "auto",
                            maxHeight: "80vh",
                            display: "flex",
                            flexDirection: "column",
                            justifyContent: "center",
                        }}
                    >
                    <h2>Please Log In</h2>
                    <p>You must be logged in to run the model</p>
                    <div style={{ marginTop: "20px" }}>
                        <button
                        className="blue-ok-button"
                        onClick={() => setShowLoginAlertRun(false)}
                        >
                        OK
                        </button>
                    </div>
                    </div>
                </div>
                )}

                {showMissingInputAlertRun && (
                <div 
                    style={{
                    position: "fixed",
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: "rgba(0,0,0,0.5)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    zIndex: 1000,
                    }}
                >
                    <div 
                    ref={MissingInputAlertRunRef}
                    style={{
                            background: "#fff",
                            padding: "20px 30px",
                            borderRadius: "10px",
                            textAlign: "center",
                            boxShadow: "0 0 10px rgba(0,0,0,0.3)",
                            width: "90%",
                            maxWidth: "410px",
                            height: "auto",
                            maxHeight: "80vh",
                            display: "flex",
                            flexDirection: "column",
                            justifyContent: "center",
                        }}
                    >
                    <h2>Please Upload Required Data</h2>
                    <p>You must upload all required input data to run the model</p>
                    <div style={{ marginTop: "20px" }}>
                        <button
                        className="blue-ok-button"
                        onClick={() => setShowMissingInputAlertRun(false)}
                        >
                        OK
                        </button>
                    </div>
                    </div>
                </div>
                )}

                {/* Output Viewer */}
                <div
                ref={outputRef}
                onClick={handleContainerClick}
                style={{
                    marginTop: "20px",
                    margin: "20px auto",
                    maxWidth: "80%",
                    height: "300px",
                    overflowY: "hidden",
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                    border: "1px solid #ccc",
                    padding: "10px",
                    fontFamily: "monospace",
                    backgroundColor: isContainerClickable ? "rgba(200, 200, 200, 0.7)" : "white",
                    color: isContainerClickable ? "#555" : "black",
                    cursor: isContainerClickable ? "pointer" : "default",
                    transition: "background-color 0.3s ease-in-out",
                    animation: isContainerClickable ? "shinyEffect 15s ease-in-out infinite" : "none",
                    userSelect: "none",
                }}
                className={isContainerClickable ? "shinyEffect" : ""}
                >
                <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word", overflowWrap: "break-word" }}>
                    {output}
                </pre>
                </div>

                <FileUploader onFilesLoaded={handleFilesLoaded} loggedIn={!!loggedInUserId} resetTrigger={resetUploader} />

                {/* Load Solution Button */}
                <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    borderRadius: "20px",
                    border: "1px solid #ccc",
                    overflow: "hidden",
                    width: "fit-content",
                    margin: "40px auto",
                    backgroundColor: "#FFFFFF",
                }}
                >
                <button
                    onClick={() => {
                        if (!loggedInUserId) {
                            setShowLoginAlertLoad(true);
                            return;
                        }
                        setModalOpen(true);
                    }}
                    disabled={isRunning}
                    onMouseEnter={() => !isRunning && setIsHoveredLoad(true)}
                    onMouseLeave={() => setIsHoveredLoad(false)}
                    style={{
                    padding: "10px 20px",
                    fontSize: "16px",
                    backgroundColor: "transparent",
                    border: "none",
                    cursor: isRunning ? "not-allowed" : "pointer",
                    opacity: isRunning ? 0.5 : 1,
                    color: isHoveredLoad && !isRunning ? "#007bff" : "black",
                    transition: "color 0.2s ease-in-out",
                    }}
                >
                    Load Solution
                </button>
                </div>
            </div>

            {showLoginAlertLoad && (
            <div 
                style={{
                position: "fixed",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: "rgba(0,0,0,0.5)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                zIndex: 1000,
                }}
            >
                <div 
                ref={loginAlertLoadRef}
                style={{
                    background: "#fff",
                    padding: "20px 30px",
                    borderRadius: "10px",
                    textAlign: "center",
                    boxShadow: "0 0 10px rgba(0,0,0,0.3)",
                    width: "90%",
                    maxWidth: "410px",
                    height: "auto",
                    maxHeight: "80vh",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                }}
                >
                <h2>Please Log In</h2>
                <p>You must be logged in to load a saved solution</p>
                <div style={{ marginTop: "20px" }}>
                    <button
                    className="blue-ok-button"
                    onClick={() => setShowLoginAlertLoad(false)}
                    >
                    OK
                    </button>
                </div>
                </div>
            </div>
            )}

            {/* Modals */}
            <SolutionListModal
            isOpen={modalOpen}
            onClose={() => setModalOpen(false)}
            onLoadSolution={handleLoadSolution}
            userID={loggedInUserId}
            />

            {showConfirmModal && (
            <div ref={confirmModalRef}
                style={{
                position: "fixed",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: "rgba(0,0,0,0.5)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                zIndex: 1000,
                }}
            >
                <div
                ref={modalRef}
                style={{
                    background: "#fff",
                    padding: "20px 30px",
                    borderRadius: "10px",
                    textAlign: "center",
                    boxShadow: "0 0 10px rgba(0,0,0,0.3)",
                }}
                >
                <h2>Overwrite Solution?</h2>
                <p>A solution is already available. Running the model again will overwrite it.</p>
                <div
                    style={{
                    marginTop: "20px",
                    display: "flex",
                    justifyContent: "center",
                    gap: "10px",
                    }}
                >
                    <button className="modal-button cancel-button" onClick={() => setShowConfirmModal(false)}>
                    Cancel
                    </button>
                    <button
                    className="modal-button continue-button"
                    onClick={() => {
                        setShowConfirmModal(false);
                        runModelWithState();
                    }}
                    >
                    Continue
                    </button>
                </div>
                </div>
            </div>
            )}

            {/* Global Styles */}
            <style>
            {`
                @keyframes shinyEffect {
                0% { background-position: -200% 0; }
                50% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
                }

                .shinyEffect {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.6) 25%, rgba(200, 200, 200, 0.5) 50%, rgba(255, 255, 255, 0.6) 75%);
                background-size: 400% 400%;
                animation: shinyEffect 2s ease-in-out infinite;
                }

                @keyframes shinyWaves {
                0% { background-position: -150% 0; }
                50% { background-position: 150% 0; }
                100% { background-position: -150% 0; }
                }

                .animatedRunContainer {
                background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 25%, #eeeeee 50%, #f9f9f9 75%, #ffffff 100%);
                background-size: 400% 400%;
                animation: shinyWaves 6s ease-in-out infinite;
                }

                .modal-button {
                padding: 8px 16px;
                border: 1px solid transparent; 
                border: none;
                border-radius: 5px;
                font-weight: bold;
                cursor: pointer;
                transition: background-color 0.3s, transform 0.1s;
                }

                .cancel-button {
                background-color: #444;
                color: #FFFFFF;
                border: 1px solid #444;
                }

                .cancel-button:hover {
                color: #444;
                background-color: #FFFFFF;
                transform: scale(0.95);
                border: 1px solid #444;
                }

                .continue-button {
                background-color: #d11a2a;
                color: white;
                border: 1px solid #d11a2a;
                }

                .continue-button:hover {
                color: #d11a2a;
                background-color: #FFFFFF;
                border: 1px solid #d11a2a;
                transform: scale(0.95);
                }

                .blue-ok-button {
                padding: 8px 16px;
                border: 1px solid transparent; 
                border: none;
                border-radius: 5px;
                font-weight: bold;
                cursor: pointer;
                transition: background-color 0.3s, transform 0.1s;
                background-color: #007bff;
                color: white;
                border: 1px solid #007bff;
                }

                .blue-ok-button:hover {
                color: #007bff;
                background-color: #FFFFFF;
                border: 1px solid #007bff;
                transform: scale(0.95);
                }
            `}
            </style>
        </div>
    );
}

export default MainScreen;
