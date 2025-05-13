async function getCuriosities(filterValues) {
  const { startTime, endTime, search } = filterValues;
  const params = new URLSearchParams();
  if (startTime) params.append("startTime", startTime);
  if (endTime) params.append("endTime", endTime);
  if (search) params.append("search", search);
  params.append("limit", "50");
  const response = await fetch(`/api/curiosities?${params.toString()}`, {
    headers: { "Content-Type": "application/json" },
  });
  const data = await response.json();
  if (data.error) {
    console.error("Error fetching curiosities:", data.error);
    throw new Error(data.error);
  } else {
    console.log("Fetched curiosities:", data);
  }
  return data.curiosities || [];
}

async function getCuriosityById(curiosityId) {
  const response = await fetch(`/api/curiosities/${curiosityId}`, {
    headers: { "Content-Type": "application/json" },
  });
  const data = await response.json();
  if (data.error) {
    console.error("Error fetching curiosity:", data.error);
    throw new Error(data.error);
  } else {
    console.log("Fetched curiosity:", data);
  }
  return data.data || {};
}

export default {
  getCuriosities,
  getCuriosityById,
};
