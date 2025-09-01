import { useState } from "react";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  PieChart,
  Pie,
  Cell,
} from "recharts";

// COMPONENTS
import {
  AntiquityChart,
  SiblingChart,
  IndexGaugeChart,
  RoomIndexGaugeChart,
  getBarColor,
  getUnderTeacherPieChartData,
  getPieChartData,
  PeakHourMatrix,
  GaugeChart,  
} from './insightsCharts';

// CSS
import './FlippableCard.css';

// Flippable Card Object
const FlippableCard = ({ title, frontContent, backContent }) => {
  const [isFlipped, setIsFlipped] = useState(false);

  return (
      <div className={`flippable-card ${isFlipped ? "flipped" : ""}`} onClick={() => setIsFlipped(!isFlipped)}>
          <div className="card-inner">
              <div className="card-front">
                  <h3>{title}</h3>
                  <div className="graph-content">{frontContent}</div>
              </div>
              <div className="card-back">
                  <h3>{title}</h3>
                  <div className="insight-content">{backContent}</div>
              </div>
          </div>
      </div>
  );
};

// Helper function fot the Peak Hour Congestion card
const convertTimeSlotToRealTime = (slot) => {
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];
    const startHour = 16;
    const intervalMinutes = 15;
    
    const dayIndex = Math.floor(slot / 20);
    const timeIndex = slot % 20;
  
    if (dayIndex < 0 || dayIndex > 4) return "Invalid Time";
  
    const hours = startHour + Math.floor(timeIndex / 4);
    const minutes = (timeIndex % 4) * intervalMinutes;
  
    return `${days[dayIndex]} ${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`;
  };

const InsightsSection = ({ insightsData, studentCount, studentNames, teacherNames, courseNames, instrumentNames, roomNames }) => {
    // Card titles
  const insightTitles = [
    "Peak Hour Congestion",
    "Room Underuse",
    "Room Utilization Rate",
    "Missing Course Students",
    "Sibling Penalties",
    "Underutilized Teachers",
    "Workload Balance Index",
    "Daily Workload Deviation",
    "Missing Instrument Students",
    "Antiquity Penalties",
  ]; 

    return (
        <div className="insights-wrapper">
            <div className="insights-container">
                {insightTitles.map((title, index) => (
                    <FlippableCard 
                    key={index}
                    title={title}
                    frontContent={
                        title === "Daily Workload Deviation" ? (
                        <div className="barchart-container">
                            <ResponsiveContainer width="90%" height="100%">
                                <BarChart
                                    data={Object.entries(insightsData.dailyWorkloadDeviation).map(([teacherID, score]) => ({
                                        name: `T${teacherID}`, 
                                        score
                                    }))}
                                    style={{ cursor: "pointer" }}
                                >
                                    <XAxis dataKey="name" height={15} />
                                    <YAxis width={30} tickMargin={5} />
                                    <Bar dataKey="score">
                                        {Object.entries(insightsData.dailyWorkloadDeviation).map(([_, score], index) => (
                                            <Cell key={index} fill={getBarColor(score)} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>        
                        ) : title === "Underutilized Teachers" ? (
                        <div className="chart-container">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart style={{ cursor: "pointer" }}>
                                    <Pie
                                        className="teachers-sector"
                                        data={getUnderTeacherPieChartData(insightsData.underutilizedTeachers)}
                                        dataKey="value"
                                        nameKey="label"
                                        cx="50%"
                                        cy="50%"
                                        outerRadius={75}
                                        innerRadius={50}
                                        label
                                    >
                                        {getUnderTeacherPieChartData(insightsData.underutilizedTeachers).map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                </PieChart>
                            </ResponsiveContainer>
                        </div>                
                        ) : title === "Room Underuse" ? (
                        <div className="chart-container">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart style={{ cursor: "pointer" }}>
                                    <Pie
                                        className="room-underuse-sector"
                                        data={getPieChartData(insightsData.roomUnderuse)}
                                        dataKey="value"
                                        nameKey="label"
                                        cx="50%"
                                        cy="50%"
                                        outerRadius={75}
                                        innerRadius={50}
                                        fill="#8884d8"
                                        label
                                    >
                                        {getPieChartData(insightsData.roomUnderuse).map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                </PieChart>
                            </ResponsiveContainer>
                        </div>                
                        ) : title === "Room Utilization Rate" ? (
                        <div className="indexgaugechart-container">
                            <RoomIndexGaugeChart 
                                key={insightsData.roomUtilizationRate}
                                value={insightsData.roomUtilizationRate}
                                label="Room Utilization Rate"
                            />
                        </div>
                        ) : title === "Sibling Penalties" ? (
                        <div className="chart-container">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart style={{ cursor: "pointer" }}>
                                    <Pie
                                        className="teachers-sector"
                                        data={SiblingChart(insightsData.siblingPenalties)}
                                        dataKey="value"
                                        nameKey="label"
                                        cx="50%"
                                        cy="50%"
                                        outerRadius={75}
                                        innerRadius={50}
                                        label
                                    >
                                        {SiblingChart(insightsData.siblingPenalties).map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                        ) : title === "Workload Balance Index" ? (
                        <div className="indexgaugechart-container">
                            <IndexGaugeChart 
                                key={insightsData.workloadBalanceIndex}
                                value={insightsData.workloadBalanceIndex}
                                label="Workload Balance Index"
                            />
                        </div>
                        ) : title === "Peak Hour Congestion" ? (
                            <div className="matrix-container">
                            <PeakHourMatrix 
                                label="Missing Instrument Students"
                                studentCount={studentCount}
                            />
                        </div>
                        ) : title === "Missing Course Students" ? (
                        <div className="gaugechart-container">
                            <GaugeChart 
                                value={(insightsData.missingCourseStudents.length / studentNames.length) * 100}
                                label="Missing Course Students"
                            />
                        </div>
                    ) : title === "Missing Instrument Students" ? (
                        <div className="gaugechart-container">
                            <GaugeChart 
                                value={(insightsData.missingInstrumentStudents.length / studentNames.length) * 100}
                                label="Missing Instrument Students"
                            />
                        </div>                             
                        ) : title === "Antiquity Penalties" ? (
                        <div className="chart-container">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart style={{ cursor: "pointer" }}>
                                    <Pie
                                        className="teachers-sector"
                                        data={AntiquityChart(insightsData.antiquityPenalties)}
                                        dataKey="value"
                                        nameKey="label"
                                        cx="50%"
                                        cy="50%"
                                        outerRadius={75}
                                        innerRadius={50}
                                        label
                                    >
                                        {AntiquityChart(insightsData.antiquityPenalties).map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                </PieChart>
                            </ResponsiveContainer>
                        </div>                  
                        ) : null
                    }
                    backContent={
                        title === "Daily Workload Deviation" ? (
                        <div className="scrollable-list">
                            {Object.entries(insightsData.dailyWorkloadDeviation).length > 0 ? (
                                Object.entries(insightsData.dailyWorkloadDeviation)
                                    .sort((a, b) => b[1] - a[1]) // Sort by score in descending order
                                    .map(([teacherID, score], index) => {
                                        const teacher = teacherNames.find(t => t.index === Number(teacherID));
                                        return (
                                            <div key={index} className="list-item">
                                                <span className="list-id">{teacher ? teacher.name : `Unknown (${teacherID})`}</span>
                                                <span className="score">{score.toFixed(2)}</span>
                                            </div>
                                        );
                                    })
                            ) : (
                                <p className="empty-message">No data</p>
                            )}
                        </div>
                        ) : title === "Underutilized Teachers" ? (
                            <div className="scrollable-list">
                                {Object.entries(insightsData.underutilizedTeachers).length > 0 ? (
                                    Object.entries(insightsData.underutilizedTeachers)
                                        .sort((a, b) => a[1] - b[1]) // Sort by score in ascending order
                                        .map(([teacherID, score]) => {
                                            const teacher = teacherNames.find(t => t.index === Number(teacherID));
                                            return (
                                                <div key={teacherID} className="list-item">
                                                    <span className="list-id">{teacher ? teacher.name : `Unknown (${teacherID})`}</span>
                                                    <span className="score">{score.toFixed(2)}</span>
                                                </div>
                                            );
                                        })
                                ) : (
                                    <p className="empty-message">No underutilized teachers</p>
                                )}
                            </div>
                        ) : title === "Room Underuse" ? (
                            <div className="scrollable-list">
                                {Object.entries(insightsData.roomUnderuse).length > 0 ? (
                                    Object.entries(insightsData.roomUnderuse)
                                        .sort((a, b) => a[1] - b[1]) // Sort by score in ascending order
                                        .map(([roomID, score]) => {
                                            const room = roomNames.find(r => r.index === Number(roomID));
                                            return (
                                                <div key={roomID} className="list-item">
                                                    <span className="list-id">{room ? room.name : `Unknown (${roomID})`}</span>
                                                    <span className="score">{score.toFixed(2)}</span>
                                                </div>
                                            );
                                        })
                                ) : (
                                    <p className="empty-message">No underutilized rooms</p>
                                )}
                            </div>
                        ) : title === "Room Utilization Rate" ? (
                            <div className="scrollable-list single-score">
                                {insightsData.roomUtilizationRate !== undefined ? (
                                    <div className="list-item">
                                        <span className="score">{insightsData.roomUtilizationRate.toFixed(2)}</span>
                                    </div>
                                ) : (
                                    <p className="empty-message">No data available</p>
                                )}
                            </div>
                        ) : title === "Sibling Penalties" ? (
                            <div className="scrollable-list">
                                {Object.entries(insightsData.siblingPenalties).length > 0 ? (
                                    Object.entries(insightsData.siblingPenalties)
                                        .sort((a, b) => b[1] - a[1]) // Sort by amount in descending order
                                        .map(([studentID, amount]) => {
                                            const student = studentNames.find(s => s.index === Number(studentID));
                                            return (
                                                <div key={studentID} className="list-item">
                                                    <span className="list-id">{student ? student.name : `Unknown (${studentID})`}</span>
                                                    <span className="score">{amount}</span>
                                                </div>
                                            );
                                        })
                                ) : (
                                    <p className="empty-message">No sibling penalties</p>
                                )}
                            </div>
                        ) : title === "Workload Balance Index" ? (
                            <div className="scrollable-list single-score">
                                {insightsData.workloadBalanceIndex !== undefined ? (
                                    <div className="list-item">
                                        <span className="score">{insightsData.workloadBalanceIndex.toFixed(2)}</span>
                                    </div>
                                ) : (
                                    <p className="empty-message">No data available</p>
                                )}
                            </div>
                        ) : title === "Peak Hour Congestion" ? (
                            <div className="scrollable-list">
                                {Object.entries(insightsData.peakHourCongestion).length > 0 ? (
                                    Object.entries(insightsData.peakHourCongestion)
                                        .sort((a, b) => b[1] - a[1]) // Sort by student count in descending order
                                        .map(([timeSlot, studentCount]) => (
                                            <div key={timeSlot} className="list-item">
                                                <span className="list-id">{convertTimeSlotToRealTime(Number(timeSlot))}</span>
                                                <span className="score">{studentCount}</span>
                                            </div>
                                        ))
                                ) : (
                                    <p className="empty-message">No congestion data</p>
                                )}
                            </div>
                        ) : title === "Missing Course Students" ? (
                            <div className="scrollable-list">
                                {insightsData.missingCourseStudents.length > 0 ? (
                                    insightsData.missingCourseStudents
                                        .sort((a, b) => a - b) // Sort by student IDs in ascending order
                                        .map((studentId, index) => {
                                            const student = studentNames.find(s => s.index === Number(studentId));
                                            return (
                                                <div key={index} className="list-item">
                                                    <span className="list-id">{student ? student.name : `Unknown (${studentId})`}</span>
                                                </div>
                                            );
                                        })
                                ) : (
                                    <p className="empty-message">No missing course students</p>
                                )}
                            </div>
                        ) : title === "Missing Instrument Students" ? (
                            <div className="scrollable-list">
                                {insightsData.missingInstrumentStudents.length > 0 ? (
                                    insightsData.missingInstrumentStudents
                                        .sort((a, b) => a - b) // Sort by student IDs in ascending order
                                        .map((studentId, index) => {
                                            const student = studentNames.find(s => s.index === Number(studentId));
                                            return (
                                                <div key={index} className="list-item">
                                                    <span className="list-id">{student ? student.name : `Unknown (${studentId})`}</span>
                                                </div>
                                            );
                                        })
                                ) : (
                                    <p className="empty-message">No missing instrument students</p>
                                )}
                            </div>
                        ) : title === "Antiquity Penalties" ? (
                            <div className="scrollable-list">
                                {Object.entries(insightsData.antiquityPenalties).length > 0 ? (
                                    Object.entries(insightsData.antiquityPenalties)
                                        .sort((a, b) => b[1] - a[1]) // Sort by penalties in descending order by amount
                                        .map(([studentID, amount]) => {
                                            const student = studentNames.find(s => s.index === Number(studentID));
                                            return (
                                                <div key={studentID} className="list-item">
                                                    <span className="list-id">{student ? student.name : `Unknown (${studentID})`}</span>
                                                    <span className="score">{amount}</span>
                                                </div>
                                            );
                                        })
                                ) : (
                                    <p className="empty-message">No antiquity penalties</p>
                                )}
                            </div>                  
                        ) : (
                            "[Data Visualization Here]"
                        )
                    }
                />
            ))}
            </div>
        </div>
    );
};

export default InsightsSection;
