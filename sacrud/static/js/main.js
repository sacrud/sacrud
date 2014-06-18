requirejs.config({
  paths: {
    "app": "app",

    "jquery": "lib/jquery/dist/jquery.min",
    "chosen": "lib/chosen/public/chosen.jquery.min",
    "jquery-ui": "lib/jquery-ui/ui/minified/jquery-ui.min",
    "speakingurl": "lib/speakingurl/speakingurl.min",
    "jquery-ui-timepicker-addon": "lib/jqueryui-timepicker-addon/src/jquery-ui-timepicker-addon",

    "popup": "app/common/popup",
    "checkbox": "app/common/checkbox",
    "selectable": "app/common/selectable",
  },
  deps: ["jquery"],
});
