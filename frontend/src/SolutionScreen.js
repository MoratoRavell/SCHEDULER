import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// COMPONENTS
import CalendarDisplay from "./CalendarDisplay";
import InsightsSection from "./InsightsSection";
import SaveModal  from "./SaveModal";
import ReturnHomeConfirmModal from "./ReturnHomeConfirmModal";
import TopBar from './TopBar';

// API CALLS
import {
 saveSolution,
} from './APIcalls';

// CSS
import './App.css';

function SolutionScreen({ solutionData, insightsData, studentCount, studentNames, teacherNames, courseNames, instrumentNames, roomNames, userID, loadedSolution}) {
  const [filterType, setFilterType] = useState("room");
  const [selectedFilter, setSelectedFilter] = useState("0"); // Default to Room 0
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [isHoveredSave, setIsHoveredSave] = useState(false);

  const [hasBeenSaved, setHasBeenSaved] = useState(false);

  const [isSaveModalOpen, setIsSaveModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [showReturnModal, setShowReturnModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (!hasBeenSaved && !loadedSolution) {
        e.preventDefault();
        e.returnValue = "";
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, [hasBeenSaved, loadedSolution]);

  const handleHeaderClick = () => {
    if (!hasBeenSaved && !loadedSolution) {
      setShowReturnModal(true);
    } else {
      sessionStorage.removeItem("currentScreen");
      navigate("/");
    }
  };

  const handleLogoutRedirect = () => {
    navigate('/'); // Main Screen
  };

  const handleConfirmReturn = () => {
    setShowReturnModal(false);
    sessionStorage.removeItem("currentScreen");
    navigate("/");
  };

  const onSaveButtonClick = () => {
    setIsSaveModalOpen(true);
  };

  // Calendar filter options
  const uniqueRooms = [...new Set(solutionData.tableData.map(item => item.room))]
    .sort()
    .map(id => ({ id, name: roomNames.find(room => room.index === Number(id))?.name || `Room ${id}` }));

  const uniqueTeachers = [...new Set(solutionData.tableData.map(item => item.teacher))]
    .sort()
    .map(id => ({ id, name: teacherNames.find(teacher => teacher.index === Number(id))?.name || `Teacher ${id}` }));

  const uniqueStudents = [...new Set(solutionData.tableData.map(item => item.student))]
    .sort()
    .map(id => ({ id, name: studentNames.find(student => student.index === Number(id))?.name || `Student ${id}` }));

  // Save solution
  const handleSaveClick = async (selection) => {
    setIsSaveModalOpen(false);

    try {
        // API call
        const res = await saveSolution(userID, selection);

        if (!res.ok) {
            throw new Error(`Failed to fetch save file: ${res.status}`);
        }

        toast.success("Solution saved!");
        setHasBeenSaved(true);
    } catch (err) {
        console.error("Save error:", err);
        alert("Failed to save the solution.");
    }
  };

  useEffect(() => {
    if (!selectedFilter) return;
  
    const slotsPerDay = 20; // (21:00 - 16:00) / 0.25h intervals
    const baseDate = new Date(2000, 0, 3); // Monday of a fixed week
  
    // Group data by startTime, endTime, room, and teacher
    const groupedClasses = {};
    solutionData.tableData.forEach((item) => {
      const key = `${item.startTime}-${item.endTime}-${item.room}-${item.teacher}`;
      if (!groupedClasses[key]) {
        groupedClasses[key] = {
          title: item.class,
          startTime: Number(item.startTime),
          endTime: Number(item.endTime),
          room: item.room,
          teacher: item.teacher,
          students: [],
        };
      }
      groupedClasses[key].students.push(item.student);
    });
  
    // Filter events based on the selected filter type and value (room, teacher, student)
    const filteredData = Object.values(groupedClasses)
      .filter((group) => {
        if (filterType === "room") {
          return group.room === selectedFilter;
        } else if (filterType === "teacher") {
          return group.teacher === selectedFilter;
        } else if (filterType === "student") {
          return group.students.includes(selectedFilter);
        }
        return true;
      })
      .map((group) => {
        const startSlot = group.startTime;
        const endSlot = group.endTime;

        const startDayIndex = Math.floor(startSlot / slotsPerDay);
        const startOffset = startSlot % slotsPerDay;
        const endDayIndex = Math.floor(endSlot / slotsPerDay);
        const endOffset = endSlot % slotsPerDay;

        const startDate = new Date(baseDate);
        startDate.setDate(baseDate.getDate() + startDayIndex);
        startDate.setHours(16 + Math.floor(startOffset / 4), (startOffset % 4) * 15);

        const endDate = new Date(baseDate);
        endDate.setDate(baseDate.getDate() + endDayIndex);
        endDate.setHours(16 + Math.floor(endOffset / 4), (endOffset % 4) * 15);

        return {
          title: `${group.title} (Room ${group.room})`,
          start: startDate,
          end: endDate,
          students: group.students,
        };
      });

    setEvents(filteredData);

  }, [selectedFilter, filterType, solutionData, insightsData, studentCount, studentNames, teacherNames, courseNames, instrumentNames, roomNames]);

  return (
    <>
      <div className="app-container" style={{ padding: "0px" }}>
        <div className="top-bar" style={{ height: '0vh', display: 'flex', flexDirection: 'column' }}>
          <div style={{ textAlign: "center", paddingTop: "30px", position: "relative" }}></div>
          <TopBar
            onHeaderClick={handleHeaderClick}
            showHeaderAsClickable={true}
            logoutConfirmMessage={
              !hasBeenSaved && !loadedSolution
                ? "If you log out now, the current solution will be permanently lost. Make sure to save it before logging out."
                : undefined // Fall back to default
            }
            afterLogout={handleLogoutRedirect}
          />
      </div>
      <div className="solution-container">
        <div style={{ marginBottom: "25px" }}>
          <div className="solution-header">SOLUTION</div>

          {showReturnModal && (
            <ReturnHomeConfirmModal
              onClose={() => setShowReturnModal(false)}
              onConfirm={handleConfirmReturn}
            />
          )}
        </div>
          <div className="filter-container">
            <label className="filter-label">Sort by:</label>
            <select
              className="filter-dropdown filter-primary"
              value={filterType}
              onChange={(e) => {
                const newFilterType = e.target.value;
                setFilterType(newFilterType);
                const firstOption =
                  newFilterType === "teacher" ? uniqueTeachers[0]?.id :
                  newFilterType === "student" ? uniqueStudents[0]?.id :
                  uniqueRooms[0]?.id;
                setSelectedFilter(firstOption);
              }}
            >
              <option value="room">Room</option>
              <option value="teacher">Teacher</option>
              <option value="student">Student</option>
            </select>

            <select
              className="filter-dropdown filter-secondary"
              value={selectedFilter}
              onChange={(e) => setSelectedFilter(e.target.value)}
            >
              {(filterType === "room" ? uniqueRooms :
                filterType === "teacher" ? uniqueTeachers :
                uniqueStudents
              ).map(({ id, name }) => (
                <option key={id} value={id}>{name}</option>
              ))}
            </select>
          </div>
          <CalendarDisplay
            events={events}
            selectedEvent={selectedEvent}
            setSelectedEvent={setSelectedEvent}
            courseNames={courseNames}
            instrumentNames={instrumentNames}
            roomNames={roomNames}
            studentNames={studentNames}
          />
          <InsightsSection
            insightsData={insightsData}
            studentCount={studentCount}
            studentNames={studentNames}
            teacherNames={teacherNames}
            courseNames={courseNames}
            instrumentNames={instrumentNames}
            roomNames={roomNames}
          />
          <div className='save-button-wrapper'>
            <div
              className={!hasBeenSaved && !loadedSolution ? "animatedRunContainer" : ""}
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
                onClick={onSaveButtonClick}
                disabled={saving}
                onMouseEnter={() => {
                  if (!saving) setIsHoveredSave(true);
                }}
                onMouseLeave={() => setIsHoveredSave(false)}
                style={{
                  padding: "10px 20px",
                  fontSize: "16px",
                  fontWeight: "bold",
                  fontFamily: "Segoe UI, Roboto, sans-serif",
                  backgroundColor: "transparent",
                  border: "none",
                  cursor: saving ? "not-allowed" : "pointer",
                  opacity: saving ? 0.5 : 1,
                  color: isHoveredSave && !saving ? "#007bff" : "black",
                  transition: "color 0.2s ease-in-out, transform 0.2s ease-in-out",
                }}
              >
                SAVE SOLUTION
              </button>
            </div>
          </div>
        </div>
      </div>
      <>
        <SaveModal
          isOpen={isSaveModalOpen}
          onClose={() => setIsSaveModalOpen(false)}
          onSave={handleSaveClick}
        />
      </>
      <ToastContainer
        position="top-right"
        autoClose={false}
        closeOnClick
        draggable
        pauseOnHover
        style={{ top: '70px' }}
      />

    </>
  );
}

export default SolutionScreen;
