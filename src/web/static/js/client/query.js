export async function submitQuery(query) {
  console.log("submitQueryApi called with query:", query);
  try {
    const response = await fetch(
      `/api/summary?prompt=${encodeURIComponent(query)}`,
      {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      },
    );
    const data = await response.json();
    if (data.error) {
      return { error: data.error };
    }
    return { summary: data.summary };
  } catch (error) {
    return { error: error.message };
  }
}
