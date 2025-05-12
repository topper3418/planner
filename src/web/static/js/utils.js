export function formatParagraph(text, width = 75, indents = 1) {
  if (typeof text !== "string") {
    console.error("Invalid text type:", typeof text);
    return "";
  }
  const space = width - 8 * indents;
  let prettyText = "";
  if (text.length > space) {
    prettyText += "    ".repeat(indents) + text.slice(0, space) + "\n";
    let remainder = text.slice(space);
    while (remainder) {
      if (remainder.length > space) {
        prettyText += "    ".repeat(indents) + remainder.slice(0, space) + "\n";
        remainder = remainder.slice(space);
      } else {
        prettyText += "    ".repeat(indents) + remainder + "\n";
        remainder = "";
      }
    }
  } else {
    prettyText += "    ".repeat(indents) + text + "\n";
  }
  return prettyText;
}
export function formatDateTime(date, include_year = false) {
  if (!date) return "";
  const d = date instanceof Date ? date : new Date(date);
  const year = d.getUTCFullYear();
  const month = String(d.getUTCMonth() + 1).padStart(2, "0");
  const day = String(d.getUTCDate()).padStart(2, "0");
  const hours = String(d.getUTCHours()).padStart(2, "0");
  const minutes = String(d.getUTCMinutes()).padStart(2, "0");
  const seconds = String(d.getUTCSeconds()).padStart(2, "0");
  if (include_year) {
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }
  return `${month}-${day} ${hours}:${minutes}:${seconds}`;
}

export function formatDateTimeFromUTC(date, include_year = false) {
  const d = date instanceof Date ? date : new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  const seconds = String(d.getSeconds()).padStart(2, "0");
  if (include_year) {
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }
  return `${month}-${day} ${hours}:${minutes}:${seconds}`;
}
