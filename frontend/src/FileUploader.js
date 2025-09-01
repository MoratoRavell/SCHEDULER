import React, { useEffect, useState, useRef } from 'react';

// CSS
import './FileUploader.css';

const REQUIRED_FILES = ['students', 'teachers', 'rooms', 'courses', 'instruments'];
const MAX_TOTAL_SIZE_MB = 5;

function FileUploader({ onFilesLoaded, loggedIn, resetTrigger }) {
  const [files, setFiles] = useState({});
  const dropRef = useRef(null);
  const inputRef = useRef(null);
  const allFilesLoaded = REQUIRED_FILES.every(name => files.hasOwnProperty(name));

  useEffect(() => {
    clearFiles();
  }, [resetTrigger]);

  useEffect(() => {
    onFilesLoaded(Object.values(files), allFilesLoaded);
  }, [files]);

  const showToast = (message, type = 'info') => {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerText = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
  };

  // Validation functions
  const validateStudents = (json) => {
    console.log("validateStudents called");

    if (!Array.isArray(json)) {
      console.error("Students JSON is not an array");
      return false;
    }

    const validDays = new Set(["Mon", "Tue", "Wed", "Thu", "Fri"]);
    const timeRangeRegex = /^([01]\d|2[0-3]):[0-5]\d-([01]\d|2[0-3]):[0-5]\d$/;

    for (const [index, student] of json.entries()) {
      console.log(`Validating student index: ${index}`);

      if (
        typeof student !== 'object' ||
        typeof student.student_id !== 'number' ||
        typeof student.name !== 'string' || !student.name.trim() ||
        !Array.isArray(student.availability) ||
        !Array.isArray(student.courses) ||
        !Array.isArray(student.instruments)
      ) {
        console.error("Invalid student structure at index", index, student);
        return false;
      }

      if (
        (student.antiquity !== null && !Array.isArray(student.antiquity)) ||
        (student.siblings !== null && !Array.isArray(student.siblings))
      ) {
        console.error("Invalid antiquity or siblings field at index", index, { antiquity: student.antiquity, siblings: student.siblings });
        return false;
      }

      if (student.antiquity !== null) {
        for (const [i, entry] of student.antiquity.entries()) {
          if (
            !Array.isArray(entry) ||
            typeof entry[0] !== 'string' || !entry[0].trim() ||
            entry.length < 2
          ) {
            console.error(`Invalid antiquity structure at student ${index}, entry ${i}:`, entry);
            return false;
          }
          for (let j = 1; j < entry.length; j++) {
            const [day, timeRange] = entry[j];
            if (!validDays.has(day) || !timeRangeRegex.test(timeRange)) {
              console.error(`Invalid antiquity time at student ${index}, entry ${i}, slot ${j}:`, [day, timeRange]);
              return false;
            }
          }
        }
      }

      if (student.siblings !== null) {
        for (const [i, siblingId] of student.siblings.entries()) {
          if (typeof siblingId !== 'number') {
            console.error(`Invalid sibling ID at student ${index}, sibling ${i}:`, siblingId);
            return false;
          }
        }
      }

      for (const [i, course] of student.courses.entries()) {
        if (typeof course !== 'string' || !course.trim()) {
          console.error(`Invalid course at student ${index}, course ${i}:`, course);
          return false;
        }
      }

      for (const [i, instrument] of student.instruments.entries()) {
        if (typeof instrument !== 'string' || !instrument.trim()) {
          console.error(`Invalid instrument at student ${index}, instrument ${i}:`, instrument);
          return false;
        }
      }
    }

    console.log('students.json has been successfully validated');
    return true;
  };

  const validateTeachers = (json) => {
    if (!Array.isArray(json)) {
      console.error("Teachers data is not an array:", json);
      return false;
    }

    const validDays = new Set(["Mon", "Tue", "Wed", "Thu", "Fri"]);
    const timeRangeRegex = /^([01]\d|2[0-3]):[0-5]\d-([01]\d|2[0-3]):[0-5]\d$/;

    for (const [index, teacher] of json.entries()) {
      if (
        typeof teacher !== 'object' ||
        typeof teacher.teacher_id !== 'number' ||
        typeof teacher.name !== 'string' || !teacher.name.trim() ||
        !Array.isArray(teacher.availability) ||
        !Array.isArray(teacher.contract) ||
        !Array.isArray(teacher.courses) ||
        !Array.isArray(teacher.instruments)
      ) {
        console.error(`Invalid teacher structure at index ${index}:`, teacher);
        return false;
      }

      for (const [day, timeRange] of teacher.availability) {
        if (!validDays.has(day) || !timeRangeRegex.test(timeRange)) {
          console.error(`Invalid availability at teacher index ${index}: day='${day}', timeRange='${timeRange}'`);
          return false;
        }
      }

      if (
        teacher.contract.length !== 2 ||
        typeof teacher.contract[0] !== 'number' || teacher.contract[0] <= 0 ||
        typeof teacher.contract[1] !== 'number' || teacher.contract[1] <= 0
      ) {
        console.error(`Invalid contract at teacher index ${index}:`, teacher.contract);
        return false;
      }

      for (const course of teacher.courses) {
        if (typeof course !== 'string' || !course.trim()) {
          console.error(`Invalid course at teacher index ${index}:`, course);
          return false;
        }
      }

      for (const instrument of teacher.instruments) {
        if (typeof instrument !== 'string' || !instrument.trim()) {
          console.error(`Invalid instrument at teacher index ${index}:`, instrument);
          return false;
        }
      }
    }

    console.log('teachers.json has been successfully validated');
    return true;
  };


  const validateRooms = (json) => {
    if (!Array.isArray(json)) {
      console.error("Rooms data is not an array:", json);
      return false;
    }

    for (const [index, room] of json.entries()) {
      if (
        typeof room !== 'object' ||
        typeof room.room_id !== 'number' ||
        typeof room.name !== 'string' || !room.name.trim() ||
        typeof room.capacity !== 'number' || room.capacity <= 0 ||
        !Array.isArray(room.features)
      ) {
        console.error(`Invalid room structure at index ${index}:`, room);
        return false;
      }

      for (const feature of room.features) {
        if (typeof feature !== 'string' || !feature.trim()) {
          console.error(`Invalid feature in room at index ${index}:`, feature);
          return false;
        }
      }
    }

    console.log('rooms.json has been successfully validated');
    return true;
  };


  const validateCourses = (json) => {
    if (!Array.isArray(json)) {
      console.error("Courses data is not an array:", json);
      return false;
    }

    for (const [index, course] of json.entries()) {
      if (
        typeof course !== 'object' ||
        typeof course.course_id !== 'number' ||
        typeof course.name !== 'string' || !course.name.trim() ||
        !Array.isArray(course.duration) || course.duration.length !== 2 ||
        typeof course.duration[0] !== 'number' || course.duration[0] <= 0 ||
        typeof course.duration[1] !== 'number' || course.duration[1] <= 0 ||
        typeof course.capacity !== 'number' || course.capacity <= 0 ||
        !Array.isArray(course.features)
      ) {
        console.error(`Invalid course structure at index ${index}:`, course);
        return false;
      }

      for (const feature of course.features) {
        if (typeof feature !== 'string' || !feature.trim()) {
          console.error(`Invalid feature in course at index ${index}:`, feature);
          return false;
        }
      }
    }

    console.log('courses.json has been successfully validated');
    return true;
  };


  const validateInstruments = (json) => {
    if (!Array.isArray(json)) {
      console.error("Instruments data is not an array:", json);
      return false;
    }

    for (const [index, instrument] of json.entries()) {
      if (
        typeof instrument !== 'object' ||
        typeof instrument.instrument_id !== 'number' ||
        typeof instrument.name !== 'string' || !instrument.name.trim() ||
        !Array.isArray(instrument.duration) || instrument.duration.length !== 2 ||
        typeof instrument.duration[0] !== 'number' || instrument.duration[0] <= 0 ||
        typeof instrument.duration[1] !== 'number' || instrument.duration[1] <= 0 ||
        typeof instrument.capacity !== 'number' || instrument.capacity <= 0 ||
        !Array.isArray(instrument.features)
      ) {
        console.error(`Invalid instrument structure at index ${index}:`, instrument);
        return false;
      }

      for (const feature of instrument.features) {
        if (typeof feature !== 'string' || !feature.trim()) {
          console.error(`Invalid feature in instrument at index ${index}:`, feature);
          return false;
        }
      }
    }

    console.log('instruments.json has been successfully validated');
    return true;
  };


  const validators = {
    students: validateStudents,
    teachers: validateTeachers,
    rooms: validateRooms,
    courses: validateCourses,
    instruments: validateInstruments,
  };

  const handleFileInput = async (fileList) => {
    const newFiles = { ...files }; // keep previous files
    let totalSize = Object.values(newFiles).reduce((acc, f) => acc + f.file.size, 0);

    const acceptedFileNames = new Set(REQUIRED_FILES.map(name => `${name}.json`));
    const seenNames = new Set(Object.keys(newFiles).map(name => `${name}.json`)); // already loaded files

    for (const file of Array.from(fileList)) {
      const baseName = file.name.replace('.json', '');
      if (!acceptedFileNames.has(file.name)) {
        showToast(`Invalid file name: ${file.name}`, 'error');
        continue;
      }
      if (seenNames.has(file.name)) {
        showToast(`Duplicate file: ${file.name}`, 'error');
        continue;
      }

      totalSize += file.size;
      if (totalSize > MAX_TOTAL_SIZE_MB * 1024 * 1024) {
        showToast(`Total file size exceeds ${MAX_TOTAL_SIZE_MB} MB`, 'error');
        totalSize -= file.size; // revert size addition
        continue;
      }

      if (file.type !== 'application/json') {
        showToast(`${file.name} is not a JSON file.`, 'error');
        continue;
      }

      try {
        const text = await file.text();
        const json = JSON.parse(text);

        const validate = validators[baseName];
        if (validate && validate(json)) {
          newFiles[baseName] = { file, content: json };
          seenNames.add(file.name);
          showToast(`${file.name} loaded successfully.`, 'success');
        } else {
          showToast(`Validation failed for ${file.name}`, 'error');
        }
      } catch {
        showToast(`Invalid JSON in ${file.name}`, 'error');
      }
    }

    setFiles(newFiles);
    onFilesLoaded(Object.values(newFiles));

    const allValid = REQUIRED_FILES.every(name => newFiles.hasOwnProperty(name));
    if (allValid) {
      showToast('All files loaded and validated successfully.', 'success');
    }
  };

  const handleFileChange = (e) => {
    handleFileInput(e.target.files);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFileInput(e.dataTransfer.files);
    dropRef.current.classList.remove('drag-over');
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    dropRef.current.classList.add('drag-over');
  };

  const handleDragLeave = () => {
    dropRef.current.classList.remove('drag-over');
  };

  const clearFiles = () => {
    setFiles({});
    onFilesLoaded([]);
    if (inputRef.current) inputRef.current.value = null;
    showToast('Files cleared.', 'info');
  };

  const removeFile = (filename) => {
    const newFiles = { ...files };
    delete newFiles[filename];
    setFiles(newFiles);
    onFilesLoaded(Object.values(newFiles));
  };

  const openFileDialog = () => {
    inputRef.current?.click();
  };

  return (
    <div className="drop-container">
      <div
      className={`drop-area ${allFilesLoaded || !loggedIn ? 'disabled' : ''}`}
      ref={dropRef}
      onDrop={allFilesLoaded || !loggedIn ? undefined : handleDrop}
      onDragOver={allFilesLoaded || !loggedIn ? undefined : handleDragOver}
      onDragLeave={allFilesLoaded || !loggedIn ? undefined : handleDragLeave}
    >
        <p className="drop-text">
          {loggedIn
            ? 'Drag and drop your 5 JSON files here'
            : 'Please log in to upload input data'}
        </p>
        <p className="or-text">
          {loggedIn
            ? 'or'
            : ''}
        </p>

        <button
          className="choose-button"
          onClick={openFileDialog}
          disabled={allFilesLoaded || !loggedIn}
        >
          Choose Files
        </button>

        <input
          ref={inputRef}
          type="file"
          accept=".json"
          multiple
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
      </div>

      <div className="file-section">
        <p className="file-status">
          {Object.keys(files).length === 0
            ? 'No valid files loaded'
            : `${Object.keys(files).length} valid file(s) loaded`}
        </p>

        <div className="file-checklist">
          <h4>Checklist:</h4>
          <ul>
            {REQUIRED_FILES.map((filename) => {
              const isLoaded = files.hasOwnProperty(filename);
              return (
                <li key={filename} className={isLoaded ? 'check-ok' : 'check-missing'}>
                  {isLoaded ? '✅' : '❌'} {filename}.json
                  {isLoaded && (
                    <button
                      className="x-delete-button"
                      onClick={() => removeFile(filename)}
                      aria-label={`Remove ${filename}`}
                    >
                      ✕
                    </button>
                  )}
                </li>
              );
            })}
          </ul>

          <button
            className="clear-btn"
            onClick={clearFiles}
            disabled={Object.keys(files).length === 0}
          >
            Clear All Files
          </button>
        </div>
      </div>
    </div>
  );
}

export default FileUploader;
