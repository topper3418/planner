export async function getActions(filterValues) {
  const {
    startTime,
    endTime,
    search,
    actions: { appliedToTodo, notAppliedToTodo },
  } = filterValues;
  const params = new URLSearchParams();
  if (startTime) params.append("startTime", startTime);
  if (endTime) params.append("endTime", endTime);
  if (search) params.append("search", search);
  // appliedToTodo
  // don't append if both, true if just applied todo, false if just not applied
  if (appliedToTodo && !notAppliedToTodo) {
    params.append("appliedToTodo", "true");
  } else if (!appliedToTodo && notAppliedToTodo) {
    params.append("appliedToTodo", "false");
  }
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
  const response = await fetch(`/api/actions/${todoId}`, {
    headers: { "Content-Type": "application/json" },
  });
  const data = await response.json();
  if (data.error) {
    console.error("Error fetching action:", data.error);
    throw new Error(data.error);
  } else {
    console.log("Fetched action:", data);
  }
  return data.data;
}
