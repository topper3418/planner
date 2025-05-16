export async function getTodos(filterValues) {
  const {
    startTime,
    endTime,
    search,
    todos: { completed, cancelled, active },
  } = filterValues;
  const params = new URLSearchParams();
  if (startTime) params.append("startTime", startTime);
  if (endTime) params.append("endTime", endTime);
  if (search) params.append("search", search);
  params.append("completed", Boolean(completed));
  params.append("cancelled", Boolean(cancelled));
  params.append("active", Boolean(active));
  params.append("limit", "50");
  const response = await fetch(`/api/todos?${params.toString()}`, {
    headers: { "Content-Type": "application/json" },
  });
  const data = await response.json();
  if (data.error) {
    console.error("Error fetching todos:", data.error);
    throw new Error(data.error);
  } else {
    console.log("Fetched todos:", data);
  }
  ///////////////////////////////////////////////////////////////////////////
  //                            ARRANGE HERITAGE                           //
  ///////////////////////////////////////////////////////////////////////////
  const todos = data.todos || [];
  const todoIds = todos.map((todo) => todo.id);
  const orphanTodos = [];
  const childTodos = [];
  for (const todo of todos) {
    if (todo.parent_id === null || !todoIds.includes(todo.parent_id)) {
      orphanTodos.push(todo);
    } else {
      childTodos.push(todo);
    }
  }
  for (const todo of childTodos) {
    const parent = todos.find((t) => t.id === todo.parent_id);
    if (parent) {
      if (!parent.children) {
        parent.children = [];
      }
      parent.children.push(todo);
    }
  }
  console.log("returning todos", orphanTodos);
  return orphanTodos;
}

export async function getTodoById(todoId) {
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
  return data.data || {};
}
