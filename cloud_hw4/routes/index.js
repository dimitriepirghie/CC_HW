var express = require('express');
var router = express.Router();


router.get('/', function(req, res, next) {
  res.send('bla bla');
});

router.post('/', function (req, res) {
  console.log(req.body);
  res.send('You`ve sent: ' + req.body);
});

module.exports = router;
