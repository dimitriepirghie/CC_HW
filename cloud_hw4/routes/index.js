var express = require('express');
var router = express.Router();
var EventEmitter = require('events').EventEmitter;
//messagebus for client requests
var messageBus = new EventEmitter();

//renders index view
router.get('/', function(req, res) {
  res.render('index', {title: 'Bla bla'});
});

//subscribe request
router.get('/messages', function(req, res){
   var msgListener = function(res){
       messageBus.once('message', function(data){
          res.json(data); 
       });
   }
   msgListener(res);
});

//emit message
router.post('/messages', function(req, res){
    messageBus.emit('message', req.body);
    res.status(200).end();
})



router.post('/', function (req, res) {
  console.log(req.body);
  res.send('You`ve sent: ' + req.body);
});

module.exports = router;
