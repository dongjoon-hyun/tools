(function(){
    // jQuery Loading into electron
    window.$ = window.jQuery = require('./js/jquery.min.js');

    var app = angular.module('viewer', [])
        .controller('ClusterController', function($scope, $interval) {
            this.clusters = [];
            this.placeHolder = '192.168.99.100:8088';
            this.ip = this.placeHolder;
            this.selected = -1;

            var clusters = this.clusters;

            this.add = function() {
                this.clusters.push({
                    ip: this.ip,
                    name: this.ip.split(':')[0],
                    racks: {}
                });
                this.ip = this.placeHolder;
            };

            this.select = function(i) {
                this.selected = i;
                updateNodes(this.clusters[this.selected]);
            };

            this.delete = function(i) {
                this.clusters.splice(i, 1);
                if (this.selected == i) {
                    this.selected = this.clusters.length - 1;
                    if (this.selected >= 0) {
                        updateNodes(this.clusters[this.selected]);
                    }
                }
            };

            this.getSelected = function() {
                return this.clusters[this.selected];
            };

            this.getNumberOfNodes = function() {
                var count = 0;
                if (this.selected >= 0) {
                    for (var rack in this.getSelected().racks) {
                        count += rack.length;
                    }
                }
                return count;
            };

            this.getTotalNumberOfNodes = function() {
                var count = 0;
                this.clusters.forEach(function(cluster,index,array) {
                    for (var rack in cluster.racks) {
                        count += cluster.racks[rack].length;
                    }
                });
                return count;
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
                        cluster.racks = {};
                        data['slaves'].forEach(function(node) {
                            node['rack'] = '/default-rack';
                            if (!(node['rack'] in cluster.racks)) {
                                cluster.racks[node['rack']] = [];
                            }
                            cluster.racks[node['rack']].push({
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
                        cluster.racks = {};
                        data['nodes']['node'].forEach(function(node) {
                            if (!(node['rack'] in cluster.racks)) {
                                cluster.racks[node['rack']] = [];
                            }
                            cluster.racks[node['rack']].push({
                                rack: node['rack'],
                                hostName: node['nodeHostName'],
                                state: node['state'],
                                core: node['availableVirtualCores'],
                                usedCore: node['usedVirtualCores']+1,
                                mem: node['availMemoryMB'],
                                usedMem: node['usedMemoryMB']+10240
                            });
                        })
                    }).fail(function() {
                        cluster.racks = {};
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
        });
    app.filter('secondsToDateTime', [function() {
        return function(seconds) {
            return new Date(1970, 0, 1).setSeconds(seconds);
        };
    }]);
})();
