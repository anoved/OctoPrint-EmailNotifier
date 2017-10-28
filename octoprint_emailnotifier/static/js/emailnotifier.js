$(function() {
    function EmailNotifierModel(parameters) {
        var self = this;

        // pull information from the custom bindings call below
        self.loginState = parameters[0];
        self.settingsViewModel = parameters[1];

        // we will set our settings variable right before bind so that the template can be binded correctly
        self.onBeforeBinding = function() {
            self.settings = self.settingsViewModel.settings;
        };

        // state variables
        self.testActive = ko.observable(false);
        self.testResult = ko.observable(false);
        self.testSuccessful = ko.observable(false);
        self.testMessage = ko.observable();

        self.testEmailConfiguration = function() {
            // set our state variables
            self.testActive(true);
            self.testResult(false);
            self.testSuccessful(false);
            self.testMessage("");

            var recipients = self.settings.plugins.emailnotifier.recipient_address();
            var smtp = self.settings.plugins.emailnotifier.mail_server();
            var smtp_port = self.settings.plugins.emailnotifier.mail_port();
            var smtp_tls = self.settings.plugins.emailnotifier.mail_tls();
            var smtp_ssl = self.settings.plugins.emailnotifier.mail_ssl();
            var user = self.settings.plugins.emailnotifier.mail_username();
            var alias = self.settings.plugins.emailnotifier.mail_useralias();
            var snapshot = self.settings.plugins.emailnotifier.include_snapshot();

            var payload = {
                command: "testmail",
                recipients: recipients,
                smtp: smtp,
                smtp_port: smtp_port,
                smtp_tls:smtp_tls,
                smtp_ssl:smtp_ssl,
                user: user,
                alias: alias,
                snapshot: snapshot
            };

            $.ajax({
                url: API_BASEURL + "plugin/emailnotifier",
                type: "POST",
                dataType: "json",
                data: JSON.stringify(payload),
                contentType: "application/json; charset=UTF-8",
                success: function(response) {
                    self.testResult(true);
                    self.testSuccessful(response.success);
                    if (!response.success && response.hasOwnProperty("msg")) {
                        self.testMessage(response.msg);
                    } else {
                        self.testMessage(undefined);
                    }
                },
                complete: function() {
                    self.testActive(false);
                }
            });
        };
    };

    ADDITIONAL_VIEWMODELS.push([
        EmailNotifierModel,
        ["loginStateViewModel", "settingsViewModel"],
        [document.getElementById("settings_plugin_emailnotifier")]
    ]);
});
