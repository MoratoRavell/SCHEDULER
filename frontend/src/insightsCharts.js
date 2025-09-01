import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  RadialBarChart, 
  RadialBar, 
  PolarAngleAxis
} from "recharts";

// CARD NAME: Antiquity Penalties
export const AntiquityChart = (data) => {
  const antiquityRanges = [
    { label: "0", min: 0, max: 0, color: "#4CAF50" }, // Green
    { label: "1", min: 1, max: 1, color: "#8BC34A" }, // Light Green
    { label: "2", min: 2, max: 2, color: "#FFD700" }, // Yellow
    { label: "3", min: 3, max: 3, color: "#FFB6B6" }, // Light Red
    { label: "4", min: 4, max: 4, color: "#FF0000" } // Red
  ];

  const rangeCounts = antiquityRanges.map(({ min, max, color }) => ({
      label: `${min}-${max}`,
      value: Object.values(data).filter(score => score >= min && score <= max).length,
      color,
  }));

  return rangeCounts.filter(entry => entry.value > 0);
};

// CARD NAME: Sibling Penalties
export const SiblingChart = (data) => {
  const siblingRanges = [
    { label: "0", min: 0, max: 0, color: "#4CAF50" }, // Green
    { label: "1", min: 1, max: 1, color: "#8BC34A" }, // Light Green
    { label: "2", min: 2, max: 2, color: "#FFD700" }, // Yellow
    { label: "3", min: 3, max: 3, color: "#FFB6B6" }, // Light Red
    { label: "4", min: 4, max: 4, color: "#FF0000" } // Red
  ];

  const rangeCounts = siblingRanges.map(({ min, max, color }) => ({
      label: `${min}-${max}`,
      value: Object.values(data).filter(score => score >= min && score <= max).length,
      color,
  }));

  return rangeCounts.filter(entry => entry.value > 0);
};

// CARD NAME: Missing Course Students
export const IndexGaugeChart = ({ value }) => {
  const getGaugePieColor = (value) => {
    if (value >= 0 && value < 0.25) return "#4CAF50";  // Green
    if (value >= 0.25 && value < 0.50) return "#8BC34A";  // Light Green
    if (value >= 0.50 && value < 0.75) return "#FFD700";  // Yellow
    if (value >= 0.75 && value < 0.90) return "#FFB6B6";  // Light Red
    if (value >= 0.90 && value < 1.00) return "#FF0000";  // Red
    return "#FF0000";  // Red
  };

  const scaledValue = Math.max(0, Math.min(value * 100, 100));  

  const data = [{ value: scaledValue, fill: getGaugePieColor(value) }];

  return (
    <div className="indexgaugechart-container">
      <ResponsiveContainer width="100%" height={200}>
        <RadialBarChart 
          className="radialgaugechart"
          style={{ cursor: "pointer" }}
          cx="50%" 
          cy="75%" 
          innerRadius={75} 
          outerRadius={100}
          startAngle={180} 
          endAngle={0} 
          barSize={25} 
          data={data}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
          <RadialBar
            minAngle={15}
            dataKey="value"
            cornerRadius={0}
            fill={getGaugePieColor(value)}
            background={{ fill: "#e0e0e0" }}
          />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="gauge-value">{Math.round(scaledValue)}</div>
    </div>
  );
};

// CARD NAME: Room Utilitzation Rate
export const RoomIndexGaugeChart = ({ value }) => {
  const getGaugePieColor = (value) => {
    if (value >= 0 && value < 0.25) return "#FF0000";  // Red
    if (value >= 0.25 && value < 0.50) return "#FFB6B6";  // Light Red
    if (value >= 0.50 && value < 0.75) return "#FFD700";  // Yellow
    if (value >= 0.75 && value < 0.90) return "#8BC34A";  // Light Green
    if (value >= 0.90 && value < 1.00) return "#4CAF50";  // Green
    return "#FF0000";  // Red
  };

  const scaledValue = Math.max(0, Math.min(value * 100, 100));  

  const data = [{ value: scaledValue, fill: getGaugePieColor(value) }];

  return (
    <div className="indexgaugechart-container">
      <ResponsiveContainer width="100%" height={200}>
        <RadialBarChart 
          className="radialgaugechart"
          style={{ cursor: "pointer" }}
          cx="50%" 
          cy="75%" 
          innerRadius={75} 
          outerRadius={100}
          startAngle={180} 
          endAngle={0} 
          barSize={25} 
          data={data}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
          <RadialBar
            minAngle={15}
            dataKey="value"
            cornerRadius={0}
            fill={getGaugePieColor(value)}
            background={{ fill: "#e0e0e0" }}
          />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="gauge-value">{Math.round(scaledValue)}</div>
    </div>
  );
};

// CARD NAME: Daily Workload Deviation
export const getBarColor = (score) => {
  if (score >= 0 && score < 0.30) return "#4CAF50";  // Green
  if (score >= 0.30 && score < 0.60) return "#8BC34A";  // Light Green
  if (score >= 0.60 && score < 0.90) return "#FFD700";  // Yellow
  if (score >= 0.90 && score < 1.20) return "#FFB6B6";  // Light Red
  if (score >= 1.20) return "#FF0000";  // Red
  return "#FF0000";  // Red
};

// CARD NAME: Underutilized Teachers
export const getUnderTeacherPieChartData = (data) => {
  const teacherScoreRanges = [
    { label: "0 - 0.25", min: 0, max: 0.25, color: "#FF0000" }, // Red
    { label: "0.25 - 0.5", min: 0.25, max: 0.5, color: "#FFB6B6" }, // Light Red
    { label: "0.5 - 0.75", min: 0.5, max: 0.75, color: "#FFD700" }, // Yellow
    { label: "0.75 - 0.9", min: 0.75, max: 0.9, color: "#8BC34A" }, // Light Green
    { label: "0.9+", min: 0.9, max: Infinity, color: "#4CAF50" } // Green
  ];

  const rangeCounts = teacherScoreRanges.map(({ min, max, color }) => ({
      label: `${min}-${max}`,
      value: Object.values(data).filter(score => score >= min && score < max).length,
      color,
  }));

  return rangeCounts.filter(entry => entry.value > 0);
};

// CARD NAME: Room Underuse
export const getPieChartData = (roomUnderuseData) => {
  const colorMap = [
      { label: "0 - 0.75", min: 0, max: 0.75, color: "#4CAF50" }, // Green
      { label: "0.75 - 1.5", min: 0.75, max: 1.5, color: "#8BC34A" }, // Light Green
      { label: "1.5 - 2.25", min: 1.5, max: 2.25, color: "#FFD700" }, // Yellow
      { label: "2.25 - 3", min: 2.25, max: 3, color: "#FFB6B6" }, // Light Red
      { label: "3+", min: 3, max: Infinity, color: "#FF0000" } // Red
  ];

  const categoryCounts = colorMap.map(category => ({
      label: category.label,
      value: Object.values(roomUnderuseData).filter(score => score >= category.min && score < category.max).length,
      color: category.color
  }));

  return categoryCounts.filter(entry => entry.value > 0);
};

// CARD NAME: Peak Hour Congestion
export const PeakHourMatrix = ({ studentCount }) => {
  console.log(studentCount);
  let maxStudents = 0;
  for (let i = 0; i < studentCount.length; i++) {
    const students = parseInt(studentCount[i].numStudents.trim(), 10);
    if (students > maxStudents) {
      maxStudents = students;
    }
  }
  const minStudents = 0;

  const getColor = (students) => {
    const range = maxStudents - minStudents || 1;
    const percentage = (students - minStudents) / range;

    if (percentage >= 0.00 && percentage < 0.20) return "#4CAF50";
    if (percentage >= 0.20 && percentage < 0.40) return "#8BC34A";
    if (percentage >= 0.40 && percentage < 0.60) return "#FFD700";
    if (percentage >= 0.60 && percentage < 0.80) return "#FFB6B6";
    if (percentage >= 0.80 && percentage < 1.00) return "#FF0000";
    return "#FF0000";
  };

  const daysOfWeek = ["M", "T", "W", "T", "F"];
  const rowHeaders = Array.from({ length: 20 }, (_, i) => (i % 4 === 0 ? 16 + i / 4 : ""));

  const grid = Array.from({ length: 5 }, (_, col) =>
    Array.from({ length: 20 }, (_, row) => {
      const timeslot = row + col * 20;
      const studentEntry = studentCount.find(entry => parseInt(entry.timeSlot) === timeslot);
      const students = studentEntry ? parseInt(studentEntry.numStudents.trim()) : 0;
      return { timeslot, students };
    })
  );

  return (
    <div className="matrix-container">
      <div className="matrix-grid-container">
        {/* Header Row: Empty space + Column Headers */}
        <div className="matrix-header-row">
          <div className="empty-header"></div>
          <div className="column-header">
            {daysOfWeek.map((day, idx) => (
              <div key={idx} className="column-header-cell">{day}</div>
            ))}
          </div>
        </div>

        {/* Matrix Content: Row Headers + Matrix */}
        <div className="matrix-content">
          {/* Row Headers */}
          <div className="row-header-column">
            {rowHeaders.map((label, idx) => (
              <div key={idx} className="cell row-header">{label}</div>
            ))}
          </div>

          {/* Matrix Grid */}
          <div className="matrix-columns">
            {grid.map((column, colIdx) => (
              <div key={colIdx} className="column">
                {column.map(({ timeslot, students }) => (
                  <div
                    key={timeslot}
                    className="cell"
                    style={{ backgroundColor: getColor(students) }}
                  />
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>

  );
};

// CARD NAME (1/2): Missing Course Students
// CARD NAME (2/2): Missing Instrument Students
export const GaugeChart = ({ value = 2 }) => {
  const sections = [
    { range: [0, 5], color: '#4CAF50' }, // Green
    { range: [5, 10], color: '#BADA55' }, // Light Green
    { range: [10, 15], color: '#FFD700' }, // Yellow
    { range: [15, 20], color: '#FFA07A' }, // Light Red
    { range: [20, 25], color: '#FF0000' } // Red
  ].map((section) => ({ ...section, value: 1 }));

  const totalSections = sections.length;
  const emptySections = [{ value: totalSections, color: 'transparent' }];

  const getNeedleAngle = (value) => {
    if (value >= 0 && value < 5) return 193; // Excellent
    if (value >= 5 && value < 7.5) return 230; // Great
    if (value >= 7.5 && value < 10) return 270; // Good
    if (value >= 10 && value < 15) return 310; // Fair
    if (value >= 15 && value <= 100) return 347; // Poor
    return 180; // Default (out of range)
  };
  
  const needleAngle = getNeedleAngle(value);

  // Custom render for the needle
  const renderNeedle = (cx, cy, radius) => {
    const needleLength = radius * 0.8; 
    const needleBaseRadius = 6; 
    const radians = (needleAngle * Math.PI) / 180;
  
    const offsetX = 5;
  
    const x1 = (cx + offsetX);
    const y1 = cy;
    const x2 = (cx + offsetX) + needleLength * Math.cos(radians);
    const y2 = cy + needleLength * Math.sin(radians);
  
    return (
      <g>
        {/* Needle base */}
        <circle cx={x1} cy={y1} r={needleBaseRadius} fill="black" stroke="black" strokeWidth={2} />
        
        {/* Needle line */}
        <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="black" strokeWidth={3} />
      </g>
    );
  };
  
  return (
    <div className="flex flex-col items-center w-full">
      <div className="relative">
        <PieChart width={300} height={200} style={{ cursor: "pointer" }}>
          {/* Colored Sections */}
          <Pie
            className = "gauge-sector"
            data={sections}
            cx={150}
            cy={150}
            startAngle={180}
            endAngle={0}
            innerRadius={60}
            outerRadius={80}
            paddingAngle={2}
            dataKey="value"
          >
            {sections.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>

          {/* Empty Semicircle */}
          <Pie
            className = "gauge-sector"
            data={emptySections}
            cx={150}
            cy={150}
            startAngle={0}
            endAngle={180}
            innerRadius={60}
            outerRadius={80}
            dataKey="value"
            fill="transparent"
          />

          {/* Section Labels */}
          {sections.map((section, index) => {
            const angle = 180 - index * (180 / (totalSections - 1)) - (180 / totalSections) / 2;
            const radian = (angle * Math.PI) / 180;
            const x = 150 + 100 * Math.cos(radian);
            const y = 150 + 100 * Math.sin(radian);

            return (
              <text key={`label-${index}`} x={x} y={y} textAnchor="middle" fontSize={12}>
                {section.name}
              </text>
            );
          })}

          {/* Render Needle */}
          {renderNeedle(150, 150, 80)}
        </PieChart>
      </div>

      {/* Value Display */}
      <div className="text-3xl font-bold mt-2">{value.toFixed(2)}%</div>
    </div>
  );
};
