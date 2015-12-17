app.controller('Arbitrager', function($scope, $mdToast, $animate, $mdDialog) {

    init();

    function init() {
        $scope.longFutureOrder = {};
        $scope.shortFutureOrder = {};
    };

    $scope.toastPosition = {
        bottom: false,
        top: true,
        left: false,
        right: true
    };

    $scope.getToastPosition = function() {
        return Object.keys($scope.toastPosition)
            .filter(function(pos) {
                return $scope.toastPosition[pos];
            })
            .join(' ');
    };

    function showToast(msg) {
        $mdToast.show(
            $mdToast.simple()
            .content(msg)
            .position($scope.getToastPosition())
            .action('OK')
            .highlightAction(true)
            .hideDelay(4000)
        );
    }

    var ws = new WebSocket("ws://192.168.1.12:9007/arbitrager");
    var ws_place_order = new WebSocket("ws://192.168.1.12:9007/autoArbitrager");

    ws_place_order.onopen = function(evt) {
        console.log('Auto Arbitrager websocket opened');
    };

    ws_place_order.onerror = function(evt) {
        console.log('Auto Arbitrager websocket error');
    };

    ws.onopen = function(evt) {
        console.log('Arbitrager websocket opened');
    };

    ws.onerror = function(evt) {
      console.log('Arbitrager websocket error');
      $mdDialog.show(
        $mdDialog.alert()
          .parent(angular.element(document.body))
          .title('Arbitrager websocket error')
          .content('Please check your connection with server.')
          .ariaLabel('Alert Dialog')
          .ok('Ok')
      );
    };

    ws.onclose = function(evt) {
      console.log('Trader websocket error');
      $mdDialog.show(
        $mdDialog.alert()
          .parent(angular.element(document.body))
          .title('Trader websocket disconnected')
          .content('Please check your connection with server.')
          .ariaLabel('Alert Dialog')
          .ok('Ok')
      );
    };

    ws.onmessage = function(evt) {
        var data = JSON.parse(evt.data).value0;
        if (data.direction == 0) {
            $scope.longFutureOrder = data;

        } else {
            $scope.shortFutureOrder = data;
        }
        $scope.$apply();
    };

    $scope.placeOrder = function() {
      ws_place_order.send("placeOrder");
    }
});
