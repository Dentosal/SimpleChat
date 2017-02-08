"use strict";

function validate_username() {
    var username = $("#username").val();
    var length_ok = 3 <= username.length && username.length <= 100;
    var al_num_ok = !!username.match(/^[a-zA-Z0-9_]+$/);

    $("#length_ok").attr("valid", length_ok);
    $("#al_num_ok").attr("valid", al_num_ok);

    if (length_ok) {
        $.getJSON("/api/user/exists/"+username, data => {
            $("#unique_ok").attr("valid", !data.result);
        });
    }
    else {
        $("#unique_ok").attr("valid", false);
    }
}

function validate_form(callback) {
    validate_username();

    var username = $("#username").val();
    var password = $("#password").val();

    if (password.length <= 8) {
        $("#error").html("Password must be longer than eight characters.");
        return false;
    }

    if (password.length > 100) {
        $("#error").html("Password cannot be longer than 100 characters.");
        return false;
    }

    if (password !== $("#password_confirm").val()) {
        $("#error").html("Passwords do not match.");
        return false;
    }

    var username_ok = _.every(
        ["length_ok", "al_num_ok", "unique_ok"],
        id => $("#"+id).attr("valid") === "true"
    );

    if (!username_ok) {
        $("#error").html("Invalid username.");
        return false;
    }

    return true;
}

function try_register() {
    if (validate_form()) {
        $.post("/api/user/create", {
            username: $("#username").val(),
            password: $("#password").val()
        }, data => {
            if (data.success) {
                // user created
                window.location.href = "/";
            }
            else {
                $("#error").html("Could not create account.");
            }
        })
    }
}


$(document).ready(() => {
    $("input[type=text]").keyup(validate_username);
    $("input[type=text],input[type=password]").keyup((e) => {
        if ((e.which || e.keyCode) == 13) {
            try_register();
        }
    });
    $("#register").click(try_register);
    $("#username").focus();
});
