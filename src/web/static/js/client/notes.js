async function getNotes(filterValues) {
  const { startTime, endTime, search } = filterValues;
  const params = new URLSearchParams();
  if (startTime) params.append("startTime", startTime);
  if (endTime) params.append("endTime", endTime);
  if (search) params.append("search", search);
  params.append("limit", "50");
  const response = await fetch(`/api/notes?${params.toString()}`, {
    headers: { "Content-Type": "application/json" },
  });
  const data = await response.json();
  if (data.error) {
    console.error("Error fetching notes:", data.error);
    throw new Error(data.error);
  } else {
    console.log("Fetched notes:", data);
  }
  return data.notes || [];
}

async function getNoteById(noteId) {
  const response = await fetch(`/api/notes/${noteId}`, {
    headers: { "Content-Type": "application/json" },
  });
  const data = await response.json();
  if (data.error) {
    console.error("Error fetching note:", data.error);
    throw new Error(data.error);
  } else {
    console.log("Fetched note:", data);
  }
  return data.data || {};
}

async function createNote(noteText) {
  const response = await fetch("/api/notes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data: { note: noteText } }),
  });
  const data = await response.json();
  if (data.error) throw new Error(data.error);
}

export default {
  getNotes,
  getNoteById,
  createNote,
};
