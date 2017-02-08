"use strict";

var Chat = (() => {
    var self = {};
    self.chats = [];
    self.activeChat = null;

    return {
        updateTimestamps: () => {
            _.each($("span[name=time][time]"), elem => {
                $(elem).html(formatTime(parseInt($(elem).attr("time"))));
            });
        },
        select: (name, isChannel, isTemporary) => {
            if (!isChannel && isTemporary === undefined) {
                var chat = _.find(self.chats, chat => chat.name === name && chat.isChannel === isChannel);
                isTemporary = chat.isTemporary;
            }
            self.activeChat = {name: name, isChannel: isChannel, isTemporary: isTemporary};
            $("#title").html((self.activeChat.isChannel ? "#" : "")+self.activeChat.name)
            $("#message").focus();
            Chat.updateMessages();
        },
        newChat: (name) => {
            if (!_.find(self.chats, chat => chat.name === name)) {
                self.chats.push({name: name, isChannel: false, isTemporary: true})
            }
            Chat.select(name, false);
            Chat.updateChats();
        },
        joinChannel: (name) => {
            $.post("/api/channel/join/"+name, data => {
                Chat.updateChats();
                Chat.select(name, true);
            }).fail(reloadOnFail);
        },
        sendMessage: () => {
            var msg = $("#message").val();
            if (msg !== "") {
                $("#message").val("");
                if (self.activeChat !== null) {
                    $.post("/api/"+(self.activeChat.isChannel?"channel":"user")+"/send/"+self.activeChat.name, {message: msg}, data => {
                        if (!self.activeChat.isChannel && self.activeChat.isTemporary) {
                            Chat.updateChats(Chat.updateMessages);
                        }
                        else {
                            Chat.updateMessages();
                        }
                    }).fail(reloadOnFail);
                }
                else {
                    $("#messages").html("<li><div>Please select a chat to send messages.</div></li>")
                }
            }
        },
        renderChat: (chat) => {
            var elem = $("<li channel=\""+chat.isChannel+"\""+(chat.isTemporary
                ? "temporary"
                : "modified=\""+chat.lastModified+"\""
            )+">"+chat.name+"</li>");
            if (self.activeChat !== null && chat.name === self.activeChat.name && chat.isChannel === self.activeChat.isChannel) {
                elem.addClass("selected");
            }
            return elem.prop("outerHTML");
        },
        updateChats: (callback) => {
            $.getJSON("/api/user/chats").done(data => {
                if (data.success) {
                    var chatnames = _.map(_.filter(data.result, item => !item.isChannel), item => item.name);
                    // update chat list
                    self.chats = _.concat(
                        _.filter(self.chats, chat => chat.isTemporary && !_.includes(chatnames, chat.name)),
                        _.map(data.result, chat => {
                            chat.isTemporary = false;
                            return chat;
                        })
                    );
                    // remove temporary status from current chat if it has received messages (including those it sent itself)
                    if (self.activeChat !== null && !self.activeChat.isChannel &&self.activeChat.isTemporary) {
                        var chat = _.find(self.chats, item => item.name === self.activeChat.name && item.isChannel === false);
                        if (chat) {
                            self.activeChat.isTemporary = false;
                        }
                    }
                    // update sidebar
                    $("#chats").html(_.map(self.chats, chat => Chat.renderChat(chat)).join(""));
                    // callback
                    if (callback) {
                        callback();
                    }
                }
            }).fail(reloadOnFail);
        },
        updateMessages: () => {
            if (self.activeChat !== null) {
                if (self.activeChat.isTemporary) {
                    $("#messages").html("");
                }
                else {
                    var isBottom = $("#messages").scrollTop() + $("#messages").height() > $("#messages")[0].scrollHeight - 10;
                    $.getJSON("/api/"+(self.activeChat.isChannel?"channel":"user")+"/messages/"+self.activeChat.name, data => {
                        if (data.success) {
                            $("#messages").html("");
                            _.each(data.result, lidata => {
                                $("#messages").prepend("<li>"+lidata+"</li>");
                            });
                            Chat.updateTimestamps();

                            // scroll to bottom if was scrolled to bottom before
                            if (isBottom) {
                                $("#messages").scrollTop($("#messages")[0].scrollHeight);
                            }
                        }
                    }).fail(reloadOnFail);
                }
            }
        },
        update: () => {
            Chat.updateChats(Chat.updateMessages);
        }
    }
})();

function reloadOnFail(xhr) {
    if (xhr.status === 403) {
        location.reload();
    }
}

$(document).ready(() => {
    $("#message").focus();

    $.getJSON("/api/user/locale", data => {
        for (var i = 0; i < data.result.length; i++) {
            // set new locale
            if (moment.locale(data.result[i]) === data.result[i]) {
                break;
            }
        }
    });

    $("#send").click(Chat.sendMessage);
    $("#message").keyup(e => {
        if ((e.which || e.keyCode) == 13) { // enter pressed
            Chat.sendMessage();
        }
    });

    $(document).on("click", "#chats > li", e => {
        var elem = $(e.currentTarget);
        Chat.select(elem.html(), elem.attr("channel") === "true", !!elem.attr("temporary"));
        Chat.updateChats(Chat.updateMessages);
    });

    Chat.update();
    setInterval(Chat.update, 1000); // update every second
});
