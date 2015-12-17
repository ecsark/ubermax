var app = angular.module('sandglass', ['ngRoute', 'angular-loading-bar', 'ngMaterial', 'uiGmapgoogle-maps', 'kendo.directives']);
//, 'ui.bootstrap'
//This configures the routes and associates each route with a view and a controller
app.config(function($routeProvider) {
    $routeProvider
        .when('/next', {
            controller: 'NextDest',
            templateUrl: 'app/partials/next_dest.html'
        })
        .when('/trader', {
            controller: 'Trader',
            templateUrl: 'app/partials/trader.html'
        })
        .when('/arbitrager', {
            controller: 'Arbitrager',
            templateUrl: 'app/partials/arbitrager.html'
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

app.controller('AppCtrl', function($scope, $mdSidenav, $mdUtil, $location) {
    $scope.toggleLeft = buildToggler('left');
    $scope.toggleRight = buildToggler('right');

    $scope.navmap = [{
        name: 'Basket',
        url: '/basket'
    }, {
        name: 'Trader',
        url: '/trader'
    }, {
        name: 'Arbitrager',
        url: '/arbitrager'
    }];

    function findPageName(url) {
        for (var i = 0; i < $scope.navmap.length; ++i) {
            if ($scope.navmap[i].url == url)
                return $scope.navmap[i].name;
        }
    }

    $scope.pageName = findPageName($location.path());

    $scope.gotoPage = function(url, name) {
        $location.path(url);
        $scope.pageName = name;
    };

    /**
     * Build handler to open/close a SideNav
     */
    function buildToggler(navID) {
        var debounceFn = $mdUtil.debounce(function() {
            $mdSidenav(navID)
                .toggle();
        }, 300);
        return debounceFn;
    }
});
app.controller('LeftCtrl', function($scope, $mdSidenav, $location) {
    $scope.close = function() {
        $mdSidenav('left').close();
    };
})
