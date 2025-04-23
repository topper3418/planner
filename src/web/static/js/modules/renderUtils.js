export function formatParagraph(text, width = 75, indents = 1) {
    const space = width - 8 * indents;
    let prettyText = '';
    if (text.length > space) {
        prettyText += '    '.repeat(indents) + text.slice(0, space) + '\n';
        let remainder = text.slice(space);
        while (remainder) {
            if (remainder.length > space) {
                prettyText += '    '.repeat(indents) + remainder.slice(0, space) + '\n';
                remainder = remainder.slice(space);
            } else {
                prettyText += '    '.repeat(indents) + remainder + '\n';
                remainder = '';
            }
        }
    } else {
        prettyText += '    '.repeat(indents) + text + '\n';
    }
    return prettyText;
}

export function formatDateTime(date, include_year = false) {
    if (!date) return '';
    const d = date instanceof Date ? date : new Date(date);
    const year = d.getUTCFullYear();
    const month = String(d.getUTCMonth() + 1).padStart(2, '0');
    const day = String(d.getUTCDate()).padStart(2, '0');
    const hours = String(d.getUTCHours()).padStart(2, '0');
    const minutes = String(d.getUTCMinutes()).padStart(2, '0');
    const seconds = String(d.getUTCSeconds()).padStart(2, '0');
    if (include_year) {
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }
    return `${month}-${day} ${hours}:${minutes}:${seconds}`;
}

export function formatDateTimeFromUTC(date, include_year = false) {
    const d = date instanceof Date ? date : new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');
    if (include_year) {
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }
    return `${month}-${day} ${hours}:${minutes}:${seconds}`;
}

export function renderNote(note) {
    const template = document.getElementById('note-template').content.cloneNode(true);
    const item = template.querySelector('.note-item');
    item.querySelector('.note-id').textContent = `[${String(note.id).padStart(4, '0')}]`;
    item.querySelector('.note-timestamp').textContent = formatDateTime(note.timestamp);
    item.querySelector('.note-category').textContent = note.category ? note.category.name : 'Uncategorized';
    if (note.processing_error) {
        const errorDiv = item.querySelector('.note-error');
        errorDiv.textContent = `Error: ${note.processing_error}`;
        errorDiv.style.display = 'block';
    }
    item.querySelector('.note-text-content').textContent = formatParagraph(note.processed_note_text || note.note_text);
    return item;
}

export function renderTodo(todo) {
    const template = document.getElementById('todo-template').content.cloneNode(true);
    const item = template.querySelector('.todo-item');
    const checkbox = item.querySelector('.todo-checkbox');
    checkbox.checked = todo.complete;
    let mainText = `[${String(todo.id).padStart(4, '0')}]: ${todo.todo_text}`;
    let detailsText = '';
    if (todo.target_start_time || todo.target_end_time) {
        detailsText += `${formatDateTime(todo.target_start_time) || '*'} -> ${formatDateTime(todo.target_end_time) || '*'}`;
    }
    const created = todo.source_annotation?.note?.timestamp || '';
    if (created) detailsText += `${detailsText ? ' | ' : ''}Created: ${formatDateTime(created)}`;
    if (todo.complete && todo.source_annotation?.note?.timestamp) {
        detailsText += `${detailsText ? ' | ' : ''}Done: ${formatDateTime(todo.source_annotation.note.timestamp)}`;
    }
    const now = new Date();
    const startTime = todo.target_start_time ? new Date(todo.target_start_time) : null;
    const endTime = todo.target_end_time ? new Date(todo.target_end_time) : null;
    const started = startTime && startTime < now;
    const late = endTime && endTime < now;
    const yellow = started && !late;
    const red = late;
    const green = todo.complete;
    const grey = todo.cancelled;
    const white = !started && !endTime;
    let colorClass = 'text-gray-800';
    if (green) colorClass = 'text-green-500';
    else if (grey) colorClass = 'text-gray-400';
    else if (red) colorClass = 'text-red-500';
    else if (yellow) colorClass = 'text-yellow-500';
    else if (white) colorClass = 'text-gray-800';
    else colorClass = 'text-pink-500';
    item.classList.add(colorClass);
    item.querySelector('.todo-main').textContent = mainText;
    item.querySelector('.todo-details').textContent = detailsText;
    return item;
}

export function renderAction(action) {
    const template = document.getElementById('action-template').content.cloneNode(true);
    const item = template.querySelector('.action-item');
    let actionText = action.action_text;
    if (action.todo_id && action.todo) {
        actionText += ` -> ${action.todo.todo_text}`;
    }
    item.classList.add(action.mark_complete ? 'text-green-500' : 'text-gray-800');
    item.querySelector('.action-id').textContent = `[${String(action.id).padStart(4, '0')}]`;
    item.querySelector('.action-timestamp').textContent = formatDateTime(action.start_time);
    item.querySelector('.action-text-content').textContent = actionText;
    return item;
}

export function renderCuriosity(curiosity) {
    const template = document.getElementById('curiosity-template').content.cloneNode(true);
    const item = template.querySelector('.curiosity-item');
    item.querySelector('.curiosity-timestamp').textContent = formatDateTime(curiosity.note.timestamp);
    item.querySelector('.curiosity-note-text').textContent = formatParagraph(curiosity.note.note_text, 75, 0);
    item.querySelector('.curiosity-annotation-text').textContent = formatParagraph(curiosity.annotation_text, 75, 1);
    return item;
}
