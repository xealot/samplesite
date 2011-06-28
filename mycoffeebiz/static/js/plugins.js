window.log = function(){
  log.history = log.history || [];
  log.history.push(arguments);
  arguments.callee = arguments.callee.caller;  
  if(this.console) console.log( Array.prototype.slice.call(arguments) );
};
(function(b){function c(){}for(var d="assert,count,debug,dir,dirxml,error,exception,group,groupCollapsed,groupEnd,info,log,markTimeline,profile,profileEnd,time,timeEnd,trace,warn".split(","),a;a=d.pop();)b[a]=b[a]||c})(window.console=window.console||{});



//JSON-RPC
(function($){
    if (typeof JSON == 'undefined') {
        throw "Must include JSON2";
    }

    $.rpc = $.rpc || function(url, options) {
        var jqXHR,
            dfd = $.Deferred(),
            ajaxOptions = {
                contentType: 'application/json',
                dataType:  'jsonp',
                processData: true
            },
            data = {
                id: 1, //Hardcoded until we implement pipeline.
                jsonrpc: '2.0',
                method: options.method || 'system.listMethods',
                params: options.params || []
            };

        ajaxOptions.data = {payload: JSON.stringify(data)};

        jqXHR = $.ajax(url, ajaxOptions);
        jqXHR.success(function(data, textStatus, jqXHR) {
            if (data.error) {
                dfd.rejectWith({}, [data.error.reason]);
            } else {
                dfd.resolveWith({}, [data.result]);
            }
        });
        jqXHR.error(function(jqXHR, textStatus, errorThrown) {
            dfd.reject();
        });

        return dfd.promise();
    };
})(jQuery);