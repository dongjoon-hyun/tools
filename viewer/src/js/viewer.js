/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
(function(){
    // jQuery Loading into electron
    window.$ = window.jQuery = require('./js/jquery.min.js');

    var logs = [];

    $( document ).ajaxError(function( event, request, settings ) {
        if (logs.length > 1) {
            logs.splice(0, 1);
        }
        logs.push({'type':'ERROR', 'timeStamp':event.timeStamp, 'url': settings.url});
    });

    var app = angular.module('viewer', ['ui.layout'])
        .controller('ClusterController', function($scope, $interval) {
            this.clusters = [];
            this.placeHolder = '192.168.99.100:8088';
            this.ip = this.placeHolder;
            this.selected = -1;
            this.logs = logs;

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
                        count += this.getSelected().racks[rack].length;
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
                        cluster.color = 'ghostwhite';
                        updateNodes(cluster);
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
                        cluster.color = 'aliceblue';
                        data['slaves'].forEach(function(node) {
                            node['rack'] = '/default-rack';
                            if (!cluster.racks.hasOwnProperty(node['rack'])) {
                                cluster.racks[node['rack']] = [];
                            }
                            cluster.racks[node['rack']].push({
                                rack: node['rack'],
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
                    }).error(function() {
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
        })
        .directive('logList', function() {
            return {
                restrict: 'E',
                templateUrl: 'templates/log-list.html'
            };
        });
    app.filter('secondsToDateTime', [function() {
        return function(seconds) {
            return new Date(1970, 0, 1).setSeconds(seconds);
        };
    }]);
})();
