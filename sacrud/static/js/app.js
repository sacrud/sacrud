requirejs.config({
    "baseUrl": "sa_static/js/lib",
    "paths": {
        "app": "../app",
        "jquery": "jquery/dist/jquery.min",
        "jquery-ui": "jquery-ui/ui/minified/jquery-ui.min"
    },
});

// Load the main app module to start the app
requirejs(["app/main"]);