var addCluster = function() {
  var url = $('#newCluster').val();
  console.info(url);
  $('#cluster').append("<div class='cluster' alt='" + url + "' onclick='toggleActive(this)'>" + url + "</div>");
}

var updateClusters = function() {
  $('#cluster > .cluster').each(updateCluster)
  updateNode();
}

var updateCluster = function(index, element) {
  var url = $(this).attr('alt');
  var cluster = $(this);
  $.get('http://' + cluster.attr('alt') + '/ws/v1/cluster', '', function(data) {
    var info = data['clusterInfo'];
    cluster.empty();
    cluster.text(cluster.attr("alt"));
    cluster.append("<div class='cluster-info'>" + info['resourceManagerVersion'] + "</div>");
    cluster.append("<div class='cluster-info'>" + ((new Date() - info['startedOn'])/1000 | 0) + "</div>");
    cluster.append("<div class='cluster-info'>" + info['state'] + "</div>");
    cluster.append("<div class='cluster-info'>" + info['haState'] + "</div>");
  }).fail(function() {
    cluster.empty();
    cluster.text(cluster.attr("alt"));
    cluster.append("<div class='cluster-info'>Disconnected</div>");
  });
};

var toggleActive = function(item) {
  $('.cluster.active').removeClass('active');
  $(item).toggleClass('active');
};

var updateNode = function() {
  if ($('#cluster > .cluster.active').length == 0) {
    $('#nodes').empty();
  } else {
    var url = $('#cluster > .cluster.active').attr("alt");
    $.get('http://' + url + '/ws/v1/cluster/nodes', '', function(data) {
      var nodes = data['nodes']['node'];
      var html = '';
      $.each(nodes, function(i,v) {
        html += '<div class="node-info">' + v['nodeHostName'] + '</div>';
      });
      $('#nodes').html(html);
    }).fail(function() {
      $('#nodes').empty();
    });
  }
};

module.exports = updateClusters;
