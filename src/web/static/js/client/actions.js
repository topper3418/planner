export async function getActions(filterValues) {
  const {
    startTime,
    endTime,
    search,
    actions: { appliedToTodo },
  } = filterValues;
  const params = new URLSearchParams();
  if (startTime) params.append("startTime", startTime);
  if (endTime) params.append("endTime", endTime);
  if (search) params.append("search", search);
  if (appliedToTodo !== undefined)
    params.append("appliedToTodo", appliedToTodo);
  params.append("limit", "50");
  const response = await fetch(`/api/actions?${params.toString()}`, {
    headers: { "Content-Type": "application/json" },
  });
  const data = await response.json();
  if (data.error) {
    console.error("Error fetching actions:", data.error);
    throw new Error(data.error);
  } else {
    console.log("Fetched actions:", data);
  }
  return data.actions;
}

export async function getActionById(todoId) {
  const response = await fetch(`/api/todos/${todoId}`, {
    headers: { "Content-Type": "application/json" },
  });
  const data = await response.json();
  if (data.error) {
    console.error("Error fetching todo:", data.error);
    throw new Error(data.error);
  } else {
    console.log("Fetched todo:", data);
  }
  return data.data;
}
