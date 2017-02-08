"use strict";

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}

function formatTime(time) {
    // show relative time if message was sent less than six hours ago
    return (time > Date.now() - 1000*60*60*6
        ? moment(time).fromNow()
        : moment(time).calendar()
    ).capitalize();
}
