var router = require('express').Router();
var EventEmitter = require('events').EventEmitter;
//messagebus for client requests
var messageBus = new EventEmitter();

    
router.get('/', function(req, res){
    res.render('websocket');
});

var WebSocketServer = require('websocket').server;
var http = require('http');
var server = http.createServer(function(request, response) {
    console.log((new Date()) + ' Received request for ' + request.url);
    response.writeHead(404);
    response.end();
});

server.listen(3001, function() {
    console.log((new Date()) + ' Server is listening on port 3001');
});
var wss = new WebSocketServer({
    httpServer: server,
    autoAcceptConnections: false
});

function originIsAllowed(origin) {
  return true;
}



wss.on('request', function (req) {
    

    
    var conn = req.accept(null, req.origin);
    console.log((new Date()) + ' Connection accepted.');
    
    
   conn.on('message', function(data){
        messageBus.once('message', function(data_m){
        conn.sendUTF(data_m.utf8Data);
        });
        
        messageBus.emit('message', data)
    });

    conn.on('close', function(reasonCode, description) {
        console.log((new Date()) + ' Peer ' + conn.remoteAddress + ' disconnected.');
    });
});

module.exports = router;