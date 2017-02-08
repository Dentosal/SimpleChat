"use strict";

function updateChatSearch() {
    var search = $("#newchatsearch").val();
    if (search.match(/^#?[a-zA-Z0-9_]+$/)) {
        $.getJSON("/api/search/"+search.replace("#", "!"), data => { // '#' is renamed to '!' for transmission
            if (data.success) {
                var options = _.map(data.result, name => "<div>"+name+"</div>").join("");
                search = search.slice(search.startsWith("#")?1:0); // remove prefix
                if (!_.includes(data.result, "#"+search)) {
                    options += "<div id=\"createchannel\">Create channel <i>#"+search+"</i></div>";
                }
                $("#newchatresults").html(options);
            }
        }).fail(reloadOnFail);
    }
    else {
        $("#newchatresults").html("");
    }
}

function searchSelect(name) {
    if (name.startsWith("#")) {
        Chat.joinChannel(name.slice(1));
        Chat.select(name.slice(1), true);
    }
    else {
        Chat.newChat(name);
        Chat.select(name, false);
    }
    $("#newchatsearch").val("");
    $("#newchatresults").html("");
}

$(document).ready(() => {
    $("#newchatsearch").keyup(e => {
        if ((e.which || e.keyCode) == 13) { // enter pressed
            // select top candidate
            var f = $("#newchatresults > div:first-child");
            if (f.attr("id") !== "createchannel") {
                searchSelect(f.html());
            }
        }
        else {
            updateChatSearch();
        }
    });
    $("#newchatsearch").focus(() => {
        updateChatSearch();
    });
    $("#newchatsearch").focusout(() => {
        if (0 === $("#newchatresults:hover").length) {
            $("#newchatresults").html("");
        }
    });
    $("#newchatresults").mouseleave(() => {
        if (0 === $("#newchatsearch:focus").length) {
            $("#newchatresults").html("");
        }
    });
    $(document).on("click", "#newchatresults > div", e => {
        if (e.currentTarget.id === "createchannel") {
            // create and join are actually same thing
            var search = $("#newchatsearch").val();
            search = search.slice(search.startsWith("#")); // remove prefix
            Chat.joinChannel(search);
        }
        else {
            searchSelect($(e.currentTarget).html());
        }
    });

    $("#logout").click(() => {
        $.post("/api/user/logout", data => {
            window.location.href = "/";
        }).fail(reloadOnFail);
    });
});
