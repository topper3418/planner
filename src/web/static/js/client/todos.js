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
  // assemble the todos into a tree, culminating in this placeholder
  const topTodo = todos.reduce(
    (acc, todo) => {
      // if there is no parent or the parent is not in the list of todos
      if (todo.parent_id === null || !todoIds.includes(todo.parent_id)) {
        acc.children.push(todo);
      }
      // find the parent
      const parent = todos.find((t) => t.id === todo.parent_id);
      if (parent) {
        // add the todo to the parent's children
        if (!parent.children) {
          parent.children = [];
        }
        parent.children.push(todo);
      }
      return acc;
    },
    { children: [] },
  );
  return topTodo.children;
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
