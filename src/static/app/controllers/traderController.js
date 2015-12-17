app.controller('Trader', function($scope, $mdToast, $animate, $mdDialog) {

    init();

    function init() {
        $scope.orderRequests = [];
        $scope.cancelRequests = [];
        $scope.trades = [];
        $scope.positions = [];
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

    function cleanOrderJSON(order) {
        var jsonMsg = {};
        jsonMsg.value0 = jQuery.extend(true, {}, order);
        delete jsonMsg.value0.$$hashKey;
        delete jsonMsg.value0.hasChanged;
        delete jsonMsg.value0.localNew;
        return JSON.stringify(jsonMsg);
    }

    var ws = new WebSocket("ws://192.168.1.12:9007/trader");
    ws.onopen = function(evt) {
        console.log('Trader websocket opened');
    };

    ws.onerror = function(evt) {
      console.log('Trader websocket error');
      $mdDialog.show(
        $mdDialog.alert()
          .parent(angular.element(document.body))
          .title('Trader websocket error')
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

        if ('_msg_type' in data) {
            switch (data._msg_type) {
                case 'OrderRequest':
                    var i = 0;
                    for (; i < $scope.orderRequests.length; ++i) {
                        if ($scope.orderRequests[i].requestId == data.requestId) {
                            $scope.orderRequests[i] = data;
                            showToast('Order status updated');
                            return;
                        }
                    }
                    if (i >= $scope.orderRequests.length) {
                        $scope.orderRequests.push(data);
                        showToast('New order placed');
                    }
                    break;
                case 'TradeRecord':
                    $scope.trades.push(data);
                    showToast('New trade');
                    break;
                case 'CancelRequest':
                    $scope.cancelRequests.push(data);
                    break;
            }
        } else {
            $scope.positions = data;
        }
    };

});
