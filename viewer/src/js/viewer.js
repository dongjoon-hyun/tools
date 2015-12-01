(function(){
    // jQuery Loading into electron
    window.$ = window.jQuery = require('./js/jquery.min.js');

    var app = angular.module('viewer', [])
        .controller('ClusterController', function($scope, $interval) {
            this.clusters = [];
            this.placeHolder = '192.168.99.100:8088';
            this.ip = this.placeHolder;
            this.selected = 0;

            var clusters = this.clusters;

            this.add = function() {
                this.clusters.push({
                    ip: this.ip,
                    name: this.ip.split(':')[0],
                    nodes: []
                });
                this.ip = this.placeHolder;
            };

            this.select = function(i) {
                this.selected = i;
                updateNodes(this.clusters[this.selected]);
            };

            this.getSelected = function() {
                return this.clusters[this.selected];
            };

            var updateCluster = function(cluster) {
                if (cluster.ip.endsWith('8088')) {
                    $.get('http://' + cluster.ip + '/ws/v1/cluster', '', function(data) {
                        var info = data['clusterInfo'];
                        cluster.resourceManagerType = 'YARN';
                        cluster.resourceManagerVersion = info['resourceManagerVersion'];
                        cluster.startedOn = ((new Date() - info['startedOn'])/1000 | 0);
                        cluster.state = info['state'];
                        cluster.haState = info['haState'];
                    }).fail(function() {
                        cluster.state = 'Disconnected';
                    });
                } else if (cluster.ip.endsWith('5050')) {
                    $.get('http://' + cluster.ip + '/master/state.json', '', function(data) {
                        cluster.resourceManagerType = 'MESOS';
                        cluster.resourceManagerVersion = data['version'];
                        cluster.startedOn = ((new Date() - data['start_time'])/1000 | 0);
                        cluster.state = 'STARTED';
                        cluster.haState = 'Unknown';
                        cluster.nodes.length = 0;
                        data['slaves'].forEach(function(node) {
                            cluster.nodes.push({
                                rack: '/default-rack',
                                hostName: node['hostname'],
                                state: node['active'] ? 'RUNNING' : 'INACTIVE',
                                core: node['resources'].cpus,
                                usedCore: node['used_resources'].cpus,
                                mem: node['resources'].mem,
                                usedMem: node['used_resources'].mem
                            });
                        })
                    }).fail(function() {
                        cluster.state = 'Disconnected';
                    });
                }
                updateNodes(cluster);
            };

            var updateNodes = function(cluster) {
                if (cluster.ip.endsWith('8088')) {
                    $.get('http://' + cluster.ip + '/ws/v1/cluster/nodes', '', function(data) {
                        cluster.nodes.length = 0;
                        data['nodes']['node'].forEach(function(node) {
                            cluster.nodes.push({
                                rack: node['rack'],
                                hostName: node['nodeHostName'],
                                state: node['state'],
                                core: node['availableVirtualCores'],
                                usedCore: node['usedVirtualCores'],
                                mem: node['availMemoryMB'],
                                usedMem: node['usedMemoryMB']
                            });
                        })
                    }).fail(function() {
                        cluster.nodes.length = 0;
                    });
                } else if (cluster.ip.endsWith('5050')) {
                    // already done.
                }
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
        })
        .filter('secondsToDateTime', [function() {
            return function(seconds) {
                return new Date(1970, 0, 1).setSeconds(seconds);
            };
        }]);
})();
