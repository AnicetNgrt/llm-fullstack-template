export function dateObjectFromUTC(s) {
    s = s.split(/\D/);
    return new Date(Date.UTC(+s[0], --s[1], +s[2], +s[3], +s[4], +s[5], 0));
}

export function formatDateTime(date) {
    // Get the current date
    let currentDate = new Date();
    currentDate.setHours(0, 0, 0, 0); // Set the time to midnight

    // Calculate the difference in days between the current date and the input date
    let timeDiff = currentDate.getTime() - date.getTime();
    let dayDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));

    if (dayDiff === 0) {
        // If the date is today, format it as "today at HH:MM"
        let hours = String(date.getHours()).padStart(2, '0');
        let minutes = String(date.getMinutes()).padStart(2, '0');
        return `today at ${hours}:${minutes}`;
    } else if (dayDiff <= 5) {
        // If the date is up to 5 days ago, format it as "X days ago at HH:MM"
        let daysAgo = dayDiff === 1 ? 'yesterday' : `${dayDiff} days ago`;
        let hours = String(date.getHours()).padStart(2, '0');
        let minutes = String(date.getMinutes()).padStart(2, '0');
        return `${daysAgo} at ${hours}:${minutes}`;
    } else {
        // Otherwise, format the date as "YYYY/MM/DD at HH:MM"
        let year = date.getFullYear();
        let month = String(date.getMonth() + 1).padStart(2, '0');
        let day = String(date.getDate()).padStart(2, '0');
        let hours = String(date.getHours()).padStart(2, '0');
        let minutes = String(date.getMinutes()).padStart(2, '0');
        return `${year}/${month}/${day} at ${hours}:${minutes}`;
    }
}