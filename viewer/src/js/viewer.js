(function(){
    // jQuery Loading into electron
    window.$ = window.jQuery = require('./js/jquery.min.js');

    var app = angular.module('viewer', [])
        .controller('ClusterController', function($scope, $interval) {
            this.clusters = [];
            this.nodes = [];
            this.placeHolder = '192.168.99.100:8088';
            this.ip = this.placeHolder;

            var clusters = this.clusters;
            var nodes = this.nodes;

            this.add = function() {
                this.clusters.push({
                    ip:this.ip,
                    resourceManagerVersion:'Unknown',
                    startedOn:'Unknown',
                    state:'Unknown',
                    haState:'Unknown'
                });
                this.ip = this.placeHolder;
            };

            var updateCluster = function(cluster) {
                var url = cluster.ip;
                $.get('http://' + url + '/ws/v1/cluster', '', function(data) {
                    var info = data['clusterInfo'];
                    cluster.resourceManagerVersion = info['resourceManagerVersion'];
                    cluster.startedOn = ((new Date() - info['startedOn'])/1000 | 0);
                    cluster.state = info['state'];
                    cluster.haState = info['haState'];
                }).fail(function() {
                    cluster.state = 'Disconnected';
                });
                updateNodes(cluster.ip);
            };

            var updateNodes = function(ip) {
                $.get('http://' + ip + '/ws/v1/cluster/nodes', '', function(data) {
                    nodes.length = 0;
                    data['nodes']['node'].forEach(function(node) { nodes.push(node); })
                }).fail(function() {
                    this.nodes = [];
                });
            };

            $scope.updateClusters = function() {
                clusters.forEach(updateCluster);
            };
            $interval(function() { $scope.updateClusters(); }, 2000);
        })
        .directive('clusterList', function() {
            return {
                restrict: 'E',
                templateUrl: 'templates/cluster-list.html'
            };
        })
        .directive('nodeList', function() {
            return {
                restrict: 'E',
                templateUrl: 'templates/node-list.html'
            };
        });
})();
