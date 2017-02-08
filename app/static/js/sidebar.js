"use strict";

function toggleSidebar(direction) {
    // test if locked
    if ($("#sidebar").attr("locked") === "true") {
        return;
    }

    var expand;
    if (direction === true || direction == false) {
        expand = direction;
    }
    else {
        expand = $("#sidebar").attr("expanded") !== "true";
    }

    $("#sidebar").attr("expanded", expand);
    $("#sidebar").css("width",      expand ? "250px" : "10px");
    $("#content").css("marginLeft", expand ? "250px" : "10px");
}

function toggleSidebarLock(direction) {
    var lock;
    if (direction === true || direction == false) {
        lock = direction;
    }
    else {
        lock = $("#sidebar").attr("locked") !== "true";
    }

    if (lock) {
        toggleSidebar(true);
    }
    $("#sidebar").attr("locked", lock);
    $("#expandlock_locked").css("visibility", lock ? "visible": "hidden");
}


$(document).ready(() => {
    $("#expandlock").click(toggleSidebarLock);
    $("#sidebar").mouseenter(() => {
        if ($("#sidebar").attr("expanded") !== "true") {
            toggleSidebar(true);
        }
    });
    $("#sidebar").mouseleave(() => {
        if ($("#sidebar").attr("expanded") === "true") {
            toggleSidebar(false);
        }
    });
});
