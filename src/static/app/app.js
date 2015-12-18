var app = angular.module('ubermax', ['ngRoute', 'angular-loading-bar', 'ngMaterial', 'uiGmapgoogle-maps', 'kendo.directives']);
//, 'ui.bootstrap'
//This configures the routes and associates each route with a view and a controller
app.config(function($routeProvider) {
    $routeProvider
        .when('/next', {
            controller: 'NextDest',
            templateUrl: 'app/partials/next_dest.html'
        })
        //Define a route that has a route parameter in it (:customerID)
        .otherwise({
            redirectTo: '/next'
        });
});

app.config(function($mdThemingProvider) {
    $mdThemingProvider.theme('default')
        .backgroundPalette('grey');
});
