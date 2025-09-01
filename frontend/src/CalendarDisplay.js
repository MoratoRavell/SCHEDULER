import { Calendar, momentLocalizer } from "react-big-calendar";
import "react-big-calendar/lib/css/react-big-calendar.css";
import Modal from "react-modal";
import moment from "moment";

// CSS
import './CalendarDisplay.css';

Modal.setAppElement('#root');

// Set Monday as the first day of the week
const localizer = momentLocalizer(moment);
moment.updateLocale("en", { week: { dow: 1 } });

const CalendarDisplay = ({
  events,
  selectedEvent,
  setSelectedEvent,
  courseNames,
  instrumentNames,
  roomNames,
  studentNames,
}) => {
  
const days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];

    return (
        <>
            <div style={{ height: 454 }}>
                <Calendar
                    localizer={localizer}
                    components={{
                    header: ({ date }) => <span>{days[moment(date).day()]}</span>,
                    event: ({ event }) => (
                        <div style={{ 
                        padding: "1.2px 0px", 
                        fontSize: "15px", 
                        fontWeight: 100,
                        fontFamily: "'Poppins', sans-serif"
                        }}>
                        {event.cleanTitle}
                        </div>
                    ),
                    }}
                    events={events.map(event => {
                    // Add 15 minutes to each event's end time
                    const endTime = new Date(event.end);
                    endTime.setMinutes(endTime.getMinutes() + 15);
                    
                    // Extract type (Course or Instrument) and ID
                    const [type, id] = event.title.split(" ").slice(0, 2); // Extracts "Course X" or "Instrument Y"
                    const index = Number(id); // Convert to a number for lookup
                    
                    // Lookup name based on type
                    let name = id; // Default to ID if not found
                    if (type === "Course") {
                        name = courseNames.find(course => course.index === index)?.name || `Course ${id}`;
                    } else if (type === "Instrument") {
                        name = instrumentNames.find(instr => instr.index === index)?.name
                        ? `${instrumentNames.find(instr => instr.index === index).name} class`
                        : `Instrument ${id} class`;
                    }
                    
                    return {
                        ...event,
                        cleanTitle: name, // Use only the name, with "Class" added for instruments
                        end: endTime, // Add 15 minutes to the end time
                    };
                    })}
                    
                    startAccessor="start"
                    endAccessor="end"
                    views={["week"]}
                    defaultView="week"
                    toolbar={false}
                    min={new Date(2000, 0, 3, 16, 0, 0)} // Start at 16:00
                    max={new Date(2000, 0, 3, 21, 0, 0)} // End at 21:00
                    step={30} // 15-minute intervals
                    timeslots={1}
                    formats={{
                    timeGutterFormat: "HH:mm", // 24-hour format
                    eventTimeRangeFormat: ({ start, end }) =>
                        `${moment(start).format("HH:mm")} - ${moment(end).format("HH:mm")}`,
                    weekdayFormat: (date, culture, localizer) =>
                        localizer.format(date, "dddd", culture),
                    }}
                    date={new Date(2000, 0, 3)}
                    className="custom-calendar"
                    eventPropGetter={(event) => ({
                    style: {
                        backgroundColor: "#333",
                        color: "white",
                        borderRadius: "0px",
                        border: "none",
                        width: "100%",
                        margin: "0px",
                    },
                    })}
                    onSelectEvent={(event) => setSelectedEvent(event)}
                />
                </div>
                {/* Event Details Modal */}
                <Modal
                isOpen={!!selectedEvent}
                onRequestClose={() => setSelectedEvent(null)}
                className="ReactModal__Content"
                overlayClassName="ReactModal__Overlay"
                closeTimeoutMS={200}
                >
                {/* Extract course/instrument ID and room ID */}
                {(() => {
                    if (!selectedEvent?.title) return null;

                    const parts = selectedEvent.title.split(" ");
                    const roomPart = parts.find(part => part.includes("Room"));
                    const roomId = roomPart ? Number(roomPart.replace(/\D/g, "")) : NaN;

                    console.log(parts);
                    console.log(roomPart);
                    console.log(roomId);


                    // Extract the type (Course/Instrument) and its ID
                    const type = parts[0]; // "Course" or "Instrument"
                    const id = Number(parts[1]); // Course/Instrument index

                    // Get course/instrument name
                    let name = id;
                    if (type === "Course") {
                    name = courseNames.find(course => course.index === id)?.name || `Course ${id}`;
                    } else if (type === "Instrument") {
                    const instrName = instrumentNames.find(instr => instr.index === id)?.name;
                    name = instrName ? `${instrName} class` : `Instrument ${id} class`;
                    }

                    // Get room name and format properly
                    const roomName = roomNames.find(r => r.index === roomId)?.name || `Room ${roomId}`;
                    const formattedRoomName = `(${roomName.trim()})`;

                    return (
                    <>
                        <h2>{`${name.trim()} ${formattedRoomName}`}</h2>
                        <p><strong>Number of Students:</strong> {selectedEvent?.students.length}</p>

                        <div className="modal-scrollable-list">
                        {selectedEvent?.students.length > 0 ? (
                            selectedEvent.students.map((studentId, index) => {
                            const student = studentNames.find(s => s.index === Number(studentId));
                            return (
                                <div key={index} className="modal-list-item">
                                <span className="modal-list-id">{student ? student.name : `Unknown (${studentId})`}</span>
                                </div>
                            );
                            })
                        ) : (
                            <p className="modal-empty-message">No students</p>
                        )}
                        </div>

                        <button 
                        className="Close__Button"
                        onClick={() => setSelectedEvent(null)}
                        >Close</button>
                    </>
                );
            })()}
            </Modal>
        </>
    );
};

export default CalendarDisplay;
