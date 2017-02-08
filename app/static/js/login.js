"use strict";

function validate(username, password) {
    if (username.length <= 2 || username.length > 100) {
        $("#error").html("Incorrect username.");
        return false;
    }

    if (!username.match(/^[a-zA-Z0-9_]+$/)) {
        $("#error").html("Incorrect username.");
        return false;
    }

    if (password.length <= 8 || password.length > 100) {
        $("#error").html("Incorrect password.");
        return false;
    }

    return true;
}

function try_login() {
    var username = $("#username").val();
    var password = $("#password").val();

    if (validate(username, password)) {
        $.post("/api/user/login", {
            username: username,
            password: password
        }, data => {
            if (data.success) {
                window.location.href = "/";
            }
            else {
                $("#error").html("Incorrect username or password.");
            }
        });
    }
}


$(document).ready(() => {
    $("input[type=text],input[type=password]").keyup((e) => {
        if ((e.which || e.keyCode) == 13) { // enter pressed
            try_login();
        }
    });
    $("#login").click(try_login);
    $("#username").focus();
})
