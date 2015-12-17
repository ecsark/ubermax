app.controller('NextDest', function($scope, $mdToast, $mdDialog, $animate, $log, $mdMedia, $http, $timeout) {

    $scope.map = { center: { latitude: 40.7733923, longitude: -73.9686394 }, zoom: 12};

    $scope.options = {scrollwheel: false};
    $scope.coordsUpdates = 0;
    $scope.dynamicMoveCtr = 0;
    $scope.start_time = null;
    $scope.end_time = null;
    $scope.result_markers = [];
    $scope.marker_st = {
      id: 0,
      coords: {
        latitude: 40.8047413,
        longitude: -73.9653582
      },
      options: { draggable: true },
      events: {
        dragend: function (marker, eventName, args) {
          $log.log('marker dragend');
          var lat = marker.getPosition().lat();
          var lon = marker.getPosition().lng();
          $log.log(lat);
          $log.log(lon);

          $scope.marker_st.options = {
            draggable: true,
            labelContent: "lat: " + $scope.marker_st.coords.latitude + ' ' + 'lon: ' + $scope.marker_st.coords.longitude,
            labelAnchor: "100 0",
            labelClass: "marker-labels"
          };

          var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && $scope.customFullscreen;
          $mdDialog.show({
            controller: DialogController,
            templateUrl: 'static/app/partials/time_picker.html',
            parent: angular.element(document.body),
            targetEvent: eventName,
            clickOutsideToClose:true,
            fullscreen: useFullScreen
          })
          .then(function(time) {
            $scope.start_time = time;
          }, function() {
          });
          $scope.$watch(function() {
            return $mdMedia('xs') || $mdMedia('sm');
          }, function(wantsFullScreen) {
            $scope.customFullscreen = (wantsFullScreen === true);
          });

        }
      }
    };

    $scope.marker_ed = {
      id: 1,
      coords: {
        latitude: 40.7089968,
        longitude: -73.9543139
      },
      options: { draggable: true },
      events: {
        dragend: function (marker, eventName, args) {
          $log.log('marker dragend');
          var lat = marker.getPosition().lat();
          var lon = marker.getPosition().lng();
          $log.log(lat);
          $log.log(lon);

          $scope.marker_ed.options = {
            draggable: true,
            labelContent: "lat: " + $scope.marker_ed.coords.latitude + ' ' + 'lon: ' + $scope.marker_ed.coords.longitude,
            labelAnchor: "100 0",
            labelClass: "marker-labels"
          };

          var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && $scope.customFullscreen;
          $mdDialog.show({
            controller: DialogController,
            templateUrl: 'static/app/partials/time_picker.html',
            parent: angular.element(document.body),
            targetEvent: eventName,
            clickOutsideToClose:true,
            fullscreen: useFullScreen
          })
          .then(function(time) {
            $scope.end_time = time;
            $scope.status = 'You said the information was "' + time + '".';
          }, function() {
            $scope.status = 'You cancelled the dialog.';
          });
          $scope.$watch(function() {
            return $mdMedia('xs') || $mdMedia('sm');
          }, function(wantsFullScreen) {
            $scope.customFullscreen = (wantsFullScreen === true);
          });
        }
      }
    };

    var createResultMarker = function(latitude, longitude, value, id) {
          var ret = {
            latitude: latitude,
            longitude: longitude,
            title: 'm' + id
          };
          ret["id"] = id;//$scope.result_markers.length();
          return ret;
    };

    $scope.toastPosition = {
        bottom: true,
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
    /*$scope.$watchCollection("marker.coords", function (newVal, oldVal) {
      if (_.isEqual(newVal, oldVal))
        return;
      $scope.coordsUpdates++;
    });
    $timeout(function () {
      $scope.marker_st.coords = {
          latitude: 40.8047413,
          longitude: -73.9653582
      };
      $scope.dynamicMoveCtr++;
      $timeout(function () {
        $scope.marker_st.coords = {
            latitude: 40.8047413,
            longitude: -73.9653582
        };
        $scope.dynamicMoveCtr++;
      }, 2000);
  }, 1000);*/
  $scope.query = function() {
      if ($scope.start_time && $scope.end_time) {
          if ($scope.start_time >= $scope.end_time) {
              showToast("Start time should be earlier than end time.");
              return;
          }
          var target = "/next/";
          function makeLocationTime(marker, time) {
              var t = marker.coords.latitude.toString() + "," + marker.coords.longitude.toString();
              return t + "@" + time.getTime().toString();
          }
          $http.get(target + makeLocationTime($scope.marker_st, $scope.start_time) + "/" + makeLocationTime($scope.marker_ed, $scope.end_time))
          .then(function(response) {
              var results = JSON.parse(response.data);
              var res = []
              for(var i=0; i< results.length; ++i) {
                  var r = results[i];
                 res.push(createResultMarker(r[0][0], r[0][1], r[1], i+2));
              };

              $scope.result_markers = res;
          });
      } else if (!$scope.start_time) {
          showToast("Please specify start time.");
          return;
      } else if (!$scope.end_time) {
          showToast("Please specify end time.");
          return;
      }
  }
});


function DialogController($scope, $mdDialog) {
  $scope.hide = function() {
    $mdDialog.hide();
  };
  $scope.cancel = function() {
    $mdDialog.cancel();
  };
  $scope.answer = function(answer) {
    $mdDialog.hide(answer);
  };
}