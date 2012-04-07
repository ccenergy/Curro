/*
 * @file index.js
 * @author Charles 'Chuck' Cheung <charles@cc-labs.net>
 * @brief This file implements rpc-json ajax queries for sample objects
 */   

$(function() {
  
  /** jQuery extensions **/
  
  $.fn.disable = function () {
    $(this).attr('disabled','disabled');
    return this;
  }
  $.fn.enable = function () {
    $(this).removeAttr('disabled');
    return this;
  }
  $.fn.update = function(c) {
    if ($(this).html().length > 15) $(this).html(c);
    else $(this).append(c);
    return this;
  };
  
  // Events
  $("button").bind("click", function() {
    var id = $(this).attr('id');
    var method = ["attr"], params = [];
    $("button").disable();
    method.push(id);
    $("input").each( function() {
      params.push(parseInt($(this).val()));
    });
    rpcRequest("math", [method], params, id);
  });

  // AJAX
  $.ajaxSetup({
    url: '/',
    type: 'POST',
    timeout: 3000, // ms
    dataType: 'json',
    contentType: 'application/json',
    cache: false
  });
  
  // JSON-RPC
  rpcRequest = function(object, method, params, id) {
    var rpcData = {object:object, method:method, params:params, id:id};
    console.log(rpcData);
    var xhrObj = $.ajax({
        data: JSON.stringify(rpcData),
        success: function(result) {
          if (result.error != true) {
            $("#result ol").append('<li>'+JSON.stringify(result)+'</li>');
            $("#result").animate({ 
              scrollTop: $("#result").attr("scrollHeight") - $("#result").height() },
              0);
            console.log(result);
            $("#indicator").update('.');
          }
          else {
            $("#indicator").update('!');
          }
        },
        error: function(xhr, textStatus) {
          $("#indicator").update('!');
        },
        complete: function(xhr, textStatus) {
          $("button").enable();
          xhr = null;
        }
    });
  };
  
  rpcRequest("str",[["attr","helloworld"]],[],"helloworld");
  
});

